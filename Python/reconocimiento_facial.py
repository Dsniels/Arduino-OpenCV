
import face_recognition
import imutils #imutils includes opencv functions
import pickle
import time
import cv2
import os
import tkinter as tk
from tkinter import filedialog
import serial
import time
import requests
	

def set_resolution(url: str, index: int=1, verbose: bool=False):
		try:
			if verbose:
				resolutions = "10: UXGA(1600x1200)\n9: SXGA(1280x1024)\n8: XGA(1024x768)\n7: SVGA(800x600)\n6: VGA(640x480)\n5: CIF(400x296)\n4: QVGA(320x240)\n3: HQVGA(240x176)\n0: QQVGA(160x120)"
				print("available resolutions\n{}".format(resolutions))

			if index in [10, 9, 8, 7, 6, 5, 4, 3, 0]:
				requests.get(url + "/control?var=framesize&val={}".format(index))
			else:
				print("Wrong index")
		except:
			print("SET_RESOLUTION: something went wrong")

def set_quality(url: str, value: int=1, verbose: bool=False):
		try:
			if value >= 10 and value <=63:
				requests.get(url + "/control?var=quality&val={}".format(value))
		except:
			print("SET_QUALITY: something went wrong")
def set_awb(url: str, awb: int=1):
		try:
			awb = not awb
			requests.get(url + "/control?var=awb&val={}".format(1 if awb else 0))
		except:
			print("SET_QUALITY: something went wrong")
		return awb

def recognize_face():


	#to find path of xml file containing haarCascade file
	cfp = os.path.dirname(cv2.__file__) + "/data/haarcascade_frontalface_alt2.xml"
	# load the harcaascade in the cascade classifier
	fc = cv2.CascadeClassifier(cfp)
	# load the known faces and embeddings saved in last file
	data = pickle.loads(open('face_enc', "rb").read())

	#Find path to the image you want to detect face and pass it here

	URL = "http://192.168.1.22"
	AWB = True
	
	set_resolution(URL, index=8)
	#Obtener video

	image = cv2.VideoCapture(URL + ":81/stream")
	rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
	while True:
		if image.isOpened():
				ret, frame = image.read()
				#convert image to Greyscale for HaarCascade
				gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
				faces = fc.detectMultiScale(gray,
				scaleFactor=1.1,
				minNeighbors=6,
				minSize=(60, 60),
				flags=cv2.CASCADE_SCALE_IMAGE)

		

				# the facial embeddings for face in input
				encodings = face_recognition.face_encodings(rgb)
				names = []
				name = "na"

				# loop over the facial embeddings incase
				# we have multiple embeddings for multiple fcaes
				for encoding in encodings:
					#Compare encodings with encodings in data["encodings"]
					#Matches contain array with boolean values True and False
					matches = face_recognition.compare_faces(data["encodings"],encoding)
						
						#set name = unknown if no encoding matches
					name = "Unknown"
						
						# check to see if we have found a match
					if True in matches:
							#Find positions at which we get True and store them
							matchedIdxs = [i for (i, b) in enumerate(matches) if b]
							count = {}
						
						# loop over the matched indexes and maintain a count for
						# each recognized face face
					for i in matchedIdxs:
							#Check the names at respective indexes we stored in matchedIdxs
							name = data["names"][i]
							
							#increase count for the name we got
							count[name] = count.get(name, 0) + 1
							#set name which has highest count
							name = max(count, key=count.get)
							# will update the list of names
							names.append(name)

							# do loop over the recognized faces
							for ((x, y, w, h), name) in zip(faces, names):
								# rescale the face coordinates
								# draw the predicted face name on the image
								cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
								cv2.putText(image, name, (x, y), cv2.FONT_HERSHEY_SIMPLEX,
								0.75, (0, 255, 0), 2)
								cv2.imshow("Frame", image)
								cv2.waitKey(0)
								print(name + " returned")
								return name
		key = cv2.waitKey(1)

		#Presiona ESC para cerrar la ventana			
		if key == 27:
        
	    	    break	 
          


def main():

	port = serial.Serial(port='COM5', baudrate=9600)
	port.timeout = 1

	while True:
		datum = recognize_face().strip()
		print("Detected face: " + datum)
		port.write(datum.encode())
		time.sleep(0.5)
	
	port.close()
	

if __name__ == '__main__':
        main()