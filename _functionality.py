import cv2
import os
import threading
from PIL import Image
from PIL import ImageTk
import tkinter as tk
import tkinter.ttk as ttk
import datetime
import time
import sys
from imageai.Detection import VideoObjectDetection
import tensorflow as tf
from keras import backend as K
import winsound

class functionality():
    def buttonsWhenCamOn(self, camnum, camname):
        # Menu for functions that are possible only when user is connected to camera
        rely = 0.05 + (camnum * 0.07) - 0.07
        self.lbl1 = tk.Label(text=camname, bg = "#9EF79F")
        self.lbl1.place(relx=0.01, rely=rely, relwidth=0.10, relheight=0.05)
        self.btn2 = ttk.Button(text="Disconnect", command=self.videoCaptureStop)
        self.btn2.place(relx=0.12, rely=rely, relwidth=0.10, relheight=0.05)
        self.btn3 = ttk.Button(text="Watch Camera", command=self.watchCameraStart)
        self.btn3.place(relx=0.23, rely=rely, relwidth=0.10, relheight=0.05)
        self.btn4 = ttk.Button(text="AI Start", command=self.AIStart)
        self.btn4.place(relx=0.34, rely=rely, relwidth=0.10, relheight=0.05)

    def videoCaptureStart(self, camnum, camname, camera, execution_path, video_detector, graph, ai_minimum_percentage, bgcolor, soundfile):
        # This function is called when user presses one of initial buttons to initiate video capture

        self.buttonsWhenCamOn(camnum, camname)

        global all_cams_videoCapture_allowed
        all_cams_videoCapture_allowed = True

        self.camnum = camnum
        self.camname = camname
        self.camera = camera

        # if a user typed in only numeric value in the camera address field, we assume that it is a locally connected camera
        if self.camera.isdigit():
            self.camera = int(self.camera) # removing quotation marks from the string
            self.backend = cv2.CAP_DSHOW  # cv2.CAP_DSHOW - backend, adding it to local cam lets working AI and watching camera at the same time without getting errors
        else:
            self.backend = cv2.CAP_FFMPEG # CAP_FFMPEG

        # stream for VIDEO WATCHING
        self.cam = cv2.VideoCapture(self.camera, self.backend)
        if self.cam is None or not self.cam.isOpened():
            print(str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + ' - WARNING: unable to open video source for video watching: ' + self.camera + " | Camera: " + self.camname)

        # stream for AI
        if isinstance(self.camera, int): # If we use a locally connected camera, then the stream for AI and for video watching is the same
            self.AIcam = self.cam
        else:  # If it's not a locally connected camera, then we create a separate stream for AI to avoid crash which is likely if they share the same stream
            self.AIcam = cv2.VideoCapture(self.camera)
            if self.AIcam is None or not self.AIcam.isOpened():
                print(str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) +' - WARNING: unable to open video source for AI: ' + self.camera + " | Camera: " + self.camname)

        self.frame = None
        self.thread = None
        self.stopEvent = None
        self.panel = None

        self.execution_path = execution_path
        self.video_detector = video_detector
        self.graph = graph
        self.ai_minimum_percentage = ai_minimum_percentage
        self.bgcolor = bgcolor
        self.soundfile = soundfile

        # start a thread that constantly pools the video sensor for the most recently read frame
        self.stopEvent = threading.Event()
        self.thread = threading.Thread(target=self.videoCaptureMain, args=())
        self.thread.start()

    def videoCaptureMain(self):
        # A video capture starting point

        print(str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + " - Video Capture Start | Camera: " + self.camname + " | Ident: " + str(threading.get_ident()) + " | Thread: " + threading.currentThread().getName())
        try:
            # keep looping over frames until we are instructed to stop
            while not self.stopEvent.is_set():
                #print("Loop works" + str(datetime.datetime.now()))
                # grab the frame from the video stream
                ret, self.frame = self.cam.read()

                # OpenCV represents images in BGR order; however PIL
                # represents images in RGB order, so we need to swap
                # the channels, then convert to PIL and ImageTk format
                try:
                    image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                    image = Image.fromarray(image)
                    image = ImageTk.PhotoImage(image)

                #----- if error happens during the getting frames from camera -----#
                except:
                    # Placing a label with error message over btn1
                    self.lbl1.destroy() # Deletes existing lbl1
                    rely = 0.05 + (self.camnum * 0.07) - 0.07
                    self.lbl1 = tk.Label(text="Conn. Error!", bg="red")
                    self.lbl1.place(relx=0.01, rely=rely, relwidth=0.10, relheight=0.05)

                    # Destroying all existing buttons and labels except btn2
                    self.btn3.destroy()  # Destroys button: Watch Camera
                    if 'lbl3' in dir(self):
                        self.lbl3.destroy() # Destroys label: Watching
                    if 'btn4' in dir(self):
                        self.btn4.destroy()  # Destroys button: AI Start
                    if 'lbl4' in dir(self):
                        self.lbl4.destroy()  # Destroys label: AI is On

                    # Same actions as in videoCaptureStop function
                    if self.panel is None:
                        ()
                    else:
                        self.panel = None  # Sets a panel for video output as None
                        self.live.destroy()  # Closes camera window
                    self.stopEvent.set()

                    if self.camera == 0:
                        self.cam.release()
                        K.clear_session()
                    else:
                        cv2.destroyAllWindows()  # Closes all windows and de-allocates any associated memory usage
                        K.clear_session()
                #----- The end of 'if error happens during the getting frames from camera' -----#

                # If the panel is None
                if self.panel is None:
                    ()
                # Otherwise, simply update the panel
                else:
                    try:
                        self.panel.configure(image=image)
                        self.panel.image = image
                    except RuntimeError as e:
                        self.panel = None
                    except:
                        print ("Couldn't update the panel")

                # If, for some reason, video captures are globally not allowed,
                # all currently performing video captures for all cameras stop
                if all_cams_videoCapture_allowed == True:
                    ()
                else:
                    self.videoCaptureStop()

        except RuntimeError as e:
            print("[INFO] caught a RuntimeError")

    def videoCaptureStop(self):
        # This function stops a video capture from a currently connected camera

        print(str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + " - Video Capture Stop | Camera: " + self.camname + " | Ident: " + str(threading.get_ident()) + " | Thread: " + threading.currentThread().getName())
        if self.panel is None:
            ()
        else:
            self.panel = None # Sets a panel for video output as None
            self.live.destroy() # Closes camera window

        self.lbl1.destroy() # Destroys label that covers Video Capture Start button (button becomes available)
        self.btn2.destroy() # Destroys button: Video Capture Stop
        if 'btn3' in dir(self):
            self.btn3.destroy() #Destroys button: Watch Camera
        if 'lbl3' in dir(self):
            self.lbl3.destroy() # Destroys label: Watching
        if 'btn4' in dir(self):
            self.btn4.destroy()  # Destroys button: AI Start
        if 'lbl4' in dir(self):
            self.lbl4.destroy() # Destroys label: AI is On
        if 'canvas_ldf' in dir(self):
            self.canvas_ldf.destroy()   # Deletes the canvas with the last detected frame
        if 'label_ldi' in dir(self):
            self.label_ldi.destroy()    # Deletes the label with the last detection info

        self.stopEvent.set()

        if self.camera == 0:
            self.cam.release()  # Closes capturing device (only if we use our PC's camera), this also stops AI
            K.clear_session()   # Clearing Keras Session - helps to avoid error when AI is launched second time after stop
                                # (valueerror: tensor tensor() is not an element of this graph)
                                # It's called always when turning off camera in case if AI stopped spontaneously
        else:
            cv2.destroyAllWindows() # Closes all windows and de-allocates any associated memory usage
            K.clear_session()

    def videoCaptureStopAll(self):
        # A function that stops video capture for all cameras

        print(str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + " - Video Capture Stop for All Cameras Initiated | Ident: " + str(threading.get_ident()) + " | Thread: " + threading.currentThread().getName())

        # Setting a global variable NOT allowing to perform video capture for all cameras
        global all_cams_videoCapture_allowed
        all_cams_videoCapture_allowed = False

    def AIStart(self):
        # This function is called when user initiates an object recognition from connected camera

        # Deleting AI Start button and putting a label on its place
        self.btn4.destroy()
        rely = 0.05 + (self.camnum * 0.07) - 0.07
        self.lbl4 = tk.Label(text="AI is Starting", bg = "#ffff4d")
        self.lbl4.place(relx=0.34, rely=rely, relwidth=0.10, relheight=0.05)

        # Variable with the Last Detection Info to put on a label at the place of the AI start button (yet no info about detections at this point)
        self.lbl4ldi = "\n No detections yet"

        '''#If we use our PC's camera, then the stream for AI and for video watching is the same
        if self.camera == 0:
            self.AIcam = self.cam
        #If it's not our PC's camera, then we create a separate stream for AI to avoid crash which is likely if they share the same stream
        else:
            self.AIcam = cv2.VideoCapture(self.camera)'''

        self.color_index = {'bus': 'red', 'handbag': 'steelblue', 'giraffe': 'orange', 'spoon': 'gray', 'cup': 'yellow',
                       'chair': 'green', 'elephant': 'pink', 'truck': 'indigo', 'motorcycle': 'azure',
                       'refrigerator': 'gold',
                       'keyboard': 'violet', 'cow': 'magenta', 'mouse': 'crimson', 'sports ball': 'raspberry',
                       'horse': 'maroon', 'cat': 'orchid', 'boat': 'slateblue', 'hot dog': 'navy', 'apple': 'cobalt',
                       'parking meter': 'aliceblue', 'sandwich': 'skyblue', 'skis': 'deepskyblue',
                       'microwave': 'peacock',
                       'knife': 'cadetblue', 'baseball bat': 'cyan', 'oven': 'lightcyan', 'carrot': 'coldgrey',
                       'scissors': 'seagreen', 'sheep': 'deepgreen', 'toothbrush': 'cobaltgreen',
                       'fire hydrant': 'limegreen',
                       'remote': 'forestgreen', 'bicycle': 'olivedrab', 'toilet': 'ivory', 'tv': 'khaki',
                       'skateboard': 'palegoldenrod', 'train': 'cornsilk', 'zebra': 'wheat', 'tie': 'burlywood',
                       'orange': 'melon', 'bird': 'bisque', 'dining table': 'chocolate', 'hair drier': 'sandybrown',
                       'cell phone': 'sienna', 'sink': 'coral', 'bench': 'salmon', 'bottle': 'brown', 'car': 'silver',
                       'bowl': 'maroon', 'tennis racket': 'palevilotered', 'airplane': 'lavenderblush',
                       'pizza': 'hotpink',
                       'umbrella': 'deeppink', 'bear': 'plum', 'fork': 'purple', 'laptop': 'indigo',
                       'vase': 'mediumpurple',
                       'baseball glove': 'slateblue', 'traffic light': 'mediumblue', 'bed': 'navy',
                       'broccoli': 'royalblue',
                       'backpack': 'slategray', 'snowboard': 'skyblue', 'kite': 'cadetblue', 'teddy bear': 'peacock',
                       'clock': 'lightcyan', 'wine glass': 'teal', 'frisbee': 'aquamarine', 'donut': 'mincream',
                       'suitcase': 'seagreen', 'dog': 'springgreen', 'banana': 'emeraldgreen', 'person': 'honeydew',
                       'surfboard': 'palegreen', 'cake': 'sapgreen', 'book': 'lawngreen', 'potted plant': 'greenyellow',
                       'toaster': 'ivory', 'stop sign': 'beige', 'couch': 'khaki'}

        self.AIthread = threading.Thread(target=self.AIMain, name="AIThread", args=()) #args=(video_detector,)
        self.AIthread.start()

    def AIMain(self):
        # Object recognition starting point

        with self.graph.as_default():
            print(str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + " - AI is about to start | Camera: " + self.camname + " | Ident/Graph : " + str(threading.get_ident()) + str(tf.get_default_graph()))
            self.video_detector.detectObjectsFromVideo(camera_input=self.AIcam,
                                              output_file_path=os.path.join(self.execution_path, "video_frame_analysis"),
                                              frames_per_second=3, per_frame_function=self.forFrame,
                                              minimum_percentage_probability=int(self.ai_minimum_percentage), return_detected_frame=True, thread_safe=False) #thread_safe=False

    def forFrame(self, frame_number, output_array, output_count, returned_frame):

        this_colors = []
        labels = []
        sizes = []

        counter = 0

        for eachItem in output_count:
            counter += 1
            labels.append(eachItem + " = " + str(output_count[eachItem]))
            sizes.append(output_count[eachItem])
            this_colors.append(self.color_index[eachItem])

        # If there is no command for camera to stop capturing and there are no objects detected
        if not self.stopEvent.is_set() and not labels:
            # AI works
            # print("AI works. Camera" + str(self.camnum) + " " + str(time.time()) + str(tf.get_default_graph()))

            self.lbl4.destroy()  # Deleting the previous label at the place of the AI Start button
            rely = 0.05 + (self.camnum * 0.07) - 0.07
            self.lbl4 = tk.Label(text="Last Scan: " + format(datetime.datetime.now().strftime("%H:%M:%S")) + self.lbl4ldi, bg="#9EF79F")
            self.lbl4.place(relx=0.34, rely=rely, relwidth=0.10, relheight=0.05)

        # If there is a command for camera to stop capturing, we release AIcam to stop object detection
        elif self.stopEvent.is_set():
            print(str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + " - AI Stop because Camera" + str(self.camnum) + " capture stopped | Camera: " + self.camname + " | Graph : " + str(tf.get_default_graph()))
            self.AIcam.release() # Necessary, otherwise the loop in ImageAI will continue working

        # If the program finds an object...
        else:
            print(output_count)
            print(time.time())

            returned_frame = cv2.cvtColor(returned_frame, cv2.COLOR_BGR2RGB)

            directory = self.execution_path + "\\frames\\" + str(datetime.datetime.now().strftime("%Y-%m-%d")) + "\\camera" + str(self.camnum)
            if not os.path.exists(directory):
                os.makedirs(directory) # Creates a directory for camera's frames
            cv2.imwrite(os.path.join(directory, "camera" + str(self.camnum) + "_" + str(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S(")) + str(frame_number) + ").png"), returned_frame)  # Saving the frame (original size)

            self.returned_frame_small = cv2.resize(returned_frame, (550, 412)) # Aspect ratio 1.333
            cv2.imwrite("frames/lastdetection.png", self.returned_frame_small)

            if 'canvas_ldf' in dir(self):
                self.canvas_ldf.destroy()  # Deletes the previous canvas with the last detected frame
            if 'label_ldi' in dir(self):
                self.label_ldi.destroy() # Deletes the label with the last detection info

            # Variable with Last Detection Info to put on a label at the place of the AI start button
            self.lbl4ldi = "\n Detect. (" + format(datetime.datetime.now().strftime("%H:%M:%S")) + ")"

            self.lbl4.destroy() # Deletes the previous label at the place of the AI Start button
            rely = 0.05 + (self.camnum * 0.07) - 0.07
            self.lbl4 = tk.Label(text="AI is On (" + format(datetime.datetime.now().strftime("%H:%M:%S")) + ")" + self.lbl4ldi,
                                 bg="#9EF79F") # New label at the place of the AI start button
            self.lbl4.place(relx=0.34, rely=rely, relwidth=0.10, relheight=0.05)

            self.show_last_detected_frame()
            self.label_ldi = tk.Label(text="Detection! " + str(self.camname) + ' ' +
                                        format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + ' ' +
                                        str(output_count), fg = "red")
            self.label_ldi.place(relx=0.45, rely=0.77, relwidth=0.50, relheight=0.05)

            threading.Thread(target=winsound.PlaySound("sounds/" + str(self.soundfile), winsound.SND_FILENAME), args=()).start()
            #winsound.PlaySound("sounds/" + str(self.soundfile), winsound.SND_FILENAME) # without new thread for sound


    def watchCameraStart(self):
        # This function is called when user initiates camera watching

        # Covering Watch Camera Start button
        rely = 0.05 + (self.camnum * 0.07) - 0.07
        self.lbl3 = tk.Label(text="Watching", bg = "#9EF79F")
        self.lbl3.place(relx=0.23, rely=rely, relwidth=0.10, relheight=0.05)

        print(str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + " - Open Camera | Camera: " + self.camname + " | Ident: " + str(threading.get_ident()) + " | Thread: " + threading.currentThread().getName())

        # Initializes the live window and image panel
        self.live = tk.Toplevel()
        self.live.resizable(width=False, height=False)
        self.live.title(str(self.camname) + " Live")
        self.live.config(bg=self.bgcolor)

        self.panel = tk.Label(self.live, bd=0, highlightthickness=0)
        self.panel.pack(side="top", padx=0, pady=0, expand="True")

        # Buttons at the bottom of the live window
        btnExit = ttk.Button(self.live, text="Exit Preview",
                             command=self.watchCameraStop)
        btnExit.pack(side="right", padx=1, pady=4, expand="False")
        btnSnapshots = ttk.Button(self.live, text="Snapshots Folder",
                             command=lambda: os.system("start frames\snapshots\ "))
        btnSnapshots.pack(side="right", padx=1, pady=4, expand="False")
        btn = ttk.Button(self.live, text="Take Snapshot",
                        command=self.takeSnapshot)
        btn.pack(side="right", padx=1, pady=4, expand="False")

        # set a callback to handle when the window is closed
        self.live.wm_protocol("WM_DELETE_WINDOW", self.watchCameraStop)

    def watchCameraStop(self):
        # A function that closes live window

        self.lbl3.destroy()  # Destroys label that covers Watch Camera Start button (button becomes available)

        print(str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + " - Close Camera | Camera: " + self.camname + " | Ident: " + str(threading.get_ident()) + " | Thread: " + threading.currentThread().getName())
        self.panel = None
        self.live.destroy()

    def takeSnapshot(self):
        # A function to save a current frame on the disk as a file

        directory = self.execution_path + "\\frames\\snapshots"
        if not os.path.exists(directory):
            os.makedirs(directory)
        # Grab the current timestamp and use it to construct the output path
        ts = datetime.datetime.now()
        filename = "{}.png".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))
        p = os.path.sep.join((directory, filename))

        # Save the file
        cv2.imwrite(p, self.frame.copy())
        print(str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + " - Saved {}".format(filename) + " | Camera: " + self.camname)

    def show_last_detected_frame(self):
        # A function to show a frame with the last detection on the main program's screen

        self.img = tk.PhotoImage(file="frames/lastdetection.png")

        self.canvas_ldf = tk.Canvas(bg=self.bgcolor, bd=0, highlightthickness=0)
        self.canvas_ldf.place(relx=0.45, rely=0.05, relwidth=0.50, relheight=0.67)
        self.canvas_ldf.bind("<Configure>", lambda event: self.resize(event))
        self.canvas_img = self.canvas_ldf.create_image(0, 0, anchor="nw", image=self.img)

    def resize(self, event):
        # A function that adjusts the last detected frame on the main screen to the main screen's size

        img = Image.open(r"frames/lastdetection.png").resize(
            (event.width, event.height), Image.ANTIALIAS
        )
        self.img = ImageTk.PhotoImage(img)
        self.canvas_ldf.itemconfig(self.canvas_img, image=self.img)

#/////////////////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////