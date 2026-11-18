#!/usr/bin/env python3
"""Formal Table 2 local subset: SCTBench reorder thread series, PERIOD vs Serial.

Three attempts per setting (course minimum; the paper used ten). Depth 3, budget
10000, assertion-based targets, first-failure replay with bounded retry. A search
with zero buggy schedules is a valid not_found outcome, not a tool error.
"""
import argparse
import json
import os
import re
import resource
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from run_table1_pilot import (REPO, ROOT, digest, environment, execute, save)
from validate_reorder3_ipc import OBSERVER, protected_ast

CONFIG_PATH = REPO / 'config/table2-local-comparison.json'
SUBJECT_PREFIX = 'CS.'


def load_config():
    return json.loads(CONFIG_PATH.read_text(encoding='utf-8'))


def validate_config(config):
    if config.get('status') != 'formal-table2-subset':
        raise ValueError('Configuration is not the reviewed Table 2 subset')
    if [m.get('name') for m in config.get('methods', [])] != ['period', 'serial']:
        raise ValueError('Formal configuration must run period then serial')
    for method in config['methods']:
        if method.get('driver') not in ('run_PDS.py', 'run_OldPDS.py'):
            raise ValueError('Unexpected driver: ' + str(method.get('driver')))
        if not (REPO / method['patch']).is_file():
            raise ValueError('Missing patch: ' + method['patch'])
    names = [m['name'] for m in config['methods']]
    if set(config.get('method_subjects', {})) != set(names):
        raise ValueError('method_subjects must define exactly the configured methods')
    if config['method_subjects']['period'] != config['subjects']:
        raise ValueError('PERIOD must cover all selected subjects')
    for key, expected in [('depth', 3), ('schedule_budget', 10000),
                          ('attempts_per_subject', 3), ('child_timeout_seconds', 5),
                          ('outer_timeout_seconds', 300), ('replay_attempts', 3)]:
        if type(config.get(key)) is not int or config[key] != expected:
            raise ValueError('Configuration differs from the reviewed setup: ' + key)
    if config.get('interactive') is not False or config.get('expected_diagnostic') != 'Assertion':
        raise ValueError('Unexpected interactive/expected diagnostic setting')


