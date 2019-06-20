import pdb

import re
from os import path


def escape_path(path):
    return path.replace(' ', '\ ')


class GoProStitcher:
    def __init__(self, conn):
        self.conn = conn

    def run(self, source_dir, target_dir, include_single_files):
        source_dir = path.expanduser(source_dir)
        target_dir = path.expanduser(target_dir)

        for head_rel_path in self.get_head_rel_paths(source_dir):
            head_path = path.join(source_dir, head_rel_path)
            target_path = path.join(target_dir, head_rel_path)

            if path.isfile(target_path):
                # already stitched before, ignore
                continue

            fragment_paths = self.get_fragment_paths(head_path)
            if not fragment_paths:
                # single file video
                if include_single_files:
                    self.copy_file(head_path, target_path)
                continue

            source_paths = [head_path]
            source_paths.extend(fragment_paths)

            self.stitch_files(source_paths, target_path)

    def get_head_rel_paths(self, source_dir):
        '''return head videos relative to source_dir'''
        result = self.conn.run('find {} -name "GOPR*.MP4"'.format(source_dir), hide=True)

        if not result.ok:
            raise Exception('No GOPRO video files found!')

        return [path.relpath(p, source_dir) for p in result.stdout.strip().split('\n')]

    def get_fragment_paths(self, head_path):
        '''return all fragment file paths of the given head video path'''
        head_directory, head_file = path.split(head_path)
        gopro_id = self.extract_gopro_id(head_file)

        fragment_paths = []

        fragment_id = 1
        while True:
            fragment_name = self.get_gopro_fragment_name(gopro_id, fragment_id)
            fragment_path = path.join(head_directory, fragment_name)

            if not path.exists(fragment_path):
                break

            fragment_paths.append(fragment_path)
            fragment_id += 1

        return fragment_paths

    def extract_gopro_id(self, file_name):
        '''return ID of given video file name, as string'''
        pattern = 'GOPR(.*).MP4'
        m = re.search(pattern, file_name)
        if m:
            return m.group(1)

    def get_gopro_fragment_name(self, gopro_id, fragment_id):
        return 'GP{}{}.MP4'.format(format(fragment_id, '02'), gopro_id)

    def copy_file(self, source_path, target_path):
        self.conn.run('mkdir -p {}'.format(escape_path(path.dirname(target_path))))
        self.conn.run('cp {} {}'.format(escape_path(source_path), escape_path(target_path)))
        self.conn.run('touch -r {} {}'.format(escape_path(source_path), escape_path(target_path)))

    def stitch_files(self, source_paths, target_path):
        with open('./input.txt', 'w') as f:
            for p in source_paths:
                f.write('file {}\n'.format(escape_path(p)))

        self.conn.run('mkdir -p {}'.format(escape_path(path.dirname(target_path))))

        escaped_target_path = escape_path(target_path)
        self.conn.run('ffmpeg -f concat -safe 0 -i input.txt -c copy {}'.format(escaped_target_path))

        escaped_source_head_path = escape_path(source_paths[0])
        self.conn.run('exiftool -api largefilesupport=1 -overwrite_original -tagsFromFile {} {}'.format(
            escaped_source_head_path, escaped_target_path))
        self.conn.run('touch -r {} {}'.format(escaped_source_head_path, escaped_target_path))
        self.conn.run('rm ./input.txt')
