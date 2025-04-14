from fastapi import APIRouter, UploadFile, File, Form
from Database.database import collection   # <-- Corrected path
import uuid, os, shutil

router = APIRouter()
UPLOAD_DIR = "UploadImage"  # <-- Updated directory name
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload/")
async def upload_form(
    name: str = Form(...),
    phone: str = Form(...),
    blood_group: str = Form(...),
    age: str = Form(...),
    image: UploadFile = File(...)
):
    filename = f"{uuid.uuid4()}_{image.filename}"
    image_path = os.path.join(UPLOAD_DIR, filename)

    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    form_data = {
        "name": name,
        "phone": phone,
        "blood_group": blood_group,
        "age": age,
        "image_path": image_path
    }

    collection.insert_one(form_data)
    return {"message": "Data saved to MongoDB"}
