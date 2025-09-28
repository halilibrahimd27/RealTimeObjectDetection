import torch
from ultralytics import YOLO
import logging
from pathlib import Path

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Training configuration
CONFIG = {
    'model_name': 'yolov8n.pt',
    'data_yaml': '/Users/halil/Halil/projects/YOLOBasedRealTimeObjectDetection/backendd/dataset2/data.yaml',
    'epochs': 50,
    'batch': 4,
    'imgsz': 640,
    'patience': 5,
    'device': 'auto',  # Automatically select best device
}

def train_model():
    """YOLO modelini eğit"""
    try:
        # GPU/CPU kontrolü
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        logger.info(f"Kullanılan cihaz: {device}")
        
        # Model yükleme
        model = YOLO(CONFIG['model_name'])
        logger.info(f"Model yüklendi: {CONFIG['model_name']}")
        
        # Veri yolu kontrolü
        data_path = Path(CONFIG['data_yaml'])
        if not data_path.exists():
            raise FileNotFoundError(f"Veri dosyası bulunamadı: {data_path}")
        
        logger.info("Model eğitimi başlıyor...")
        
        # Model eğitimi
        results = model.train(
            data=str(data_path),
            epochs=CONFIG['epochs'],
            batch=CONFIG['batch'],
            imgsz=CONFIG['imgsz'],
            patience=CONFIG['patience'],
            device=device
        )
        
        logger.info("Model eğitimi başarıyla tamamlandı!")
        return results
        
    except Exception as e:
        logger.error(f"Eğitim sırasında hata oluştu: {str(e)}")
        raise

if __name__ == "__main__":
    train_model()