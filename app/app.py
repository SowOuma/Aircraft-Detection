from flask import Flask, Response, render_template, request, jsonify, url_for 
import cv2
import os
from torch.hub import load as hub_load
import numpy as np
from ultralytics import YOLO

app = Flask(__name__)

# Initialisation des variables globales
camera1_url = None#"rtsp://169.254.197.98:554/media/video1"
camera2_url =None
camera = None
camera1 = None
points_camera1 = []
points_camera2 = []

# Chargement du modèle YOLOv8 pré-entraîné
#model = YOLO("yolov8n.pt")

# --- ÉTAT PARTAGÉ POUR LA DERNIÈRE DÉTECTION ---
latest_detection = {
    "class": None,
    "confidence": None,
    "bbox": None  # (x1, y1, x2, y2)
}

model = YOLO("best_aircraft_yolo11s.pt")
print("Model loaded ✅")
model.eval()


#definition du route principale 
@app.route("/")


#appelle de la appelle page html pour son affichage 

@app.route("/App")
def home1():
    return render_template('index.html')



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

        # 2. Si on a détecté quelque chose
        if boxes is not None and len(boxes) > 0:
            for box, conf, cls in zip(boxes.xyxy, boxes.conf, boxes.cls):
                x1, y1, x2, y2 = map(int, box.tolist())
                conf = float(conf)
                cls = int(cls)
                # ... dans la boucle for des détections ...
                name = result.names.get(cls, f"class_{cls}")

                # mise à jour de l'état global
                latest_detection["class"] = name
                latest_detection["confidence"] = round(conf, 3)
                latest_detection["bbox"] = [x1, y1, x2, y2]


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


        # 5. Encoder l'image annotée pour l'envoyer au navigateur
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        compteur += 1

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' +
               frame_bytes +
               b'\r\n')


@app.route('/recuperer_source', methods=['POST'])
def recuperer_source():
    global camera1_url, camera2_url, camera, camera1
    data = request.json
    try:
        if not data:
            return jsonify({'error': 'Aucune donnée reçue'}), 400
        """"
        if 'camera1_url' not in data or 'camera2_url' not in data:
            return jsonify({'error': 'Les URLs des deux caméras doivent être fournies'}), 400
        """
        camera1_url = data.get('camera1_url')
        
        
        print(f"URL de la caméra 1 : {camera1_url}")
      
        
        # Libération des caméras précédemment ouvertes

        if camera is not None:
            camera.release()
        


        def captureVideo(url):
            if url.startswith("rtsp://"):
                capture=cv2.VideoCapture(url)
                capture.set(cv2.CAP_PROP_BUFFERSIZE,2)
                
                return capture
            elif(url=='0'):
                return cv2.VideoCapture(0)
            else:

                return cv2.VideoCapture(url)
    
        camera = captureVideo(camera1_url)
        
        
        # Vérification si les caméras ont été ouvertes avec succès
        if not camera.isOpened():
            camera = None
            print(f"Échec de l'ouverture de la caméra avec l'URL {camera1_url}")
            return jsonify({'error': f'Échec de l\'ouverture de la caméra avec l\'URL {camera1_url}'}), 500
        
        return jsonify({'message': 'Flux démarrés avec succès'})
    except Exception as e:
        print(f"Erreur lors de la recuperation des urls: {str(e)}")   
     



@app.route("/video")
def video():
    if camera is None:
        return "Camera 1 non initialisée", 500
    return Response(generation_video(camera), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/cliquer_bouton", methods=["POST"])
def cliquer_bouton():
    button = request.form.get("button")
    if button == "camera1":
        url = url_for("video", _external=True)  
    elif button == "camera2":
        url = url_for("video1", _external=True) 
    else:
        url = None

    if url:
        return jsonify({"url": url})
    else:
        return jsonify({"error": "Flux vidéo non disponible"}), 400
    

@app.route("/last_detection", methods=["GET"])
def last_detection():
    return jsonify(latest_detection)


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0', port=5000)
