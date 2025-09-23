# -*- coding: utf-8 -*-
"""
Created on Sun May 12 19:01:56 2024

@author: eya
"""


import numpy as np
import pandas as pd
import sqlalchemy
import mysql.connector
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt


# Établir la connexion à la base de données
conn = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="Ilyes/148639527",
    database="optinergie"
)

# Créer la chaîne de connexion SQLAlchemy
conn_str = 'mysql+mysqlconnector://root:Ilyes/148639527@localhost/optinergie'

# Créer le moteur SQLAlchemy
engine = sqlalchemy.create_engine(conn_str)

# Récupérer les données de la table depuis la base de données
query = "SELECT * FROM sensor"
data = pd.read_sql(query, engine)

# Chargement des données de puissance
puissance = data['puissance']
courant = data['courant']

# Simple prédiction d'état basée sur la moyenne de la puissance
seuil = np.mean(puissance)

# Prédiction d'état
etats_pred = np.where(puissance > seuil, 1, 0)

# Évaluation de l'exactitude
accuracy = np.mean(etats_pred == courant)
print("Accuracy:", accuracy)

# Visualisation des résultats
plt.figure(figsize=(10, 6))
# plt.plot(puissance, label='Puissance')
plt.plot(courant, label='État réel', linestyle='--')
plt.plot(etats_pred, label='États prédits', linestyle='-.')
plt.xlabel('Temps')
plt.ylabel('Valeur')
plt.title('Prédiction des états')
plt.legend()
plt.show()