def prepare(config):
    base = Path('/root/cs340-period/table2')
    base.mkdir(parents=True, exist_ok=True)
    output = Path(tempfile.mkdtemp(prefix=config['experiment_id'] + '-', dir=str(base)))
    print('Evidence directory: ' + str(output), flush=True)
    save(output / 'config.json', config)
    shutil.copy2(str(REPO / 'scripts/linux/run_table2_formal.py'),
                 str(output / 'run_table2_formal.py'))
    shutil.copy2(str(REPO / 'licenses/PERIOD-MIT.txt'), str(output / 'LICENSE.PERIOD.txt'))
    (output / 'observe_driver.py').write_text(OBSERVER, encoding='utf-8')
    manifest = {
        'experiment_id': config['experiment_id'],
        'config_sha256': digest(CONFIG_PATH),
        'runner_sha256': digest(Path(__file__)),
        'upstream_commit': ROOT.name,
        'kernel': os.uname().release,
        'python': sys.version,
        'cpu_affinity': sorted(os.sched_getaffinity(0)),
        'methods': {}, 'targets': {}, 'frozen_driver_files': {},
        'upstream_driver_hashes': {}, 'original_hashes': {}, 'runs': [],
        'started_utc': datetime.now(timezone.utc).isoformat(),
        'status': 'preparing',
    }
    env = environment()
    for method in config['methods']:
        name = method['name']
        driver_dir = output / ('driver-' + name)
        driver_dir.mkdir()
        for src in sorted((ROOT / 'tool/DBDS').glob('*.py')):
            shutil.copy2(str(src), str(driver_dir / src.name))
            manifest['upstream_driver_hashes'][str(src)] = digest(src)
        patch = REPO / method['patch']
        applied = execute(['patch', '--batch', '--fuzz=0',
                           str(driver_dir / method['driver']), str(patch)],
                          output, env, 'patch-' + name, 30)
        if applied['exit_code'] or applied['outer_timeout']:
            raise RuntimeError('Patch failed for method ' + name)
        if name == 'period':
            upstream = (ROOT / 'tool/DBDS/run_PDS.py').read_text(encoding='utf-8')
            patched = (driver_dir / 'run_PDS.py').read_text(encoding='utf-8')
            if protected_ast(upstream) != protected_ast(patched):
                raise RuntimeError('Period patch changed protected control flow')
            protected = True
        else:
            protected = None
        manifest['methods'][name] = {
            'driver': method['driver'], 'driver_sha256': digest(driver_dir / method['driver']),
            'patch': method['patch'], 'patch_sha256': digest(patch),
            'protected_ast_unchanged': protected,
        }
        manifest['frozen_driver_files'][name] = {
            path.name: digest(path) for path in sorted(driver_dir.glob('*.py'))
        }
    manifest['frozen_driver_files']['observe_driver.py'] = digest(output / 'observe_driver.py')
    save(output / 'manifest.json', manifest)

    probe = execute([sys.executable, str(REPO / 'scripts/linux/probe_deadline.py')],
                    output, env, 'deadline-probe', 15)
    if probe['exit_code'] or probe['outer_timeout']:
        raise RuntimeError('Scheduler probe failed')
    versions = ''
    versions += subprocess_check(['dpkg-query', '-W', 'gcc', 'g++', 'libc6', 'python3',
                                  'python-numpy'], env)
    versions += subprocess_check(['clang', '--version'], env)
    versions += subprocess_check(['gcc', '--version'], env)
    (output / 'tool-versions.txt').write_text(versions, encoding='utf-8')

    for subject in config['subjects']:
        binary = subject + '_bad'
        source = ROOT / 'evaluation/CS' / subject
        build = output / 'build' / subject
        build.mkdir(parents=True)
        for name in [binary + '.c', 'README.md']:
            shutil.copy2(str(source / name), str(build / name))
            manifest['original_hashes'][str(source / name)] = digest(source / name)
        build_env = environment()
        build_env['Con_PATH'] = str(build / ('ConConfig.' + binary))
        commands = [
            ['clang', '-g', '-emit-llvm', '-c', './' + binary + '.c', '-o', binary + '.bc'],
            ['bash', str(ROOT / 'tool/staticAnalysis/staticAnalysis.sh'), binary],
            [str(ROOT / 'tool/staticAnalysis/DBDS-INSTRU/dbds-clang-fast++'), '-g',
             './' + binary + '.bc', '-o', binary, '-lpthread', '-ldl'],
        ]
        for index, command in enumerate(commands):
            result = execute(command, build, build_env, 'build-' + str(index + 1), 300)
            if result['exit_code'] or result['outer_timeout']:
                raise RuntimeError('Build failed: ' + str(build))
        dump = subprocess_check(['readelf', '--debug-dump=info', str(build / binary)], env)
        start = dump.index(': Sched_Info')
        excerpt = dump[start:start + 7000]
        (build / 'target-dwarf.txt').write_text(excerpt, encoding='utf-8')
        for pattern in [r'DW_AT_byte_size\s*:\s*24008', r'DW_AT_data_member_location:\s*8148',
                        r'DW_AT_data_member_location:\s*16076']:
            if not re.search(pattern, excerpt):
                raise RuntimeError('Unexpected target ABI: ' + subject)
        manifest['targets'][subject] = {
            name: digest(build / name) for name in [binary, binary + '.c', 'ConConfig.' + binary]
        }
        save(output / 'manifest.json', manifest)
        print('Built and ABI checked: ' + subject, flush=True)

    manifest['runtime_build_file_hashes'] = {
        name: digest(ROOT / name) for name in
        ['tool/staticAnalysis/DBDS-INSTRU/llvm-mode/DBDSFunction.cpp',
         'tool/staticAnalysis/DBDS-INSTRU/dbds-clang-fast++',
         'tool/staticAnalysis/staticAnalysis.sh']
    }
    manifest['status'] = 'prepared'
    save(output / 'manifest.json', manifest)
    return output


def subprocess_check(command, env):
    import subprocess
    return subprocess.check_output(command, env=env).decode()


def parse_search(text, errors):
    if 'End Testing!' not in text or 'Candidate IPC ABI: size=24008' not in text:
        return {}, 'incomplete_search'
    result = {}
    for key, pattern in [('schedules', r'^Round\s+\d+\s+(\d+)'),
                         ('error_schedules', r'Total Error Interleavings:\s*(\d+)'),
                         ('timeouts', r'Total Timeouts Interleavings:\s*(\d+)')]:
        match = re.search(pattern, text, re.M)
        if not match:
            return result, 'missing_metric_' + key
        result[key] = int(match.group(1))
    match = re.search(r'^Time\s+\S+\s+(\d+):(\d+):([\d.]+)', text, re.M)
    if not match:
        return result, 'missing_tool_time'
    h, m, s = match.groups()
    result['tool_elapsed_seconds'] = 3600 * int(h) + 60 * int(m) + float(s)
    if result['error_schedules'] != len(errors) or result['timeouts']:
        return result, 'error_count_mismatch_or_timeout'
    if errors:
        indices = [int(p.name.split('_')[1]) for p in errors]
        result['first_bug_schedule'] = min(indices)
        result['found'] = True
        if max(indices) > result['schedules']:
            return result, 'failure_schedule_index_mismatch'
    else:
        result['first_bug_schedule'] = None
        result['found'] = False
    result['effective_depth_confirmed'] = 'bugDepth: 3' in text
    if not result['effective_depth_confirmed']:
        return result, 'effective_depth_not_confirmed'
    return result, None


