from ultralytics import YOLO
import os

def run_prediction(image_path):
    model = YOLO("runs/detect/train4/weights/best.pt")

    results = model(image_path, save=True)

    save_dir = results[0].save_dir
    output_image = os.path.join(save_dir, os.path.basename(image_path))

    return output_image