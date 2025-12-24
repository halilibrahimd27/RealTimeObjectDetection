# 🎯 YOLODetect - Real-Time Object Detection

<div align="center">

![YOLOv8](https://img.shields.io/badge/YOLOv8-Custom%20Trained-blue)
![Angular](https://img.shields.io/badge/Angular-18-red)
![Flask](https://img.shields.io/badge/Flask-Python-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

**Yapay zeka destekli gerçek zamanlı nesne tespit sistemi**

[Demo](#demo) • [Özellikler](#özellikler) • [Kurulum](#kurulum) • [Kullanım](#kullanım)

</div>

---

## 📖 Proje Hakkında

Bu proje, **YOLOv8** (You Only Look Once) algoritması kullanarak gerçek zamanlı nesne tespiti yapan modern bir web uygulamasıdır. Özel eğitilmiş model ile **14 farklı nesne sınıfını** tespit edebilir ve anlık mobil bildirimler gönderir.

### 🎯 Tespit Edilebilen Nesneler
| Kategori | Nesneler |
|----------|----------|
| 👤 Canlılar | insan |
| 💻 Elektronik | laptop, monitor, klavye, mouse |
| 🪑 Mobilya | masa, sandalye, dolap |
| 👜 Aksesuarlar | çanta, cüzdan, gözlük, kalem, kol saati |
| 🍶 Diğer | şişe |

---

## ✨ Özellikler

### 🖥️ Modern Arayüz
- 🌙 **Dark Theme** - Göz yormayan karanlık tema
- 📤 **Drag & Drop** - Sürükle bırak ile kolay görsel yükleme
- 📊 **Dashboard** - Gerçek zamanlı istatistikler
- 📱 **Responsive** - Mobil uyumlu tasarım

### 🤖 Yapay Zeka
- ⚡ **YOLOv8** - En güncel YOLO modeli
- 🎓 **Custom Training** - Özel eğitilmiş model (14 sınıf)
- 🎯 **Yüksek Doğruluk** - Confidence skorları ile sonuçlar
- 🖼️ **Görsel İşaretleme** - Tespit edilen nesneler üzerinde bounding box

### 🔔 Bildirim Sistemi
- 📱 **iPhone/Android** - Pushover ile gerçek mobil bildirimler
- 🌐 **Web Notifications** - Tarayıcı bildirimleri
- 📋 **Bildirim Geçmişi** - Tüm tespitlerin kaydı
- 🔕 **Sessiz Mod** - İsteğe bağlı bildirim kontrolü

---

## 🛠️ Teknolojiler

<table>
<tr>
<td align="center"><b>Backend</b></td>
<td align="center"><b>Frontend</b></td>
<td align="center"><b>AI/ML</b></td>
<td align="center"><b>Bildirimler</b></td>
</tr>
<tr>
<td>

- Python 3.9+
- Flask
- OpenCV
- NumPy

</td>
<td>

- Angular 18
- TypeScript
- Bootstrap 5
- RxJS

</td>
<td>

- Ultralytics YOLOv8
- PyTorch
- Custom Dataset
- Roboflow

</td>
<td>

- Pushover API
- Web Push API
- Firebase (opsiyonel)

</td>
</tr>
</table>

---

## 📦 Kurulum

### Gereksinimler
- Python 3.9+
- Node.js 18+
- npm veya yarn

### 1️⃣ Repoyu Klonla
```bash
git clone https://github.com/halilibrahimd27/RealTimeObjectDetection.git
cd RealTimeObjectDetection
```

### 2️⃣ Backend Kurulumu
```bash
cd backendd
pip install -r requirements.txt
```

### 3️⃣ Frontend Kurulumu
```bash
cd frontend
npm install
```

### 4️⃣ Mobil Bildirimler (Opsiyonel)
iPhone/Android bildirimleri için:
1. [Pushover](https://pushover.net) hesabı oluştur
2. Mobil uygulamayı indir
3. `backendd/notification_service.py` dosyasına API anahtarlarını ekle:
```python
PUSHOVER_USER_KEY = "your_user_key"
PUSHOVER_API_TOKEN = "your_api_token"
```

---

## 🚀 Kullanım

### Uygulamayı Başlat

**Terminal 1 - Backend:**
```bash
cd backendd
python3 main.py
# Çalışır: http://localhost:5001
```

**Terminal 2 - Frontend:**
```bash
cd frontend
ng serve --open
# Açılır: http://localhost:4200
```

### Nesne Tespiti Yap
1. 🌐 Tarayıcıda `http://localhost:4200` adresine git
2. 📤 Görsel yükle (sürükle-bırak veya tıkla)
3. 🔍 "Nesne Tespit Et" butonuna tıkla
4. 📊 Sonuçları gör
5. 📱 iPhone'dan bildirimi al!

---

## 📁 Proje Yapısı

```
YOLOBasedRealTimeObjectDetection/
├── 📂 backendd/
│   ├── main.py                 # Flask API sunucusu
│   ├── notification_service.py # Pushover bildirim servisi
│   ├── train.py               # Model eğitim scripti
│   ├── requirements.txt       # Python bağımlılıkları
│   ├── 📂 dataset/            # Eğitim veri seti
│   └── 📂 train50/weights/    # Eğitilmiş model ağırlıkları
│
├── 📂 frontend/
│   ├── 📂 src/app/
│   │   ├── header/            # Üst menü bileşeni
│   │   ├── upload/            # Görsel yükleme bileşeni
│   │   ├── notification-panel/# Bildirim paneli
│   │   └── services/          # Angular servisleri
│   └── ...
│
└── 📂 runs/                   # YOLO çıktıları
```

---

## 📸 Ekran Görüntüleri

| Ana Sayfa | Tespit Sonucu | Bildirimler |
|-----------|---------------|-------------|
| ![Home](docs/home.png) | ![Detection](docs/detection.png) | ![Notifications](docs/notifications.png) |

---

## 🔧 API Endpoints

| Method | Endpoint | Açıklama |
|--------|----------|----------|
| POST | `/predict` | Görsel üzerinde nesne tespiti |
| POST | `/notifications/register` | Cihaz token kayıt |
| POST | `/notifications/test-pushover` | Pushover test bildirimi |
| GET | `/notifications/stats` | Bildirim istatistikleri |

---

## 🎓 Model Eğitimi

Kendi modelinizi eğitmek için:

```bash
cd backendd
python train.py
```

Eğitim parametreleri `train.py` dosyasında ayarlanabilir.

---

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

---

## 👨‍💻 Geliştirici

<div align="center">

**Halil İbrahim Demirtaş**

[![GitHub](https://img.shields.io/badge/GitHub-halilibrahimd27-black?style=flat&logo=github)](https://github.com/halilibrahimd27)

</div>

---

<div align="center">

⭐ Bu projeyi beğendiyseniz yıldız vermeyi unutmayın!

</div>
