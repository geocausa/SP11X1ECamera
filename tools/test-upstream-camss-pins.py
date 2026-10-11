#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Check real descriptor-tool rejection of altered, absent and symlink inputs."""
import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference', required=True, type=Path)
    parser.add_argument('--candidate', required=True, type=Path)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    names = ['camss-vfe.c', 'camss-vfe.h', 'camss-vfe-680.c', 'camss-vfe-17x.c',
             'camss-vfe-340.c', 'camss-vfe-480.c', 'camss-vfe-690.c', 'camss-vfe-780.c']
    prefix = Path('drivers/media/platform/qcom/camss')
    cases = ['reference_changed', 'reference_missing', 'reference_symlink',
             'candidate_changed', 'patch_changed']
    for case in cases:
        with tempfile.TemporaryDirectory(prefix='camss-pin-rejection-') as directory:
            work = Path(directory)
            tool = work / 'tools/test-upstream-camss-descriptors.py'
            tool.parent.mkdir()
            shutil.copyfile(repo / 'tools/test-upstream-camss-descriptors.py', tool)
            shutil.copytree(repo / 'src/upstream/camss/patches', work / 'src/upstream/camss/patches')
            for root, original in [('reference', args.reference), ('candidate', args.candidate)]:
                target = work / root / prefix
                target.mkdir(parents=True)
                for name in names:
                    shutil.copyfile(original / prefix / name, target / name)
            path = work / 'reference' / prefix / names[0]
            if case == 'reference_missing':
                path.unlink()
            elif case == 'reference_symlink':
                target = path.with_name('actual.c')
                path.rename(target)
                path.symlink_to(target.name)
            else:
                if case == 'candidate_changed':
                    path = work / 'candidate' / prefix / names[0]
                elif case == 'patch_changed':
                    path = work / 'src/upstream/camss/patches/0001-camss-drop-unused-rfc-format-helper.patch'
                with path.open('a') as output:
                    output.write('\n/* synthetic source mutation */\n')
            result = subprocess.run(['python3', str(tool), '--reference', str(work / 'reference'),
                                     '--candidate', str(work / 'candidate')], capture_output=True, text=True)
            reason = 'missing or symlink source' if case in ['reference_missing', 'reference_symlink'] else 'changed pinned source'
            if result.returncode == 0 or reason not in result.stderr:
                raise RuntimeError(f'{case}: incorrect rejection: {result.returncode} {result.stderr}')
            print(case + ' PASS')
    print('PASS actual source/patch pin rejection cases=5; no camera access')


if __name__ == '__main__':
    main()
