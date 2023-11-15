import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime
import requests
import matplotlib.pyplot as plt


esp32cam_url = 'http://192.168.1.151/640x480.jpg'

def get_esp32cam_image():
    try:
        response = requests.get(esp32cam_url, timeout=10)
        if response.status_code == 200:
            img_array = np.array(bytearray(response.content), dtype=np.uint8)
            img = cv2.imdecode(img_array, -1)
            return img
    except Exception as e:
        print(f"Error fetching image from ESP32-CAM: {str(e)}")
    return None



asistencias_estudiantes = {
    'JUAN': [
        {'Fecha': '13-11-23', 'Hora': '09:00:00'},
        {'Fecha': '14-11-23', 'Hora': '09:15:00'}
    ],
    'MARIA': [
        {'Fecha': '13-11-23', 'Hora': '09:10:00'}
    ]
}
path = 'Images'
images = []
classNames = []
mylist = os.listdir(path)
print(mylist)
for cl in mylist:
    curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    classNames.append(os.path.splitext(cl)[0])
print(classNames)




def find_encodings(images):
    encodeList = []
    i = 0
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
        print(f'Encoding {i}/{len(mylist)} done!')
        i=i+1
    return encodeList



def Marcar_Asistencia(name):
    now = datetime.now()
    fecha = now.strftime('%d-%m-%y')
    hora = now.strftime('%H:%M:%S')

    with open('Lista.csv', 'r+') as f:
        myDataList = f.readlines()
        nameList = []
        for line in myDataList:
            entry = line.split(',')
            nameList.append(entry[0])
        if name not in nameList:
            f.writelines(f'\n{name},{fecha},{hora}')

    if name not in asistencias_estudiantes:
        asistencias_estudiantes[name] = []


    for asistencia in asistencias_estudiantes[name]:
        if asistencia['Fecha'] == fecha:
            asistencia['Hora'] = hora
            break
    else:
        asistencias_estudiantes[name].append({'Fecha': fecha, 'Hora': hora})




encodelistknown = find_encodings(images)
print('Encoding Completado!!')


def Maximo_Clases():
    # Encuentra el máximo número de clases (basado en las fechas)
    max_clases = max(len(Asistencia) for Asistencia in asistencias_estudiantes.values())
    return max_clases



def dias_con_max_asistencias():
    max_clases_totales = Maximo_Clases()
    dias_por_asistencia = {i + 1: 0 for i in range(max_clases_totales)}
    
    for studiante in asistencias_estudiantes.values():
        dias_asistencia = len(studiante)
        if dias_asistencia == max_clases_totales:
            dias_por_asistencia[dias_asistencia] += 1
    
    return dias_por_asistencia

def plot_asistencias_individuales():
    dias = [str(day) for day in range(13, 18)]  
    fechas = set() 

    for attendance_list in asistencias_estudiantes.values():
        for asistencia in attendance_list:
            fecha = asistencia['Fecha']
            fechas.add(fecha)  # Almacenar fechas únicas en el conjunto

    max_clases = len(fechas)  

    for student, attendance_list in asistencias_estudiantes.items():
        asistencias = [0 for _ in range(13, 18)]
        for asistencia in attendance_list:
            fecha = asistencia['Fecha']
            dia = fecha.split('-')[0]  
            if dia in dias:
                index = dias.index(dia)
                asistencias[index] += 1

        plt.plot(dias, asistencias, marker='o', label=student) 

    plt.xlabel('Días')
    plt.ylabel('Asistencias Registradas')
    plt.title('Asistencias Individuales por Estudiante')
    plt.legend()
    plt.yticks(range(max_clases + 1)) 
    plt.show()


def Grafica_asistencias():
    dias = [str(day) for day in range(12, 18)] 
    asistencias = [0 for _ in range(12, 18)]  

    for studiante in asistencias_estudiantes.values():
        for asistencia in studiante:
            fecha = asistencia['Fecha']
            dia = fecha.split('-')[0] 
            if dia in dias:
                index = dias.index(dia)
                asistencias[index] += 1

    plt.bar(dias, asistencias, color='skyblue')
    plt.xlabel('Días')
    plt.ylabel('Asistencias Registradas')
    plt.title('Asistencias por Día (13-17)')
    plt.show()




while True:

    img = get_esp32cam_image()

    if img is not None:
        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        faceCurFrame = face_recognition.face_locations(imgS, 2)
        encodesCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

        for encodeFace, faceLoc in zip(encodesCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodelistknown, encodeFace)
            faceDis = face_recognition.face_distance(encodelistknown, encodeFace)
            matchIndex = np.argmin(faceDis)
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            if matches[matchIndex]:
                name = classNames[matchIndex].upper()
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                Marcar_Asistencia(name)
            else:
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 3)

        cv2.imshow('ESP32-CAM', img)
        key = cv2.waitKey(1)
        if key == 27:
            break

cv2.destroyAllWindows()


def mostrar_asistencias_estudiantes():
    for estudiante, asistencias in asistencias_estudiantes.items():
        print(f"Estudiante: {estudiante}")
        print("Asistencias:")
        for asistencia in asistencias:
            print(f"- {asistencia}")
        print()




def menu():
    print("MENU")
    print("1. Grafica de asistencias por dia")
    print("2. Grafica de asistencias individuales")
    print("3. Escriba 0 para salir")

def Opcion1():
    Grafica_asistencias()

def Opcion2():
    plot_asistencias_individuales()


MENU = {
    1: Opcion1,
    2: Opcion2
}


menu()

while True:


    Eleccion =  int(input("Eliga una opcion a realizar: "))
    if Eleccion == 0:
        break
    else:
        func = MENU.get(Eleccion)
        func()

print("¡Hasta luego!")
