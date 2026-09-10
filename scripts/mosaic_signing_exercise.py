"""Public artifact transport checks for the manual protected-main signing exercise."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import zipfile

from mosaic_version import EPOCH, UPSTREAM_BASELINE, allocate, artifact_record, git


IDENTITY_FIELDS = (
    'versionCode', 'versionName', 'sourceSha', 'sourceTree', 'buildTime',
    'dirty', 'publication', 'epoch', 'upstreamBaseline',
)


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


def shallow_checkout_identity(root, record):
    """Authenticate build-produced identity using only the checked-out commit and tree."""
    if set(record) != {*IDENTITY_FIELDS, 'apkSha256', 'runId', 'runAttempt'}:
        raise ValueError('Unsigned artifact identity fields are incomplete or unexpected')
    identity = {field: record[field] for field in IDENTITY_FIELDS}
    source = git(root, 'rev-parse', 'HEAD')
    tree = git(root, 'rev-parse', 'HEAD^{tree}')
    build_time = int(git(root, 'show', '-s', '--format=%ct', 'HEAD')) * 1000
    if (identity.get('sourceSha') != source or identity.get('sourceTree') != tree
            or identity.get('buildTime') != build_time
            or identity.get('epoch') != EPOCH or identity.get('upstreamBaseline') != UPSTREAM_BASELINE
            or identity.get('publication') is not True or identity.get('dirty') is not False
            or git(root, 'status', '--porcelain', '--untracked-files=normal')):
        raise ValueError('Unsigned artifact identity differs from the exact clean checkout')
    artifact_name(identity, record['runId'], record['runAttempt'])
    return identity


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


def prepare_mapping(root, unsigned_directory, directory):
    """Retain existing main Release mapping separately from authenticated APK input."""
    record = json.loads((unsigned_directory / 'provenance.json').read_text(encoding='utf-8'))
    mapping = (root / 'app/build/outputs/mapping/defaultRelease/mapping.txt').read_bytes()
    if not mapping.strip():
        raise ValueError('Authoritative Release mapping is empty')
    directory.mkdir(parents=True, exist_ok=False)
    (directory / 'mapping.txt').write_bytes(mapping)
    metadata = dict(schemaVersion=1, mappingSha256=hashlib.sha256(mapping).hexdigest(),
                    immutableIdentity=f"downstream-build-{record['versionCode']}",
                    buildWorkflow='.github/workflows/ci.yml', source=record)
    (directory / 'mapping.json').write_text(json.dumps(metadata, indent=2) + '\n', encoding='utf-8')


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
    run, attempt = os.environ['GITHUB_RUN_ID'], os.environ['GITHUB_RUN_ATTEMPT']
    if args.mode == 'prepare':
        identity = allocate(root, publication=True)
        name = artifact_name(identity, run, attempt, os.environ.get('MOSAIC_ARTIFACT_PREFIX', 'mosaic-signing-exercise'))
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
        identity = shallow_checkout_identity(root, record)
        validate_record(record, identity, directory / 'unsigned.apk', run, attempt)
    apk = directory / 'unsigned.apk'
    if b'APK Sig Block 42' in apk.read_bytes():
        raise ValueError('Input already contains APK signing block')
    payload(apk)


if __name__ == '__main__':
    main()
