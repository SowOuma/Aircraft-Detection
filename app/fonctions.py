import cv2
from ultralytics import YOLO
from openai import OpenAI
import os





# Chargement du modèle YOLOv8 pré-entraîné
#model = YOLO("yolov8n.pt")

# --- ÉTAT PARTAGÉ POUR LA DERNIÈRE DÉTECTION ---
latest_detection = {
    "class": None,
    "confidence": None,
    "bbox": None  # (x1, y1, x2, y2)
}

model = YOLO(r"models\best_aircraft_yolo11s.pt")
print("Model loaded ✅")
model.eval()


def generation_video(camera):
    compteur = 0
    os.makedirs("captures", exist_ok=True)
    # éviter de sauver 1000 fois

    CLASS_NAMES = ['A10', 'B1', 'B52', 'C130', 'C5', 'F117', 'F15', 'F22', 'MQ9', 'Tu160', 'aircraft', 'jet']  # correspond à ton data.yaml

    while True:
        success, frame = camera.read()
        if not success:
            break

        # 1. Inférence YOLOv8 sur la frame
        results = model(frame)        # results = liste
        result = results[0]           # premier résultat (batch=1)
        boxes = result.boxes          # boîtes détectées
        # Reset léger si rien détecté (optionnel)
        updated_this_frame = False
        
        # 2. Si on a détecté quelque chose
        if boxes is not None and len(boxes) > 0:
            for box, conf, cls in zip(boxes.xyxy, boxes.conf, boxes.cls):
                x1, y1, x2, y2 = map(int, box.tolist())
                conf = float(conf)
                cls = int(cls)
                # ... dans la boucle for des détections ...
                name = result.names.get(cls, f"class_{cls}")


                # Label de la classe détectée
                label_text = f"{CLASS_NAMES[cls]} {conf:.2f}"

                # Couleur différente par classe (optionnel)
                color = (0, 255, 0)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(
                    frame,
                    label_text,
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    color,
                    2
                )

    
# MAJ de l'état global (prend la détection la + conf.)
                if (not updated_this_frame) or (conf > (latest_detection.get("confidence") or 0.0)):
                    latest_detection["class"] = name
                    latest_detection["confidence"] = round(conf, 3)
                    latest_detection["bbox"] = [x1, y1, x2, y2]
                    updated_this_frame = True 
                    
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' +
               frame_bytes +
               b'\r\n')








# === Configuration Groq ===
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or 

# Initialise le client Groq
client = OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")
def analyze_aircraft_with_groq(ac_class: str, confidence: float, context: str = "") -> str:
    """
    Analyse un avion détecté à l’aide de Groq (LLaMA 3.1-70B).
    """
    # --- 1️⃣ Cas spéciaux : classes trop génériques ---
    generic_classes = ["aircraft", "jet"]
    if ac_class.lower() in generic_classes:
        return (
            f"Classe détectée : {ac_class} (générique)\n"
            f"- Confiance : {confidence:.2f}\n"
            f"- Aucun modèle précis identifié.\n"
            f"- Suggéré : approchez l'appareil ou fournissez plus d’images pour identification.\n"
            f"Note : catégorie générale — pas d’analyse détaillée disponible."
        )

    # --- 2️⃣ Sinon, appel au LLM Groq ---
    try:
        prompt = f"""
Tu es un expert aéronautique militaire.
Analyse l'appareil {ac_class} et décris :
1) Une phrase courte sur son rôle et ses caractéristiques.
2) Jusqu’à 3 puces (- ...) avec faits notables (pays, mission, époque).
3) Une ligne "Note:" si incertain.

Confiance de détection : {confidence:.2f}
Contexte : {context or "aucun"}.
""".strip()

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Tu es un analyste militaire spécialisé en aéronautique. Réponds en français, de manière concise et structurée."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=300,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"⚠️ Erreur Groq: {str(e)}\nClasse: {ac_class}\nConfiance: {confidence:.2f}"

