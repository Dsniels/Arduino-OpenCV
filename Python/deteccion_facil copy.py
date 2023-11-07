import cv2
import requests
import face_recognition
import os
import serial
import time
import numpy as np

serial = serial.Serial('COM4', 115200, timeout= 1)
time.sleep(2)

# Codificación de rostros
def Codificar_Rostros(folder_path):
    face_encodings = []
    face_names = []

    for filename in os.listdir(folder_path):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            name = os.path.splitext(filename)[0]
            image = face_recognition.load_image_file(os.path.join(folder_path, filename))
            face_encoding = face_recognition.face_encodings(image)
            if len(face_encoding) > 0:
                face_encodings.append(face_encoding[0])
                face_names.append(name)

    return face_encodings, face_names

# Direccion URL de la camara
URL = "http://192.168.1.21"
AWB = True 

# Obtener video
cap = cv2.VideoCapture(URL + ":81/stream")

# Ruta de la carpeta que contiene imágenes de referencia
folder_path = "D:/Repositories/Arduino-OpenCV/Images"

# Cargar las codificaciones de referencia
known_face_encodings, known_face_names = Codificar_Rostros(folder_path)

# Definir Resolucion
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

# Definir Calidad
def set_quality(url: str, value: int=1, verbose: bool=False):
    try:
        if value >= 10 and value <=63:
            requests.get(url + "/control?var=quality&val={}".format(value))
    except:
        print("SET_QUALITY: something went wrong")

# Balanceo automático de blancos para una mejor imagen según la iluminación
def set_awb(url: str, awb: int=1):
    try:
        awb = not awb
        requests.get(url + "/control?var=awb&val={}".format(1 if awb else 0))
    except:
        print("SET_QUALITY: something went wrong")
    return awb

# Función inicio
if __name__ == '__main__':
    set_resolution(URL, index=8)
    cap = cv2.VideoCapture(URL + ":81/stream")
    if not cap.isOpened():
        print("No se puede abrir la camara")
        exit()

    while True:
        
        if cap.isOpened():
            ret, frame = cap.read()

            if ret == False:
                break

            frame = cv2.flip(frame, 1)

            face_locations = face_recognition.face_locations(frame)
            cv2.imshow("Video", frame)
            if face_locations:
                for face_location in face_locations:
                    face_frame_encodings = face_recognition.face_encodings(frame, known_face_locations=[face_location])[0]

                    for i, known_face_encoding in enumerate(known_face_encodings):
                        match = face_recognition.compare_faces([known_face_encoding], face_frame_encodings)

                        if match[0]:
                            color = (0, 255, 0)  # Verde para coincidencia
                            name = known_face_names[i]
                            serial.write(b'H')
                            cv2.putText(frame, name, (face_location[3], face_location[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                            break
                    else:
                        color = (0, 0, 255)  # Rojo para no coincidencia

                    cv2.rectangle(frame, (face_location[3], face_location[0]), (face_location[1], face_location[2]), color, 2)
            else:
                serial.write(b'L')
            cv2.imshow("Video", frame)

            key = cv2.waitKey(3)

            # Presiona ESC para cerrar la ventana
            if key == 27:
                break
cv2.destroyAllWindows()
frame = None
serial.close()
