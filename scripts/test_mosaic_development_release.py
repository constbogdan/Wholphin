"""Offline publisher state-machine and workflow boundary fixtures; never calls GitHub."""
import copy
import json
from pathlib import Path
import unittest

import mosaic_development_release as release

ROOT = Path(__file__).resolve().parent.parent


class FakeGitHub:
    def __init__(self):
        self.refs, self.tags, self.releases, self.uploads = {}, {}, {}, {}
        self.calls = []
        self.fail_upload = False

    def pages(self, path, key=None):
        if path == 'releases':
            return list(self.releases.values())
        if path.endswith('/assets'):
            rid = int(path.split('/')[1])
            return [a for a in self.uploads.values() if a['release'] == rid]
        raise AssertionError(path)

    def call(self, method, path, data=None, missing=False, upload=False):
        self.calls.append((method, path, copy.deepcopy(data)))
        if path.startswith('git/ref/tags/'):
            return self.refs.get(path.removeprefix('git/ref/tags/'))
        if method == 'POST' and path == 'git/tags':
            sha = str(len(self.tags) + 1) * 40
            self.tags[sha] = dict(tag=data['tag'], message=data['message'], object=dict(type='commit', sha=data['object'], url='fixture'))
            return dict(sha=sha)
        if method == 'GET' and path.startswith('git/tags/'):
            return self.tags[path.split('/')[-1]]
        if method == 'POST' and path == 'git/refs':
            tag = data['ref'].removeprefix('refs/tags/')
            if tag in self.refs:
                raise ValueError('ref conflict')
            self.refs[tag] = dict(object=dict(type='tag' if data['sha'] in self.tags else 'commit', sha=data['sha']))
            return self.refs[tag]
        if method == 'PATCH' and path == 'git/refs/tags/develop':
            self.refs['develop'] = dict(object=dict(type='commit', sha=data['sha']))
            return self.refs['develop']
        if method == 'POST' and path == 'releases':
            rid = len(self.releases) + 1
            self.releases[rid] = dict(data, id=rid, immutable=False)
            return self.releases[rid]
        if method == 'PATCH' and path.startswith('releases/'):
            self.releases[int(path.split('/')[1])].update(data)
            return self.releases[int(path.split('/')[1])]
        if method == 'POST' and upload:
            if self.fail_upload:
                raise ValueError('interrupted upload')
            aid = max(self.uploads, default=0) + 1
            a = dict(id=aid, release=int(path.split('/')[1]), name=path.split('name=')[1],
                     size=len(data), digest='sha256:' + release.digest(data), state='uploaded')
            self.uploads[aid] = a
            return a
        if method == 'DELETE' and path.startswith('releases/assets/'):
            del self.uploads[int(path.split('/')[-1])]
            return None
        raise AssertionError((method, path))


