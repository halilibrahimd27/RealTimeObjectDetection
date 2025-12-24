from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import cv2
from ultralytics import YOLO
from io import BytesIO
import numpy as np
import base64
from notification_service import notification_service

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"], "allow_headers": ["Content-Type"]}})
# YOLO model yolunu belirt
model = YOLO(r'/Users/halil/Halil/projects/YOLOBasedRealTimeObjectDetection/backendd/train50/weights/best.pt')

# Çıktı klasörü
output_folder = "Kaydedilenler"
os.makedirs(output_folder, exist_ok=True)

# Bildirim ayarları
SEND_NOTIFICATIONS = True  # Bildirim gönderimi açık/kapalı

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
    results = model(image)

    # Tespit edilen nesneleri topla
    detected_objects = []           # Tespit edilen nesne isimleri
    image_with_boxes = image.copy() # Orijinal görselin kopyası

    for result in results[0].boxes:
        label = int(result.cls[0])                  # Nesne sınıfı
        name = model.names[label]                   # Sınıf ismi
        detected_objects.append(name)

        # Kutu koordinatları (x1, y1, x2, y2)
        x1, y1, x2, y2 = map(int, result.xyxy[0])

        # Kutu çiz
        cv2.rectangle(image_with_boxes, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Sadece nesne ismini yaz (confidence yazılmaz)
        cv2.putText(image_with_boxes, name, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    # Nesnelerin sayısını al
    object_count = {obj: detected_objects.count(obj) for obj in set(detected_objects)}

    # Annotated image'i kaydet
    output_path = os.path.join(output_folder, "detected_sample.jpg")
    cv2.imwrite(output_path, image_with_boxes)

    # Annotated image'i base64 formatına dönüştür
    _, buffer = cv2.imencode('.jpg', image_with_boxes)
    img_byte_arr = BytesIO(buffer.tobytes())
    img_base64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')

    # Push notification gönder (eğer açıksa ve nesne tespit edildiyse)
    notification_result = None
    if SEND_NOTIFICATIONS and object_count:
        notification_result = notification_service.send_detection_notification(object_count)

    # JSON olarak döndür
    return jsonify({
        'image': img_base64, 
        'object_count': object_count,
        'notification': notification_result
    })


# ==================== NOTIFICATION ENDPOINTS ====================

@app.route('/notifications/register', methods=['POST'])
def register_device():
    """Cihaz token'ı kaydet"""
    data = request.get_json()
    token = data.get('token')
    
    if not token:
        return jsonify({"error": "Token gerekli"}), 400
    
    success = notification_service.register_token(token)
    
    return jsonify({
        "success": success,
        "message": "Cihaz kaydedildi" if success else "Cihaz zaten kayıtlı"
    })


@app.route('/notifications/unregister', methods=['POST'])
def unregister_device():
    """Cihaz token'ı sil"""
    data = request.get_json()
    token = data.get('token')
    
    if not token:
        return jsonify({"error": "Token gerekli"}), 400
    
    success = notification_service.unregister_token(token)
    
    return jsonify({
        "success": success,
        "message": "Cihaz silindi" if success else "Cihaz bulunamadı"
    })


@app.route('/notifications/test', methods=['POST'])
def test_notification():
    """Test bildirimi gönder"""
    result = notification_service.send_detection_notification({
        "test": 1,
        "insan": 2,
        "laptop": 1
    })
    
    return jsonify(result)


@app.route('/notifications/stats', methods=['GET'])
def notification_stats():
    """Bildirim servisi istatistikleri"""
    return jsonify(notification_service.get_stats())


@app.route('/notifications/test-pushover', methods=['POST'])
def test_pushover():
    """Pushover bildirimini test et"""
    if not notification_service.pushover:
        return jsonify({
            "success": False, 
            "message": "Pushover yapılandırılmamış. PUSHOVER_USER_KEY ve PUSHOVER_API_TOKEN ortam değişkenlerini ayarlayın."
        }), 400
    
    result = notification_service.pushover.send(
        title="🔔 Test Bildirimi",
        message="YOLODetect bildirim sistemi çalışıyor!",
        priority=0,
        sound="magic"
    )
    return jsonify(result)


@app.route('/notifications/send', methods=['POST'])
def send_custom_notification():
    """Özel bildirim gönder"""
    data = request.get_json()
    
    title = data.get('title', 'YOLODetect Bildirimi')
    body = data.get('body', '')
    
    if not body:
        return jsonify({"error": "Bildirim içeriği gerekli"}), 400
    
    from notification_service import NotificationPayload
    payload = NotificationPayload(title=title, body=body)
    result = notification_service.send_notification(payload)
    
    return jsonify(result)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)