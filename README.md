# FaceMatch

Personal project to build an Ubuntu desktop application. Face Match parses through a folder of photos searching for one or more known faces. The application then returns a new desktop folder containing all the matches.

## Getting Started

These instructions will allow you to get a copy of the project running on your machine. I have also provided a simple test case to demonstrate how the application functions.

### Prerequisites

You need Python 3.6 or later to run this application. The module dependencies are listed below with links to their installation guides:

dlib - https://gist.github.com/ageitgey/629d75c1baac34dfa5ca2a1928a7aeaf
gi - https://pygobject.readthedocs.io/en/latest/getting_started.html#ubuntu-getting-started
numpy - https://numpy.org/install/
cv2 - https://pypi.org/project/opencv-python/
face_recognition - https://pypi.org/project/face-recognition/
os - https://pypi.org/project/os-sys/
shutil - https://pypi.org/project/pytest-shutil/

## Running the test case

Save face.py, famous_environmentalists and David Attenborough.jpg in a directory of your choice. Open Terminal and enter the directory containing face.py. Execute the following command:
```
python3 face.py
```
Now follow these steps:

1. Click on "Choose Folder" and select famous_environmentalists
2. In the "Name" tab, write "David"
3. Click on "Upload a photo" and select David Attenborough.jpg
4. Click on "Search for matches"

After the program runs, there will be a new folder on your Desktop containing only the photographs featuring David Attenborough.

## Running the application

Currently the application only parses folders containing only image files. With this limitation in mind, feel free to sort through your own photographs and try searching for yourself by taking a picture with the webcam.



