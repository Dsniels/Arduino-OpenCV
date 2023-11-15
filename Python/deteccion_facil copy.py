import cv2
import requests
import face_recognition
import os
import serial
import time
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Configuración global
URL = "http://192.168.1.21"
PUERTO_STREAM = ":81/stream"
SERIAL_PORT = 'COM4'
USUARIOS = set()
nombres_detectados = set()

def generar_pdf():
    pdf_nombre = "Personas detectadas.pdf"

    c = canvas.Canvas(pdf_nombre, pagesize=letter)

    c.drawString(100, 750, "Personas detectadas:")

    Coordenada = 720  # Coordenada Y inicial para imprimir los nombres

    for usuario in USUARIOS:
        c.drawString(100, Coordenada, usuario)
        Coordenada -= 15  # Espacio vertical entre cada nombre

    c.save()

    print(f"Los nombres de personas detectadas se han guardado en {pdf_nombre}")
# Codificación de rostros
def codificar_rostros(folder_path):
    face_encodings = []
    face_names = []

    for filename in os.listdir(folder_path):
        if filename.lower().endswith((".jpg", ".png")):
            name = os.path.splitext(filename)[0]
            image = face_recognition.load_image_file(os.path.join(folder_path, filename))
            face_encoding = face_recognition.face_encodings(image)
            if face_encoding:
                face_encodings.append(face_encoding[0])
                face_names.append(name)

    return face_encodings, face_names

# Definir Resolución
def set_resolution(url, index=8, verbose=False):
    resolutions = {
        10: 'UXGA(1600x1200)',
        9: 'SXGA(1280x1024)',
        8: 'XGA(1024x768)',
        7: 'SVGA(800x600)',
        6: 'VGA(640x480)',
        5: 'CIF(400x296)',
        4: 'QVGA(320x240)',
        3: 'HQVGA(240x176)',
        0: 'QQVGA(160x120)'
    }
    if verbose:
        print("Available resolutions:")
        for idx, resolution in resolutions.items():
            print(f"{idx}: {resolution}")

    if index in resolutions:
        requests.get(f"{url}/control?var=framesize&val={index}")
    else:
        print("Wrong index")

# Definir Calidad
def set_quality(url, value=1):
    if 10 <= value <= 63:
        requests.get(f"{url}/control?var=quality&val={value}")

# Balanceo automático de blancos para una mejor imagen según la iluminación
def set_awb(url, awb=True):
    awb = not awb
    requests.get(f"{url}/control?var=awb&val={1 if awb else 0}")
    return awb

# Procesamiento de video
def procesar_video(cap, known_face_encodings, known_face_names, serial_port):
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        face_locations = face_recognition.face_locations(frame)

        if face_locations:
            for face_location in face_locations:
                face_frame_encodings = face_recognition.face_encodings(frame, known_face_locations=[face_location])[0]

                for i, known_face_encoding in enumerate(known_face_encodings):
                    match = face_recognition.compare_faces([known_face_encoding], face_frame_encodings, tolerance=0.5)

                    if match[0]:
                        color = (0, 255, 0)  # Verde para coincidencia
                        name = known_face_names[i]
                        serial_port.write(b'H')
                        serial_port.write(name.encode())
                        # Verifica si el nombre ya ha sido detectado
                        if name not in nombres_detectados:
                            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                            usuario = f"({timestamp})---{name}"
                            USUARIOS.add(usuario)
                            # Agrega el nombre al conjunto de nombres detectados
                            nombres_detectados.add(name)
                        break

                else:
                    color = (0, 0, 255)  # Rojo para no coincidencia

                cv2.rectangle(frame, (face_location[3], face_location[0]), (face_location[1], face_location[2]), color, 2)
        else:
            serial_port.write(b'L')
        cv2.imshow("Video", frame)

        key = cv2.waitKey(3)

        if key == 27:
            break

# Función inicio
if __name__ == '__main__':
    
    # Obtener video
    video_url = URL + PUERTO_STREAM
    print(f"Conectando Camara")
    cap = cv2.VideoCapture(video_url)
    print(f"Camara Conectada")

    if not cap.isOpened():
        print("No se puede abrir la cámara")
        exit()
    
    print(f"Conectando Puerto Serial")
    serial_port = serial.Serial(SERIAL_PORT, 115200, timeout=1)
    time.sleep(2)
    print(f"Puerto Serial Conectado")

    try:
        # Ruta de la carpeta que contiene imágenes de referencia
        folder_path = "D:/Repositories/Arduino-OpenCV/Images"

        # Cargar las codificaciones de referencia
        known_face_encodings, known_face_names = codificar_rostros(folder_path)

        set_resolution(URL, index=8)
        cap = cv2.VideoCapture(video_url)
        procesar_video(cap, known_face_encodings, known_face_names, serial_port)
    except Exception as e:
        print(f"Error: {e}")
        cap.release()
        cv2.destroyAllWindows()
        serial_port.close()
        procesar_video()
    finally:
        cap.release()
        cv2.destroyAllWindows()
        serial_port.close()

if USUARIOS:
    print("Nombres detectados:")
    for name in USUARIOS:
        print(name)

    generar_pdf()
