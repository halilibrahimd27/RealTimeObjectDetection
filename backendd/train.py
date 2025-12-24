import torch
from ultralytics import YOLO

if __name__ == "__main__" :
    from roboflow import Roboflow

    model = YOLO('yolov8n.pt')

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Kullanılan cihaz: {device}")

    model.train(
        data=r'/Users/halil/Halil/projects/YOLOBasedRealTimeObjectDetection/backendd/dataset2/data.yaml',  # Path to YAML file
        epochs=50,
        batch=4,
        imgsz=640,
        patience=5,
        device=device,
    )