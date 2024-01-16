import cv2
from PIL import Image, ImageTk


def apply_line_detection(self, frame):
    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply GaussianBlur to reduce noise and improve line detection
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Use Canny edge detector to find edges in the frame
    edges = cv2.Canny(blurred, 50, 150)

    # Use HoughLinesP to detect lines in the frame
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=50, minLineLength=100, maxLineGap=50)

    # Draw only 3 detected lines on the frame
    line_frame = frame.copy()
    for i, line in enumerate(lines):
        if i < 5:  # Draw only the first 3 lines
            x1, y1, x2, y2 = line[0]
            cv2.line(line_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

    # Merge the original frame with the line-drawn frame
    overlay_frame = cv2.addWeighted(frame, 0.8, line_frame, 1, 0)

    return overlay_frame


def start_video_stream_overlay(self):
    # open a video capture object (use 0 for the default camera)
    cap = cv2.VideoCapture("http://127.0.0.1:2345/video_feed")  # REPLACE WITH URL TO CAMERA

    while True:
        # read a frame from the video capture object
        ret, frame = cap.read()
        if ret:
            # apply line detection overlay
            # from the apply line detection function above
            overlay_frame = self.apply_line_detection(frame)

            # convert the frame from BGR to RGB
            rgb_frame = cv2.cvtColor(overlay_frame, cv2.COLOR_BGR2RGB)

            # resize the frame to fit the canvas
            rgb_frame = cv2.resize(rgb_frame, (300, 300))

            # convert the frame to a Photo-Image format
            image = Image.fromarray(rgb_frame)
            photo = ImageTk.PhotoImage(image=image)

            # update the overlay canvas with the new frame
            self.overlay_canvas.create_image(0, 0, anchor=tk.NW, image=photo)

        # sleep for a short duration to control the frame rate
        # otherwise it becomes wayyy too choppy for some reason
        self.root.update()
        self.root.after(10)

    # release the video capture object when the window is closed
    cap.release()
