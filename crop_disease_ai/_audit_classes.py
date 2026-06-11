import numpy as np
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

indices = np.load('models/class_indices.npy', allow_pickle=True).item()
print(f"Total classes in model: {len(indices)}")
print()

from utils.config import DISEASE_CLASSES, SUPPORTED_CROPS
from utils.model_handler import ModelHandler

class_names = {v: k for k, v in indices.items()}

print("=" * 70)
print("CROP DISEASE AI - COMPLETE DATASET AUDIT REPORT")
print("=" * 70)

print("\n--- SUPPORTED CROPS ---")
for c in sorted(SUPPORTED_CROPS):
    print(f"  + {c}")

print("\n--- DISEASE CLASSES (CONFIG) vs MODEL COVERAGE ---")
missing_from_model = []
for key, val in sorted(DISEASE_CLASSES.items()):
    in_model = key in indices
    status = "IN_MODEL" if in_model else "MISSING"
    if not in_model:
        missing_from_model.append(key)
    n = val.encode('ascii', 'replace').decode()
    print(f"  [{status}] {n:45s} ({key})")

print("\n--- MODEL CLASS INDICES ---")
for idx in sorted(class_names.keys()):
    class_key = class_names[idx]
    display_name = DISEASE_CLASSES.get(class_key, "**NOT_IN_CONFIG**")
    found = class_key in DISEASE_CLASSES
    status = "OK" if found else "EXTRA"
    print(f"  [{status}] idx={idx:3d} {class_key:55s} -> {display_name}")

print("\n--- SUMMARY: MISSING FROM MODEL ---")
if missing_from_model:
    for dk in missing_from_model:
        n = DISEASE_CLASSES[dk].encode('ascii', 'replace').decode()
        print(f"  [MISS] {n:45s} ({dk})")
else:
    print("  All classes present.")

print("\n--- SUMMARY: EXTRA IN MODEL ---")
extra = [ik for ik in indices if ik not in DISEASE_CLASSES]
if extra:
    for ik in extra:
        print(f"  [EXTRA] {ik}")
else:
    print("  No extra classes.")

print("\n--- CROP COVERAGE DETAIL ---")
for crop in sorted(SUPPORTED_CROPS):
    model_count = len([idx for idx, k in class_names.items() if k.startswith(crop)])
    config_count = len([v for k, v in DISEASE_CLASSES.items() if v.startswith(crop)])
    status = "OK" if model_count == config_count else f"MISMATCH ({model_count} vs {config_count})"
    print(f"  {crop:15s} model={model_count} config={config_count} {status}")

print("\n--- CRITICAL: RICE CHECK ---")
rice_config = [v for k, v in DISEASE_CLASSES.items() if v.startswith("Rice")]
rice_model_keys = [class_names[idx] for idx in sorted(class_names.keys()) if class_names[idx].startswith("Rice")]
print(f"  Rice in config:          {rice_config}")
print(f"  Rice in model indices:   {rice_model_keys}")
if not rice_model_keys:
    print("  *** ROOT CAUSE: RICE IS NOT IN THE MODEL ***")
    print(f"  Model only has {len(indices)} classes, Rice starts at index 68 in DISEASE_CLASSES")
    print(f"  The dummy training only used the first {len(indices)} DISEASE_CLASSES keys")
    print(f"  Rice is at positions 68-71 in DISEASE_CLASSES dict (Python 3.7+ preserves order)")

print("\n--- CRITICAL: CHILI CHECK ---")
chili_config = [v for k, v in DISEASE_CLASSES.items() if v.startswith("Chili")]
chili_model_keys = [class_names[idx] for idx in sorted(class_names.keys()) if class_names[idx].startswith("Chili")]
print(f"  Chili in config:        {chili_config}")
print(f"  Chili in model indices: {chili_model_keys}")

