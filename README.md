# Motion Tracker CLI

A Python command-line tool for motion tracking using Background Subtraction and Spatio-Temporal Analysis. This script processes video files to identify and track moving objects without requiring a GUI.

## Overview

The tool uses OpenCV to apply the following pipeline:
1. **Background Subtraction**: Uses `cv2.createBackgroundSubtractorMOG2()` to dynamically model the background and separate moving foreground objects.
2. **Morphological Filtering**: Applies erosion and dilation to the foreground mask to remove noise and fill in gaps within moving objects.
3. **Contour Detection**: Identifies bounding boxes for the cleaned foreground objects that meet a minimum area threshold.
4. **Logging**: Calculates the timestamp of detected motion and logs it (maintaining a maximum of one entry per second).

## Requirements

- Python 3.6+
- OpenCV
- NumPy

```bash
pip install opencv-python numpy
```

## Usage

The `tracker.py` script requires an input video and a log file path. It can optionally output the processed video with bounding boxes.

### Arguments

- `--input` (required): Path to the input video file.
- `--log` (required): Path to save the `.txt` log file with motion timestamps.
- `--output-vid` (optional): Path to save the processed video.
- `--min-area` (optional): Minimum contour area in pixels to be considered actual motion. Default is `500`.

### Example

```bash
python tracker.py --input sample.mp4 --log motion_events.txt --output-vid processed_sample.mp4 --min-area 800
```

## Local Testing

A `generate_test_video.py` script is included if you want to quickly verify the tracker. It generates a 5-second test video (`test_video.mp4`) with a moving object.

1. Generate the video:
   ```bash
   python generate_test_video.py
   ```
2. Run the tracker on the generated video:
   ```bash
   python tracker.py --input test_video.mp4 --output-vid processed_video.mp4 --log motion_events.txt
   ```
"# cv_project_motion-tracking" 
