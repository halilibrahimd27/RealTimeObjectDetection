import torch
from ultralytics import YOLO


from roboflow import Roboflow

#rf = Roboflow(api_key="0rsJB6ZbFyymaVTudxgx")
#project = rf.workspace("yolo-u0uiv").project("yapayzeka-sot4y")
#version = project.version(1)
#dataset = version.download("yolov8")

#rf = Roboflow(api_key="0rsJB6ZbFyymaVTudxgx")
#project = rf.workspace("yolo-u0uiv").project("yapayzeka-sot4y")
#version = project.version(2)
#dataset = version.download("yolov8")

#1500 sandalye
#from roboflow import Roboflow
#rf = Roboflow(api_key="0rsJB6ZbFyymaVTudxgx")
#project = rf.workspace("yolo-u0uiv").project("yapayzeka-sot4y")
#version = project.version(3)
#dataset = version.download("yolov8")



# Modeli eğit
if __name__ == "__main__" :
    from roboflow import Roboflow

    model = YOLO('yolov8n.pt')  # YOLOv8 Nano modeli

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Kullanılan cihaz: {device}")

    #rf = Roboflow(api_key="0rsJB6ZbFyymaVTudxgx")
    #project = rf.workspace("yolo-u0uiv").project("meubels-2zefz")
    #version = project.version(2)
    #dataset = version.download("yolov8")

    #from roboflow import Roboflow
    #sandalye+benim
    #rf = Roboflow(api_key="0rsJB6ZbFyymaVTudxgx")
    #project = rf.workspace("yolo-u0uiv").project("yapayzeka-sot4y")
    #version = project.version(4)
    #dataset = version.download("yolov8")

#tüm fotolar
    #from roboflow import Roboflow
    #rf = Roboflow(api_key="0rsJB6ZbFyymaVTudxgx")
    #project = rf.workspace("yolo-u0uiv").project("yapayzeka-sot4y")
    #version = project.version(5)
    #dataset = version.download("yolov8")

#yeni
    #from roboflow import Roboflow
    #rf = Roboflow(api_key="0rsJB6ZbFyymaVTudxgx")
    #project = rf.workspace("yolo-u0uiv").project("yapayzeka2-ysbz4")
    #version = project.version(1)
    #dataset = version.download("yolov8")


    #model.train(data=f"{dataset.location}/data.yaml", epochs=40, device=device)

    model.train(
        data=r'/Users/halil/Halil/projects/YOLOBasedRealTimeObjectDetection/backendd/dataset2/data.yaml',  # Path to YAML file
        epochs=50,
        batch=4,
        imgsz=640,
        patience=5,
        
    )