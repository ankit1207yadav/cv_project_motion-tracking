"""
Motion Tracking CLI Tool

This script performs motion tracking using Background Subtraction and Spatio-Temporal Analysis.
It processes a video frame by frame, isolating the foreground using a Gaussian Mixture Model (GMM).
Morphological operations refine the foreground mask to eliminate noise and group objects before
bounding boxes are drawn and motion events are logged.
"""

import cv2
import argparse
import sys
import math

def get_args():
    parser = argparse.ArgumentParser(description="CLI tool for motion tracking using Background Subtraction.")
    parser.add_argument("--input", required=True, help="Path to the input video file.")
    parser.add_argument("--output-vid", required=False, help="Path to save the processed video with bounding boxes.")
    parser.add_argument("--log", required=True, help="Path to save the output text file containing motion timestamps.")
    parser.add_argument("--min-area", type=int, default=500, help="Minimum contour area to be considered actual motion (to ignore small noise).")
    return parser.parse_args()

def main():
    args = get_args()
    
    # Initialize resource variables
    cap = None
    writer = None
    log_f = None
    
    try:
        # 1. Load the video file
        cap = cv2.VideoCapture(args.input)
        if not cap.isOpened():
            print(f"Error: Cannot open input video: {args.input}", file=sys.stderr)
            sys.exit(1)
            
        # Get video properties for calculations and writer
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps == 0 or math.isnan(fps):
            fps = 30.0  # Fallback FPS
            
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Initialize VideoWriter if output is requested
        if args.output_vid:
            # mp4v is a standard codec for mp4 containers
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(args.output_vid, fourcc, fps, (width, height))
            
        # Open the log file
        log_f = open(args.log, "w")
        log_f.write("Motion Detected Timestamps (seconds):\n")
        
        # 2. Initialize Gaussian Mixture Model (GMM) background subtractor
        # Mathematical/CV Purpose:
        # GMM models each background pixel as a mixture of K Gaussian distributions.
        # It updates the weights of these distributions based on the time each color stays in the scene.
        # Pixels that do not fit the background distributions are considered foreground (motion).
        # This approach effectively handles dynamic backgrounds (like swaying trees) and gradual lighting changes.
        bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=16, detectShadows=True)
        
        # Kernel for morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        
        frame_number = 0
        last_logged_sec = -1
        
        # 3. Process the video frame by frame
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            frame_number += 1
            
            # 4. Apply background subtractor to get foreground mask
            # Shadows are drawn in gray (value 127), true foreground in white (255)
            fg_mask = bg_subtractor.apply(frame)
            
            # Threshold to remove shadows, keeping only the raw foreground pixels
            _, fg_mask = cv2.threshold(fg_mask, 254, 255, cv2.THRESH_BINARY)
            
            # 5. Apply morphological operations
            # Mathematical/CV Purpose:
            # - Erosion: Replaces a pixel with the minimum value of its neighborhood (defined by the kernel).
            #   This strips away the boundaries of foreground objects, effectively eliminating small, isolated 
            #   noise points (e.g., sensor noise or tiny background movements) that shouldn't be tracked.
            mask_eroded = cv2.erode(fg_mask, kernel, iterations=1)
            
            # - Dilation: Replaces a pixel with the maximum value of its neighborhood.
            #   After erosion removes noise (and slightly shrinks our actual targets), dilation expands
            #   the remaining foreground objects. This fills in holes inside moving objects and joins 
            #   fragmented parts of a single object back together.
            mask_cleaned = cv2.dilate(mask_eroded, kernel, iterations=2)
            
            # 6. Find contours on the cleaned mask
            contours, _ = cv2.findContours(mask_cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            motion_in_frame = False
            
            for contour in contours:
                area = cv2.contourArea(contour)
                
                # 7. Check if contour area meets minimum threshold
                if area > args.min_area:
                    motion_in_frame = True
                    # Draw a green bounding box around the object (in BGR: 0, 255, 0)
                    x, y, w, h = cv2.boundingRect(contour)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # 8. Calculate timestamp and log appropriately
            if motion_in_frame:
                timestamp_sec = frame_number / fps
                current_sec_int = int(timestamp_sec)
                
                # Ensure we don't write duplicate timestamps for the same second
                if current_sec_int != last_logged_sec:
                    log_f.write(f"{timestamp_sec:.2f}\n")
                    last_logged_sec = current_sec_int
                    
            # 9. Write the drawn frames to a new video file
            if writer:
                writer.write(frame)
                
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)
        
    finally:
        # Ensure resources are properly released
        if cap is not None:
            cap.release()
        if writer is not None:
            writer.release()
        if log_f is not None:
            log_f.close()
            
if __name__ == "__main__":
    main()
