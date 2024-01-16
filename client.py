import tkinter as tk
import numpy as np
import requests
import threading
from userlog import UserLog
import cv2
from PIL import Image, ImageTk

# read the username from the temporary file
with open("temp_username.txt", "r") as temp_file:
 username = temp_file.read().strip()

class RobotControlApp:
 def __init__(self, root):
     self.root = root
     self.root.geometry("600x600")
     self.root.title("Robot Control App")

     # create four quadrants
     self.quadrant1 = tk.Frame(root, bg="gray", width=300, height=300)
     self.quadrant1.grid(row=0, column=0, rowspan=2, columnspan=2)

     self.quadrant2 = tk.Frame(root, bg="lightgray", width=300, height=300)
     self.quadrant2.grid(row=0, column=2, rowspan=2, columnspan=2)

     self.quadrant3 = tk.Frame(root, bg="lightgray", width=300, height=300)
     self.quadrant3.grid(row=2, column=0, rowspan=2, columnspan=2)

     self.quadrant4 = tk.Frame(root, bg="gray", width=300, height=300)
     self.quadrant4.grid(row=2, column=2, rowspan=2, columnspan=2)

     # Create directional buttons, stop, and play buttons in quadrant 2 (top right)
     button_size = ("Helvetica", 12)

     self.forward_button = tk.Button(self.quadrant2, text="↑", command=lambda: self.send_command("forward"), font=button_size)
     self.forward_button.grid(row=0, column=1)

     self.left_button = tk.Button(self.quadrant2, text="←", command=lambda: self.send_command("left"), font=button_size)
     self.left_button.grid(row=1, column=0)

     self.right_button = tk.Button(self.quadrant2, text="→", command=lambda: self.send_command("right"), font=button_size)
     self.right_button.grid(row=1, column=2)

     self.backward_button = tk.Button(self.quadrant2, text="↓", command=lambda: self.send_command("backward"), font=button_size)
     self.backward_button.grid(row=2, column=1)

     self.stop_button = tk.Button(self.quadrant2, text="⛔", command=lambda: self.send_command("stop"), font=button_size, foreground='red')
     self.stop_button.grid(row=3, column=0, pady=10)

     self.play_button = tk.Button(self.quadrant2, text="▶", command=lambda: self.send_command("play"), font=button_size, foreground='green')
     self.play_button.grid(row=3, column=2, pady=10)

     # Bind WASD keys to directional commands
     root.bind("<w>", lambda event: self.send_command("forward"))
     root.bind("<a>", lambda event: self.send_command("left"))
     root.bind("<s>", lambda event: self.send_command("backward"))
     root.bind("<d>", lambda event: self.send_command("right"))
     root.bind("<q>", lambda event: self.send_command("stop"))


     # Initialize UserLog with the obtained username
     self.user_log = UserLog(root, username=username)

     # Create a label for displaying the video stream
     self.video_canvas = tk.Canvas(root, width=300, height=300, bg="gray")
     self.video_canvas.grid(row=0, column=0, rowspan=2, columnspan=2)

     # Start the video stream thread
     self.video_stream_thread = threading.Thread(target=self.start_video_stream)
     self.video_stream_thread.start()

     # Create a label for displaying the video stream with overlay
     self.overlay_canvas = tk.Canvas(root, width=300, height=300, bg="gray")
     self.overlay_canvas.grid(row=2, column=0, rowspan=2, columnspan=2)

     # Start the video stream thread with overlay
     self.video_overlay_thread = threading.Thread(target=self.start_video_stream_overlay)
     self.video_overlay_thread.start()

 def start_video_stream_overlay(self):
      # Open a video capture object (use 0 for the default camera)
      cap = cv2.VideoCapture("http://127.0.0.1:2345/video_feed")  # REPLACE WITH URL TO CAMERA

      while True:
          # Read a frame from the video capture object
          ret, frame = cap.read()
          if ret:
              # Apply line detection overlay
              overlay_frame = self.apply_line_detection(frame)

              # Convert the frame from BGR to RGB
              rgb_frame = cv2.cvtColor(overlay_frame, cv2.COLOR_BGR2RGB)

              # Resize the frame to fit the canvas
              rgb_frame = cv2.resize(rgb_frame, (300, 300))

              # Convert the frame to a PhotoImage format
              image = Image.fromarray(rgb_frame)
              photo = ImageTk.PhotoImage(image=image)

              # Update the overlay canvas with the new frame
              self.overlay_canvas.create_image(0, 0, anchor=tk.NW, image=photo)

          # Sleep for a short duration to control the frame rate
          self.root.update()
          self.root.after(10)

      # Release the video capture object when the window is closed
      cap.release()

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
 def start_video_stream(self):
     # Open a video capture object (use 0 for the default camera)
     cap = cv2.VideoCapture("http://127.0.0.1:2345/video_feed") #REPLACE WITH URL TO CAMERA

     while True:
         # Read a frame from the video capture object
         ret, frame = cap.read()
         if ret:
             # Convert the frame from BGR to RGB
             rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

             # Resize the frame to fit the canvas
             rgb_frame = cv2.resize(rgb_frame, (600, 400))

             # Convert the frame to a PhotoImage format
             image = Image.fromarray(rgb_frame)
             photo = ImageTk.PhotoImage(image=image)

             # Update the video canvas with the new frame
             self.video_canvas.create_image(0, 0, anchor=tk.NW, image=photo)

         # Sleep for a short duration to control the frame rate
         self.root.update()
         self.root.after(10)

     # Release the video capture object when the window is closed
     cap.release()

 def send_command(self, command):
     # Log user action before sending the command
     self.user_log.log_action(command)

     # Send the command to the robot
     threading.Thread(target=self.send_request, args=(command,)).start()

 def send_request(self, command):
     api_url = "http://localhost:4444/control"
     payload = {"command": command}

     try:
         response = requests.post(api_url, json=payload)
         if response.status_code == 200:
             print(f"Command '{command}' sent successfully.")
         else:
             print(f"Failed to send command '{command}'.")
     except requests.RequestException as e:
         print(f"Error sending command: {e}")

if __name__ == '__main__':
 root = tk.Tk()
 app = RobotControlApp(root)
 root.mainloop()
