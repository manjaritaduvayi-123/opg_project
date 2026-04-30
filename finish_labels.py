import os

img_folder = "new_missing_teeth_images"
label_folder = "opg_labels/train"

os.makedirs(label_folder, exist_ok=True)

CLASS_ID = 2  # Missing_teeth

for img in os.listdir(img_folder):
    if img.endswith((".jpg", ".png", ".jpeg")):
        label_path = os.path.join(label_folder, img.replace(".jpg", ".txt").replace(".png", ".txt"))

        if os.path.exists(label_path):
            continue

        with open(label_path, "w") as f:
            f.write(f"{CLASS_ID} 0.5 0.5 1.0 1.0\n")

print("✅ Labels created successfully")