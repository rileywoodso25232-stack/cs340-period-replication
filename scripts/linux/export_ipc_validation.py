#!/usr/bin/env python3
"""Copy one completed validation's small evidence to the repository, hash checked."""
import hashlib
import json
from pathlib import Path
import shutil
import sys

source = Path(sys.argv[1]).resolve()
repo = Path(__file__).resolve().parents[2]
destination = repo / 'results/raw/local-ipc-validation-20261115'
manifest = json.loads((source / 'manifest.json').read_text())
if manifest.get('status') != 'search_and_replay_passed_both_candidates':
    raise RuntimeError('Only a completed validation can use this export helper')
destination.mkdir()  # Refuse to overwrite earlier evidence.
hashes = {}
excluded = {}
for path in sorted(source.rglob('*')):
    if not path.is_file():
        continue
    relative = path.relative_to(source)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if path.name == 'reorder_3_bad' or '__pycache__' in relative.parts:
        excluded[str(relative)] = digest
        continue
    target = destination / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(str(path), str(target))
    if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
        raise RuntimeError('Copy checksum mismatch: ' + str(relative))
    hashes[str(relative)] = digest
(destination / 'packaging.json').write_text(json.dumps({
    'linux_full_evidence': str(source), 'excluded_files_sha256': excluded,
    'copied_files_sha256': hashes, 'all_copied_bytes_verified': True,
    'note': 'Binary remains in Linux; metadata README/gitattributes added after export.'
}, indent=2) + '\n', encoding='utf-8')
print('Exported and verified', len(hashes), 'files;', len(excluded), 'excluded')
