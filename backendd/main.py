from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import cv2
from ultralytics import YOLO
from io import BytesIO
import numpy as np
import base64
import logging

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# YOLO model yolunu belirt
MODEL_PATH = r'/Users/halil/Halil/projects/YOLOBasedRealTimeObjectDetection/backendd/train50/weights/best.pt'
model = YOLO(MODEL_PATH)
logger.info(f"YOLO model loaded from: {MODEL_PATH}")

# Çıktı klasörü
output_folder = "Kaydedilenler"
os.makedirs(output_folder, exist_ok=True)

@app.route('/predict', methods=['POST'])
def detect_objects():
    # Fotoğrafı al
    image_file = request.files.get('image')
    if not image_file:
        return jsonify({"error": "Image file is missing"}), 400

    # Fotoğrafı numpy array'e dönüştür
    image = np.frombuffer(image_file.read(), np.uint8)
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)

    if image is None:
        return jsonify({"error": "Invalid image"}), 400

    # YOLO modeliyle tahmin yap
    logger.info("Running inference on uploaded image")
    results = model(image)

    # Tespit edilen nesneleri topla
    detected_objects = []
    image_with_boxes = image.copy()

    for result in results[0].boxes:
        label = int(result.cls[0])
        name = model.names[label]
        confidence = float(result.conf[0])
        detected_objects.append(name)

        # Kutu koordinatları (x1, y1, x2, y2)
        x1, y1, x2, y2 = map(int, result.xyxy[0])

        # Kutu çiz
        cv2.rectangle(image_with_boxes, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Nesne ismi ve confidence değeri
        label_text = f"{name} {confidence:.2f}"
        cv2.putText(image_with_boxes, label_text, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # Nesnelerin sayısını al
    object_count = {obj: detected_objects.count(obj) for obj in set(detected_objects)}
    logger.info(f"Detected objects: {object_count}")

    # Annotated image'i kaydet
    output_path = os.path.join(output_folder, "detected_sample.jpg")
    cv2.imwrite(output_path, image_with_boxes)
    logger.info(f"Saved detection result to {output_path}")

    # Annotated image'i base64 formatına dönüştür
    _, buffer = cv2.imencode('.jpg', image_with_boxes)
    img_byte_arr = BytesIO(buffer.tobytes())
    img_base64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')

    # JSON olarak döndür
    return jsonify({
        'image': img_base64, 
        'object_count': object_count,
        'total_objects': len(detected_objects)
    })

if __name__ == '__main__':
    logger.info("Starting Flask server on port 5001")
    app.run(host='0.0.0.0', port=5001, debug=True)
