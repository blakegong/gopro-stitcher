from invoke import task

from gopro_stitcher import GoProStitcher

@task(help={
    'source-dir': 'Source directory of imported GoPro videos',
    'target-dir': 'Target directory for stitched GoPro videos. By default it uses \'{source-dir}_stitched\' if not specified',
    'include-single-files': 'If enabled, single (not stitched) files would be copied to target directory too, otherwise ignored'
})
def stitch_gopro_videos(c, source_dir, target_dir='', include_single_files=False):
    '''
    Automatically scan GoPro videos and stitch ones that have more than 1 fragments.

    Stitched videos will be put into {target-dir} with the original directory hierachy.
    '''
    if not target_dir:
        target_dir = source_dir + '_stitched'

    gopro_stitcher = GoProStitcher(c)
    gopro_stitcher.run(source_dir, target_dir, include_single_files)
