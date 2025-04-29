# app/utils/cloudinary_utils.py

import cloudinary
import cloudinary.uploader
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

def upload_image_to_cloudinary(local_path, folder="gradcam"):
    try:
        response = cloudinary.uploader.upload(
            local_path,
            folder=folder,
            use_filename=True,
            unique_filename=False,
            overwrite=True
        )
        return response.get("secure_url")
    except Exception as e:
        raise RuntimeError(f"Cloudinary upload failed: {e}")
