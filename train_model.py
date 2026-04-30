from ultralytics import YOLO

# Load model
model = YOLO("yolov8m.pt")  # lightweight model

# Train
model.train(
    data="opg_dataset/dataset.yaml",
    epochs=20,
    imgsz=416,
    batch=4,
    augment=False
)