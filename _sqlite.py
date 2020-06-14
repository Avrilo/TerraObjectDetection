import sqlite3
import tkinter as tk
import datetime
#import _functionality as _f

##########-----FIRST START-----###########

def firstStart():
    conn = sqlite3.connect('_data.db')  # ':memory:'
    c = conn.cursor()

    # Cameras table and initial entries
    c.execute("""CREATE TABLE IF NOT EXISTS cameras (
        id integer,
        name text,
        ipcam_streaming_url text)""")

    c.execute("""INSERT INTO cameras (id, name, ipcam_streaming_url) VALUES
       (1, 'My Camera', '0'),
       (2, '', ''),
       (3, '', ''),
       (4, '', ''),
       (5, '', ''),
       (6, '', ''),
       (7, '', ''),
       (8, '', '')
       """)

    # Visual table and its initial entries
    c.execute("""CREATE TABLE IF NOT EXISTS visual (
            id integer,
            name text,
            transparency text,
            bgcolor text,
            data1 text,
            data2 text,
            data3 text,
            data4 text,
            data5 text)""")

    c.execute("""INSERT INTO visual (id, name, transparency, bgcolor, data1, data2, data3, data4, data5) VALUES
           (1, 'dark_transparent', '0.90', '#3A3939', '', '', '', '', '')
           """)

    # Sound table and its initial entries
    c.execute("""CREATE TABLE IF NOT EXISTS sound (
                id integer,
                name text,
                soundfile text)""")

    c.execute("""INSERT INTO sound (id, name, soundfile) VALUES
               (1, 'clang', 'alarm.wav')
               """)

    # ai table and its initial entries
    c.execute("""CREATE TABLE IF NOT EXISTS ai (
            id integer,
            ai_model_type text,
            ai_model_file text,
            ai_detection_speed text,
            ai_minimum_percentage text)""")

    c.execute("""INSERT INTO ai (id, ai_model_type, ai_model_file, ai_detection_speed, ai_minimum_percentage) VALUES
           (1, 'setModelTypeAsYOLOv3', 'yolo.h5', 'fastest', '50')
           """)

    conn.commit()
    conn.close()

##########-----CAMERAS-----###########

def updateCameras(id, name, ipcam_streaming_url):

    conn = sqlite3.connect('_data.db')  # ':memory:'
    c = conn.cursor()

    c.execute("UPDATE cameras SET name = :name, ipcam_streaming_url = :ipcam_streaming_url WHERE id = :id",
              {'id': id, 'name': name, 'ipcam_streaming_url': ipcam_streaming_url})

    print(str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + " - Camera Updated | Id: " + id + " | Camera Name: " + name + " | Address: " + ipcam_streaming_url)
    #print(name)
    #print(ipcam_streaming_url)

    conn.commit()
    conn.close()

def getCameras():

    conn = sqlite3.connect('_data.db')
    c = conn.cursor()

    try:
        result = c.execute("""SELECT id, name, ipcam_streaming_url FROM cameras""")
                       #{'id': id})                      # WHERE id = :id
        getCameras.result = result
    except sqlite3.OperationalError:
        print("The table does not exist (getCameras)")
    except:
        print("Wasn't possible to do it (getCameras)")

    conn.commit()
    # conn.close() # There is no conn.close

##########-----VISUAL-----###########
def updateVisual(name):

    if name == "Standard Dark":
        name = "Standard Dark"
        transparency = "1"
        bgcolor = "#3A3939"
    elif name == "Standard Bright":
        name = "Standard Bright"
        transparency = "1"
        bgcolor = "#DBD8D8"
    elif name == "Dark Transparent":
        name = "Dark Transparent"
        transparency = "0.90"
        bgcolor = "#3A3939"
    elif name == "Navy Transparent":
        name = "Navy Transparent"
        transparency = "0.90"
        bgcolor = "#134269"
    else:
        print("updateVisual: Entered value does not exist.")

    conn = sqlite3.connect('_data.db')
    c = conn.cursor()
    c.execute("UPDATE visual SET name = :name, transparency = :transparency, bgcolor = :bgcolor WHERE id = 1",
              {'name': name, 'transparency': transparency, 'bgcolor': bgcolor})
    conn.commit()
    conn.close()

def getVisual():

    conn = sqlite3.connect('_data.db')
    c = conn.cursor()

    try:
        result = c.execute("""SELECT id, name, transparency, bgcolor, data1, data2, data3, data4, data5 FROM visual WHERE id = 1""")
        getVisual.result = result
    except sqlite3.OperationalError:
        print("The table does not exist (getVisual)")
    except:
        print("Wasn't possible to do it (getVisual)")

    conn.commit()
    #conn.close() # There is no conn.close

##########-----SOUND-----###########
def updateSound(name):
    conn = sqlite3.connect('_data.db')
    c = conn.cursor()
    c.execute("UPDATE sound SET name = :name, soundfile = :soundfile WHERE id = 1",
              {'name': name, 'soundfile': name + '.wav'})
    conn.commit()
    conn.close()

def getSound():

    conn = sqlite3.connect('_data.db')
    c = conn.cursor()

    try:
        result = c.execute("""SELECT id, name, soundfile FROM sound WHERE id = 1""")
        getSound.result = result
    except sqlite3.OperationalError:
        print("The table does not exist (getSound)")
    except:
        print("Wasn't possible to do it (getSound)")

    conn.commit()
    #conn.close() # There is no conn.close

def connClose():
    conn = sqlite3.connect('_data.db')
    conn.close()
##########-----AI-----###########
def updateAI(ai_model, ai_detection_speed, ai_minimum_percentage):

    if ai_model == "TinyYOLOv3":
        ai_model_type = "setModelTypeAsTinyYOLOv3"
        ai_model_file = "yolo-tiny.h5"
    elif ai_model == "YOLOv3":
        ai_model_type = "setModelTypeAsYOLOv3"
        ai_model_file = "yolo.h5"
    elif ai_model == "RetinaNet":
        ai_model_type = "setModelTypeAsRetinaNet"
        ai_model_file = "resnet50_coco_best_v2.0.1.h5"

    conn = sqlite3.connect('_data.db')
    c = conn.cursor()
    c.execute("UPDATE ai SET ai_model_type = :ai_model_type, ai_model_file = :ai_model_file, ai_detection_speed = :ai_detection_speed, ai_minimum_percentage = :ai_minimum_percentage WHERE id = 1",
              {'ai_model_type': ai_model_type, 'ai_model_file': ai_model_file, 'ai_detection_speed': ai_detection_speed, 'ai_minimum_percentage': ai_minimum_percentage})
    conn.commit()
    conn.close()

def getAI():

    conn = sqlite3.connect('_data.db')
    c = conn.cursor()

    try:
        result = c.execute("""SELECT id, ai_model_type, ai_model_file, ai_detection_speed, ai_minimum_percentage FROM ai WHERE id = 1""")
        getAI.result = result
    except sqlite3.OperationalError:
        print("The table does not exist (getAI)")
    except:
        print("Wasn't possible to do it (getAI)")

    conn.commit()
    #conn.close() # There is no conn.close

#firstStart()
#updateCameras()
#getCameras()

#entryCameras()