# -*- coding: utf-8 -*-
"""
Created on Sun May 12 18:31:31 2024

@author: eya
"""

import numpy as np
import pandas as pd
import sqlalchemy
import mysql.connector
from hmmlearn import hmm
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt


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
courant = data['courant']
# Normalisation des données
scaler = MinMaxScaler()
puissance_norm = scaler.fit_transform(puissance.reshape(-1, 1))

# Définition du modèle HMM avec 2 états (marche/arrêt)
model = hmm.GaussianHMM(n_components=2, covariance_type="full")

# Entraînement du modèle sur les données de puissance
model.fit(puissance_norm)

# Prédiction des états pour les données de puissance
etats_pred = model.predict(puissance_norm)




# Définir les états en fonction du courant
etats = np.where(courant == 0, 0, 1)

# Évaluation des performances du modèle
accuracy = np.mean(etats_pred == etats)
print("Accuracy:", accuracy)


# Prédiction de l'état futur à partir des données de puissance actuelles
proba_etat_futur = model.predict_proba(puissance_norm.reshape(1, -1))
print("Proba état futur:", proba_etat_futur)

# Visualisation des résultats
plt.figure(figsize=(10, 6))
plt.plot(puissance, label='Puissance')
plt.plot(etats_pred, label='États prédits', linestyle='--')
plt.xlabel('Temps')
plt.ylabel('Valeur')
plt.title('Prédiction des états avec HMM')
plt.legend()
plt.show()