def search_attempt(attempt, output, config, subject, binary, build, driver):
    cwd = attempt / 'search'
    cwd.mkdir(parents=True)
    for name in [binary, binary + '.c', 'ConConfig.' + binary]:
        shutil.copy2(str(build / name), str(cwd / name))
    command = ['unshare', '--ipc', '--fork', sys.executable, '-u',
               str(output / 'observe_driver.py'), str(driver), '-y', '-d', str(config['depth']),
               '-f', str(config['schedule_budget']), '-t', str(config['child_timeout_seconds']),
               './' + binary]
    env = environment()
    env['CS340_TARGET_EXITS'] = str(cwd / 'target-exits.jsonl')
    result = execute(command, cwd, env, 'search', config['outer_timeout_seconds'])
    text = re.sub(r'\x1b\[[0-9;]*m', '', (cwd / 'search.log').read_text(
        encoding='utf-8', errors='replace'))
    errors = sorted((cwd / ('out_' + binary + '_1') / 'Errors').glob('*'))
    parsed, issue = parse_search(text, errors)
    result.update(parsed)
    if (issue == 'incomplete_search' and 'Perform Dry Run!' in text
            and 'Perform DBDS Run' not in text and 'Aborted' in text):
        issue = 'dry_run_abort'
        result['dry_run_abort'] = True
    result['validation_issue'] = issue
    save(cwd / 'search.result.json', result)
    return result


