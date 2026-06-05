from ultralytics import YOLO

# 🔥 Load pretrained YOLOv8 medium model
model = YOLO("yolov8m.pt")

# 🔥 Train model
model.train(

    data="opg_dataset/dataset.yaml",

    epochs=120,

    imgsz=1024,

    batch=8,

    augment=True,

    patience=25,

    workers=2,

    name="dental_ai_model"
)