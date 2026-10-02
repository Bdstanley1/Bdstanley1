#!/usr/bin/env python3
"""Publish only matching-source QA evidence, without rebasing binary images.

Normal fast-forward pushes and a bounded retry protect unrelated files and newer
runs. A stale candidate remains available in its CI artifact, never as latest.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

PROJECT = 'knit-riot-3d-garment'
INPUTS = [f'{PROJECT}/{p}' for p in ('patches', 'tools', 'fixtures', 'recovered', 'requirements-test.txt')]
INPUTS += ['.github/workflows/knit-riot-render-tests.yml']


def _git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(['git', '-C', str(repo), *args], check=check,
                          text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def verify_evidence(evidence: Path, tested: str) -> None:
    if not re.fullmatch(r'[0-9a-f]{40}', tested):
        raise ValueError('Expected a full tested commit SHA')
    provenance = json.loads((evidence / 'PROVENANCE.json').read_text())
    if provenance.get('tested_commit') != tested:
        raise ValueError('Evidence provenance does not match tested commit')
    files = [p for p in evidence.rglob('*') if not p.is_dir()]
    if any(p.is_symlink() for p in evidence.rglob('*')):
        raise ValueError('Evidence may not contain symbolic links')
    if len(files) > 1000 or sum(p.stat().st_size for p in files) > 100_000_000:
        raise ValueError('Evidence exceeds bounded publication size')
    expected = {'PROVENANCE.json'}
    for item in provenance['files']:
        name = item['path']
        p = evidence / name
        if not p.resolve().is_relative_to(evidence.resolve()) or p.is_symlink():
            raise ValueError('Unsafe evidence path')
        if name in expected:
            raise ValueError('Duplicate evidence path')
        expected.add(name)
        if p.stat().st_size != item['bytes'] or hashlib.sha256(p.read_bytes()).hexdigest() != item['sha256']:
            raise ValueError(f'Evidence checksum/size mismatch: {name}')
    if {p.relative_to(evidence).as_posix() for p in files} != expected:
        raise ValueError('Evidence contains unmanifested files')


def publish(repo: Path, evidence: Path, tested: str, attempts: int = 3, destination: str = "latest") -> dict:
    repo, evidence = repo.resolve(), evidence.resolve()
    if attempts < 1 or attempts > 3:
        raise ValueError('Publication attempts must be between one and three')
    if destination not in ('latest', 'staging'):
        raise ValueError('Only latest or staging evidence destinations are authorized')
    inputs = INPUTS if destination == 'latest' else [
        '.github/workflows/knit-riot-staging-verification.yml',
        f'{PROJECT}/tools/publish_evidence.py']
    scope = f'{PROJECT}/validation/{destination}'
    verify_evidence(evidence, tested)
    for attempt in range(1, attempts + 1):
        _git(repo, 'fetch', 'origin', 'refs/heads/main')
        parent = _git(repo, 'rev-parse', 'FETCH_HEAD').stdout.strip()
        different = _git(repo, 'diff', '--quiet', tested, parent, '--', *inputs, check=False)
        if different.returncode == 1:
            return {'status': 'stale_source_not_published', 'tested_commit': tested,
                    'current_main': parent, 'attempt': attempt,
                    'evidence': 'Retained in this workflow artifact; published evidence unchanged', 'destination': destination}
        if different.returncode:
            raise RuntimeError(different.stderr)
        with tempfile.TemporaryDirectory(prefix='kr-evidence-') as temporary:
            worktree = Path(temporary) / 'worktree'
            _git(repo, 'worktree', 'add', '--detach', str(worktree), parent)
            try:
                target = worktree / scope
                if target.exists():
                    shutil.rmtree(target)
                shutil.copytree(evidence, target)
                _git(worktree, 'add', '--', scope)
                diff = _git(worktree, 'diff', '--cached', '--quiet', check=False)
                if diff.returncode == 0:
                    return {'status': 'already_current', 'tested_commit': tested, 'current_main': parent}
                if diff.returncode != 1:
                    raise RuntimeError(diff.stderr)
                changed = _git(worktree, 'diff', '--cached', '--name-only').stdout.splitlines()
                if any(not p.startswith(scope + '/') for p in changed):
                    raise RuntimeError('Refusing to publish changes outside ' + scope)
                _git(worktree, '-c', 'user.name=github-actions[bot]', '-c',
                     'user.email=41898282+github-actions[bot]@users.noreply.github.com',
                     'commit', '-m', 'Preserve actual Knit Riot render evidence and validation provenance')
                commit = _git(worktree, 'rev-parse', 'HEAD').stdout.strip()
                pushed = _git(worktree, 'push', 'origin', 'HEAD:refs/heads/main', check=False)
                if pushed.returncode == 0:
                    return {'status': 'published', 'tested_commit': tested,
                            'evidence_commit': commit, 'parent': parent, 'attempt': attempt, 'destination': destination}
                _git(repo, 'fetch', 'origin', 'refs/heads/main')
                new_parent = _git(repo, 'rev-parse', 'FETCH_HEAD').stdout.strip()
                if new_parent == parent:
                    raise RuntimeError('Evidence push failed without a concurrent update: ' + pushed.stderr)
            finally:
                _git(repo, 'worktree', 'remove', '--force', str(worktree))
    raise RuntimeError('Evidence publication lost three concurrent update races; artifact retained')


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', type=Path, default=Path.cwd())
    parser.add_argument('--tested-commit', required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    result = publish(args.repo, args.repo / PROJECT / 'validation/latest', args.tested_commit)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
