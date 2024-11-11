import os
import cv2
import numpy as np
import face_recognition
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import pickle
import os


def save_encodings_and_names(encodings, names, filename='encodings.pkl'):
    with open(filename, 'wb') as f:
        pickle.dump((encodings, names), f)

def load_encodings_and_names(filename='encodings.pkl'):
    try:
        with open(filename, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:

        print("no hay archivo pickle")
        return [], []  
    
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


images = []
path = './Images'
# path = 'D:\Repositorios\Arduino-OpenCVPython\API\Images'

classNames = []
mylist = os.listdir(path)
print(f"Imágenes encontradas: {mylist}")


def find_encodings(images):
    encodeList = []
    validClassNames = []
    for img, name in zip(images, classNames):
        print(f"Procesando imagen: {name}")
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(img)
        if encodings:
            encodeList.append(encodings[0])
            validClassNames.append(name)  
        else:
            print(f"No se encontró encoding   para la imagen: {name}")
    return encodeList, validClassNames


encodelistknown, classNames = load_encodings_and_names()

if not encodelistknown:
    print("No hay archivo Pickle. Generando encodings.")

    for cl in mylist:
        curImg = cv2.imread(f'{path}/{cl}')
        images.append(curImg)
        classNames.append(os.path.splitext(cl)[0])
    encodelistknown, classNames = find_encodings(images)

    save_encodings_and_names(encodelistknown, classNames)

print("Encodings cargados o generados")

@app.put("/edit")
async def update(currentName : str = Form(...), newName:str=Form(...)):
    try:
        print(currentName in classNames)
        if currentName in classNames:
            index = classNames.index(currentName)
            print(classNames)
            print(newName)
            classNames[index] = newName
            print(classNames)

            save_encodings_and_names(encodelistknown, classNames)
            #os.rename(f'{path}/{currentName}.jpg',f'{path}/{newName}.jpg')
            return {"status":"success", "message":"Usuario Actualizado"}
        else:
            return {"status":"fail", "message": "Usuario No encontrado"}
    except Exception as e:
        return {"status":"fail", "message":str(e)}



@app.post("/delete_user")
async def delete_user(nombre: str = Form(...)):
    try:
        if nombre in classNames:
            index = classNames.index(nombre)
            print(classNames)
            classNames.pop(index)
            encodelistknown.pop(index)
            print(classNames)
            save_encodings_and_names(encodelistknown, classNames)
            os.remove(f'{path}/{nombre}.jpg')
            return {"status": "success", "message": "Usuario eliminado"}
        else:
            return {"status": "fail", "message": "Usuario no encontrado"}
    except Exception as e:
        return {"status": "fail", "message": str(e)}




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
        save_encodings_and_names(encodelistknown, classNames)

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


        # imgS = cv2.resize(img_np, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB)

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
