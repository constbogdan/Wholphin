"""Public-only recovery provenance and trust-boundary fixtures."""
import copy
import json
from pathlib import Path
import unittest
from unittest.mock import Mock, patch

import mosaic_resume as resume
from mosaic_development_release import verified_manifest, digest
from mosaic_signing_exercise import artifact_name

ROOT = Path(__file__).resolve().parent.parent


class ResumeTests(unittest.TestCase):
    def setUp(self):
        self.source = 'a' * 40
        self.execution = 'b' * 40
        self.identity = dict(sourceSha=self.source, sourceTree='c' * 40, versionName='1.0.5', versionCode=5,
                             epoch=resume.EPOCH, upstreamBaseline=resume.UPSTREAM_BASELINE,
                             dirty=False, publication=True, buildTime=1000)
        self.run = dict(id=123, run_attempt=1, repository=dict(full_name=resume.REPOSITORY),
                        head_repository=dict(full_name=resume.REPOSITORY), event='workflow_dispatch',
                        head_branch='main', head_sha=self.source, path=resume.WORKFLOW,
                        status='completed', conclusion='failure')
        self.a = dict(id=456, name='unsigned-' + artifact_name(self.identity, '123', '1'), expired=False,
                      digest='sha256:' + 'f' * 64, created_at='2026-09-09T10:42:00Z',
                      workflow_run=dict(id=123, repository_id=1, head_repository_id=1, head_branch='main', head_sha=self.source))
        self.job = dict(name='build', status='completed', conclusion='success',
                        started_at='2026-09-09T10:34:00Z', completed_at='2026-09-09T10:42:03Z')
        self.api = Mock()
        self.reset_api()

    def reset_api(self):
        self.api.call.side_effect = [self.a, self.run]
        self.api.pages.return_value = [self.job]

    def metadata(self):
        return resume.artifact_metadata(self.api, '456', self.identity, 'unsigned', [self.execution, self.source])

    def test_successful_build_in_failed_run_can_be_recovered(self):
        self.assertEqual(self.metadata()['id'], 456)
        self.api.pages.assert_called_once_with('actions/runs/123/attempts/1/jobs', 'jobs')

    def test_automatic_producer_preserves_unsigned_and_signed_recovery(self):
        self.run['event'] = 'workflow_run'
        self.reset_api()
        self.assertEqual(self.metadata()['id'], 456)
        self.a['name'] = 'signed-' + artifact_name(self.identity, '123', '1')
        self.job['name'] = 'sign'
        self.reset_api()
        resume.artifact_metadata(self.api, '456', self.identity, 'signed', [self.execution, self.source])
        self.job['name'] = 'build'
        self.api.call.side_effect = None
        self.api.call.return_value = self.run
        record = dict(self.identity, apkSha256='f' * 64, runId='123', runAttempt='1')
        resume.validate_original_source(self.api, record, self.identity)
        # Recovery itself stays manual; only the canonical development producer may be automatic.
        with self.assertRaises(ValueError):
            resume.run_identity(dict(self.run, path=resume.RESUME_WORKFLOW), self.source, resume.RESUME_WORKFLOW)

    def test_artifact_metadata_fails_closed(self):
        original = copy.deepcopy(self.a)
        for field, value in [('expired', True), ('digest', None), ('id', 457), ('name', 'unrelated'),
                             ('created_at', '2026-09-09T11:00:00Z')]:
            self.a = dict(original, **{field: value})
            self.reset_api()
            with self.subTest(field=field), self.assertRaises((ValueError, TypeError)):
                self.metadata()
        self.a = original
        self.a['workflow_run']['head_repository_id'] = 99
        self.reset_api()
        with self.assertRaises(ValueError):
            self.metadata()

    def test_forks_branches_workflows_and_failed_build_are_rejected(self):
        original = dict(self.run)
        for field, value in [('head_repository', dict(full_name='fork/Wholphin')), ('event', 'pull_request'),
                             ('head_branch', 'feature'), ('path', '.github/workflows/other.yml'),
                             ('head_sha', self.execution), ('status', 'in_progress')]:
            self.run = dict(original, **{field: value})
            self.reset_api()
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.metadata()
        self.run = original
        self.job['conclusion'] = 'failure'
        self.reset_api()
        with self.assertRaises(ValueError):
            self.metadata()

    def test_original_build_record_cannot_be_rebased_to_resume_run(self):
        record = dict(self.identity, apkSha256='f' * 64, runId='123', runAttempt='1')
        self.api.call.side_effect = None
        self.api.call.return_value = self.run
        resume.validate_original_source(self.api, record, self.identity)
        for field, value in [('sourceSha', self.execution), ('versionCode', 6), ('sourceTree', '0' * 40),
                             ('publication', False), ('apkSha256', 'bad')]:
            with self.subTest(field=field), self.assertRaises(ValueError):
                resume.validate_original_source(self.api, dict(record, **{field: value}), self.identity)

    def test_historical_identity_reads_git_objects_without_checking_out_source(self):
        chain = [self.execution, self.source, '1' * 40, '2' * 40, '3' * 40, '4' * 40, resume.EPOCH]
        with patch.object(resume, 'git', side_effect=['false', self.execution, '', '\n'.join(chain), 'c' * 40, '1']) as git:
            self.assertEqual(resume.historical_identity(ROOT, self.source, self.execution), self.identity)
            self.assertFalse(any('checkout' in c.args or 'worktree' in c.args for c in git.call_args_list))
        with patch.object(resume, 'git', return_value='true'), self.assertRaises(ValueError):
            resume.historical_identity(ROOT, self.source, self.execution)
        with patch.object(resume, 'git', side_effect=['false', self.execution, '', self.execution + '\n' + resume.EPOCH]), self.assertRaises(ValueError):
            resume.historical_identity(ROOT, self.source, self.execution)

    def test_signed_checkpoint_requires_successful_signer_not_whole_run(self):
        self.a['name'] = 'signed-' + artifact_name(self.identity, '123', '1')
        self.job['name'] = 'sign'
        self.reset_api()
        resume.artifact_metadata(self.api, '456', self.identity, 'signed', [self.execution, self.source])
        self.job['conclusion'] = 'failure'
        self.reset_api()
        with self.assertRaises(ValueError):
            resume.artifact_metadata(self.api, '456', self.identity, 'signed', [self.execution, self.source])

    def test_signed_resume_checkpoint_uses_recovery_run_and_original_source(self):
        self.run.update(path=resume.RESUME_WORKFLOW, head_sha=self.execution)
        self.a['workflow_run']['head_sha'] = self.execution
        self.a['name'] = f'signed-mosaic-resume-{self.source}-run-123-attempt-1'
        self.job['name'] = 'sign'
        self.reset_api()
        resume.artifact_metadata(self.api, '456', self.identity, 'signed', [self.execution, self.source])

    def test_manifest_identity_preserves_original_build_run(self):
        policy = json.loads((ROOT / 'scripts/mosaic-signing.json').read_text())
        apk = b'public fixture'
        record = dict(schemaVersion=1, applicationId=policy['applicationId'], certificateSha256=policy['expectedCertificateSha256'],
                      signedApkSha256=digest(apk), source=dict(self.identity, apkSha256='f' * 64, runId='123', runAttempt='1'))
        m = verified_manifest(record, apk, self.identity, '123', '1', policy)
        self.assertEqual(m['sourceSha'], self.source)
        self.assertEqual(m['buildRunId'], '123')
        self.assertNotIn('recoveryRun', m)
        with self.assertRaises(ValueError):
            verified_manifest(record, apk, self.identity, '999', '1', policy)

    def test_cli_preserves_original_manifest_through_unsigned_recovery(self):
        import os
        import tempfile
        import zipfile
        env = dict(GITHUB_ACTIONS='true', GITHUB_REPOSITORY=resume.REPOSITORY, GITHUB_REF='refs/heads/main',
                   GITHUB_REF_PROTECTED='true', GITHUB_EVENT_NAME='workflow_dispatch', GITHUB_SHA=self.execution,
                   MOSAIC_EXERCISE_SHA=self.execution, MOSAIC_SOURCE_SHA=self.source, MOSAIC_ARTIFACT_ID='456',
                   MOSAIC_CHECKPOINT='unsigned', GITHUB_RUN_ID='999', GITHUB_RUN_ATTEMPT='2',
                   GITHUB_WORKFLOW_REF=f'{resume.REPOSITORY}/{resume.RESUME_WORKFLOW}@refs/heads/main')
        self.api.call.side_effect = None
        self.api.call.return_value = self.run
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            with zipfile.ZipFile(directory / 'unsigned.apk', 'w') as z:
                z.writestr('classes.dex', b'public fixture only')
            source = dict(self.identity, runId='123', runAttempt='1', apkSha256=digest((directory / 'unsigned.apk').read_bytes()))
            (directory / 'provenance.json').write_text(json.dumps(source))
            policy = json.loads((ROOT / 'scripts/mosaic-signing.json').read_text())
            (directory / 'Mosaic-release.apk').write_bytes(b'public signed-output fixture')
            record = dict(schemaVersion=1, applicationId=policy['applicationId'], certificateSha256=policy['expectedCertificateSha256'],
                          signedApkSha256=digest((directory / 'Mosaic-release.apk').read_bytes()), source=source)
            (directory / 'verification.json').write_text(json.dumps(record))
            with patch.dict(os.environ, env), patch.object(resume, 'historical_identity', return_value=self.identity), \
                    patch.object(resume, 'GitHub', return_value=self.api), patch.object(resume, 'trusted_ci'), \
                    patch.object(resume, 'git', return_value=self.execution + '\n' + self.source), \
                    patch.object(resume, 'artifact_metadata', return_value=self.a), patch.object(resume, 'publish') as publish:
                for mode in ['check', 'manifest', 'publish']:
                    with patch('sys.argv', ['resume', mode, '--directory', str(directory)]):
                        resume.main()
                m = json.loads((directory / resume.MANIFEST_NAME).read_text())
                self.assertEqual(m['buildRunId'], '123')
                self.assertEqual(m['buildRunAttempt'], '1')
                self.assertEqual(json.loads((directory / 'recovery.json').read_text())['runId'], '999')
                publish.assert_called_once_with(self.api, m, b'public signed-output fixture')
                # A signed retry must have a fresh identical public SDK acceptance record.
                os.environ['MOSAIC_CHECKPOINT'] = 'signed'
                (directory / 'reverified.json').write_text(json.dumps(dict(record, signedApkSha256='0' * 64)))
                with patch('sys.argv', ['resume', 'manifest', '--directory', str(directory)]), self.assertRaises(SystemExit):
                    resume.main()
                (directory / 'reverified.json').write_text(json.dumps(record))
                with patch('sys.argv', ['resume', 'manifest', '--directory', str(directory)]):
                    resume.main()
                self.assertEqual(json.loads((directory / resume.MANIFEST_NAME).read_text()), m)

    def test_recovery_guard_and_zero_build_secret_isolation(self):
        env = dict(GITHUB_ACTIONS='true', GITHUB_REPOSITORY=resume.REPOSITORY, GITHUB_REF='refs/heads/main',
                   GITHUB_REF_PROTECTED='true', GITHUB_EVENT_NAME='workflow_dispatch', GITHUB_SHA=self.execution,
                   MOSAIC_EXERCISE_SHA=self.execution, MOSAIC_SOURCE_SHA=self.source, MOSAIC_ARTIFACT_ID='456',
                   MOSAIC_CHECKPOINT='unsigned', GITHUB_WORKFLOW_REF=f'{resume.REPOSITORY}/{resume.RESUME_WORKFLOW}@refs/heads/main')
        resume.guard(env)
        for key, value in [('GITHUB_EVENT_NAME', 'push'), ('GITHUB_REF', 'refs/heads/feature'),
                           ('MOSAIC_EXERCISE_SHA', self.source), ('MOSAIC_SOURCE_SHA', 'main'), ('MOSAIC_ARTIFACT_ID', '../123')]:
            with self.subTest(key=key), self.assertRaises(ValueError):
                resume.guard(dict(env, **{key: value}))
        workflow = (ROOT / resume.RESUME_WORKFLOW).read_text()
        sign, rest = workflow.split('\n  recover_signed:\n')
        readonly, publish = rest.split('\n  publish:\n')
        for forbidden in ('gradlew', 'secrets: inherit', 'SYNC_BOT', 'pull_request:', 'push:', 'workflow_run:'):
            self.assertNotIn(forbidden, workflow)
        self.assertEqual(workflow.count('secrets.MOSAIC_'), 4)
        self.assertNotIn('secrets.', readonly + publish)
        self.assertNotIn('environment:', readonly + publish)
        self.assertIn('environment: mosaic-release-signing', sign)
        self.assertNotIn('contents: write', sign + readonly)
        self.assertIn('contents: write', publish)
        self.assertIn('mosaic-sign-apk', sign)
        self.assertNotIn('mosaic-sign-apk', readonly)
        self.assertIn('reverified.json', readonly)
        self.assertIn('digest-mismatch: error', sign)
        self.assertIn('run-id: ${{ steps.origin.outputs.run_id }}', sign)
        self.assertIn('group: mosaic-development-release', workflow)


if __name__ == '__main__':
    unittest.main()
