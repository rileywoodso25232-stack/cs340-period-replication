#!/usr/bin/env python3
"""Formal Table 1 local runs: PERIOD and Serial, 10 attempts per subject (3.6+).

Prepare builds the three CVE targets once, applies the reviewed IPC-compatible
patches to independent driver copies, and freezes every hash. Run executes
method-major, subject round-robin, attempts 1..10, each attempt in its own
directory and IPC namespace, with first-failure replay and bounded replay retry.
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

from run_table1_pilot import (REPO, ROOT, EXPECTED, digest, environment, execute,
                              parse_search, save)
from validate_reorder3_ipc import OBSERVER, protected_ast

CONFIG_PATH = REPO / 'config/table1-local-runs.json'


def load_config():
    return json.loads(CONFIG_PATH.read_text(encoding='utf-8'))


def validate_config(config):
    if config.get('status') != 'formal-local-subset':
        raise ValueError('Configuration is not the reviewed formal subset')
    if set(config.get('subjects', [])) != set(EXPECTED) or len(config['subjects']) != 3:
        raise ValueError('Formal configuration must use the three reviewed CVE subjects')
    if [m.get('name') for m in config.get('methods', [])] != ['period', 'serial']:
        raise ValueError('Formal configuration must run period then serial')
    for method in config['methods']:
        if method.get('driver') not in ('run_PDS.py', 'run_OldPDS.py'):
            raise ValueError('Unexpected driver: ' + str(method.get('driver')))
        if not (REPO / method['patch']).is_file():
            raise ValueError('Missing patch: ' + method['patch'])
    method_subjects = config.get('method_subjects') or {}
    method_names = [m['name'] for m in config['methods']]
    if set(method_subjects) != set(method_names):
        raise ValueError('method_subjects must define exactly the configured methods')
    if method_subjects.get('period') != config['subjects']:
        raise ValueError('PERIOD must cover all reviewed subjects')
    for name in method_names:
        listed = method_subjects[name]
        if not listed or any(subject not in config['subjects'] for subject in listed):
            raise ValueError('Invalid subject list for method ' + name)
    for key, expected in [('depth', 5), ('schedule_budget', 10000),
                          ('attempts_per_subject', 10), ('child_timeout_seconds', 5),
                          ('outer_timeout_seconds', 120), ('replay_attempts', 3)]:
        if type(config.get(key)) is not int or config[key] != expected:
            raise ValueError('Configuration differs from the reviewed formal setup: ' + key)
    if config.get('interactive') is not False:
        raise ValueError('Formal runs must be non-interactive')


def prepare(config):
    base = Path('/root/cs340-period/formal')
    base.mkdir(parents=True, exist_ok=True)
    output = Path(tempfile.mkdtemp(prefix=config['experiment_id'] + '-', dir=str(base)))
    print('Evidence directory: ' + str(output), flush=True)
    save(output / 'config.json', config)
    shutil.copy2(str(REPO / 'scripts/linux/run_table1_formal.py'),
                 str(output / 'run_table1_formal.py'))
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
        'methods': {},
        'targets': {},
        'frozen_driver_files': {},
        'upstream_driver_hashes': {},
        'original_hashes': {},
        'runs': [],
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
            'driver': method['driver'],
            'driver_sha256': digest(driver_dir / method['driver']),
            'patch': method['patch'],
            'patch_sha256': digest(patch),
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
        binary = subject[4:]
        source = ROOT / 'evaluation/ConVul-CVE-Benchmarks' / subject
        build = output / 'build' / subject
        build.mkdir(parents=True)
        for name in [binary + '.cpp', 'build.sh', 'cleanDIR.sh', 'README.md']:
            shutil.copy2(str(source / name), str(build / name))
            manifest['original_hashes'][str(source / name)] = digest(source / name)
        build_env = environment()
        build_env['Con_PATH'] = str(build / ('ConConfig.' + binary))
        commands = [
            ['clang', '-g', '-emit-llvm', '-c', './' + binary + '.cpp', '-o', binary + '.bc'],
            ['bash', str(ROOT / 'tool/staticAnalysis/staticAnalysis.sh'), binary],
            [str(ROOT / 'tool/staticAnalysis/DBDS-INSTRU/dbds-clang-fast++'), '-g',
             '-fsanitize=address', './' + binary + '.cpp', '-o', binary, '-lpthread', '-ldl'],
        ]
        for index, command in enumerate(commands):
            result = execute(command, build, build_env, 'build-' + str(index + 1), 180)
            if result['exit_code'] or result['outer_timeout']:
                raise RuntimeError('Build failed: ' + str(build))
        dump = subprocess_check(['readelf', '--debug-dump=info', str(build / binary)], env)
        start = dump.index(': Sched_Info')
        excerpt = dump[start:start + 7000]
        (build / 'target-dwarf.txt').write_text(excerpt, encoding='utf-8')
        for pattern in [r'DW_AT_byte_size\s*:\s*24008', r'DW_AT_count\s*:\s*3964',
                        r'DW_AT_data_member_location:\s*8148',
                        r'DW_AT_data_member_location:\s*16076']:
            if not re.search(pattern, excerpt):
                raise RuntimeError('Unexpected target ABI: ' + subject)
        manifest['targets'][subject] = {
            name: digest(build / name) for name in
            [binary, binary + '.cpp', 'ConConfig.' + binary, 'mempair.' + binary + '.npz']
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


def replay_attempt(attempt, output, config, method, subject, binary, build, driver, index):
    cwd = attempt / ('replay' if index == 1 else 'replay-try-' + str(index))
    cwd.mkdir(parents=True)
    inputs = [binary, binary + '.cpp', 'ConConfig.' + binary, 'mempair.' + binary + '.npz']
    for name in inputs:
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
    result['observed_child_exits'] = exits
    result['last_child_exit'] = last_exit
    result['replay_exit_confirmed'] = last_exit in (1, -6)
    result['dry_run_abort'] = ('Perform Reproduction!' not in text
                               and 'Perform Dry Run!' in text
                               and 'AddressSanitizer' in text)
    expected = EXPECTED[subject]
    result['expected_diagnostic'] = expected
    result['diagnostic_confirmed'] = ('Perform Reproduction!' in text
                                      and 'AddressSanitizer' in text
                                      and expected in text and binary in text
                                      and result['replay_exit_confirmed'])
    if subject == 'CVE-2016-7911' and result['diagnostic_confirmed']:
        result['near_null_address'] = bool(re.search(r'address 0x0{8,}[0-9a-f]{0,3}\b', text))
        result['diagnostic_confirmed'] &= result['near_null_address']
    if result['outer_timeout']:
        result['status'] = 'outer_timeout'
    elif result['dry_run_abort']:
        result['status'] = 'dry_run_asan_abort'
    elif result['diagnostic_confirmed']:
        result['status'] = 'confirmed'
    else:
        result['status'] = 'ran_without_expected_diagnostic'
    save(cwd / 'replay.result.json', result)
    return result


def search_attempt(attempt, output, config, subject, binary, build, driver):
    cwd = attempt / 'search'
    cwd.mkdir(parents=True)
    inputs = [binary, binary + '.cpp', 'ConConfig.' + binary, 'mempair.' + binary + '.npz']
    for name in inputs:
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
    result['validation_issue'] = None
    if result['outer_timeout'] or result['exit_code']:
        result['validation_issue'] = 'driver_or_outer_timeout'
    else:
        errors = sorted((cwd / ('out_' + binary + '_1') / 'Errors').glob('*'))
        parsed, issue = parse_search(text, errors)
        result.update(parsed)
        if (issue == 'incomplete_search' and 'Perform Dry Run!' in text
                and 'Perform DBDS Run' not in text and 'AddressSanitizer' in text):
            issue = 'dry_run_asan_abort'
            result['dry_run_abort'] = True
        result['validation_issue'] = issue
    save(cwd / 'search.result.json', result)
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
        for file_name, expected_hash in manifest['frozen_driver_files'][name].items():
            if digest(output / ('driver-' + name) / file_name) != expected_hash:
                raise RuntimeError('Frozen driver changed: ' + name + '/' + file_name)
    if digest(output / 'observe_driver.py') != manifest['frozen_driver_files']['observe_driver.py']:
        raise RuntimeError('Observer changed after preparation')
    manifest['status'] = 'running'
    save(output / 'manifest.json', manifest)

    for attempt_number in range(1, config['attempts_per_subject'] + 1):
        for method in config['methods']:
            name = method['name']
            driver = output / ('driver-' + name) / method['driver']
            for subject in config['method_subjects'][name]:
                binary = subject[4:]
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
                    print('%s %s run %d: dry-run ASan abort; counted and continuing' % (
                        name, subject, attempt_number), flush=True)
                    continue
                if search['validation_issue']:
                    record['status'] = 'needs_inspection'
                    save(output / 'manifest.json', manifest)
                    raise RuntimeError('Stopped for inspection; preserving attempt: ' + str(attempt))
                replay_tries = []
                confirmed = False
                invalid_replay = False
                for replay_index in range(1, config['replay_attempts'] + 1):
                    replay = replay_attempt(attempt, output, config, method, subject, binary,
                                            build, driver, replay_index)
                    replay_tries.append(replay)
                    record['replay_tries'] = replay_tries
                    if replay['status'] == 'confirmed':
                        record['replay'] = replay
                        confirmed = True
                        break
                    if replay['status'] == 'dry_run_asan_abort':
                        continue
                    if replay['status'] == 'ran_without_expected_diagnostic':
                        # The saved schedule ran but did not reproduce the bug. Keep the
                        # search row for audit, exclude it from aggregate metrics, and
                        # continue; no replacement run is made.
                        record['replay'] = replay
                        invalid_replay = True
                        break
                    record['status'] = 'needs_inspection'
                    save(output / 'manifest.json', manifest)
                    raise RuntimeError('Replay timeout or unexpected state: ' + str(attempt))
                if confirmed:
                    record['status'] = 'completed'
                elif invalid_replay:
                    record['status'] = 'invalid_replay'
                else:
                    record['status'] = 'replay_unverified_at_dry_run'
                save(output / 'manifest.json', manifest)
                print('%s %s run %d: %s (replay tries=%d)' % (
                    name, subject, attempt_number, record['status'], len(replay_tries)), flush=True)

    manifest['aborted_at_dry_run'] = sum(
        1 for record in manifest['runs'] if record.get('status') == 'aborted_at_dry_run')
    manifest['replay_unverified'] = sum(
        1 for record in manifest['runs'] if record.get('status') == 'replay_unverified_at_dry_run')
    manifest['invalid_replay'] = sum(
        1 for record in manifest['runs'] if record.get('status') == 'invalid_replay')
    manifest['originals_unchanged'] = (
        all(digest(Path(path)) == value for path, value in manifest['original_hashes'].items())
        and all(digest(Path(path)) == value for path, value in manifest['upstream_driver_hashes'].items()))
    manifest['status'] = 'formal_completed' if manifest['originals_unchanged'] else 'original_changed'
    manifest['ended_utc'] = datetime.now(timezone.utc).isoformat()
    save(output / 'manifest.json', manifest)
    if not manifest['originals_unchanged']:
        raise RuntimeError('Original files changed')
    print('Formal runs completed: ' + str(output), flush=True)


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
