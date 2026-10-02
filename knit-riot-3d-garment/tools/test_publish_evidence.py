"""Offline Git integration tests; no customer data, credentials or network."""
from pathlib import Path
import hashlib
import json
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import publish_evidence as publication


def git(repo, *args):
    return subprocess.run(['git', '-C', str(repo), *args], check=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).stdout.strip()


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.remote = self.root / 'remote.git'
        self.remote.mkdir()
        git(self.remote, 'init', '--bare', '--initial-branch=main')
        self.repo = self.root / 'runner'
        git(self.root, 'clone', str(self.remote), str(self.repo))
        git(self.repo, 'config', 'user.name', 'Test')
        git(self.repo, 'config', 'user.email', 'test@example.invalid')
        (self.repo / 'README.md').write_text('Profile: preserve me\n')
        source = self.repo / publication.PROJECT / 'patches' / 'footwear.js'
        source.parent.mkdir(parents=True)
        source.write_text('const fixture = 1;\n')
        git(self.repo, 'add', '.')
        git(self.repo, 'commit', '-m', 'fixture')
        git(self.repo, 'push', 'origin', 'main')
        self.tested = git(self.repo, 'rev-parse', 'HEAD')
        self.other = self.root / 'other'
        git(self.root, 'clone', str(self.remote), str(self.other))
        git(self.other, 'config', 'user.name', 'Test')
        git(self.other, 'config', 'user.email', 'test@example.invalid')
        self.evidence = self.repo / publication.PROJECT / 'validation' / 'latest'
        self.evidence.mkdir(parents=True)
        data = b'actual rendered fixture bytes for publication test'
        (self.evidence / 'frame.bin').write_bytes(data)
        (self.evidence / 'PROVENANCE.json').write_text(json.dumps({
            'tested_commit': self.tested,
            'files': [{'path': 'frame.bin', 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}]
        }))

    def tearDown(self):
        self.tmp.cleanup()

    def change_remote(self, name, data):
        git(self.other, 'pull', '--ff-only')
        p = self.other / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(data)
        git(self.other, 'add', '--', name)
        git(self.other, 'commit', '-m', 'concurrent update')
        git(self.other, 'push', 'origin', 'main')

    def test_publish_preserves_profile_and_source(self):
        result = publication.publish(self.repo, self.evidence, self.tested)
        self.assertEqual(result['status'], 'published')
        self.assertEqual(git(self.remote, 'show', 'main:README.md'), 'Profile: preserve me')
        self.assertEqual(git(self.remote, 'show', f'main:{publication.PROJECT}/patches/footwear.js'), 'const fixture = 1;')
        self.assertEqual(publication.publish(self.repo, self.evidence, self.tested)['status'], 'already_current')

    def test_metadata_update_preserved(self):
        self.change_remote('README.md', 'New profile content\n')
        self.change_remote(f'{publication.PROJECT}/PROJECT_HANDOFF.json', '{"lease":"new owner"}\n')
        self.assertEqual(publication.publish(self.repo, self.evidence, self.tested)['status'], 'published')
        self.assertEqual(git(self.remote, 'show', 'main:README.md'), 'New profile content')
        self.assertEqual(git(self.remote, 'show', f'main:{publication.PROJECT}/PROJECT_HANDOFF.json'), '{"lease":"new owner"}')

    def test_stale_source_not_published(self):
        self.change_remote(f'{publication.PROJECT}/patches/footwear.js', 'const fixture = 2;\n')
        before = git(self.remote, 'rev-parse', 'main')
        self.assertEqual(publication.publish(self.repo, self.evidence, self.tested)['status'], 'stale_source_not_published')
        self.assertEqual(git(self.remote, 'rev-parse', 'main'), before)

    def test_race_retries_without_rebase(self):
        original = publication._git
        raced = False
        def concurrent(repo, *args, **kwargs):
            nonlocal raced
            self.assertNotIn('rebase', args)
            if args and args[0] == 'push' and not raced:
                raced = True
                self.change_remote('README.md', 'Concurrent profile\n')
            return original(repo, *args, **kwargs)
        with patch.object(publication, '_git', side_effect=concurrent):
            result = publication.publish(self.repo, self.evidence, self.tested)
        self.assertEqual(result['status'], 'published')
        self.assertEqual(result['attempt'], 2)
        self.assertEqual(git(self.remote, 'show', 'main:README.md'), 'Concurrent profile')

    def test_race_new_source_skips_old_evidence(self):
        original = publication._git
        raced = False
        def concurrent(repo, *args, **kwargs):
            nonlocal raced
            if args and args[0] == 'push' and not raced:
                raced = True
                self.change_remote(f'{publication.PROJECT}/patches/footwear.js', 'const fixture = 3;\n')
            return original(repo, *args, **kwargs)
        with patch.object(publication, '_git', side_effect=concurrent):
            result = publication.publish(self.repo, self.evidence, self.tested)
        self.assertEqual(result['status'], 'stale_source_not_published')
        self.assertEqual(git(self.remote, 'show', f'main:{publication.PROJECT}/patches/footwear.js'), 'const fixture = 3;')

    def test_corrupt_evidence_rejected(self):
        (self.evidence / 'frame.bin').write_bytes(b'corrupt')
        with self.assertRaisesRegex(ValueError, 'checksum/size'):
            publication.publish(self.repo, self.evidence, self.tested)

    def test_symlink_rejected(self):
        (self.evidence / 'untracked').symlink_to(self.repo / 'README.md')
        with self.assertRaisesRegex(ValueError, 'symbolic links'):
            publication.publish(self.repo, self.evidence, self.tested)


if __name__ == '__main__':
    unittest.main()
