# -*- coding: utf-8 -*-
"""
Created on Wed May 15 17:52:36 2024

@author: eya
"""

# Import des bibliothèques nécessaires
import numpy as np
import pandas as pd
import sqlalchemy
import mysql.connector
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Établir la connexion à la base de données
conn = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="Azerty1234",
    database="testt"
)

# Créer la chaîne de connexion SQLAlchemy
conn_str = 'mysql+mysqlconnector://root:Azerty1234@localhost/testt'

# Créer le moteur SQLAlchemy
engine = sqlalchemy.create_engine(conn_str)

# Récupérer les données de la table depuis la base de données
query = "SELECT * FROM sensor"
# Charger les données
data = pd.read_sql(query, engine)

# Prétraitement des données, création des caractéristiques, et étiquetage des données
# (Supposons que vous avez déjà effectué ces étapes)
# Définir un seuil de puissance pour détecter les arrêts
seuil_puissance = 10  # À ajuster selon vos données

# Définir l'intervalle de temps pour la détection des arrêts (par exemple, 1 heure)
intervalle_temps = 3600  # en secondes

# Créer une liste pour stocker les étiquettes des arrêts
arrets = []

# Parcourir les données par intervalles de temps
for i in range(0, len(data), intervalle_temps):
    # Extraire la puissance pour cet intervalle
    puissance_interval = data['puissance'][i:i+intervalle_temps]
    # Vérifier si la puissance est inférieure au seuil pendant cet intervalle
    if puissance_interval.min() < seuil_puissance:
        arrets.append(1)  # Marquer cet intervalle comme un arrêt
    else:
        arrets.append(0)  # Pas d'arrêt dans cet intervalle

# S'assurer que la liste des arrêts a la même longueur que l'index du DataFrame
arrets += [0] * (len(data) - len(arrets))
# Créer une nouvelle colonne dans le DataFrame pour stocker les étiquettes des arrêts
data['arret'] = arrets

# Séparation des données en features (X) et target (y)
X = data[['puissance']]  # Caractéristiques pertinentes pour la détection des arrêts
y = data['arret']  # Variable cible indiquant si un arrêt s'est produit (1) ou non (0) dans l'intervalle de temps

# Division des données en ensembles d'entraînement et de test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Choix et entraînement du modèle
model = RandomForestClassifier()
model.fit(X_train, y_train)

# Évaluation du modèle
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print("Accuracy:", accuracy)

# Prédiction pour le prochain intervalle de temps
prochaine_prediction_arret = model.predict(data['puissance'])
