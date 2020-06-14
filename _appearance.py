print ("Starting... Please wait.")
import tkinter as tk
import tkinter.ttk as ttk
import _functionality as _f
import _sqlite
from PIL import Image, ImageTk
import datetime
import time
import cv2
import threading
import tensorflow as tf
#from imageai.Detection import VideoObjectDetection
import os
import winsound
import sys

class appearance():
    def load_model(self):

        from imageai.Detection import VideoObjectDetection

        # Program starts from model loading for image recognition. Object detection from all cameras use a model loaded here.
        #print("Model loading is about to start. Please wait...")
        #print(tf.__version__)

        try:
            self.label_loading = tk.Label(self.frame, text="Loading...", bg=self.bgcolor, fg="#9EF79F")
            self.label_loading.config(font=("Courier", 16))
            self.label_loading.place(relx=0.0, rely=0.0, relwidth=1, relheight=1)
        except:
            ()

        # AI MODEL LOADING
        # Getting AI information from DB
        _sqlite.getAI()
        for row in _sqlite.getAI.result:
            self.ai_model_type = row[1]
            self.ai_model_file = row[2]
            self.ai_detection_speed = row[3]
            self.ai_minimum_percentage = row[4]
        #print("Model type: " + self.ai_model_type + " File: " + self.ai_model_file + " Speed: " + self.ai_detection_speed + " Percentage: " + self.ai_minimum_percentage)

        self.execution_path = os.getcwd()
        self.video_detector = VideoObjectDetection()

        if self.ai_model_type == "setModelTypeAsTinyYOLOv3":
            self.video_detector.setModelTypeAsTinyYOLOv3()
        elif self.ai_model_type == "setModelTypeAsYOLOv3":
            self.video_detector.setModelTypeAsYOLOv3()
        elif self.ai_model_type == "setModelTypeAsRetinaNet":
            self.video_detector.setModelTypeAsRetinaNet()
        self.video_detector.setModelPath(os.path.join(self.execution_path, self.ai_model_file))
        self.video_detector.loadModel(detection_speed=self.ai_detection_speed)

        # Tensorflow graph used for loading a model should be the same as we use for object detection in AIMain function.
        global graph
        graph = tf.get_default_graph()

        if 'label_loading' in dir(self):
            self.label_loading.destroy()

    def program_start(self):

        # Getting VISUAL information from DB
        _sqlite.getVisual()
        for row in _sqlite.getVisual.result:
            self.schemename = row[1]
            self.transparency = row[2]
            self.bgcolor = row[3]

        # Root window
        self.root = tk.Tk()
        self.root.attributes('-alpha', self.transparency)
        self.root.iconbitmap(default='icon.ico')
        self.root.title('Terra Object Detection')

        # container with its initial values
        HEIGHT = 620
        WIDTH = 1100
        self.canvas = tk.Canvas(self.root, height=HEIGHT, width=WIDTH, bg="blue")  # real canvas for use
        self.canvas.pack()

        # menu on a top
        self.menubar()

        # main program's screen
        self.main_screen(program_just_started=True)

    #MENUBAR#
    def menubar(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        settingsMenu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settingsMenu)
        settingsMenu.add_command(label="Visual Settings", command=self.visual_settings)
        settingsMenu.add_command(label="Cameras Settings", command=self.cameras_settings)
        settingsMenu.add_command(label="Sound Settings", command=self.sound_settings)
        settingsMenu.add_command(label="Artificial Intelligence Settings", command=self.ai_settings)

        programMenu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Program", menu=programMenu)
        programMenu.add_command(label="Disconnect All Cameras/Refresh Screen", command=lambda: [_f.functionality().videoCaptureStopAll(), self.main_screen(program_just_started=False)])
        programMenu.add_command(label="About Program", command=self.about)
        programMenu.add_command(label="Exit", command=self.program_exit)

    #MAIN SCREEN#
    def main_screen(self, program_just_started):

        # Getting SOUND information from DB
        _sqlite.getSound()
        for row in _sqlite.getSound.result:
            self.soundname = row[1]
            self.soundfile = row[2]
        #print("Sound: " + self.soundname + " Title: " + self.soundfile)

        if 'frame' in dir(self):
            self.frame.destroy()    # destroying frame if it existed before (in case if main_screen
                                    # is not launching the first time but is being refreshed). Necessary in order to
                                    # 'forget' all old buttons and other widgets that are placed within that frame


        # Frame for all widgets on a main screen
        self.frame = tk.Frame(self.root, bg=self.bgcolor)
        self.frame.place(relx=0.00, rely=0.00, relwidth=1, relheight=1)

        if program_just_started == True:
            # Calling a function to load an AI model
            self.thread = threading.Thread(target=self.load_model, args=())
            self.thread.start()
        else:
            ()

        # Calling function to get a cameras list from DB
        _sqlite.getCameras()

        # Creating buttons for each camera
        for row in _sqlite.getCameras.result:

            # Creating necessary variables for each database output
            globals()["id" + str(row[0])] = row[0]
            globals()["name" + str(row[0])] = row[1]
            globals()["ipcam_streaming_url" + str(row[0])] = row[2]

        _sqlite.connClose()

        # Initial buttons - pressing an initial button initiates a video capture from camera
        # Every initial button has an id (camnum) which is passed to buttonsWhenCameraOn function for the purpose
        # to create additional buttons next to initial ones for enabling functionality to each camera (location of later generated
        # buttons depends on which initial button was pressed - id1, id2, id3...)

        ttk.Style().map("C.TButton", background=[('pressed', 'yellow')], foreground=[('pressed', 'black')])

        if 'id1' in globals():
            if name1 != "" and ipcam_streaming_url1 != "":
                button1 = ttk.Button(self.frame, text=name1, style="C.TButton", command=lambda: _f.functionality().videoCaptureStart(id1, name1, ipcam_streaming_url1, self.execution_path, self.video_detector, graph, self.ai_minimum_percentage, self.bgcolor, self.soundfile)) #command=_f.functionality().videoCaptureStart
                button1.place(relx=0.01, rely=0.05, relwidth=0.10, relheight=0.05)
        if 'id2' in globals():
            if name2 != "" and ipcam_streaming_url2 != "":
                button2 = ttk.Button(self.frame, text=name2, style="C.TButton", command=lambda: _f.functionality().videoCaptureStart(id2, name2, ipcam_streaming_url2, self.execution_path, self.video_detector, graph, self.ai_minimum_percentage, self.bgcolor, self.soundfile))
                button2.place(relx=0.01, rely=0.12, relwidth=0.10, relheight=0.05)
        if 'id3' in globals():
            if name3 != "" and ipcam_streaming_url3 != "":
                button3 = ttk.Button(self.frame, text=name3, style="C.TButton", command=lambda: _f.functionality().videoCaptureStart(id3, name3, ipcam_streaming_url3, self.execution_path, self.video_detector, graph, self.ai_minimum_percentage, self.bgcolor, self.soundfile))
                button3.place(relx=0.01, rely=0.19, relwidth=0.10, relheight=0.05)
        if 'id4' in globals():
            if name4 != "" and ipcam_streaming_url4 != "":
                button4 = ttk.Button(self.frame, text=name4, style="C.TButton", command=lambda: _f.functionality().videoCaptureStart(id4, name4, ipcam_streaming_url4, self.execution_path, self.video_detector, graph, self.ai_minimum_percentage, self.bgcolor, self.soundfile))
                button4.place(relx=0.01, rely=0.26, relwidth=0.10, relheight=0.05)
        if 'id5' in globals():
            if name5 != "" and ipcam_streaming_url5 != "":
                button5 = ttk.Button(self.frame, text=name5, style="C.TButton", command=lambda: _f.functionality().videoCaptureStart(id5, name5, ipcam_streaming_url5, self.execution_path, self.video_detector, graph, self.ai_minimum_percentage, self.bgcolor, self.soundfile))
                button5.place(relx=0.01, rely=0.33, relwidth=0.10, relheight=0.05)
        if 'id6' in globals():
            if name6 != "" and ipcam_streaming_url6 != "":
                button6 = ttk.Button(self.frame, text=name6, style="C.TButton", command=lambda: _f.functionality().videoCaptureStart(id6, name6, ipcam_streaming_url6, self.execution_path, self.video_detector, graph, self.ai_minimum_percentage, self.bgcolor, self.soundfile))
                button6.place(relx=0.01, rely=0.40, relwidth=0.10, relheight=0.05)
        if 'id7' in globals():
            if name7 != "" and ipcam_streaming_url7 != "":
                button7 = ttk.Button(self.frame, text=name7, style="C.TButton", command=lambda: _f.functionality().videoCaptureStart(id7, name7, ipcam_streaming_url7, self.execution_path, self.video_detector, graph, self.ai_minimum_percentage, self.bgcolor, self.soundfile))
                button7.place(relx=0.01, rely=0.47, relwidth=0.10, relheight=0.05)
        if 'id8' in globals():
            if name8 != "" and ipcam_streaming_url8 != "":
                button8 = ttk.Button(self.frame, text=name8, style="C.TButton", command=lambda: _f.functionality().videoCaptureStart(id8, name8, ipcam_streaming_url8, self.execution_path, self.video_detector, graph, self.ai_minimum_percentage, self.bgcolor, self.soundfile))
                button8.place(relx=0.01, rely=0.54, relwidth=0.10, relheight=0.05)

        button_openFolder = ttk.Button(self.frame, text="Open Detections Folder", command=lambda: os.system("start frames\ "))
        button_openFolder.place(relx=0.45, rely=0.87, relwidth=0.50, relheight=0.05)

        # set a callback to handle when the main window is closed; trying to close all working cameras if user initiates program closure (DOESN'T WORK YET)
        self.root.wm_protocol("WM_DELETE_WINDOW", self.program_exit)

        # runs application
        self.root.mainloop()

    def visual_settings(self):
        visual_window = tk.Toplevel()
        visual_window.geometry('260x180+180+80')
        visual_window.attributes('-alpha', self.transparency)
        visual_window.resizable(width=False, height=False)
        visual_window.title('Visual Settings')
        canvas = tk.Canvas(visual_window, height=180, width=260)
        canvas.pack()
        frame = tk.Frame(visual_window, bg=self.bgcolor)
        frame.place(relx=0.00, rely=0.00, relwidth=1, relheight=1)

        label1 = tk.Label(frame, text="Current scheme: " + self.schemename, anchor='center')
        label1.place(relx=0.01, rely=0.05, relwidth=0.98, relheight=0.14)
        label2 = tk.Label(frame, text="Choose scheme:", anchor='w')
        label2.place(relx=0.01, rely=0.24, relwidth=0.48, relheight=0.14)

        Entry1List = [self.schemename, "Standard Dark", "Standard Bright", "Dark Transparent", "Navy Transparent"]
        entry1 = tk.StringVar(frame)
        entry1.set(Entry1List[0])
        opt = ttk.OptionMenu(frame, entry1, *Entry1List)
        opt.place(relx=0.51, rely=0.24, relwidth=0.48, relheight=0.14)

        button = ttk.Button(frame, text="Apply",
                       command=lambda: [_sqlite.updateVisual(entry1.get()),
                                        visual_window.destroy()])
        button.place(relx=0.51, rely=0.43, relwidth=0.48, relheight=0.14)

        label3 = tk.Label(frame, text="Important: you must restart the program \n for the visual changes to take effect.", anchor='center')
        label3.place(relx=0.01, rely=0.62, relwidth=0.98, relheight=0.30)


    def cameras_settings(self):
        cameras_window = tk.Toplevel()
        cameras_window.grab_set() #this forces all focus on the this top level window until it is closed
        cameras_window.geometry('650x400+180+80')
        cameras_window.attributes('-alpha', self.transparency)
        cameras_window.resizable(width=False, height=False)
        cameras_window.title('Cameras Settings')
        canvas = tk.Canvas(cameras_window, height=400, width=650)
        canvas.pack()
        frame = tk.Frame(cameras_window, bg=self.bgcolor)
        frame.place(relx=0.00, rely=0.00, relwidth=1, relheight=1)

        label1 = tk.Label(frame, text="Id")
        label1.place(relx=0.01, rely=0.05, relwidth=0.20, relheight=0.05)
        label2 = tk.Label(frame, text="Camera Name")
        label2.place(relx=0.01, rely=0.12, relwidth=0.20, relheight=0.05)
        label3 = tk.Label(frame, text="Camera address")
        label3.place(relx=0.01, rely=0.19, relwidth=0.20, relheight=0.05)

        # We allow to choose camera id from the list (range 1-8), not to type any number
        Entry1List = ["1", "1", "2", "3", "4", "5", "6", "7", "8"]
        entry1 = tk.StringVar(frame)
        entry1.set(Entry1List[0])
        opt = ttk.OptionMenu(frame, entry1, *Entry1List)
        opt.place(relx=0.22, rely=0.05, relwidth=0.20, relheight=0.05)
        entry2 = tk.Entry(frame)
        entry2.place(relx=0.22, rely=0.12, relwidth=0.20, relheight=0.05)
        entry3 = tk.Entry(frame)
        entry3.place(relx=0.22, rely=0.19, relwidth=0.20, relheight=0.05)

        # By pressing button, we are submitting entries to updateCameras, stopping all currently working cameras and refreshing the main_screen
        button = ttk.Button(frame, text="Submit",
                       command=lambda: [_sqlite.updateCameras(entry1.get(), entry2.get(), entry3.get()),
                                        cameras_window.destroy(), self.cameras_settings(), _f.functionality().videoCaptureStopAll(), self.main_screen(program_just_started=False)])
        button.place(relx=0.22, rely=0.26, relwidth=0.20, relheight=0.05)

        label4 = tk.Label(frame, text="Note: when you press 'Submit', all \n currently connected cameras disconnect.",
                          anchor='center')
        label4.place(relx=0.01, rely=0.33, relwidth=0.41, relheight=0.15)

        # Showing the actual information about cameras in the database to the user
        _sqlite.getCameras()

        label = tk.Label(frame, text="Cameras information (" + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + ")")
        label.place(relx=0.45, rely=0.05, relwidth=0.54, relheight=0.05)

        # Inserting cameras addresses to the list
        rely = 0.11
        for row in _sqlite.getCameras.result:
            id_label = tk.Label(frame, text=(row[0]))
            id_label.place(relx=0.45, rely=rely, relwidth=0.05, relheight=0.05)
            name_label = tk.Label(frame, text=(row[1]))
            name_label.place(relx=0.51, rely=rely, relwidth=0.20, relheight=0.05)
            ipcam_streaming_url_entry = tk.Entry(frame)
            ipcam_streaming_url_entry.configure(state='normal')
            ipcam_streaming_url_entry.insert(0, (row[2]))
            ipcam_streaming_url_entry.configure(state='readonly')
            ipcam_streaming_url_entry.place(relx=0.72, rely=rely, relwidth=0.27, relheight=0.05)
            rely += 0.06

        _sqlite.connClose()

    def sound_settings(self):
        sound_window = tk.Toplevel()
        sound_window.geometry('260x210+180+80')
        sound_window.attributes('-alpha', self.transparency)
        sound_window.resizable(width=False, height=False)
        sound_window.title('Sound Settings')
        canvas = tk.Canvas(sound_window, height=180, width=260)
        canvas.pack()
        frame = tk.Frame(sound_window, bg=self.bgcolor)
        frame.place(relx=0.00, rely=0.00, relwidth=1, relheight=1)

        label1 = tk.Label(frame, text="Current alarm sound: " + self.soundname, anchor='center')
        label1.place(relx=0.01, rely=0.04, relwidth=0.98, relheight=0.12)
        label2 = tk.Label(frame, text="Choose sound:", anchor='w')
        label2.place(relx=0.01, rely=0.20, relwidth=0.48, relheight=0.12)

        Entry1List = [self.soundname, "alarm", "clang", "crow", "glass", "harp_run", "meadow_lark", "trolley_bell"]
        entry1 = tk.StringVar(frame)
        entry1.set(Entry1List[0])
        opt = ttk.OptionMenu(frame, entry1, *Entry1List)
        opt.place(relx=0.51, rely=0.20, relwidth=0.48, relheight=0.12)

        button_listen = ttk.Button(frame, text="Play selected sound",
                                  command=lambda:play_sound(entry1.get()))
        button_listen.place(relx=0.51, rely=0.36, relwidth=0.48, relheight=0.12)

        button = ttk.Button(frame, text="Apply",
                           command=lambda: [_sqlite.updateSound(entry1.get()),
                                            sound_window.destroy(), _f.functionality().videoCaptureStopAll(), self.main_screen(program_just_started=False)])
        button.place(relx=0.51, rely=0.52, relwidth=0.48, relheight=0.12)

        label3 = tk.Label(frame,
                          text="Note: when you press 'Apply', all \n currently connected cameras disconnect.",
                          anchor='center')
        label3.place(relx=0.01, rely=0.68, relwidth=0.98, relheight=0.26)

        def play_sound(sound):
            winsound.PlaySound("sounds/" + sound + ".wav", winsound.SND_FILENAME)

    def ai_settings(self):
        ai_window = tk.Toplevel()
        ai_window.grab_set()  # this forces all focus on the this top level window until it is closed
        ai_window.geometry('500x400+180+80')
        ai_window.attributes('-alpha', self.transparency)
        ai_window.resizable(width=False, height=False)
        ai_window.title('Artificial Intelligence Settings')
        canvas = tk.Canvas(ai_window, height=400, width=500)
        canvas.pack()
        frame = tk.Frame(ai_window, bg=self.bgcolor)
        frame.place(relx=0.00, rely=0.00, relwidth=1, relheight=1)

        if self.ai_model_file == "yolo-tiny.h5":
            ai_model = "TinyYOLOv3"
        elif self.ai_model_file == "yolo.h5":
            ai_model = "YOLOv3"
        elif self.ai_model_file == "resnet50_coco_best_v2.0.1.h5":
            ai_model = "RetinaNet"

        label1 = tk.Label(frame, text="Current parameters: " + ai_model + "; " + self.ai_detection_speed + "; " + self.ai_minimum_percentage + ".", anchor='center')
        label1.place(relx=0.01, rely=0.05, relwidth=0.98, relheight=0.05)
        label2 = tk.Label(frame, text="AI Model")
        label2.place(relx=0.01, rely=0.12, relwidth=0.48, relheight=0.05)
        label3 = tk.Label(frame, text="Detection Speed")
        label3.place(relx=0.01, rely=0.19, relwidth=0.48, relheight=0.05)
        label4 = tk.Label(frame, text="Minimum Percentage")
        label4.place(relx=0.01, rely=0.26, relwidth=0.48, relheight=0.05)

        # We allow to choose ai model from the list
        Entry1List = [ai_model, "TinyYOLOv3", "YOLOv3"] # "RetinaNet" - program supports it but is not included here (reasons: loads slowly, detects slowly, low detection confidence, does not work after disconnect)
        entry1 = tk.StringVar(frame)
        entry1.set(Entry1List[0])
        opt1 = ttk.OptionMenu(frame, entry1, *Entry1List)
        opt1.place(relx=0.51, rely=0.12, relwidth=0.48, relheight=0.05)

        Entry2List = [self.ai_detection_speed, "normal", "fast", "faster", "fastest", "flash"]
        entry2 = tk.StringVar(frame)
        entry2.set(Entry2List[0])
        opt2 = ttk.OptionMenu(frame, entry2, *Entry2List)
        opt2.place(relx=0.51, rely=0.19, relwidth=0.48, relheight=0.05)

        Entry3List = [self.ai_minimum_percentage, "20", "25", "30", "35", "40", "45", "50", "55", "60", "65", "70", "75", "80", "85", "90", "91", "92", "93", "94", "95", "96", "97", "98", "99"]
        entry3 = tk.StringVar(frame)
        entry3.set(Entry3List[0])
        opt3 = ttk.OptionMenu(frame, entry3, *Entry3List)
        opt3.place(relx=0.51, rely=0.26, relwidth=0.48, relheight=0.05)

        # By pressing button, we are submitting entries to updateAI and closing the ai_window
        button = ttk.Button(frame, text="Submit",
                            command=lambda: [_sqlite.updateAI(entry1.get(), entry2.get(), entry3.get()),
                                             ai_window.destroy()])
        button.place(relx=0.51, rely=0.33, relwidth=0.48, relheight=0.05)

        label5 = tk.Label(frame,
                          text="Important: you must restart the program \n for the changes to take effect.",
                          anchor='center')
        label5.place(relx=0.01, rely=0.40, relwidth=0.98, relheight=0.15)

        instructions_scrollbar = ttk.Scrollbar(frame)
        instructions_text = tk.Text(frame, height=4, width=50)
        instructions_scrollbar.place(relx=0.01, rely=0.57, relwidth=0.98, relheight=0.39)
        instructions_text.place(relx=0.01, rely=0.57, relwidth=0.98, relheight=0.39)
        instructions_scrollbar.config(command=instructions_text.yview)
        instructions_text.config(yscrollcommand=instructions_scrollbar.set, state=tk.NORMAL, font=("Courier", 10))
        quote = """    Approximate parameters for different types of devices
        
        1. Machines with advanced dedicated graphics
        (For the best performance)
        GeForce GTX 1050 and better
        AI Model: YOLOv3; 
        Detection Speed: normal; 
        Minimum Percentage: >90

        2. Machines with dedicated graphics
        (For Optimal performance)
        AI Model: YOLOv3 or TinyYOLOv3; 
        Detection Speed: faster; 
        Minimum Percentage: ~50
        
        3. Machines with integrated graphics
        (For increasing detection speed)
        Due to limited resources, only the low performance 
        mode may be available. 
        It is not recommended to connect more than 1 or 2 
        cameras simultaneously.
        AI Model: TinyYOLOv3; 
        Detection Speed: flash; 
        Minimum Percentage: ~20

        """
        instructions_text.insert(tk.END, quote)
        instructions_text.config(yscrollcommand=instructions_scrollbar.set, state=tk.DISABLED) # After entering text, making DISABLED

    def about(self):
        about_window = tk.Toplevel()
        about_window.geometry('500x300+180+80')
        about_window.attributes('-alpha', self.transparency)
        about_window.resizable(width=False, height=False)
        about_window.title('Terra Object Detection')
        canvas = tk.Canvas(about_window, height=120, width=240)
        canvas.pack()
        frame = tk.Frame(about_window, bg=self.bgcolor)
        frame.place(relx=0.00, rely=0.00, relwidth=1, relheight=1)
        self.label1= tk.Label(frame, text="Terra Object Detection \n v. 0.9.0 Beta \n avrilo@tutanota.com", anchor='center', bg=self.bgcolor, fg="#9EF79F")
        self.label1.config(font=("Courier", 12))
        self.label1.place(relx=0.25, rely=0.35, relwidth=0.5, relheight=0.3)
        #self.label2 = tk.Label(frame, text="avrilo@tutanota.com", anchor='n', bg=self.bgcolor, fg="red")
        #self.label2.config(font=("Courier", 10))
        #self.label2.place(relx=0.0, rely=0.5, relwidth=1, relheight=0.5)

    def program_exit(self):
        # self.root.destroy - destroys root but keeps cameras loops working, shouldn't be used
        sys.exit()

appearance().program_start()