def replay_attempt(attempt, output, config, binary, build, driver, index):
    cwd = attempt / ('replay' if index == 1 else 'replay-try-' + str(index))
    cwd.mkdir(parents=True)
    for name in [binary, binary + '.c', 'ConConfig.' + binary]:
        shutil.copy2(str(build / name), str(cwd / name))
    errors = sorted((attempt / 'search' / ('out_' + binary + '_1') / 'Errors').glob('*'))
    if not errors:
        raise RuntimeError('No saved failure available: ' + str(attempt))
    shutil.copy2(str(errors[0]), str(cwd / 'failure.schedule'))
    command = ['unshare', '--ipc', '--fork', sys.executable, '-u',
               str(output / 'observe_driver.py'), str(driver), '-y', '-d', str(config['depth']),
               '-f', str(config['schedule_budget']), '-t', str(config['child_timeout_seconds']),
               '-r', 'failure.schedule', './' + binary]
    env = environment()
    env['CS340_TARGET_EXITS'] = str(cwd / 'target-exits.jsonl')
    label = 'replay' if index == 1 else 'replay-try-' + str(index)
    result = execute(command, cwd, env, label, config['outer_timeout_seconds'])
    text = re.sub(r'\x1b\[[0-9;]*m', '',
                  (cwd / (label + '.log')).read_text(encoding='utf-8', errors='replace'))
    exits = []
    if (cwd / 'target-exits.jsonl').is_file():
        exits = [json.loads(line)['returncode'] for line in
                 (cwd / 'target-exits.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()]
    last_exit = exits[-1] if exits else None
    confirmed = ('Perform Reproduction!' in text and 'Bug found!' in text
                 and 'Assertion' in text and binary in text and last_exit in (1, -6))
    dry_abort = ('Perform Reproduction!' not in text and 'Perform Dry Run!' in text
                 and ('Assertion' in text or 'Aborted' in text))
    result.update({'observed_child_exits': exits, 'last_child_exit': last_exit,
                   'diagnostic_confirmed': confirmed, 'dry_run_abort': dry_abort})
    result['status'] = ('confirmed' if confirmed else
                        ('dry_run_asan_abort' if dry_abort else
                         ('ran_without_expected_diagnostic' if 'Perform Reproduction!' in text
                          else 'other_error')))
    save(cwd / 'replay.result.json', result)
    return result


def run_formal(output, config):
    manifest = json.loads((output / 'manifest.json').read_text(encoding='utf-8'))
    if manifest['status'] != 'prepared':
        raise RuntimeError('Only a freshly prepared directory can run')
    if digest(Path(__file__)) != manifest['runner_sha256']:
        raise RuntimeError('Runner changed after preparation')
    if digest(CONFIG_PATH) != manifest['config_sha256']:
        raise RuntimeError('Configuration changed after preparation')
    for method in config['methods']:
        name = method['name']
        if digest(output / ('driver-' + name) / method['driver']) != manifest['methods'][name]['driver_sha256']:
            raise RuntimeError('Driver changed after preparation: ' + name)
        for file_name, expected in manifest['frozen_driver_files'][name].items():
            if digest(output / ('driver-' + name) / file_name) != expected:
                raise RuntimeError('Frozen driver changed: ' + name + '/' + file_name)
    manifest['status'] = 'running'
    save(output / 'manifest.json', manifest)

    for attempt_number in range(1, config['attempts_per_subject'] + 1):
        for method in config['methods']:
            name = method['name']
            driver = output / ('driver-' + name) / method['driver']
            for subject in config['method_subjects'][name]:
                binary = subject + '_bad'
                build = output / 'build' / subject
                attempt = output / 'runs' / name / subject / ('run-' + str(attempt_number))
                attempt.mkdir(parents=True)
                record = {'method': name, 'case': subject, 'run': attempt_number, 'status': 'started'}
                manifest['runs'].append(record)
                save(output / 'manifest.json', manifest)
                search = search_attempt(attempt, output, config, subject, binary, build, driver)
                record['search'] = search
                if search.get('dry_run_abort'):
                    record['status'] = 'aborted_at_dry_run'
                    save(output / 'manifest.json', manifest)
                    print('%s %s run %d: dry-run abort; counted and continuing' % (
                        name, subject, attempt_number), flush=True)
                    continue
                if search.get('validation_issue'):
                    record['status'] = 'needs_inspection'
                    save(output / 'manifest.json', manifest)
                    raise RuntimeError('Stopped for inspection; preserving attempt: ' + str(attempt))
                if not search.get('found'):
                    record['status'] = 'not_found'
                    save(output / 'manifest.json', manifest)
                    print('%s %s run %d: not_found within budget; recorded' % (
                        name, subject, attempt_number), flush=True)
                    continue
                confirmed = False
                invalid = False
                tries = []
                for index in range(1, config['replay_attempts'] + 1):
                    replay = replay_attempt(attempt, output, config, binary, build, driver, index)
                    tries.append(replay)
                    record['replay_tries'] = tries
                    if replay['status'] == 'confirmed':
                        confirmed = True
                        record['replay'] = replay
                        break
                    if replay['status'] == 'dry_run_asan_abort':
                        continue
                    if replay['status'] == 'ran_without_expected_diagnostic':
                        invalid = True
                        record['replay'] = replay
                        break
                    record['status'] = 'needs_inspection'
                    save(output / 'manifest.json', manifest)
                    raise RuntimeError('Replay timeout or unexpected state: ' + str(attempt))
                record['status'] = ('completed' if confirmed else
                                    ('invalid_replay' if invalid else
                                     'replay_unverified_at_dry_run'))
                save(output / 'manifest.json', manifest)
                print('%s %s run %d: %s (replay tries=%d)' % (
                    name, subject, attempt_number, record['status'], len(tries)), flush=True)

    manifest['aborted_at_dry_run'] = sum(
        1 for r in manifest['runs'] if r.get('status') == 'aborted_at_dry_run')
    manifest['invalid_replay'] = sum(
        1 for r in manifest['runs'] if r.get('status') == 'invalid_replay')
    manifest['replay_unverified'] = sum(
        1 for r in manifest['runs'] if r.get('status') == 'replay_unverified_at_dry_run')
    manifest['not_found'] = sum(1 for r in manifest['runs'] if r.get('status') == 'not_found')
    manifest['originals_unchanged'] = (
        all(digest(Path(path)) == value for path, value in manifest['original_hashes'].items())
        and all(digest(Path(path)) == value for path, value in manifest['upstream_driver_hashes'].items()))
    manifest['status'] = 'formal_completed' if manifest['originals_unchanged'] else 'original_changed'
    manifest['ended_utc'] = datetime.now(timezone.utc).isoformat()
    save(output / 'manifest.json', manifest)
    if not manifest['originals_unchanged']:
        raise RuntimeError('Original files changed')
    print('Table 2 formal runs completed: ' + str(output), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=['prepare', 'run'], required=True)
    parser.add_argument('--directory')
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    config = load_config()
    validate_config(config)
    if args.phase == 'prepare':
        prepare(config)
    else:
        if not args.directory:
            parser.error('--directory is required for run')
        output = Path(args.directory).resolve()
        if json.loads((output / 'config.json').read_text(encoding='utf-8')) != config:
            raise RuntimeError('Configuration changed after preparation')
        try:
            run_formal(output, config)
        except Exception as error:
            manifest = json.loads((output / 'manifest.json').read_text(encoding='utf-8'))
            manifest['status'] = 'stopped_for_inspection'
            manifest['exception'] = type(error).__name__ + ': ' + str(error)
            save(output / 'manifest.json', manifest)
            raise


if __name__ == '__main__':
    main()
