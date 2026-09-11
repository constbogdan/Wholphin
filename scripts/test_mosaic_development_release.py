"""Offline publisher state-machine and workflow boundary fixtures; never calls GitHub."""
import copy
from datetime import datetime, timezone
import json
from pathlib import Path
import unittest
import tempfile
from unittest.mock import Mock, patch

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

    def test_manifest_records_authoritative_ci_producer(self):
        ci = dict(workflow=release.CI_WORKFLOW, runId='100', runAttempt='2')
        record = copy.deepcopy(self.record)
        record['source']['runId'] = '100'
        record['source']['runAttempt'] = '2'
        manifest = release.manifest(record, self.apk, self.identity, self.env, self.policy, ci)
        self.assertEqual(manifest['buildWorkflow'], release.CI_WORKFLOW)
        self.assertEqual(manifest['buildRunId'], '100')
        self.assertEqual(manifest['buildRunAttempt'], '2')

    def test_automatic_trigger_requires_exact_successful_main_ci(self):
        run = dict(id=100, run_attempt=2, workflow_id=42, head_sha='a' * 40,
                   head_branch='main', event='push', path='.github/workflows/ci.yml',
                   head_repository=dict(full_name=release.REPOSITORY), status='completed', conclusion='success')
        event = dict(action='completed', repository=dict(full_name=release.REPOSITORY), workflow_run=run)
        ci = dict(workflow='.github/workflows/ci.yml', runId='100', runAttempt='2')
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'event.json'
            env = dict(self.env, GITHUB_EVENT_NAME='workflow_run', GITHUB_EVENT_PATH=str(path))
            path.write_text(json.dumps(event))
            self.assertEqual(release.guard(env), 'a' * 40)
            api = Mock()
            api.call.return_value = dict(id=42)
            with patch.object(release, 'trusted_ci', return_value=ci) as trust:
                self.assertEqual(release.authorized_ci(api, 'a' * 40, env), ci)
                trust.assert_called_once_with(api, 'a' * 40)
            for field, value in [('conclusion', 'failure'), ('conclusion', 'cancelled'),
                                 ('status', 'in_progress'), ('event', 'pull_request'), ('event', 'workflow_dispatch'),
                                 ('head_branch', 'feature'), ('head_sha', 'b' * 40),
                                 ('head_repository', dict(full_name='fork/Wholphin')),
                                 ('path', '.github/workflows/other.yml'), ('id', 0), ('run_attempt', 0)]:
                path.write_text(json.dumps(dict(event, workflow_run=dict(run, **{field: value}))))
                with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                    release.guard(env)
            path.write_text(json.dumps(event))
            for changed in [dict(ci, runId='101'), dict(ci, runAttempt='3')]:
                with patch.object(release, 'trusted_ci', return_value=changed), self.assertRaises(ValueError):
                    release.authorized_ci(api, 'a' * 40, env)
            api.call.return_value = dict(id=43)
            with patch.object(release, 'trusted_ci', return_value=ci), self.assertRaises(ValueError):
                release.authorized_ci(api, 'a' * 40, env)
            # Main advancing or CI being re-run must fail before any publisher mutation.
            with patch.object(release, 'trusted_ci', side_effect=ValueError('superseded')), self.assertRaises(ValueError):
                release.authorized_ci(api, 'a' * 40, env)

    def test_contract_and_exact_rerun(self):
        api = FakeGitHub()
        with patch.object(api, 'pages', wraps=api.pages) as pages:
            release.publish(api, self.m, self.apk)
        self.assertEqual(1, sum(call.args[0] == 'releases' for call in pages.call_args_list))
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

    def test_published_development_source_requires_matching_release_tag_and_assets(self):
        api = FakeGitHub()
        release.publish(api, self.m, self.apk)
        with patch.object(api, 'pages', wraps=api.pages) as pages:
            self.assertEqual(release.published_development_source(api), self.m['sourceSha'])
        self.assertEqual(1, sum(call.args[0] == 'releases' for call in pages.call_args_list))

        rolling_asset = next(
            asset for asset in api.uploads.values()
            if asset['release'] == next(
                item['id'] for item in api.releases.values() if item['tag_name'] == 'develop'
            ) and asset['name'] == release.APK_NAME
        )
        rolling_asset['digest'] = 'sha256:' + '0' * 64
        with self.assertRaisesRegex(ValueError, 'differs'):
            release.published_development_source(api)

    def test_unresolved_published_baseline_requires_conservative_release(self):
        result = release.release_eligibility(FakeGitHub(), ROOT, 'a' * 40)
        self.assertEqual(result['outcome'], 'ready')
        self.assertEqual(result['releaseRelevance'], release.change_classification.UNKNOWN)
        self.assertEqual(result['validationRisk'], release.change_classification.HIGH)
        self.assertTrue(result['releaseRequired'])

    def test_unreadable_changed_path_requires_conservative_release(self):
        api = FakeGitHub()
        release.publish(api, self.m, self.apk)
        with patch.object(
            release.change_classification,
            'classify_range',
            side_effect=UnicodeError('unreadable path'),
        ):
            result = release.release_eligibility(api, ROOT, 'f' * 40)
        self.assertEqual(result['releaseRelevance'], release.change_classification.UNKNOWN)
        self.assertEqual(result['validationRisk'], release.change_classification.HIGH)
        self.assertTrue(result['releaseRequired'])

    def test_eligibility_classifies_from_authenticated_published_source(self):
        api = FakeGitHub()
        release.publish(api, self.m, self.apk)
        classified = dict(
            releaseRelevance=release.change_classification.DOCS_ONLY,
            validationRisk=release.change_classification.LOW,
            releaseRequired=False,
            paths=[],
            baselineSha=self.m['sourceSha'],
            currentSha='f' * 40,
        )
        with patch.object(release.change_classification, 'classify_range', return_value=classified) as classify:
            result = release.release_eligibility(api, ROOT, 'f' * 40)
        classify.assert_called_once_with(ROOT, self.m['sourceSha'], 'f' * 40)
        self.assertEqual(result['outcome'], 'skipped_non_apk')
        self.assertFalse(result['releaseRequired'])

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

    def test_ci_guard_requires_exact_protected_main_push(self):
        env = dict(GITHUB_ACTIONS='true', GITHUB_REPOSITORY=release.REPOSITORY,
                   GITHUB_REF='refs/heads/main', GITHUB_REF_PROTECTED='true',
                   GITHUB_EVENT_NAME='push', GITHUB_SHA='a' * 40,
                   GITHUB_WORKFLOW_REF=f'{release.REPOSITORY}/{release.CI_WORKFLOW}@refs/heads/main')
        self.assertEqual(release.ci_guard(env), 'a' * 40)
        for field, value in [('GITHUB_REPOSITORY', 'fork/Wholphin'), ('GITHUB_REF', 'refs/heads/feature'),
                             ('GITHUB_REF_PROTECTED', 'false'), ('GITHUB_EVENT_NAME', 'pull_request'),
                             ('GITHUB_SHA', 'main'), ('GITHUB_WORKFLOW_REF', 'other')]:
            with self.subTest(field=field), self.assertRaises(ValueError):
                release.ci_guard(dict(env, **{field: value}))

    def test_unsigned_artifact_binds_exact_ci_run_attempt_sha_job_and_id(self):
        ci = dict(workflow=release.CI_WORKFLOW, runId='100', runAttempt='2')
        now = datetime.now(timezone.utc)
        stamp = now.isoformat()
        artifact = dict(id=456, name=release.ci_artifact_name(self.identity, '100', '2'), expired=False,
                        digest='sha256:' + 'f' * 64, created_at=stamp,
                        workflow_run=dict(id=100, repository_id=1, head_repository_id=1,
                                          head_branch='main', head_sha=self.identity['sourceSha']))
        job = dict(name=release.CI_JOB, status='completed', conclusion='success',
                   head_sha=self.identity['sourceSha'], started_at=stamp, completed_at=stamp)
        api = Mock()
        api.pages.side_effect = [[artifact], [job]]
        result = release.trusted_ci_artifact(api, self.identity, ci)
        self.assertEqual(result['artifactId'], '456')
        self.assertEqual(result['runId'], '100')
        self.assertEqual(result['runAttempt'], '2')
        self.assertEqual(result['versionName'], self.identity['versionName'])

        for field, value in [('id', 0), ('expired', True), ('digest', None),
                             ('name', 'wrong'), ('created_at', '2000-01-01T00:00:00+00:00')]:
            changed = dict(artifact, **{field: value})
            api.pages.side_effect = [[changed], [job]]
            with self.subTest(field=field), self.assertRaises(ValueError):
                release.trusted_ci_artifact(api, self.identity, ci)
        for field, value in [('head_sha', 'f' * 40), ('head_branch', 'feature'),
                             ('head_repository_id', 2), ('id', 101)]:
            changed = copy.deepcopy(artifact)
            changed['workflow_run'][field] = value
            api.pages.side_effect = [[changed], [job]]
            with self.subTest(owner_field=field), self.assertRaises(ValueError):
                release.trusted_ci_artifact(api, self.identity, ci)
        for field, value in [('conclusion', 'failure'), ('status', 'in_progress'),
                             ('head_sha', 'f' * 40), ('name', 'Other')]:
            api.pages.side_effect = [[artifact], [dict(job, **{field: value})]]
            with self.subTest(job_field=field), self.assertRaises(ValueError):
                release.trusted_ci_artifact(api, self.identity, ci)
        api.pages.side_effect = [[], [job]]
        with self.assertRaisesRegex(ValueError, 'exactly one'):
            release.trusted_ci_artifact(api, self.identity, ci)

        selection = dict(MOSAIC_ARTIFACT_ID='456', MOSAIC_ARTIFACT_NAME=artifact['name'],
                         MOSAIC_BUILD_RUN_ID='100', MOSAIC_BUILD_RUN_ATTEMPT='2')
        trusted = dict(artifactId='456', artifactName=artifact['name'], artifactDigest=artifact['digest'],
                       runId='100', runAttempt='2', versionName=self.identity['versionName'])
        release.require_ci_artifact_selection(selection, trusted)
        self.assertEqual(
            release.ci_identity_from_env(selection),
            dict(workflow=release.CI_WORKFLOW, runId='100', runAttempt='2'),
        )
        for field, value in [('MOSAIC_ARTIFACT_ID', '457'), ('MOSAIC_ARTIFACT_NAME', 'wrong'),
                             ('MOSAIC_BUILD_RUN_ID', '101'), ('MOSAIC_BUILD_RUN_ATTEMPT', '3')]:
            with self.subTest(selection_field=field), self.assertRaises(ValueError):
                release.require_ci_artifact_selection(dict(selection, **{field: value}), trusted)
        for field in ('MOSAIC_BUILD_RUN_ID', 'MOSAIC_BUILD_RUN_ATTEMPT'):
            with self.subTest(identity_field=field), self.assertRaises(ValueError):
                release.ci_identity_from_env(dict(selection, **{field: ''}))

    def test_downloaded_ci_artifact_requires_exact_provenance_and_bytes(self):
        import zipfile
        artifact = dict(artifactId='456', artifactName='fixture', artifactDigest='sha256:' + 'f' * 64,
                        runId='100', runAttempt='2', versionName=self.identity['versionName'])
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            with zipfile.ZipFile(directory / 'unsigned.apk', 'w') as archive:
                archive.writestr('classes.dex', b'public fixture')
            from mosaic_version import artifact_record
            provenance = artifact_record(self.identity, directory / 'unsigned.apk')
            provenance.update(runId='100', runAttempt='2')
            (directory / 'provenance.json').write_text(json.dumps(provenance))
            self.assertEqual(release.verify_ci_artifact_directory(directory, self.identity, artifact), provenance)
            provenance['runId'] = '101'
            (directory / 'provenance.json').write_text(json.dumps(provenance))
            with self.assertRaises(ValueError):
                release.verify_ci_artifact_directory(directory, self.identity, artifact)

    def test_workflow_boundaries_main_owns_release_and_development_has_zero_gradle(self):
        workflow = (ROOT / release.WORKFLOW).read_text()
        classify, remainder = workflow.split('\n  sign:\n')
        signer, publish = remainder.split('\n  publish:\n')
        for forbidden in ('push:', 'pull_request:', 'schedule:', 'SYNC_BOT', 'secrets: inherit'):
            self.assertNotIn(forbidden, workflow + signer)
        for part in (classify, publish, signer):
            self.assertIn("github.ref == 'refs/heads/main' && github.ref_protected", part)
            self.assertIn('inputs.expected_sha == github.sha', part)
            self.assertIn("github.event.workflow_run.event == 'push'", part)
            self.assertIn("github.event.workflow_run.conclusion == 'success'", part)
            self.assertIn("github.event.workflow_run.head_branch == 'main'", part)
            self.assertIn("github.event.workflow_run.head_repository.full_name == 'constbogdan/Wholphin'", part)
            self.assertIn('github.event.workflow_run.head_sha == github.sha', part)
            self.assertIn("github.repository == 'constbogdan/Wholphin'", part)
        self.assertIn('workflows: [CI]', classify)
        self.assertIn('types: [completed]', classify)
        self.assertIn('branches: [main]', classify)
        self.assertEqual(workflow.count('ref: ${{ github.sha }}'), 3)
        self.assertIn('mosaic_development_release.py eligibility', classify)
        self.assertIn("needs.classify.outputs.release_required == 'true'", signer)
        self.assertNotIn('gradlew', workflow)
        self.assertNotIn('uses: ./.github/actions/setup', workflow)
        self.assertIn('run-id: ${{ needs.classify.outputs.ci_run_id }}', signer)
        self.assertIn('artifact-ids: ${{ needs.classify.outputs.artifact_id }}', signer)
        self.assertIn('mosaic_development_release.py artifact', signer)
        self.assertIn('uses: ./.github/actions/mosaic-sign-apk', signer)
        for part in (publish, signer):
            self.assertNotIn('gradlew', part)
        self.assertNotIn('secrets.', classify + publish)
        self.assertNotIn('contents: write', signer)
        self.assertIn('contents: write', publish)
        self.assertNotIn('environment:', publish)
        self.assertIn('environment: mosaic-release-signing', signer)
        self.assertEqual(signer.count('secrets.MOSAIC_'), 4)
        self.assertIn('artifact-ids: ${{ needs.sign.outputs.artifact_id }}', publish)
        self.assertIn('digest-mismatch: error', publish)
        self.assertIn('verify_mosaic_apk.py', signer)
        self.assertIn('mosaic_signing_exercise.py compare', signer)

        ci = (ROOT / release.CI_WORKFLOW).read_text()
        debug = ci.index('      - name: Run full validation')
        release_build = ci.index('      - name: Build authoritative unsigned Release after validation')
        upload = ci.index('      - name: Upload authoritative unsigned Release artifact')
        self.assertLess(debug, release_build)
        self.assertLess(release_build, upload)
        self.assertEqual(ci.count('./gradlew '), 3)
        self.assertIn("steps.main-validation-reuse.outputs.reuse_full != 'true'", ci)
        self.assertIn("if: github.event_name == 'pull_request' && steps.pr-validation.outputs.validation_mode == 'targeted-android'", ci)
        self.assertIn(':app:assembleDefaultRelease -PmosaicPublication=true --no-daemon --no-parallel --max-workers=1', ci)
        self.assertIn("if: steps.release-classification.outputs.release_required == 'true'", ci)
        self.assertIn('mosaic_development_release.py ci-eligibility', ci)
        self.assertIn('MOSAIC_ARTIFACT_PREFIX: mosaic-main-ci', ci)


if __name__ == '__main__':
    unittest.main()
