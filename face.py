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
tolerance = 0.51
include_unknown = True
strict_search = True

# Global functions

def picture_taker():
	"""Attempt to create and store face encoding from webcam image."""
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
	"""Call create_new_folder() and pass result to search()."""
	new_folder_name = create_new_folder(path_to_folder)
	global tolerance
	search(path_to_folder, new_folder_name, tolerance, faces, faces_encodings)

def search(path_to_folder, new_folder_name, tolerance, faces, faces_encodings):
	"""Search for matches."""
	for fil in os.listdir(path_to_folder):
		# Call search() recursively on directories contained within chosen search folder
		if os.path.isdir(f"{path_to_folder}/{fil}"):
			search(f"{path_to_folder}/{fil}", new_folder_name, tolerance, faces, faces_encodings)
		else:
			# Allow non-image files to be passed over
			try:
				image = face_recognition.load_image_file(f"{path_to_folder}/{fil}")
				encoding = face_recognition.face_encodings(image)
				matches = [False for x in faces]

				print ("processing " + fil)

				for i in range(len(faces)):
					results = face_recognition.compare_faces(encoding, faces_encodings[i][0], tolerance)

					if True in results:
						matches[i] = True

				global include_unknown, strict_search
				# Apply settings
				if not include_unknown and sum(matches) == len(encoding):
					if strict_search and all(matches):
						copy(f"{path_to_folder}/{fil}", os.path.expanduser(f"~/Desktop/{new_folder_name}"))
					elif not strict_search and True in matches:
						copy(f"{path_to_folder}/{fil}", os.path.expanduser(f"~/Desktop/{new_folder_name}"))
				elif include_unknown:
					if strict_search and all(matches):
						copy(f"{path_to_folder}/{fil}", os.path.expanduser(f"~/Desktop/{new_folder_name}"))
					elif not strict_search and True in matches:
						copy(f"{path_to_folder}/{fil}", os.path.expanduser(f"~/Desktop/{new_folder_name}"))
			except:
				print("incompatible file found")

def create_new_folder(path_to_folder):
	"""Create new folder."""
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

	return new_folder_name

# GUI

