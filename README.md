# Real-Time Object Detection

## Proje Hakkında
Bu proje, YOLO (You Only Look Once) algoritması kullanarak gerçek zamanlı nesne tespiti yapan bir uygulamadır. Kullanıcılar fotoğraf yükleyerek mobilya tespiti yapabilir ve sonuçları görselleştirebilir.

## Özellikler
- YOLOv8 modeli ile nesne tespiti
- Angular frontend arayüzü
- FastAPI backend servisi
- Gerçek zamanlı video işleme
- Confidence skorları ile detaylı sonuçlar
- Kullanıcı dostu modern arayüz

## Teknolojiler
- **Backend**: Python, Flask, YOLOv8, OpenCV
- **Frontend**: Angular, TypeScript, Bootstrap
- **AI/ML**: Ultralytics YOLO, PyTorch

## Kurulum

### Backend
```bash
cd backendd
pip install -r requirements.txt
python main.py
```

### Frontend
```bash
cd frontend
npm install
npm start
```

## Kullanım
1. Frontend uygulamasını başlatın (http://localhost:4200)
2. Backend servisini başlatın (http://localhost:5001)
3. Bir fotoğraf yükleyin
4. Tespit edilen nesneleri ve sayılarını görün

## Geliştirici
halilibrahimd27