class PublisherTests(unittest.TestCase):
    def setUp(self):
        self.apk = b'public fixture, not a signed APK'
        self.identity = dict(publication=True, dirty=False, sourceSha='a' * 40, sourceTree='b' * 40,
                             upstreamBaseline='c' * 40, epoch='d' * 40, versionName='1.0.5', versionCode=5, buildTime=123)
        self.env = dict(GITHUB_ACTIONS='true', GITHUB_REPOSITORY=release.REPOSITORY,
                        GITHUB_REF='refs/heads/main', GITHUB_REF_PROTECTED='true', GITHUB_SHA='a' * 40,
                        MOSAIC_EXERCISE_SHA='a' * 40, GITHUB_EVENT_NAME='workflow_dispatch',
                        GITHUB_RUN_ID='123', GITHUB_RUN_ATTEMPT='1',
                        GITHUB_WORKFLOW_REF=f'{release.REPOSITORY}/{release.WORKFLOW}@refs/heads/main')
        self.policy = json.loads((ROOT / 'scripts/mosaic-signing.json').read_text())
        self.record = dict(schemaVersion=1, applicationId=self.policy['applicationId'],
                           certificateSha256=self.policy['expectedCertificateSha256'], signedApkSha256=release.digest(self.apk),
                           source=dict(self.identity, apkSha256='e' * 64, runId='123', runAttempt='1'))
        self.m = release.manifest(self.record, self.apk, self.identity, self.env, self.policy)

    def test_exact_main_authorization(self):
        for key, value in [('GITHUB_REPOSITORY', 'fork/Wholphin'), ('GITHUB_REF', 'refs/heads/feature'),
                           ('GITHUB_REF_PROTECTED', 'false'), ('GITHUB_EVENT_NAME', 'push'),
                           ('GITHUB_EVENT_NAME', 'pull_request'), ('MOSAIC_EXERCISE_SHA', 'b' * 40),
                           ('GITHUB_WORKFLOW_REF', 'other')]:
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                release.guard(dict(self.env, **{key: value}))

    def test_manifest_mismatches(self):
        for field, value in [('applicationId', 'upstream'), ('certificateSha256', '0' * 64),
                             ('signedApkSha256', '0' * 64), ('schemaVersion', 2)]:
            with self.subTest(field=field), self.assertRaises(ValueError):
                release.manifest(dict(self.record, **{field: value}), self.apk, self.identity, self.env, self.policy)
        for field, value in [('versionCode', 6), ('versionName', '1.0.6'), ('runId', '124'), ('runAttempt', '2'),
                             ('sourceSha', 'f' * 40), ('sourceTree', 'f' * 40), ('publication', False), ('dirty', True)]:
            record = copy.deepcopy(self.record)
            record['source'][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                release.manifest(record, self.apk, self.identity, self.env, self.policy)
        with self.assertRaises(ValueError):
            release.manifest(self.record, self.apk + b'tampered', self.identity, self.env, self.policy)

    def test_contract_and_exact_rerun(self):
        api = FakeGitHub()
        release.publish(api, self.m, self.apk)
        self.assertEqual(set(api.refs), {'downstream-build-5', 'develop'})
        self.assertEqual({r['tag_name'] for r in api.releases.values()}, {'downstream-build-5', 'develop'})
        for r in api.releases.values():
            self.assertEqual(r['name'], 'v1.0.5')
            self.assertTrue(r['prerelease'])
            self.assertFalse(r['draft'])
            self.assertEqual(r['make_latest'], 'false')
        self.assertEqual({a['name'] for a in api.uploads.values()}, {'Wholphin-release.apk', 'mosaic-release.json'})
        self.assertEqual(self.m['signedApkSha256'], release.digest(self.apk))
        self.assertEqual(self.m['immutableIdentity'], 'downstream-build-5')
        count = len(api.calls)
        release.publish(api, self.m, self.apk)
        self.assertTrue(all(method == 'GET' for method, _, _ in api.calls[count:]))

    def test_conflicting_bytes_or_provenance_never_replace_identity(self):
        api = FakeGitHub()
        release.publish(api, self.m, self.apk)
        for field, value in [('signedApkSha256', '0' * 64), ('sourceSha', 'f' * 40), ('buildRunAttempt', '2')]:
            count = len(api.calls)
            with self.assertRaises(ValueError):
                release.publish(api, dict(self.m, **{field: value}), self.apk)
            self.assertTrue(all(method == 'GET' for method, _, _ in api.calls[count:]))

    def test_rolling_reuse_and_no_immutable_mutation(self):
        api = FakeGitHub()
        release.publish(api, self.m, self.apk)
        rid = next(r['id'] for r in api.releases.values() if r['tag_name'] == 'develop')
        newer = dict(self.m, immutableIdentity='downstream-build-6', versionCode=6, versionName='1.0.6', sourceSha='f' * 40)
        count = len(api.calls)
        release.publish(api, newer, self.apk)
        self.assertEqual(api.releases[rid]['name'], 'v1.0.6')
        self.assertEqual(api.refs['downstream-build-5']['object']['sha'], '1' * 40)
        changes = api.calls[count:]
        self.assertTrue(any(method == 'PATCH' and path == f'releases/{rid}' and data.get('draft') is True for method, path, data in changes))
        self.assertFalse(any(method == 'DELETE' and re_path == f'releases/{rid}' for method, re_path, _ in changes))
        with self.assertRaises(ValueError):
            release.publish(api, self.m, self.apk)

    def test_interruption_reserves_identity_and_exact_resume(self):
        api = FakeGitHub()
        api.fail_upload = True
        with self.assertRaises(ValueError):
            release.publish(api, self.m, self.apk)
        self.assertIn('downstream-build-5', api.refs)
        self.assertNotIn('develop', api.refs)
        self.assertTrue(all(r['draft'] for r in api.releases.values()))
        api.fail_upload = False
        with self.assertRaises(ValueError):
            release.publish(api, dict(self.m, signedApkSha256='f' * 64), self.apk)
        release.publish(api, self.m, self.apk)
        self.assertFalse(any(r['draft'] for r in api.releases.values()))

    def test_remote_asset_tampering_fails(self):
        api = FakeGitHub()
        release.publish(api, self.m, self.apk)
        api.uploads[1]['digest'] = 'sha256:' + '0' * 64
        with self.assertRaises(ValueError):
            release.publish(api, self.m, self.apk)

    def test_immutable_rolling_setting_fails_before_mutation(self):
        api = FakeGitHub()
        release.publish(api, self.m, self.apk)
        next(r for r in api.releases.values() if r['tag_name'] == 'develop')['immutable'] = True
        count = len(api.calls)
        with self.assertRaises(ValueError):
            release.publish(api, self.m, self.apk)
        self.assertEqual(len(api.calls), count)

    def test_trust_requires_current_main_latest_ci_attempt_and_full_job(self):
        from unittest.mock import Mock
        api = Mock()
        branch = dict(protected=True, commit=dict(sha='a' * 40))
        run = dict(id=100, run_attempt=2, head_sha='a' * 40, head_branch='main', event='push',
                   workflow_id=42, head_repository=dict(full_name=release.REPOSITORY),
                   status='completed', conclusion='success')
        job = dict(name='Full validation', status='completed', conclusion='success', head_sha='a' * 40)
        def configure():
            api.call.side_effect = [branch, dict(id=42)]
            api.pages.side_effect = [[run], [job]]
        configure()
        self.assertEqual(release.trusted_ci(api, 'a' * 40)['runAttempt'], '2')
        for field, value in [('head_branch', 'feature'), ('event', 'pull_request'), ('workflow_id', 43),
                             ('head_sha', 'f' * 40), ('head_repository', dict(full_name='fork/Wholphin')),
                             ('status', 'in_progress'), ('conclusion', 'failure')]:
            changed = dict(run, **{field: value})
            api.call.side_effect = [branch, dict(id=42)]
            api.pages.side_effect = [[changed], [job]]
            with self.subTest(field=field), self.assertRaises(ValueError):
                release.trusted_ci(api, 'a' * 40)
        for field, value in [('conclusion', 'skipped'), ('head_sha', 'f' * 40), ('name', 'Other validation')]:
            api.call.side_effect = [branch, dict(id=42)]
            api.pages.side_effect = [[run], [dict(job, **{field: value})]]
            with self.subTest(field=field), self.assertRaises(ValueError):
                release.trusted_ci(api, 'a' * 40)
        api.call.side_effect = [dict(protected=False, commit=branch['commit'])]
        with self.assertRaises(ValueError):
            release.trusted_ci(api, 'a' * 40)

    def test_workflow_boundaries_and_no_duplicate_debug(self):
        workflow = (ROOT / release.WORKFLOW).read_text()
        build, remainder = workflow.split('\n  sign:\n')
        call, publish = remainder.split('\n  publish:\n')
        signer = call
        for forbidden in ('push:', 'pull_request:', 'schedule:', 'SYNC_BOT', 'secrets: inherit'):
            self.assertNotIn(forbidden, workflow + signer)
        for part in (build, call, publish, signer):
            self.assertIn("github.ref == 'refs/heads/main' && github.ref_protected && inputs.expected_sha == github.sha", part)
            self.assertIn("github.repository == 'constbogdan/Wholphin'", part)
        self.assertEqual(build.count('./gradlew '), 1)
        self.assertIn('mosaic_development_release.py trust', build)
        self.assertIn(':app:assembleDefaultRelease', build)
        self.assertNotIn('DefaultDebug', build)
        self.assertIn('uses: ./.github/actions/mosaic-sign-apk', signer)
        for part in (call, publish, signer):
            self.assertNotIn('gradlew', part)
        self.assertNotIn('secrets.', build + publish)
        self.assertNotIn('contents: write', signer + build + call)
        self.assertIn('contents: write', publish)
        self.assertNotIn('environment:', publish)
        self.assertIn('environment: mosaic-release-signing', signer)
        self.assertEqual(signer.count('secrets.MOSAIC_'), 4)
        self.assertIn('artifact-ids: ${{ needs.sign.outputs.artifact_id }}', publish)
        self.assertIn('artifact-ids: ${{ needs.build.outputs.artifact_id }}', signer)
        self.assertIn('digest-mismatch: error', publish)
        self.assertIn('verify_mosaic_apk.py', signer)
        self.assertIn('mosaic_signing_exercise.py compare', signer)


if __name__ == '__main__':
    unittest.main()
