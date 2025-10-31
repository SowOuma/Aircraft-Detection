from ultralytics import YOLO

# 1. Charger un modèle pré-entraîné comme base
model = YOLO("yolov8n.pt")  # tu peux mettre yolov8s.pt si tu veux un modèle plus gros

# 2. Lancer l'entraînement sur ton dataset Roboflow
results = model.train(
    data="C:/Users/SOW/Desktop/Projet/Aircraft_detection/data/data.yaml",  # chemin vers TON data.yaml
    epochs=50,              # tu peux mettre 5 pour tester rapide
    imgsz=640,              # taille d'image
)

print("Entraînement terminé ✅")
print("Les poids sont dans runs/detect/train/weights/best.pt")
