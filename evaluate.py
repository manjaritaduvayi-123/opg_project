from ultralytics import YOLO

# 🔥 Load trained model
model = YOLO("best.pt")   # ensure path is correct

# 🔥 Run validation
metrics = model.val(data="dataset_filtered.yaml")

print("\n===== PERFORMANCE METRICS =====\n")

# ✅ Overall metrics
print("---- Overall Metrics ----")
print(f"Precision      : {metrics.box.p.mean():.4f}")
print(f"Recall         : {metrics.box.r.mean():.4f}")
print(f"F1 Score       : {metrics.box.f1.mean():.4f}")
print(f"mAP@0.5        : {metrics.box.map50:.4f}")
print(f"mAP@0.5:0.95   : {metrics.box.map:.4f}")

# ✅ Class names (safer way)
names = metrics.names  # better than model.names

# ✅ Per-class metrics
print("\n---- Per Class Metrics ----")

for i in range(len(metrics.box.p)):
    print(f"\nClass {i} ({names[i]}):")
    print(f"  Precision  : {metrics.box.p[i]:.4f}")
    print(f"  Recall     : {metrics.box.r[i]:.4f}")
    print(f"  F1 Score   : {metrics.box.f1[i]:.4f}")

print("\n===== DONE =====")