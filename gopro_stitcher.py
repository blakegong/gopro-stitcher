import argparse
from os import path
import re
import subprocess

import utils


def run(source_dir, target_dir, include_single_files):
    source_dir = path.expanduser(source_dir)
    target_dir = path.expanduser(target_dir)

    for head_rel_path in get_head_rel_paths(source_dir):
        head_path = path.join(source_dir, head_rel_path)
        target_path = path.join(target_dir, head_rel_path)

        if path.isfile(target_path):
            # already stitched before, ignore
            continue

        fragment_paths = get_fragment_paths(head_path)
        if not fragment_paths:
            # single file video
            if include_single_files:
                copy_file(head_path, target_path)
            continue

        source_paths = [head_path]
        source_paths.extend(fragment_paths)

        stitch_files(source_paths, target_path)


def get_head_rel_paths(source_dir):
    '''return head videos relative to source_dir'''
    result = subprocess.check_output(
        'find {} -name "GOPR*.MP4"'.format(source_dir), shell=True)

    return [path.relpath(p, source_dir) for p in result.strip().split('\n')]


def get_fragment_paths(head_path):
    '''return all fragment file paths of the given head video path'''
    head_directory, head_file = path.split(head_path)
    gopro_id = utils.extract_gopro_id(head_file)

    fragment_paths = []

    fragment_id = 1
    while True:
        fragment_name = utils.get_gopro_fragment_name(gopro_id, fragment_id)
        fragment_path = path.join(head_directory, fragment_name)

        if not path.exists(fragment_path):
            break

        fragment_paths.append(fragment_path)
        fragment_id += 1

    return fragment_paths


def copy_file(source_path, target_path):
    subprocess.call('mkdir -p {}'.format(
        utils.escape_path(path.dirname(target_path))),
                    shell=True)
    subprocess.call('cp {} {}'.format(utils.escape_path(source_path),
                                      utils.escape_path(target_path)),
                    shell=True)
    subprocess.call('touch -r {} {}'.format(utils.escape_path(source_path),
                                            utils.escape_path(target_path)),
                    shell=True)


def stitch_files(source_paths, target_path):
    with open('./input.txt', 'w') as f:
        for p in source_paths:
            f.write('file {}\n'.format(utils.escape_path(p)))

    subprocess.call('mkdir -p {}'.format(
        utils.escape_path(path.dirname(target_path))),
                    shell=True)

    escaped_target_path = utils.escape_path(target_path)
    subprocess.call('ffmpeg -f concat -safe 0 -i input.txt -c copy {}'.format(
        escaped_target_path),
                    shell=True)

    escaped_source_head_path = utils.escape_path(source_paths[0])
    subprocess.call(
        'exiftool -api largefilesupport=1 -overwrite_original -tagsFromFile {} {}'
        .format(escaped_source_head_path, escaped_target_path),
        shell=True)
    subprocess.call('touch -r {} {}'.format(escaped_source_head_path,
                                            escaped_target_path),
                    shell=True)
    subprocess.call('rm ./input.txt', shell=True)


def parse_args():
    parser = argparse.ArgumentParser(
        description=
        'Automatically scan GoPro videos and stitch ones that have more than 1 fragments.'
        'Stitched videos will be put into {target-dir} with the original directory hierachy.'
    )
    parser.add_argument('source_dir',
                        type=str,
                        help='Source directory of GoPro videos to be imported')
    parser.add_argument(
        '-t',
        '--target-dir',
        action='store',
        type=str,
        help=
        'Target directory for stitched GoPro videos. By default it uses \'{source-dir}_stitched\' if not specified'
    )
    parser.add_argument(
        '-i',
        '--include-single-files',
        action='store_true',
        help=
        'If enabled, single (not stitched) files would be copied to target directory too, otherwise ignored'
    )

    args = vars(parser.parse_args())

    if not args['target_dir']:
        args['target_dir'] = args['source_dir'] + '_stitched'

    return args


if __name__ == '__main__':
    args = parse_args()
    run(args['source_dir'], args['target_dir'], args['include_single_files'])
