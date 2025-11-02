# 🛩️ Aircraft Detection & Analysis AI

Projet étudiant complet de **détection et d’analyse d’aéronefs en temps réel** à l’aide d’un modèle **YOLOv8** pour la détection visuelle et d’un modèle **Groq (LLaMA 3.1)** pour l’analyse automatique de l’appareil détecté.  
L’application est intégrée dans une **interface web Flask**, permettant de visualiser la caméra en direct, les résultats de détection, et les analyses IA détaillées.

---

## 🚀 Fonctionnalités principales

- 🎥 **Flux vidéo en direct** (webcam ou caméra RTSP)  
- 🤖 **Détection d’aéronefs** via **YOLOv8 personnalisé**  
- 🧠 **Analyse IA du modèle détecté** (Groq / LLaMA)  
- 🗂️ **Affichage dynamique** : type, rôle, origine et description  
- 🔁 **Mise à jour automatique** (polling AJAX toutes les 2.5s)  
- 🧩 **Réinitialisation des détections**  
- 🌐 **Interface web responsive** (HTML / CSS / Bootstrap)

---

## 🏗️ Architecture du projet

```plaintext
Aircraft_detection/
├── app/
│   ├── app.py                    # Application Flask principale
│   ├── fonctions.py              # Fonctions de détection et d’analyse
│   ├── templates/
│   │   └── index.html            # Interface principale
│   └── static/
│       ├── style.css             # Styles personnalisés
│       └── script.js             # Logique côté client (JavaScript)
│
├── models/
│   └── best_aircraft_yolo11s.pt  # Modèle YOLO entraîné
│
├── Aircraft_Dataset/
│   └── data.yaml                 # Fichier de configuration du dataset
│
├── requirements.txt              # Dépendances Python
├── Dockerfile                    # Image Docker pour le déploiement
├── docker-compose.yml            # Configuration multi-conteneurs
└── README.md                     # Documentation du projet


## ⚙️ Installation et configuration
1️⃣ **Cloner le dépôt**
```bash
git clone https://github.com/SowOuma/Aircraft_detection.git
cd Aircraft_detection
```

2️⃣ **Créer un environnement virtuel (recommandé)**
```bash
python -m venv venv
venv\Scripts\activate   # sous Windows
# ou
source venv/bin/activate   # sous Linux/Mac
```

3️⃣ **Installer les dépendances**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

4️⃣ **(Optionnel) Définir la clé API Groq**

Crée un fichier `.env` à la racine :

```env
GROQ_API_KEY=ta_cle_api_groq
```

💡 *Sinon, tu peux définir la clé directement dans ton script Flask (déjà prévu par défaut).*

---

## 🧠 Entraînement du modèle YOLO

Si tu veux réentraîner le modèle :

```python
from ultralytics import YOLO

model = YOLO('yolo11.pt')  # ou un autre modèle
model.train(
    data='Aircraft_Dataset/data.yaml',
    epochs=50,
    imgsz=640,
    name='aircraft_yolo_train'
)
```

### 🔍 Évaluation du modèle
```python
metrics = model.val(data='Aircraft_Dataset/data.yaml')
print(metrics)
```

**Principales métriques :**
- **Precision (P)** : taux de vraies détections parmi les positives  
- **Recall (R)** : taux de détections correctes parmi les vrais objets  
- **mAP50 / mAP50-95** : mesure globale de performance du modèle

---

## 🧩 Lancement de l’application

### 🖥️ En local
```bash
python app/app.py
```

Puis ouvre ton navigateur à l’adresse :  
👉 [http://127.0.0.1:5000](http://127.0.0.1:5000)

### 🐳 Avec Docker
```bash
docker-compose up --build
```

L’application sera accessible sur :  
👉 [http://localhost:5000](http://localhost:5000)

---

## 🎯 Utilisation

Dans la barre supérieure, saisis la source caméra (ex: `0` pour webcam locale ou une URL RTSP).  
Clique sur **“Envoyer”** ou sur le bouton **“Camera1”**.  

Observe la détection temps réel :
- Les avions détectés apparaissent avec un cadre vert et le nom du modèle.  
- Consulte à droite : le type, rôle, origine et description de l’appareil.  
- L’analyse IA générée par **Groq (LLaMA 3.1)**.

---

## 📊 Exemple de sortie IA

**Détection :** `F117 (0.92)`

**Analyse IA :**
```
Rôle et caractéristiques :
L’avion F-117 Nighthawk est un appareil furtif conçu pour les missions d’attaque de précision.

Faits notables :
- Pays d’origine : États-Unis
- Mission principale : attaque furtive nocturne
- Époque : service actif entre 1983 et 2008

Note : modèle emblématique de la guerre du Golfe.
```

---

## 🧩 Technologies utilisées
| Domaine | Technologie |
|----------|--------------|
| IA / Vision | YOLO11 (Ultralytics) |
| IA / LLM | Groq (LLaMA 3.1) |
| Backend | Flask |
| Frontend | HTML, CSS, JavaScript, Bootstrap |
| Conteneurisation | Docker, Docker Compose |

---




## 📌 Notes
En cas d’erreur `Groq model_decommissioned`, consulte la doc Groq :  
👉 [https://console.groq.com/docs/deprecations](https://console.groq.com/docs/deprecations)

Si la page “infos IA” n’affiche rien, vérifie :
- que le flux caméra fonctionne  
- que YOLO détecte bien (✅ ex: `Détection: F117 (0.93)` dans la console)  
- que la route `/last_detection` renvoie bien des données JSON  


