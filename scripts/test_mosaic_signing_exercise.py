"""Offline public fixtures and workflow trust-boundary regression checks; no keys."""

import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import mosaic_signing_exercise as exercise
from mosaic_signing_exercise import artifact_name, payload, validate_record
from mosaic_version import artifact_record


class ExerciseTests(unittest.TestCase):
    def setUp(self):
        self.identity = dict(publication=True, dirty=False, sourceSha='a' * 40,
                             sourceTree='b' * 40, epoch='c' * 40, upstreamBaseline='d' * 40,
                             versionCode=2, versionName='1.0.2', buildTime=123)

    def test_artifact_identity(self):
        name = artifact_name(self.identity, '123', '2')
        self.assertEqual(name, 'mosaic-signing-exercise-1.0.2-' + 'a' * 40 + '-run-123-attempt-2')
        self.assertEqual(
            artifact_name(self.identity, '123', '2', 'mosaic-main-ci'),
            'mosaic-main-ci-1.0.2-' + 'a' * 40 + '-run-123-attempt-2',
        )
        for run, attempt in [('123/other', '1'), ('123', '0')]:
            with self.assertRaises(ValueError):
                artifact_name(self.identity, run, attempt)
        with self.assertRaises(ValueError):
            artifact_name(self.identity, '123', '2', 'caller-controlled')

    def test_provenance_binds_source_run_attempt_and_exact_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            apk = Path(tmp) / 'fixture.apk'
            apk.write_bytes(b'public unsigned fixture')
            record = artifact_record(self.identity, apk)
            record.update(runId='123', runAttempt='1')
            validate_record(record, self.identity, apk, '123', '1')
            for field, value in [('sourceSha', 'e' * 40), ('versionCode', 3), ('apkSha256', '0' * 64),
                                 ('runId', '124'), ('runAttempt', '2'), ('publication', False)]:
                changed = dict(record, **{field: value})
                with self.assertRaises(ValueError):
                    validate_record(changed, self.identity, apk, '123', '1')
            apk.write_bytes(b'changed bytes')
            with self.assertRaises(ValueError):
                validate_record(record, self.identity, apk, '123', '1')

    def test_sign_only_identity_check_requires_only_exact_shallow_checkout(self):
        identity = dict(self.identity, buildTime=123000, epoch=exercise.EPOCH,
                        upstreamBaseline=exercise.UPSTREAM_BASELINE)
        record = dict(identity, apkSha256='e' * 64, runId='123', runAttempt='1')
        with patch.object(exercise, 'git', side_effect=[identity['sourceSha'], identity['sourceTree'], '123', '']) as git:
            self.assertEqual(exercise.shallow_checkout_identity(Path('fixture'), record), identity)
        commands = [call.args[1:] for call in git.call_args_list]
        self.assertNotIn(('rev-list', '--first-parent', 'HEAD'), commands)
        self.assertNotIn(('rev-parse', '--is-shallow-repository'), commands)
        for field, value in [('sourceSha', 'f' * 40), ('sourceTree', 'f' * 40),
                             ('epoch', 'f' * 40), ('upstreamBaseline', 'f' * 40),
                             ('publication', False), ('dirty', True), ('versionName', '1.0.3')]:
            with self.subTest(field=field), patch.object(
                exercise, 'git', side_effect=[identity['sourceSha'], identity['sourceTree'], '123', '']
            ), self.assertRaises(ValueError):
                exercise.shallow_checkout_identity(Path('fixture'), dict(record, **{field: value}))

    def test_sign_only_identity_check_runs_in_real_shallow_clone(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'source'
            checkout = Path(tmp) / 'checkout'
            source.mkdir()
            subprocess.run(['git', 'init', '--quiet'], cwd=source, check=True)
            subprocess.run(['git', 'config', 'user.name', 'Fixture'], cwd=source, check=True)
            subprocess.run(['git', 'config', 'user.email', 'fixture@example.invalid'], cwd=source, check=True)
            (source / 'fixture.txt').write_text('fixture\n')
            subprocess.run(['git', 'add', 'fixture.txt'], cwd=source, check=True)
            subprocess.run(['git', 'commit', '--quiet', '-m', 'Fixture'], cwd=source, check=True)
            subprocess.run(['git', 'clone', '--quiet', '--depth=1', source.as_uri(), str(checkout)], check=True)
            self.assertEqual('true', exercise.git(checkout, 'rev-parse', '--is-shallow-repository'))
            identity = dict(
                publication=True,
                dirty=False,
                sourceSha=exercise.git(checkout, 'rev-parse', 'HEAD'),
                sourceTree=exercise.git(checkout, 'rev-parse', 'HEAD^{tree}'),
                epoch=exercise.EPOCH,
                upstreamBaseline=exercise.UPSTREAM_BASELINE,
                versionCode=12,
                versionName='1.0.12',
                buildTime=int(exercise.git(checkout, 'show', '-s', '--format=%ct', 'HEAD')) * 1000,
            )
            record = dict(identity, apkSha256='e' * 64, runId='123', runAttempt='1')
            self.assertEqual(identity, exercise.shallow_checkout_identity(checkout, record))

    def test_payload_allows_only_signature_entries(self):
        with tempfile.TemporaryDirectory() as tmp:
            unsigned, signed = Path(tmp) / 'unsigned.apk', Path(tmp) / 'signed.apk'
            with zipfile.ZipFile(unsigned, 'w') as archive:
                archive.writestr('classes.dex', b'public fixture')
            with zipfile.ZipFile(signed, 'w') as archive:
                archive.writestr('classes.dex', b'public fixture')
                archive.writestr('META-INF/CERT.RSA', b'not a real certificate')
            self.assertEqual(payload(unsigned), payload(signed, signed=True))
            with self.assertRaises(ValueError):
                payload(signed)
            with zipfile.ZipFile(signed, 'a') as archive:
                archive.writestr('unexpected', b'changed')
            self.assertNotEqual(payload(unsigned), payload(signed, signed=True))

    def test_prepare_and_check_exact_universal_transport(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'repo'
            metadata_dir = root / 'app/build/outputs/apk/default/release'
            metadata_dir.mkdir(parents=True)
            with zipfile.ZipFile(metadata_dir / 'release.apk', 'w') as archive:
                archive.writestr('classes.dex', b'public fixture')
            metadata = dict(variantName='defaultRelease', applicationId='io.github.constbogdan.mosaic',
                            elements=[dict(type='UNIVERSAL', filters=[], outputFile='release.apk',
                                           versionCode=2, versionName='1.0.2')])
            (metadata_dir / 'output-metadata.json').write_text(json.dumps(metadata))
            directory = Path(tmp) / 'transport'
            env = dict(GITHUB_RUN_ID='123', GITHUB_RUN_ATTEMPT='1', GITHUB_OUTPUT=str(Path(tmp) / 'outputs'))
            with patch.object(exercise, '__file__', str(root / 'scripts/mosaic_signing_exercise.py')), \
                    patch.object(exercise, 'allocate', return_value=self.identity), \
                    patch.object(exercise, 'shallow_checkout_identity', return_value=self.identity), \
                    patch.dict('os.environ', env):
                with patch('sys.argv', ['exercise', 'prepare', '--directory', str(directory)]):
                    exercise.main()
                self.assertEqual((directory / 'unsigned.apk').read_bytes(), (metadata_dir / 'release.apk').read_bytes())
                with patch('sys.argv', ['exercise', 'check', '--directory', str(directory)]):
                    exercise.main()
                    (directory / 'unsigned.apk').write_bytes(b'tampered')
                    with self.assertRaisesRegex(ValueError, 'mismatch'):
                        exercise.main()

    def test_workflow_is_manual_main_only_with_separate_signer(self):
        workflow = (Path(__file__).resolve().parent.parent / '.github/workflows/mosaic-signing-exercise.yml').read_text(encoding='utf-8-sig')
        build, sign = workflow.split('\n  sign:\n')
        action = (Path(__file__).resolve().parent.parent / '.github/actions/mosaic-sign-apk/action.yml').read_text()
        self.assertIn('workflow_dispatch:', build)
        for forbidden in ('pull_request:', 'push:', 'schedule:', 'contents: write', 'gh release', 'git push', 'SYNC_BOT', 'GITHUB_TOKEN }}'):
            self.assertNotIn(forbidden, workflow)
        self.assertIn('contents: read', workflow)
        guard = "github.ref == 'refs/heads/main' && github.ref_protected && inputs.expected_sha == github.sha"
        self.assertIn(guard, build)
        self.assertIn(guard, sign)
        self.assertNotIn('secrets.', build)
        self.assertNotIn('environment:', build)
        self.assertIn('needs: build', sign)
        self.assertIn('environment: mosaic-release-signing', sign)
        self.assertIn('artifact-ids: ${{ needs.build.outputs.artifact_id }}', sign)
        self.assertIn('digest-mismatch: error', sign)
        self.assertIn('[[ "$INPUT_ARTIFACT_ID" =~ ^[1-9][0-9]*$ ]]', sign)
        self.assertNotIn('gradlew', sign)
        self.assertNotIn('./.github/actions/setup', sign)
        secret_step = sign.split('      - name: Sign exact input without rebuilding')[1].split('      - name: Verify signed identity')[0]
        self.assertEqual(sign.count('secrets.'), 4)
        self.assertEqual(secret_step.count('secrets.'), 4)
        self.assertIn("trap '", action)
        self.assertIn('>/dev/null 2>&1', action)
        self.assertIn('uses: ./.github/actions/mosaic-sign-apk', secret_step)
        self.assertIn('verify_mosaic_apk.py', sign)
        self.assertIn('mosaic_signing_exercise.py compare', sign)
        self.assertIn('retention-days: 7', sign)
        self.assertIn('path: ${{ runner.temp }}/mosaic-result/', sign)
        self.assertIn('fetch-depth: 0', build)
        self.assertIn('fetch-depth: 1', sign)
        for task in ('compileDefaultDebugKotlin', 'testDefaultDebugUnitTest', 'assembleDefaultDebug',
                     'assembleDefaultRelease'):
            self.assertIn(':app:' + task, build)

    def test_direct_environment_binding_and_shared_operation_do_not_drift(self):
        root = Path(__file__).resolve().parent.parent
        exercise = (root / '.github/workflows/mosaic-signing-exercise.yml').read_text()
        development = (root / '.github/workflows/ci.yml').read_text()
        sign = exercise.split('\n  sign:\n')[1].strip()
        development_sign = development.split('\n  sign-development:\n')[1].split('\n  publish-development:\n')[0].strip()
        # Artifact acquisition differs (same-run diagnostic versus same-run Release build),
        # while key isolation and the signing operation remain identical.
        self.assertFalse((root / '.github/workflows/mosaic-isolated-sign.yml').exists())
        for job in (sign, development_sign):
            self.assertIn('environment: mosaic-release-signing', job)
            self.assertIn('permissions:\n      contents: read', job)
        self.assertNotIn('secrets: inherit', exercise + development_sign)
        secret_steps = []
        for job in (sign, development_sign):
            before, secret = job.split('      - name: Sign exact input without rebuilding')
            secret, after = secret.split('      - name: Verify signed identity')
            self.assertNotIn('secrets.', before + after)
            self.assertEqual(secret.count('secrets.MOSAIC_'), 4)
            self.assertIn('uses: ./.github/actions/mosaic-sign-apk', secret)
            secret_steps.append(secret)
        self.assertEqual(secret_steps[0], secret_steps[1])
        action = (root / '.github/actions/mosaic-sign-apk/action.yml').read_text()
        for forbidden in ('gradlew', 'checkout', 'setup-', 'secrets:', 'inputs:', 'SYNC_BOT'):
            self.assertNotIn(forbidden, action)
        self.assertEqual(action.count('/apksigner" sign '), 1)
        self.assertLess(action.index('Missing required signing secret'), action.index('mktemp'))

    def test_presence_diagnostics_never_print_values_and_fail_before_signing(self):
        import os
        import shutil
        import subprocess
        root = Path(__file__).resolve().parent.parent
        action = (root / '.github/actions/mosaic-sign-apk/action.yml').read_text()
        body = action.split('      run: |\n')[1]
        script = '\n'.join(line[8:] for line in body.splitlines()).split('umask 077')[0]
        bash = shutil.which('bash')
        if os.name == 'nt':
            bash = str(Path(os.environ.get('ProgramFiles', 'C:/Program Files')) / 'Git/bin/bash.exe')
        if not bash or not Path(bash).exists():
            self.skipTest('Bash required for executing public-only presence fixtures')
        names = ['MOSAIC_SIGNING_KEY', 'MOSAIC_KEY_ALIAS', 'MOSAIC_KEYSTORE_PASSWORD', 'MOSAIC_KEY_PASSWORD']
        fixture = {name: 'public-test-value-' + name for name in names}
        for missing in [None, *names]:
            env = dict(os.environ, **fixture)
            if missing:
                env[missing] = ''
            result = subprocess.run([bash, '-c', script], env=env, capture_output=True, text=True, timeout=20)
            with self.subTest(missing=missing):
                self.assertEqual(result.returncode, 1 if missing else 0)
                output = result.stdout + result.stderr
                for name in names:
                    self.assertNotIn(fixture[name], output)
                    self.assertIn('Missing required signing secret: ' + name if name == missing else name + ': present', output)

    def test_validation_and_release_are_sequential_bounded_steps(self):
        workflow = (Path(__file__).resolve().parent.parent / '.github/workflows/mosaic-signing-exercise.yml').read_text()
        build = workflow.split('\n  sign:\n')[0]
        debug, release = build.split('      - name: Build unsigned Release after validation\n')
        debug = debug.split('      - name: Full Debug validation\n')[1]
        release = release.split('      - name: Prepare exact universal unsigned input\n')[0]
        for phase in (debug, release):
            self.assertEqual(phase.count('./gradlew '), 1)
            for flag in ('-PmosaicPublication=true', '--no-daemon', '--no-parallel', '--max-workers=1'):
                self.assertIn(flag, phase)
            for bypass in ('continue-on-error', 'if:', 'always()', '||', ' &', 'clean', '--exclude-task', ' -x '):
                self.assertNotIn(bypass, phase)
        for task in ('compileDefaultDebugKotlin', 'testDefaultDebugUnitTest', 'assembleDefaultDebug'):
            self.assertIn(':app:' + task, debug)
            self.assertNotIn(':app:' + task, release)
        self.assertNotIn(':app:assembleDefaultRelease', debug)
        self.assertIn(':app:assembleDefaultRelease', release)


if __name__ == '__main__':
    unittest.main()
