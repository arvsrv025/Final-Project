from fastapi import APIRouter, UploadFile, File, Form
from Database.database import collection
from MlModel.model import predict, generate_grad_cam
from Utils.cloudianary_utils import upload_image_to_cloudinary
import uuid, os, shutil

router = APIRouter()
UPLOAD_DIR = "UploadImage"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload/")
async def upload_form(
    name: str = Form(...),
    phone: str = Form(...),
    blood_group: str = Form(...),
    age: str = Form(...),
    image: UploadFile = File(...)
):
    # Save uploaded file locally
    filename = f"{uuid.uuid4()}_{image.filename}"
    local_image_path = os.path.join(UPLOAD_DIR, filename)

    with open(local_image_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    # ✅ Upload to Cloudinary
    cloudinary_url = upload_image_to_cloudinary(local_image_path)

    # ✅ Predict using model (if you want)
    with open(local_image_path, "rb") as f:
        image_bytes = f.read()
    prediction_result, prediction_confidence = predict(image_bytes)

    # ✅ Save form data + Cloudinary image URL to MongoDB
    form_data = {
        "name": name,
        "phone": phone,
        "blood_group": blood_group,
        "age": age,
        "image_url": cloudinary_url,  # <-- Store the Cloudinary URL
    }

    collection.insert_one(form_data)

    return {
        "message": "Data saved successfully",
        "cloudinary_url": cloudinary_url,
        "prediction": prediction_result,
        "confidence": float(prediction_confidence)
    }
