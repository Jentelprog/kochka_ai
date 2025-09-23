# -*- coding: utf-8 -*-
"""
Created on Sun May 12 20:04:51 2024

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

# Détection des variations de puissance
variations_puissance = np.diff(puissance)

# Compteur d'arrêts
arrets = 0

# Vérification des arrêts
for variation in variations_puissance:
    if variation <= 0:
        arrets += 1
    else:
        if arrets > 0:
            print("Arrêt détecté après", arrets, "intervalle(s) de temps")
        arrets = 0

# Vérification s'il n'y a pas eu d'arrêt après trois fois ces intervalles
defaillance = 0
if arrets > 0:
    print("Arrêt détecté après", arrets, "bcp de temps")
    if arrets >= 3:
        defaillance = 1
        
        
# Détection du prochain arrêt
prochain_arret = 0
for variation in variations_puissance:
    if variation <= 0:
        prochain_arret += 1
    else:
        break

# Affichage du prochain arrêt
print("Prochain arrêt détecté après", prochain_arret, "intervalles de temps")

# Vérification s'il y a une alerte
if prochain_arret > 10:
    print("Alerte : Prochain arrêt dans plus de 4 intervalles de temps")


# Visualisation des résultats
plt.figure(figsize=(10, 6))
plt.plot(puissance, label='Puissance')
plt.xlabel('Temps')
plt.ylabel('Puissance')
plt.title('Variation de la puissance au cours du temps')
plt.legend()
plt.show()

# Affichage de la variable "defaillance"
print("Variable de défaillance:", defaillance)
