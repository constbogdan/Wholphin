"""Public artifact transport checks for the manual protected-main signing exercise."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import zipfile

from mosaic_version import allocate, artifact_record


def artifact_name(identity, run, attempt, prefix='mosaic-signing-exercise'):
    if not re.fullmatch(r"[0-9a-f]{40}", identity['sourceSha']) or not re.fullmatch(r"[1-9][0-9]*", str(run)) or not re.fullmatch(r"[1-9][0-9]*", str(attempt)):
        raise ValueError('Invalid artifact run/source identity')
    if prefix not in ('mosaic-signing-exercise', 'mosaic-main-ci'):
        raise ValueError('Invalid artifact producer identity')
    if type(identity['versionCode']) is not int or identity['versionName'] != f"1.0.{identity['versionCode']}" or identity['versionCode'] < 1:
        raise ValueError('Invalid artifact version')
    return f"{prefix}-{identity['versionName']}-{identity['sourceSha']}-run-{run}-attempt-{attempt}"


def validate_record(record, identity, apk, run, attempt):
    expected = artifact_record(identity, apk)
    expected.update(runId=str(run), runAttempt=str(attempt))
    if record != expected:
        raise ValueError('Unsigned artifact hash/source/run provenance mismatch')


def payload(apk, signed=False):
    with zipfile.ZipFile(apk) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValueError('Duplicate APK ZIP entries')
        result = {}
        for name in names:
            signature = re.fullmatch(r'META-INF/(MANIFEST\.MF|[^/]+\.(SF|RSA|DSA|EC))', name, re.I)
            if signature:
                if not signed:
                    raise ValueError('Expected unsigned input')
                continue
            result[name] = hashlib.sha256(archive.read(name)).hexdigest()
        return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['prepare', 'check', 'compare'])
    parser.add_argument('--directory', type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    directory = args.directory
    if args.mode == 'compare':
        if payload(directory / 'unsigned.apk') != payload(directory / 'signed.apk', signed=True):
            raise ValueError('Signing changed validated APK payload')
        return
    identity = allocate(root, publication=True)
    run, attempt = os.environ['GITHUB_RUN_ID'], os.environ['GITHUB_RUN_ATTEMPT']
    name = artifact_name(identity, run, attempt, os.environ.get('MOSAIC_ARTIFACT_PREFIX', 'mosaic-signing-exercise'))
    if args.mode == 'prepare':
        metadata_path = root / 'app/build/outputs/apk/default/release/output-metadata.json'
        metadata = json.loads(metadata_path.read_text())
        if metadata['variantName'] != 'defaultRelease' or metadata['applicationId'] != 'io.github.constbogdan.mosaic':
            raise ValueError('Wrong Release variant/package')
        entries = [e for e in metadata['elements'] if e['type'] == 'UNIVERSAL' and not e['filters']]
        if len(entries) != 1:
            raise ValueError('Expected one universal Release APK')
        entry = entries[0]
        if entry['versionCode'] != identity['versionCode'] or entry['versionName'] != identity['versionName']:
            raise ValueError('Wrong APK version')
        filename = entry['outputFile']
        if Path(filename).name != filename or not re.fullmatch(r'[A-Za-z0-9.-]+\.apk', filename):
            raise ValueError('Invalid APK path')
        directory.mkdir(parents=True, exist_ok=False)
        shutil.copyfile(metadata_path.parent / filename, directory / 'unsigned.apk')
        record = artifact_record(identity, directory / 'unsigned.apk')
        record.update(runId=run, runAttempt=attempt)
        (directory / 'provenance.json').write_text(json.dumps(record, indent=2) + '\n')
        with open(os.environ['GITHUB_OUTPUT'], 'a') as output:
            output.write(f'name={name}\n')
    else:
        record = json.loads((directory / 'provenance.json').read_text())
        validate_record(record, identity, directory / 'unsigned.apk', run, attempt)
    apk = directory / 'unsigned.apk'
    if b'APK Sig Block 42' in apk.read_bytes():
        raise ValueError('Input already contains APK signing block')
    payload(apk)


if __name__ == '__main__':
    main()
