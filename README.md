# GoPro Stitcher

<img src="./assets/gopro_logo.svg" width="200">

Automatic stitcher for your fragmented GoPro videos.

![sample](assets/sample.png)

## Usage

MacOS:
Install required third-party packages:
```
brew install ffmpeg
brew install exiftool
```

This tool should work with Python 2.7/3.6 with no dependencies, so:
```
python gopro_stitcher.py -h
python gopro_stitcher.py {YOUR_GOPRO_DIRECTORY}
```

## Notes

Geo-location data stitching (GPS info) is not supported, since the work is for my dated GoPro 4.

I will be happy to explore the feasibility if you could kindly help provide sample videos!
