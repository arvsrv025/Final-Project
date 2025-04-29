from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from Routes import upload
from dotenv import load_dotenv
from MlModel.model import predict, generate_grad_cam


load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)

@app.post("/predict")
async def make_prediction(file: UploadFile = File(...)):
    img_bytes = await file.read()
    label, prob = predict(img_bytes)
    cam_path = generate_grad_cam(img_bytes)

    return {
        "prediction": label,
        "confidence": f"{prob:.2f}",
        "grad_cam_image": cam_path  # You can serve this statically
    }

@app.get("/")
def read_root():
    return {"message": "API is running!"}
