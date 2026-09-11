"""Offline I05 presentation and preserved delivery-contract checks."""
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import textwrap
import unittest
from unittest.mock import Mock, patch

import hosted_upstream as upstream
import mosaic_delivery_output as output
import mosaic_development_release as development
import mosaic_signing_exercise as transport
import mosaic_stable as stable
import test_mosaic_development_release as fixtures


ROOT = Path(__file__).resolve().parent.parent


class DeliveryOutputTests(unittest.TestCase):
    def setUp(self):
        fixture = fixtures.PublisherTests()
        fixture.setUp()
        self.m, self.apk = fixture.m, fixture.apk

    def test_release_titles_still_match_installed_updater_and_asset_contract(self):
        checker = (ROOT / 'app/src/main/java/com/github/damontecres/wholphin/services/UpdateChecker.kt').read_text(encoding='utf-8')
        version = (ROOT / 'app/src/main/java/com/github/damontecres/wholphin/util/Version.kt').read_text(encoding='utf-8')
        self.assertIn('result.jsonObject["name"]', checker)
        self.assertIn('Version.tryFromString(name)', checker)
        self.assertIn('const val ASSET_NAME = "Wholphin"', checker)
        self.assertIn('add("$ASSET_NAME$releaseSuffix.apk")', checker)
        pattern = re.search(r'VERSION_REGEX = Regex\("(.+)"\)', version)[1].replace('\\\\', '\\')
        for fields in (development.release_fields(self.m, False),
                       development.release_fields(self.m, False, archive=True), stable.fields(self.m, False)):
            self.assertEqual('v1.0.5', fields['name'])
            self.assertIsNotNone(re.fullmatch(pattern, fields['name']))
        self.assertIsNone(re.fullmatch(pattern, 'Mosaic v1.0.5 — Development'))
        self.assertEqual('Wholphin-release.apk', development.APK_NAME)
        self.assertEqual('Wholphin-release.apk', self.m['assetName'])

    def test_release_bodies_distinguish_channels_without_changing_identity(self):
        before = copy.deepcopy(self.m)
        bodies = [development.release_fields(self.m, False)['body'],
                  development.release_fields(self.m, False, archive=True)['body'],
                  stable.fields(self.m, False)['body']]
        for body in bodies:
            for value in (self.m['versionName'], self.m['immutableIdentity'], self.m['sourceSha'],
                          self.m['signedApkSha256'], 'mosaic-release.json', 'Wholphin-release.apk'):
                self.assertIn(value, body)
            self.assertIn('/commit/' + self.m['sourceSha'], body)
        self.assertIn('rolling Development', bodies[0])
        self.assertIn('Immutable archive', bodies[1])
        self.assertIn('Promoted unchanged', bodies[2])
        self.assertEqual(before, self.m)

    def test_existing_published_bodies_are_not_backfilled_on_retry(self):
        api = fixtures.FakeGitHub()
        development.publish(api, self.m, self.apk)
        for release in api.releases.values():
            release['body'] = 'Historical body retained'
        before = copy.deepcopy((api.refs, api.tags, api.releases, api.uploads))
        api.calls.clear()
        development.publish(api, self.m, self.apk)
        self.assertEqual(before, (api.refs, api.tags, api.releases, api.uploads))
        self.assertFalse(any(method in ('POST', 'PATCH', 'DELETE') for method, _, _ in api.calls))

    def test_publication_summaries_preserve_original_and_recovery_identity(self):
        env = dict(MOSAIC_CHECKPOINT='signed', MOSAIC_ARTIFACT_ID='123', GITHUB_SHA='e' * 40,
                   GITHUB_RUN_ID='999', GITHUB_RUN_ATTEMPT='2')
        for operation, heading in [('publish', 'Published'), ('promote', 'Promoted'), ('recover', 'Recovered')]:
            text = output.publication_summary(self.m, operation, env)
            self.assertTrue(text.startswith('## ' + heading))
            for value in (self.m['sourceSha'], self.m['signedApkSha256'], self.m['immutableIdentity']):
                self.assertIn(value, text)
            self.assertIn('Original build run: ' + self.m['buildRunId'], text)
        recovered = output.publication_summary(self.m, 'recover', env)
        self.assertIn('signed artifact', recovered)
        self.assertIn('Recovery tooling source: ' + env['GITHUB_SHA'], recovered)
        self.assertIn('Recovery run: 999 / attempt 2', recovered)
        self.assertIn('Gradle work: none', recovered)
        self.assertIn('unsigned artifact', output.publication_summary(self.m, 'recover', dict(env, MOSAIC_CHECKPOINT='unsigned')))
        promoted = output.publication_summary(self.m, 'promote', env)
        self.assertIn('Exact Development bytes reused', promoted)
        self.assertIn('/releases/tag/mosaic-v1.0.5', promoted)

    def test_non_apk_summary_preserves_machine_outputs_and_immutable_compare(self):
        result = dict(releaseRequired=False, outcome='skipped_non_apk', releaseRelevance='tooling-only',
                      validationRisk='high', baselineSha='a' * 40, currentSha='b' * 40,
                      paths=[dict(path=f'scripts/fixture{i}.py') for i in range(24)], reason='fixture')
        with tempfile.TemporaryDirectory() as temp:
            env = dict(GITHUB_OUTPUT=str(Path(temp) / 'outputs'), GITHUB_STEP_SUMMARY=str(Path(temp) / 'summary'))
            development.record_eligibility(result, None, env)
            values = dict(line.split('=', 1) for line in Path(env['GITHUB_OUTPUT']).read_text().splitlines())
            summary = Path(env['GITHUB_STEP_SUMMARY']).read_text(encoding='utf-8')
        self.assertEqual('skipped_non_apk', values['outcome'])
        self.assertEqual('false', values['release_required'])
        self.assertTrue(summary.startswith('## Skipped'))
        self.assertIn('tooling-only', summary)
        self.assertIn('high', summary)
        self.assertIn('Changed paths: 24', summary)
        self.assertIn('build/sign/publish not required', summary)
        self.assertIn('/compare/' + 'a' * 40 + '...' + 'b' * 40, summary)

    def test_sync_heading_distinguishes_conflict_and_operational_failure_without_changing_json(self):
        for outcome, conflict, error, label in [('no_delta', False, False, 'No upstream delta'),
                                               ('ready', False, False, 'Ready candidate'),
                                               ('blocked', True, False, 'Blocked · semantic conflicts'),
                                               ('blocked', False, True, 'Publication error')]:
            record = dict(outcome=outcome, textual_conflicts=conflict, reason='<untrusted>')
            before = copy.deepcopy(record)
            summary = upstream.upstream_summary(record, publication=True, operation_error=error)
            self.assertTrue(summary.startswith('## ' + label))
            self.assertIn('&lt;untrusted&gt;', summary)
            self.assertNotIn('<untrusted>', summary)
            self.assertEqual(before, record)
        with patch.object(upstream.subprocess, 'run', return_value=Mock(returncode=1)):
            with self.assertRaises(upstream.OperationError) as error:
                upstream.command(['gh', 'api'])
        self.assertIsInstance(error.exception, upstream.Blocked)

    def test_mapping_is_exact_existing_output_with_source_and_digest(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            mapping = root / 'app/build/outputs/mapping/defaultRelease/mapping.txt'
            mapping.parent.mkdir(parents=True)
            mapping.write_bytes(b'original.Class -> a:\n')
            unsigned = root / 'unsigned'
            unsigned.mkdir()
            (unsigned / 'provenance.json').write_text(json.dumps(self.m['source']))
            destination = root / 'diagnostic'
            transport.prepare_mapping(root, unsigned, destination)
            record = json.loads((destination / 'mapping.json').read_text())
            self.assertEqual(mapping.read_bytes(), (destination / 'mapping.txt').read_bytes())
            self.assertEqual(self.m['source'], record['source'])
            self.assertEqual(self.m['immutableIdentity'], record['immutableIdentity'])
            self.assertEqual(hashlib.sha256(mapping.read_bytes()).hexdigest(), record['mappingSha256'])
            self.assertEqual('.github/workflows/ci.yml', record['buildWorkflow'])
            self.assertEqual({'mapping.txt', 'mapping.json'}, {p.name for p in destination.iterdir()})
            mapping.write_bytes(b'')
            with self.assertRaises(ValueError):
                transport.prepare_mapping(root, unsigned, root / 'empty')
            mapping.unlink()
            with self.assertRaises(FileNotFoundError):
                transport.prepare_mapping(root, unsigned, root / 'missing')

    def test_workflow_display_changes_preserve_authenticated_jobs_and_names(self):
        expected = {'mosaic-development-release.yml': 'Mosaic — Development Release',
                    'mosaic-development-resume.yml': 'Mosaic — Development Recovery',
                    'mosaic-stable-promotion.yml': 'Mosaic — Stable Promotion',
                    'mosaic-signing-exercise.yml': 'Mosaic — Signing Diagnostic',
                    'upstream-sync.yml': 'Upstream — Synchronization'}
        for file, name in expected.items():
            source = (ROOT / '.github/workflows' / file).read_text(encoding='utf-8')
            self.assertEqual('name: ' + name, source.splitlines()[0])
            run_name = source.splitlines()[1]
            self.assertTrue(run_name.startswith('run-name:'))
            run_name_source = source.split('\non:\n', 1)[0]
            for forbidden in ('needs.', 'steps.', 'github.run_number'):
                self.assertNotIn(forbidden, run_name_source)
            if file in ('mosaic-development-release.yml', 'mosaic-development-resume.yml'):
                sign = source.split('\n  sign:\n')[1].split('\n  publish:\n')[0]
                self.assertFalse(re.match(r'    name:', sign))
                self.assertNotIn('signing exercise', source.lower())
                self.assertIn('environment: mosaic-release-signing', source)
        ci = (ROOT / development.CI_WORKFLOW).read_text(encoding='utf-8')
        self.assertEqual('name: CI', ci.splitlines()[0])
        self.assertIn('    name: Full validation', ci)
        self.assertEqual('Full validation', development.CI_JOB)
        diagnostic = (ROOT / '.github/workflows/mosaic-signing-exercise.yml').read_text(encoding='utf-8')
        self.assertIn('no GitHub Release publication', diagnostic)
        self.assertNotIn('publication is a separate job', diagnostic.lower())

    def test_lifecycle_run_names_use_best_trigger_time_human_identity(self):
        ci = (ROOT / '.github/workflows/ci.yml').read_text(encoding='utf-8')
        ci_run_name = ci.split('\non:\n', 1)[0]
        self.assertIn("format('PR #{0} · {1}', github.event.pull_request.number, github.head_ref)", ci_run_name)
        self.assertIn("format('Validate · {0}', github.ref_name)", ci_run_name)
        self.assertIn("|| ' '", ci_run_name)

        development = (ROOT / '.github/workflows/mosaic-development-release.yml').read_text(encoding='utf-8')
        development_run_name = development.split('\non:\n', 1)[0]
        self.assertIn('Development fallback · ${{ inputs.expected_sha }}', development_run_name)
        self.assertNotIn('github.event.workflow_run', development_run_name)
        self.assertNotIn('head_commit.message', development_run_name)

        stable = (ROOT / '.github/workflows/mosaic-stable-promotion.yml').read_text(encoding='utf-8')
        self.assertEqual('run-name: Stable · from ${{ inputs.build }}', stable.splitlines()[1])

    def test_mapping_workflow_is_conditional_separate_and_never_rebuilds(self):
        ci = (ROOT / development.CI_WORKFLOW).read_text(encoding='utf-8')
        mapping = ci.split('      - name: Retain authoritative Release mapping and identity')[1].split('\n  sign-development:')[0]
        self.assertEqual(3, mapping.count("if: steps.eligibility.outputs.release_required == 'true'"))
        self.assertIn('mapping-${{ steps.prepared.outputs.name }}', mapping)
        self.assertIn('compression-level: 6', mapping)
        self.assertIn('retention-days: 7', mapping)
        self.assertNotIn('gradlew', mapping)
        self.assertIn('mosaic-main-mapping', mapping)
        self.assertIn('mosaic-main-release', mapping)

    def test_guard_explanation_executes_without_credentials_and_does_not_authorize(self):
        source = (ROOT / development.WORKFLOW).read_text(encoding='utf-8')
        job = source.split('\n  explain_guard:\n')[1].split('\n  classify:\n')[0]
        self.assertNotIn('checkout', job.split('    steps:')[1].split('      - name:')[1])
        self.assertNotIn('GH_TOKEN', job)
        self.assertNotIn('GITHUB_OUTPUT', job)
        script = textwrap.dedent(job.split("python3 - <<'PY'\n")[1].rsplit('          PY', 1)[0])
        base = dict(EVENT_NAME='workflow_run', CI_EVENT='push', CI_RESULT='success', CI_BRANCH='main',
                    CI_REPOSITORY=development.REPOSITORY, CI_SHA='a' * 40, GITHUB_SHA='a' * 40, EXPECTED_SHA='a' * 40)
        for changes, reason in [({}, None), ({'CI_RESULT': 'failure'}, 'did not succeed'),
                                ({'CI_SHA': 'b' * 40}, 'Superseded source'),
                                ({'CI_EVENT': 'pull_request'}, 'not a push'),
                                ({'EVENT_NAME': 'workflow_dispatch', 'EXPECTED_SHA': 'b' * 40}, 'Approved source differs')]:
            with self.subTest(changes=changes), tempfile.TemporaryDirectory() as temp:
                summary = Path(temp) / 'summary'
                with patch.dict(os.environ, dict(base, **changes, GITHUB_STEP_SUMMARY=str(summary)), clear=True):
                    exec(compile(script, '<workflow guard summary>', 'exec'), {})
                if reason:
                    self.assertIn(reason, summary.read_text(encoding='utf-8'))
                else:
                    self.assertFalse(summary.exists())


if __name__ == '__main__':
    unittest.main()
