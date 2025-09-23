# -*- coding: utf-8 -*-
"""
Created on Tue May 21 14:34:16 2024

@author: eya
"""

import numpy as np
import pandas as pd
import mysql.connector
import sqlalchemy
import time
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

# Configuration
power_threshold = 1000.0  # Seuil de puissance pour détecter un arrêt (par exemple, en watts)
alert_interval = 1.5  # Facteur multiplicatif pour déclencher une alerte
intervalle_temps = 1  # Intervalle de temps entre les mesures (en secondes)
stop_times = []
last_stop_time = None
arrets_duree = []
defaillance = 0

# Récupérer la puissance actuelle depuis la base de données
for i in range(10):
    print(f"Iteration {i + 1}")
    
    # Récupérer la puissance actuelle depuis la base de données
    query = "SELECT puissance FROM sensor ORDER BY ttime DESC LIMIT 1"
    result = pd.read_sql(query, engine)
    if not result.empty:
        current_power = result.iloc[0]['puissance']
        print(f"Current power: {current_power}")
    else:
        print("No power data available.")
        continue  # Passer à l'itération suivante si aucune donnée n'est disponible

    # Vérifier si la puissance est en dessous du seuil
    if current_power < power_threshold:
        print(f"Power {current_power} is below threshold {power_threshold}.")
        current_time = time.time()
        if last_stop_time is not None:
            interval = current_time - last_stop_time
            stop_times.append(interval)
            stop_times = stop_times[-10:]  # Garder seulement les 10 derniers intervalles
            print(f"Stop detected. Interval: {interval:.2f} seconds.")
        last_stop_time = current_time
    else:
        print(f"Power {current_power} is above threshold {power_threshold}.")

    # Calculer l'intervalle moyen entre les arrêts
    if len(stop_times) >= 2:
        average_interval = np.mean(stop_times)
        print(f"Average interval: {average_interval:.2f} seconds.")

        # Vérifier s'il y a une alerte
        if (time.time() - last_stop_time) > alert_interval * average_interval:
            print("Alerte: L'intervalle entre les arrêts est plus long que d'habitude!")
"""
# Récupérer toutes les données de puissance pour analyse
query = "SELECT puissance FROM sensor"
data = pd.read_sql(query, engine)
puissance = data['puissance']

# Analyser les variations de puissance
variations_puissance = np.diff(puissance)
arrets = 0
for variation in variations_puissance:
    if variation <= 0:
        arrets += 1
    else:
        if arrets > 0:
            arrets_duree.append(arrets * intervalle_temps)
            if arrets >= 6:  # Si plus de 6 arrêts, déclencher une défaillance
                defaillance += 1
        arrets = 0

# Afficher la durée des arrêts
print("Durée des arrêts (en intervalles de temps):", arrets_duree)

# Calculer le pourcentage de défaillance
if len(arrets_duree) > 0:
    pourcentage_defaillance = (defaillance / len(arrets_duree)) * 100
else:
    pourcentage_defaillance = 0
print("Pourcentage de défaillance:", pourcentage_defaillance, "%")

# Détection du prochain arrêt
prochain_arret = 0
for variation in variations_puissance:
    if variation <= 0:
        prochain_arret += 1
    else:
        break

# Affichage du prochain arrêt
print("Prochain arrêt détecté après", prochain_arret, "intervalles de temps")

# Vérification s'il y a une alerte pour un prochain arrêt
if prochain_arret > 7:
    print("Attention prochain arrêt dans trop de temps")

# Visualisation des résultats
plt.figure(figsize=(10, 6))
plt.plot(puissance, label='Puissance')
plt.xlabel('Temps')
plt.ylabel('Puissance')
plt.title('Variation de la puissance au cours du temps')
plt.legend()
plt.show()
"""