import cv2
import numpy as np

def create_test_video(filename='test_video.mp4', frames=150, fps=30.0, width=640, height=480):
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(filename, fourcc, fps, (width, height))
    
    # Background color (gray)
    bg_color = (100, 100, 100)
    
    # Object properties
    radius = 30
    color = (0, 0, 255) # Red circle
    
    for i in range(frames):
        # Create a solid background
        frame = np.full((height, width, 3), bg_color, dtype=np.uint8)
        
        # Add a moving circle
        x = int(100 + i * 4)
        if x > width - radius:
            x = width - radius - (x - (width - radius))
        y = height // 2 + int(50 * np.sin(i * 0.15))
        
        cv2.circle(frame, (x, y), radius, color, -1)
        
        # Add slight random noise to be realistic
        noise = np.random.normal(0, 3, (height, width, 3)).astype(np.uint8)
        frame = cv2.add(frame, noise)
        
        out.write(frame)
        
    out.release()
    print(f"Test video '{filename}' generated successfully.")

if __name__ == '__main__':
    create_test_video()