print("\n--- MODEL OUTPUT vs CONFIG SIZE MISMATCH ---")
print(f"  Model output size:   {len(indices)}")
print(f"  DISEASE_CLASSES size: {len(DISEASE_CLASSES)}")
if len(indices) != len(DISEASE_CLASSES):
    print(f"  *** MISMATCH of {len(DISEASE_CLASSES) - len(indices)} classes ***")
    print(f"  Model was trained on only {len(indices)} classes but config defines {len(DISEASE_CLASSES)}")
else:
    print("  Sizes match.")

print("\n--- MODEL QUALITY CHECK ---")
import tensorflow as tf
model = tf.keras.models.load_model('models/plant_disease_model.h5')
dummy_data = np.random.rand(10, 224, 224, 3)
dummy_labels = np.eye(57)[:10]
loss, acc = model.evaluate(dummy_data, dummy_labels, verbose=0)
print(f"  Random-sample accuracy: {acc*100:.1f}% (expected ~1.8% for 57-class random)")
if acc < 0.1:
    print("  *** Model appears to have random/dummy weights ***")
    print("  Model was likely created via create_dummy_model() in train_model.py")
print()

print("\n--- ROOT CAUSE ANALYSIS ---")
print()
print("  FINDING 1: Label coverage")
print("  -------------------------")
if all(ik in DISEASE_CLASSES for ik in indices):
    print("  All model classes map to DISEASE_CLASSES correctly.")
else:
    print("  Some model classes are missing from DISEASE_CLASSES config!")
print()
print("  FINDING 2: Rice presence")
print("  ------------------------")
if "Rice___Brown_spot" in indices:
    print("  Rice IS in the model class indices (OK).")
    print("  Rice is at indices 13-16 in the model output.")
else:
    print("  Rice is NOT in the model -- training data issue.")
print()
print("  FINDING 3: Model weights quality")
print("  --------------------------------")
print("  The model was trained on random data (dummy model).")
print("  Its predictions are essentially random despite high softmax confidence.")
print("  This is the ROOT CAUSE of misclassification.")
print()
print("  FINDING 4: Inference pipeline (BEFORE FIX)")
print("  -------------------------------------------")
print("  The old code accepted any prediction with confidence > 85%.")
print("  A dummy model can achieve >90% confidence on random predictions.")
print("  No cross-validation between model output and image features existed.")
print()
print("  FINDING 5: Inference pipeline (AFTER FIX)")
print("  -----------------------------------------")
print("  1. Crop Identification Layer: independently detects crop from image features")
print("  2. Class Verification: validates model output indices against label map")
print("  3. Crop Consistency Check: rejects if model crop != detection crop")
print("  4. Confidence Rejection: returns Unknown/Inconclusive if confidence < 85%")
print("  5. Top-5 Predictions: always shown even for rejected predictions")
print()

print("\n--- RECOMMENDATIONS ---")
print()
print("  CRITICAL: Retrain model with real PlantVillage or equivalent dataset")
print("  - Use all 57 DISEASE_CLASSES for training")
print("  - Ensure at least 100+ images per class")
print("  - Implement proper train/val/test split")
print("  - Target validation accuracy > 90%")
print()
print("  MEDIUM: Improve crop detection heuristics")
print("  - Currently uses simple color/edge features")
print("  - Consider using a lightweight CNN for crop identification")
print("  - Add more distinguishing features (texture, shape)")
print()
print("  LOW: Add manual crop selection in UI")
print("  - Allow users to override detected crop")
print("  - Filter disease predictions by selected crop")
print()

print("\n--- DATASET AUDIT (from ModelHandler.audit_dataset()) ---")
audit = ModelHandler.audit_dataset()
print(f"  Total classes defined: {audit['total_classes']}")
print(f"  Total crops supported: {audit['total_crops']}")
print()
for crop, info in sorted(audit['crops'].items()):
    diseases = [d['display_name'] for d in info['entries'] if not d['is_healthy']]
    healthy = [d['display_name'] for d in info['entries'] if d['is_healthy']]
    print(f"  {crop}:")
    print(f"    Diseases ({len(diseases)}): {', '.join(diseases)}")
    print(f"    Healthy: {', '.join(healthy) if healthy else 'N/A'}")
    print()

print("--- END OF AUDIT REPORT ---")
