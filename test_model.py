from ultralytics import YOLO

model = YOLO("backend/models/best.pt")

results = model("test.jpg", save=True)

print("Prediction done!")