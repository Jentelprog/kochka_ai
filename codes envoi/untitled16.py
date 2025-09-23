# -*- coding: utf-8 -*-
"""
Created on Sun May 12 18:12:30 2024

@author: eya
"""
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sqlalchemy
import mysql.connector
from sklearn.metrics import precision_score, recall_score, f1_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split


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
data = pd.read_sql(query, engine)
# Chargement des données de puissance
puissance = data['puissance']

# Conversion en états 0/1
seuil = 0.05 * max(puissance)
etats = [1 if p > seuil else 0 for p in puissance]

# Split train/test
X_train, X_test, y_train, y_test = train_test_split(puissance, etats, test_size=0.2)

def puissance_moyenne(data, index, window_size):
    start_index = max(0, index - window_size)
    end_index = min(len(data), index + window_size)
    return np.mean(data[start_index:end_index])

# Création des features
window_size = 5 # minutes
X_train_features = [puissance_moyenne(X_train, i, window_size) for i in range(len(X_train))]
X_test_features = [puissance_moyenne(X_test, i, window_size) for i in range(len(X_test))]
X_train_features = np.array(X_train_features).reshape(-1, 1)  # Garder la deuxième dimension pour chaque fenêtre
X_test_features = np.array(X_test_features).reshape(-1, 1)  # Garder la deuxième dimension pour chaque fenêtre

# Entraînement du modèle
model = DecisionTreeClassifier()
model.fit(X_train_features, y_train)

# Évaluation sur le test
y_pred = model.predict(X_test_features)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
# Affichage de la courbe de consommation avec l'ensemble de test en pointillés
plt.plot(X_test.index, X_test, linestyle='dotted', label='Consommation (test set)')

# Affichage des prédictions en rouge
plt.plot(X_test.index, y_pred, color='red', label='Prédictions')

plt.xlabel('Index des échantillons')
plt.ylabel('Puissance')
plt.title('Prédictions de la consommation')
plt.legend()
plt.show()