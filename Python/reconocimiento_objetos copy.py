import cv2
import requests

# Dirección URL de la cámara
URL = "http://192.168.1.21"
AWB = True

# Obtener video
cap = cv2.VideoCapture(URL + ":81/stream")

# Definir resolución
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

# Definir calidad
def set_quality(url: str, value: int=1, verbose: bool=False):
    try:
        if value >= 10 and value <= 63:
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

# Línea de interés (línea horizontal en la parte inferior)
line_y = cap.get(4) - 80 # 10 píxeles desde la parte inferior

# Contador total
total_count = 0

# Lista de IDs de objetos rastreados
tracked_ids = []

# Función para verificar si un objeto ha cruzado la línea
def check_crossing(contours):
    global total_count
    for contour in contours:
        (x, y, w, h) = cv2.boundingRect(contour)
        # Verifica si el centro del objeto ha cruzado la línea
        if y + h // 2 > line_y:
            object_id = id(contour)  # Identificador único del objeto
            if object_id not in tracked_ids:
                total_count += 1
                tracked_ids.append(object_id)
                # Dibuja un rectángulo alrededor del objeto
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)


if __name__ == '__main__':
    set_resolution(URL, index=8)

    while True:
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                canny = cv2.Canny(cv2.GaussianBlur(gray, (11, 11), 0), 30, 150, 3)
                dilated = cv2.dilate(canny, (1, 1), iterations=2)
                (cnt, _) = cv2.findContours(dilated.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
                k = frame
                cv2.drawContours(k, cnt, -1, (0, 255, 0), 2)
                check_crossing(cnt)  # Verificar si un objeto cruza la línea
                cv2.line(frame, (0, int(line_y)), (frame.shape[1], int(line_y)), (255, 0, 0), 2)  # Dibujar la línea de interés
 # Dibujar la línea de interés
                cv2.imshow("Video", frame)
            
            key = cv2.waitKey(5)
            if key == ord('a'):
                print("Total de objetos cruzados:", total_count)
            if key == 27:
                break

cap.release()
cv2.destroyAllWindows()
