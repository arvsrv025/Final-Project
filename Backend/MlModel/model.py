# app/model/model.py

import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras import backend as K
from PIL import Image
import io
import cv2
import os
import uuid

# Load model once when the file is imported
MODEL_PATH = "C:/Users/Admin/Downloads/brain_tumor_model.h5"
model = tf.keras.models.load_model(MODEL_PATH)

IMG_SIZE = (224, 224)

# Define your class names in the correct order
class_names = ['No Tumor', 'Meningioma Tumor', 'Glioma Tumor', 'Pituitary Tumor']

def preprocess_image(image_bytes):
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB").resize(IMG_SIZE)
    arr = np.array(img) / 255.0  # Normalize to [0,1]
    arr = np.expand_dims(arr, axis=0)  # Shape (1,224,224,3)
    return arr, img

def predict(image_bytes):
    input_arr, _ = preprocess_image(image_bytes)
    preds = model.predict(input_arr)[0]  # preds shape -> (4,)
    
    predicted_class_idx = np.argmax(preds)
    predicted_class = class_names[predicted_class_idx]
    confidence = float(np.max(preds))

    return predicted_class, confidence

def generate_grad_cam(image_bytes, output_dir="outputs"):
    # Preprocess image
    input_arr, original_img = preprocess_image(image_bytes)

    # Grad-CAM model setup
    grad_model = tf.keras.models.Model(
        [model.inputs], [model.get_layer("conv2d_14").output, model.output]
    )

    with tf.GradientTape() as tape:
        conv_outputs, predictions = grad_model(input_arr)
        predicted_class_idx = tf.argmax(predictions[0])
        loss = predictions[:, predicted_class_idx]

    # Get gradients
    grads = tape.gradient(loss, conv_outputs)
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
    conv_outputs = conv_outputs[0]

    # Generate heatmap
    heatmap = tf.reduce_sum(tf.multiply(pooled_grads, conv_outputs), axis=-1)
    heatmap = np.maximum(heatmap, 0)
    heatmap /= tf.math.reduce_max(heatmap) + 1e-8
    heatmap = heatmap.numpy()

    # Resize and convert to color
    heatmap = cv2.resize(heatmap, IMG_SIZE)
    heatmap_color = cv2.applyColorMap(np.uint8(255 * heatmap), cv2.COLORMAP_JET)

    # Convert original image to OpenCV BGR
    original_img = cv2.cvtColor(np.array(original_img), cv2.COLOR_RGB2BGR)

    # Blend the heatmap with original image
    superimposed_img = cv2.addWeighted(original_img, 0.6, heatmap_color, 0.4, 0)

    # Save result
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{uuid.uuid4()}.jpg"
    filepath = os.path.join(output_dir, filename)
    
    success = cv2.imwrite(filepath, superimposed_img)
    if not success:
        raise RuntimeError("Grad-CAM image failed to save.")

    return filepath
