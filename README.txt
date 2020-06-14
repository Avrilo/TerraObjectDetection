Terra Object Detection
v. 0.9.0 Beta

An application based on ImageAI library which can run object detection tasks from device cameras and IP cameras in real time.

- Detects and saves detections as separate images as well as immediately notifies user about detection
- Availability to choose detection speed and accuracy
- Up to 8 cameras can be saved and work simultaneously in the current version

Object Detection
An application uses YOLOv3 and TinyYOLOv3 models for object detection.

Requirements for Developers
Python 3.7.4
ImageAI 2.1.5 (pip3 install imageai --upgrade)
Tensorflow 1.11 (pip3 install tensorflow==1.11.0)
OpenCV 4.1.0.25 (pip3 install opencv-python)
Keras 2.2.4 (pip3 install keras)
yolo.h5 and yolo-tiny.h5 models

Installation

1. Install ImageAI 2.1.5 and all necessary dependencies
2. Locate the provided file __init__.py to venv\Lib\site-packages\imageai\Detection (change the existing file)

Run _appearance.py to launch the application.

License
This project is licensed under the MIT License.

Contacts
avrilo@tutanota.com
