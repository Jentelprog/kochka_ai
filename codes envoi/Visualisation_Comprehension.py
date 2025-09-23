# -*- coding: utf-8 -*-
"""
Created on Wed May  8 11:45:19 2024

@author: eya
"""

import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import sqlalchemy
import seaborn as sns
import numpy as np
from matplotlib.dates import date2num

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



# convertir les dates en flot
x_values = date2num(data['ttime'])

# calcul de la régression linéaire
z = np.polyfit(x_values, data['puissance'], 3)
p = np.poly1d(z)
print("------------------------")
print(p)
print("------------------------")
# tracer la régression linéaire
plt.scatter(data['ttime'], data['puissance'])
plt.plot(data['ttime'], p(x_values), color='red')  # Régression linéaire
plt.xlabel('Time')
plt.ylabel('Puissance')
plt.title('Relation entre Time et Puissance avec régression linéaire')
plt.show()
###### exploration des données
# afichage des premières lignes 
print("Aperçu des données :")
print(data.head())
###### visualisation des données
#histogramme de la distribution d'une variable numérique
sns.histplot(data['puissance'])
plt.xlabel('ttime')
plt.ylabel('puissance')
plt.title('Distribution de la variable')
plt.show()
###### Analyse des statistiques descriptives
# Calcul des statistiques descriptives pour une variable numérique
mean = data['puissance'].mean()
std_dev = data['puissance'].std()
median = data['puissance'].median()
# Affichage des statistiques descriptives
print("\nStatistiques descriptives pour la variable 'variable' :")
print("Moyenne :", mean)
print("Écart-type :", std_dev)
print("Médiane :", median)

