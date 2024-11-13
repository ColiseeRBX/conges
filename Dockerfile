# Utiliser l'image Python officielle
FROM python:3.9-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de l'application dans le conteneur
COPY . /app

# Installer les dépendances
RUN pip install -r requirements.txt

# Exposer le port 5000 pour Flask
EXPOSE 6000

# Lancer l'application
CMD ["python", "app.py"]
