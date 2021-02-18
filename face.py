#!/usr/bin/env python

# Import modules
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio
import numpy as np
import cv2
import face_recognition
import os
from shutil import copy

# Initialising back-end variables
path_to_folder = ""
faces = []
faces_encodings = []

# Global functions

def picture_taker():
	"""Return face encoding from webcam image."""
	video = cv2.VideoCapture(0)
	font = cv2.FONT_HERSHEY_DUPLEX
	moreThanOne = False
	lessThanOne = False

	while True:
		check, frame = video.read()
		
		if moreThanOne:
			cv2.putText(frame, "More than 1 face detected. Try again.", (10, 475), font, 1.0, (255, 0, 0), 1)
		elif lessThanOne:
			cv2.putText(frame, "No face detected. Try again.", (10, 475), font, 1.0, (255, 0, 0), 1)
		else:
			cv2.putText(frame, "Press \'q\' to take a picture.", (10, 475), font, 1.0, (255, 0, 0), 1)
		
		cv2.imshow("Capturing", frame)
		cv2.setWindowProperty("Capturing", cv2.WND_PROP_FULLSCREEN, 1)
		
		if cv2.waitKey(1) & 0xFF == ord("q"):
			encodings = face_recognition.face_encodings(frame)
			if len(encodings) > 1:
				moreThanOne = True
			elif len(encodings) == 0:
				lessThanOne = True
			else:
				global faces_encodings
				faces_encodings.append(encodings)
				break

	video.release()
	cv2.destroyAllWindows()

def image_encoder(file_name):
	"""Return face encoding from uploaded image."""
	image = face_recognition.load_image_file(file_name)
	encodings = face_recognition.face_encodings(image)

	if len(encodings) == 1:
		global faces_encodings
		faces_encodings.append(encodings)
	else:
		return False

def search_for_matches(path_to_folder, faces, faces_encodings):
	"""Search for matches and copy matches to new folder."""
	# Create new folder
	if len(faces) == 1:
		new_folder_name = "Photos of " + faces[0]
	elif len(faces) == 2:
		new_folder_name = "Photos of " + faces[0] + " and " + faces[1]
	else:
		new_folder_name = "Photos of "
		for name in faces[:-2]:
			new_folder_name += name + ", "
		new_folder_name += faces[-2] + " and " + faces[-1]

	os.mkdir(os.path.expanduser(f"~/Desktop/{new_folder_name}"))

	# Search for matches
	tolerance = 0.51

	for photo in os.listdir(path_to_folder):

		matches = [False for x in faces]

		image = face_recognition.load_image_file(f"{path_to_folder}/{photo}")
		encoding = face_recognition.face_encodings(image)

		print ("processing " + photo)

		for i in range(len(faces)):
			results = face_recognition.compare_faces(encoding, faces_encodings[i][0], tolerance)

			if True in results:
				matches[i] = True

		if all(matches):
			print("match found")
			copy(f"{path_to_folder}/{photo}", os.path.expanduser(f"~/Desktop/{new_folder_name}"))

	print("all matches found")

# GUI

class MainWindow(Gtk.Window):
	
	"""Main window class."""

	def __init__(self):
		Gtk.Window.__init__(self, title = "Face Match")
		self.set_default_size(400, 500)

		# Scrolled window
		self.scroll = Gtk.ScrolledWindow()
		self.scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
		self.add(self.scroll)

		# Box
		self.vbox1 = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, spacing = 40)
		self.vbox1.set_border_width(40)
		self.scroll.add(self.vbox1)

		# Sections
		self.section1 = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, spacing = 20)
		self.section2 = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, spacing = 20)
		self.section3 = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, spacing = 40)
		self.vbox1.pack_start(self.section1, True, True, 0)
		self.vbox1.pack_start(self.section2, True, True, 0)
		self.vbox1.pack_start(self.section3, True, True, 0)

		# Label 1
		self.label1 = Gtk.Label("Which folder would you like to choose?")
		self.section1.pack_start(self.label1, True, True, 0)

		# Folder chooser
		self.folder_chooser = Gtk.Button("Choose folder")
		self.folder_chooser.connect("clicked", self.on_folder_chooser_clicked)
		self.section1.pack_start(self.folder_chooser, True, True, 0)

		# Label 2
		self.label2 = Gtk.Label("Whose face(s) would you like to search for?")
		self.section2.pack_start(self.label2, True, True, 0)

		# Initialise ListBox to upload faces
		self.list_box = Gtk.ListBox()
		self.list_box.set_selection_mode(Gtk.SelectionMode.NONE)
		self.section2.pack_start(self.list_box, True, True, 0)

		# Add row to ListBox
		self.list_box.insert(ListBoxRow(self.list_box), -1)

		# Button to add another face
		self.button = Gtk.Button("+ another face", relief = Gtk.ReliefStyle.NONE)
		self.button.connect("clicked", self.on_button_clicked)
		self.button.set_alignment(0, 0)
		self.section2.pack_start(self.button, True, True, 0)

		# Button to search for matches
		self.search_button = Gtk.Button("Search for matches")
		self.search_button.connect("clicked", self.on_search_button_clicked)
		self.section3.pack_start(self.search_button, True, True, 0)

	# Click Functions

	def on_folder_chooser_clicked(self, widget):
		"""Select folder to search through."""
		dialog = Gtk.FileChooserDialog("Select a folder", self, Gtk.FileChooserAction.SELECT_FOLDER, 
			("Cancel", Gtk.ResponseType.CANCEL,
				"OK", Gtk.ResponseType.OK))

		response = dialog.run()

		# Path to folder
		if response == Gtk.ResponseType.OK:
			global path_to_folder
			path_to_folder = dialog.get_filename()

		# Change button label to folder path
		widget.set_label(path_to_folder)

		dialog.destroy()

	def on_button_clicked(self, widget):
		"""Add another tab to upload another known face."""
		self.list_box.insert(ListBoxRow(self.list_box), -1)

	def on_search_button_clicked(self, widget):
		"""Call search_for_matches()."""
		global path_to_folder, faces, faces_encodings
		search_for_matches(path_to_folder, faces, faces_encodings)
		Gtk.main_quit()

