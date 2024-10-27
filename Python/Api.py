import os
from turtle import Turtle
import cv2
import numpy as np
import face_recognition
from fastapi import FastAPI, File, Form, UploadFile
from typing import List
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
import pickle

def save_encodings(encodings, filename='encodings.pkl'):
    with open(filename, 'wb') as f:
        pickle.dump(encodings, f)

def load_encodings(filename='encodings.pkl'):
    try:
        
        with open(filename, 'rb') as f:
            print("se encontro Archivo pickel")
            return pickle.load(f)
    except FileNotFoundError:
        return []  # Si no existe el archivo, devuelve una lista vacía

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


images = []
path = 'D:/Repositorios/Arduino-OpenCVPython/Python/Images'

classNames = []
mylist = os.listdir(path)
print(f"Imágenes encontradas: {mylist}")

for cl in mylist:
    curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    classNames.append(os.path.splitext(cl)[0])

def find_encodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList


encodelistknown = load_encodings()
if not encodelistknown:
    print("No hay archivo Picke")
    encodelistknown = find_encodings(images)
    save_encodings(encodelistknown)  


print("Encodings cargados o generados")



@app.post("/register")
async def register(file: UploadFile = File(...),nombre : str = Form(...),):
    try:
        if not file.content_type.startswith('image/'):
            return {"status": "fail", "message": "Formato no valido"}

        img = await file.read()
        np_img = np.frombuffer(img, np.uint8)
        img_np = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

        if img_np is None:
            return {"status": "fail", "message": "Error al decodificar la imagen"}

        img_rgb = cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img_rgb)

        if not encode:
            return {"status": "fail", "message": "No se detectó un rostro en la imagen"}

        encodelistknown.append(encode[0])
        classNames.append(nombre.upper())  

        save_encodings(encodelistknown)

        return {"status": "success", "message": "Usuario registrado exitosamente"}

    except Exception as e:
        return {"status": "error", "message": str(e)}



@app.get("/")
def read_root():
    return {"status": "success", "message": "API funcionando correctamente"}


@app.post("/recognize")
async def recognize(file: UploadFile = File(...)):
    try:
        if not file.content_type.startswith('image/'):
            return {"status": "fail", "message": "El archivo no es una imagen válida"}

        img = await file.read()
        np_img = np.frombuffer(img, np.uint8)
        img_np = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

        if img_np is None:
            return {"status": "fail", "message": "Error al decodificar la imagen"}
        if img_np.shape[0] < img_np.shape[1]: 
            img_np = cv2.rotate(img_np, cv2.ROTATE_90_CLOCKWISE)  

        imgS = cv2.resize(img_np, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        faceCurFrame = face_recognition.face_locations(imgS, model='hog')
        encodesCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

        if not encodesCurFrame:
            return {"status": "fail", "message": "No se detectaron rostros"}

        matched_names = []  

        for encodeFace, faceLoc in zip(encodesCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodelistknown, encodeFace)
            faceDis = face_recognition.face_distance(encodelistknown, encodeFace)
            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:
                name = classNames[matchIndex].upper()
                matched_names.append(name)  

        if matched_names:
            return {"status": "success", "message": "Matches encontrados", "matches": matched_names}
        else:
            return {"status": "fail", "message": "No se encontraron coincidencias"}

    except Exception as e:
        return {"status": "error", "message": str(e)}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("Api:app", host="0.0.0.0", port=8000, workers=2, reload=True)
