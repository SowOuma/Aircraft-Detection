FROM python:3.10-slim

WORKDIR /app

# Dépendances système pour OpenCV, etc.
RUN apt-get update && apt-get install -y libgl1 libglib2.0-0 ffmpeg && rm -rf /var/lib/apt/lists/*

# Copie tout le projet
COPY . /app

# Installation des dépendances Python
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Port exposé
EXPOSE 5000

# ✅ Lancer le vrai fichier Flask
CMD ["python", "app/app.py"]
