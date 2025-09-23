# -*- coding: utf-8 -*-
"""
Created on Thu May 16 12:22:42 2024

@author: eya
"""

import numpy as np
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import sqlalchemy
from scipy.optimize import minimize

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


consommation = data['energie'].astype(float)


# Fonction objectif
def fonction_objectif(x):
    return np.sum(x * consommation)

# Contraintes
def contraintes(x):
    # Vérifier les temps d'arrêt
    arret = 0
    rb = 0
    for i in range(len(x)):
        if x[i] == 0:
            arret += 1
        else:
            if arret > 10:
                rb += 1
            arret = 0
    
    # Contrainte de temps d'arrêt maximal
    if arret > 10:
        rb += 1
    
    # Contrainte de consommation maximale
    return np.array([np.sum(x) - 1000, -rb])

# Bornes des paramètres
bound = [(0, 1)] * len(consommation)

# Point de départ initial
x0 = np.ones(len(consommation))

# Optimisation
resultat = minimize(fonction_objectif, x0, bounds=bound, constraints={'type': 'ineq', 'fun': contraintes})
"""
# Affichage du résultat
print("Consommation optimale :", resultat.x)
print("Récompense rb :", -resultat.fun[1])"""