class MainWindow(Gtk.Window):
	
	"""Main window class."""

	def __init__(self):
		Gtk.Window.__init__(self, title = "Face Match")
		self.set_default_size(400, 500)

		# Header bar
		header = Gtk.HeaderBar()
		header.set_show_close_button(True)
		header.props.title = "Face Match"
		self.set_titlebar(header)

		# Settings button
		settings_button = Gtk.Button()
		cog_icon = Gio.ThemedIcon(name = "emblem-system-symbolic")
		cog_image = Gtk.Image.new_from_gicon(cog_icon, Gtk.IconSize.BUTTON)
		settings_button.add(cog_image)
		settings_button.connect("clicked", self.on_settings_button_clicked)
		header.pack_end(settings_button)

		# Help button
		help_button = Gtk.Button()
		help_icon = Gio.ThemedIcon(name = "dialog-question-symbolic")
		help_image = Gtk.Image.new_from_gicon(help_icon, Gtk.IconSize.BUTTON)
		help_button.add(help_image)
		help_button.connect("clicked", self.on_help_button_clicked)
		header.pack_start(help_button)

		# Scrolled window
		scroll = Gtk.ScrolledWindow()
		scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
		self.add(scroll)

		# Box
		vbox1 = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, spacing = 40)
		vbox1.set_border_width(40)
		scroll.add(vbox1)

		# Sections
		section1 = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, spacing = 20)
		section2 = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, spacing = 20)
		section3 = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, spacing = 40)
		vbox1.pack_start(section1, True, True, 0)
		vbox1.pack_start(section2, True, True, 0)
		vbox1.pack_start(section3, True, True, 0)

		# Label 1
		label1 = Gtk.Label("Which folder would you like to choose?")
		section1.pack_start(label1, True, True, 0)

		# Folder chooser
		folder_chooser = Gtk.Button("Choose folder")
		folder_chooser.connect("clicked", self.on_folder_chooser_clicked)
		section1.pack_start(folder_chooser, True, True, 0)

		# Label 2
		label2 = Gtk.Label("Whose face(s) would you like to search for?")
		section2.pack_start(label2, True, True, 0)

		# Initialise ListBox to upload faces
		self.list_box = Gtk.ListBox()
		self.list_box.set_selection_mode(Gtk.SelectionMode.NONE)
		section2.pack_start(self.list_box, True, True, 0)

		# Add row to ListBox
		self.list_box.insert(ListBoxRow(self.list_box), -1)

		# Button to add another face
		button = Gtk.Button("+ another face", relief = Gtk.ReliefStyle.NONE)
		button.connect("clicked", self.on_button_clicked)
		button.set_alignment(0, 0)
		section2.pack_start(button, True, True, 0)

		# Button to search for matches
		search_button = Gtk.Button("Search for matches")
		search_button.connect("clicked", self.on_search_button_clicked)
		section3.pack_start(search_button, True, True, 0)

	# Click Functions

	def on_settings_button_clicked(self, widget):
		"""Open settings dialog"""
		dialog = Gtk.Dialog("Settings",
			self,
			Gtk.DialogFlags.MODAL,
			("Cancel", Gtk.ResponseType.CANCEL, "Apply", Gtk.ResponseType.APPLY))
		dialog.set_border_width(20)

		# Grid for settings options
		grid = Gtk.Grid(row_homogeneous = True, row_spacing = 20)
		grid.attach(Gtk.Label("Tolerance:"), 0, 0, 1, 1)
		grid.attach(Gtk.Label("Include unknown faces:"), 0, 1, 1, 1)
		grid.attach(Gtk.Label("Strict search:"), 0, 2, 1, 1)

		# Settings options
		tolerance_entry = Gtk.Entry()
		global tolerance
		tolerance_entry.set_text(str(tolerance))
		grid.attach(tolerance_entry, 1, 0, 1, 1)

		include_unknown_check = Gtk.CheckButton(active = True, halign = Gtk.Align(3))
		grid.attach(include_unknown_check, 1, 1, 1, 1)

		strict_search_check = Gtk.CheckButton(active = True, halign = Gtk.Align(3))
		grid.attach(strict_search_check, 1, 2, 1, 1)

		# Add grid to dialog
		area = dialog.get_content_area()
		area.add(grid)
		dialog.show_all()

		response = dialog.run()

		# Apply changes
		if response == Gtk.ResponseType.APPLY:
			global include_unknown, strict_search
			tolerance = float(tolerance_entry.get_text())
			include_unknown = include_unknown_check.get_active()
			strict_search = strict_search_check.get_active()

		dialog.destroy()

	def on_help_button_clicked(self, widget):
		"""Open help dialog"""
		help_text = "help text"
		dialog = Gtk.MessageDialog(
			self,
			0,
			Gtk.MessageType.INFO,
			Gtk.ButtonsType.OK,
			"Welcome to Face Match")
		dialog.format_secondary_text(help_text)
		dialog.run()
		dialog.destroy()

	def on_folder_chooser_clicked(self, widget):
		"""Select folder to search through."""
		dialog = Gtk.FileChooserDialog(
			"Select a folder",
			self,
			Gtk.FileChooserAction.SELECT_FOLDER, 
			("Cancel", Gtk.ResponseType.CANCEL, "OK", Gtk.ResponseType.OK))

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

	# File chooser

	def file_chooser(self):
		"""Select image to upload and store new face encoding."""
		dialog1 = Gtk.FileChooserDialog(
			"Select a photo",
			self,
			Gtk.FileChooserAction.OPEN, 
			("Cancel", Gtk.ResponseType.CANCEL, "OK", Gtk.ResponseType.OK))

		response = dialog1.run()
		path_to_image = dialog1.get_filename()
		dialog1.destroy()

		# Attempt to create face encoding with uploaded image
		if image_encoder(path_to_image) == False:
			dialog2 = Gtk.MessageDialog(
				self,
				0,
				Gtk.MessageType.INFO,
				Gtk.ButtonsType.OK,
				"Problem loading image")
			dialog2.format_secondary_text(
				"No face detected or multiple faces detected.\nTry again.")
			dialog2.run()
			dialog2.destroy()
		else:
			return True

class ListBoxRow(Gtk.ListBoxRow):

	"""ListBoxRow class."""

	def __init__(self, parent):
		Gtk.ListBoxRow.__init__(self)

		# Container
		vbox2 = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, spacing = 10)
		vbox2.set_border_width(20)
		self.add(vbox2)

		# Box for name entry
		hbox1 = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL, spacing = 20)
		vbox2.pack_start(hbox1, True, True, 0)

		label3 = Gtk.Label("Name:")
		label3.set_justify(Gtk.Justification.RIGHT)
		hbox1.pack_start(label3, True, True, 0)

		entry = Gtk.Entry()
		hbox1.pack_start(entry, True, True, 0)

		# Face upload Stack
		vbox3 = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, spacing = 10)
		vbox2.pack_start(vbox3, True, True, 0)

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
		"""Call picture_taker() and store new face name."""
		picture_taker()
		global faces
		faces.append(entry.get_text())
		widget.set_label("Face uploaded")

	def on_photo_chooser_clicked(self, widget, entry):
		"""Call file_chooser() and store new face name."""
		if self.get_toplevel().file_chooser() == True:
			global faces
			faces.append(entry.get_text())
			widget.set_label("Face uploaded")

if __name__ == "__main__":
	window = MainWindow()
	window.connect("delete-event", Gtk.main_quit)
	window.show_all()
	Gtk.main()