class ListBoxRow(Gtk.ListBoxRow):

	"""ListBoxRow class."""

	def __init__(self, parent):
		Gtk.ListBoxRow.__init__(self)

		vbox2 = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, spacing = 10)
		vbox2.set_border_width(20)
		self.add(vbox2)

		# Box for name entry
		hbox1 = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL, spacing = 20)
		vbox2.pack_start(hbox1, True, True, 0)

		# Label 3
		label3 = Gtk.Label("Name:")
		label3.set_justify(Gtk.Justification.RIGHT)
		hbox1.pack_start(label3, True, True, 0)

		# Entry
		entry = Gtk.Entry()
		hbox1.pack_start(entry, True, True, 0)

		# Box for face upload Stack
		vbox3 = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, spacing = 10)
		vbox2.pack_start(vbox3, True, True, 0)

		# Stack
		stack = Gtk.Stack()
		stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
		stack.set_transition_duration(500)

		# Button to take a picture with webcam
		camera_button = Gtk.Button()
		camera_icon = Gio.ThemedIcon(name = "camera-photo-symbolic")
		camera_image = Gtk.Image.new_from_gicon(camera_icon, Gtk.IconSize.BUTTON)
		camera_button.add(camera_image)
		camera_button.connect("clicked", self.on_camera_button_clicked, entry)
		stack.add_titled(camera_button, "camera_button", "Take a picture")

		# Button to upload a photo
		photo_chooser = Gtk.Button()
		photo_icon = Gio.ThemedIcon(name = "insert-image-symbolic")
		photo_image = Gtk.Image.new_from_gicon(photo_icon, Gtk.IconSize.BUTTON)
		photo_chooser.add(photo_image)
		photo_chooser.connect("clicked", self.on_photo_chooser_clicked, entry)
		stack.add_titled(photo_chooser, "photo_chooser", "Upload a photo")

		# StackSwitcher
		stack_switcher = Gtk.StackSwitcher()
		stack_switcher.set_stack(stack)

		vbox3.pack_start(stack_switcher, True, True, 0)
		vbox3.pack_start(stack, True, True, 0)

		self.show_all()

	# Click Functions for ListBoxRow

	def on_camera_button_clicked(self, widget, entry):
		"""Call picture_taker() and store new face encoding."""
		picture_taker()
		global faces
		faces.append(entry.get_text())
		widget.set_label("Face uploaded")

	def on_photo_chooser_clicked(self, widget, entry):
		"""Select image to upload and store new face encoding."""
		dialog1 = Gtk.FileChooserDialog("Select a photo", None, Gtk.FileChooserAction.OPEN, 
			("Cancel", Gtk.ResponseType.CANCEL,
				"OK", Gtk.ResponseType.OK))

		response = dialog1.run()
		path_to_image = dialog1.get_filename()
		dialog1.destroy()

		# Attempt to create face encoding with uploaded image
		if image_encoder(path_to_image) == False:
			dialog2 = Gtk.MessageDialog(
				None,
				0,
				Gtk.MessageType.INFO,
				Gtk.ButtonsType.OK,
				"Problem loading image")
			dialog2.format_secondary_text(
				"No face detected or multiple faces detected.\nTry again.")
			dialog2.run()
			dialog2.destroy()
		else:
			global faces
			faces.append(entry.get_text())
			widget.set_label("Face uploaded")

if __name__ == "__main__":
	window = MainWindow()
	window.connect("delete-event", Gtk.main_quit)
	window.show_all()
	Gtk.main()




