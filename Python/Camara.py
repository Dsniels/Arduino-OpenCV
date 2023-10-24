import cv2
import requests


#NOTA: si al ejecutar el programa obtienes un error en la direccion ip,
#significa que cambio por lo que tienes que ir al editor arduino o abrir el monitor serial en vscode
# y presionar reset en la camara para obtener la nueva direccion ip de la camara




#Direccion url de la camara
URL = "http://192.168.1.6"
AWB = True 

#Obtener video
cap = cv2.VideoCapture(URL + ":81/stream")

#Archivo clasificador pre-entrenado para detectar rostros incluidos en la libreria OpenCV
f_h = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

#Definir Resolucion
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

#Definir Calidad
def set_quality(url: str, value: int=1, verbose: bool=False):
    try:
        if value >= 10 and value <=63:
            requests.get(url + "/control?var=quality&val={}".format(value))
    except:
        print("SET_QUALITY: something went wrong")


#Balanceo automatico de blancos para una mejor imagen segun la iluminacion
def set_awb(url: str, awb: int=1):
    try:
        awb = not awb
        requests.get(url + "/control?var=awb&val={}".format(1 if awb else 0))
    except:
        print("SET_QUALITY: something went wrong")
    return awb


#Funcion inicio
if __name__ == '__main__':

    set_resolution(URL, index=8)

    while True:
        if cap.isOpened():

            ret, img = cap.read()

            if ret:

                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) #Convierte a escalas de grises la imagen para identificar mas facil los pixeles del rostro
                gray = cv2.equalizeHist(gray) #mejora la calidad de la imagen en escalas de grises
                face = f_h.detectMultiScale(gray,scaleFactor=1.1, minNeighbors=5)  #compara la imagen del video para identifiar los rostros
                
                #identifica la parte de la cara e itera por las coordenadas de la cara y dibuja el rectangulo
                for x, y, w, h in face:
                    cv2.rectangle(img,(x,y),(x+w, y+h), (0,0,255),3)
                    roi_gray = gray[y:y+h, x:x+w]
                    roi_color = img[y:y+h, x:x+w]
                
            cv2.imshow("Video", img)

            key = cv2.waitKey(5)

            #Presiona ESC para cerrar la ventana
            if key == 27:
                break

    cv2.destroyAllWindows()
    cap.release() #libera las imagenes capturadas en la memoria y evitar problemas