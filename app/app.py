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
model = YOLO("yolov8n.pt")
model.eval()


#definition du route principale 
@app.route("/")


#appelle de la appelle page html pour son affichage 

@app.route("/App")
def home1():
    return render_template('index.html')



def generation_video(camera):
    compteur = 0
    # Assurez-vous que le répertoire "captures" existe
    os.makedirs("captures", exist_ok=True)
    capture=False
    

    while True:
        success, frame = camera.read()

        if not success:
            break

        # Application du modèle YOLOv5
        results = model(frame)  # Faire des prédictions
        

                
        # Encoder l'image pour l'afficher
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        compteur += 1
        

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')



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
    



if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0', port=5000)
