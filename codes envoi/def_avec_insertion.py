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
from sqlalchemy import Table, Column, Integer, Float, MetaData
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
metadata = MetaData()

# Définir les tables
etat_table = Table(
    'etat', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('timestamp', Float, nullable=False),
    Column('etat', Integer, nullable=False)
)

defaillance_table = Table(
    'defaillance', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('timestamp', Float, nullable=False),
    Column('pourcentage', Float, nullable=False)
)

# Créer les tables dans la base de données
metadata.create_all(engine)

# Récupérer les données de la table depuis la base de données
query = "SELECT * FROM sensor"
data = pd.read_sql(query, engine)

# Configuration
power_threshold = 10.0  # Seuil de puissance pour détecter un arrêt (par exemple, en watts)
alert_interval = 1.5    # Facteur multiplicatif pour déclencher une alerte
intervalle_temps = 1    # Intervalle de temps entre les mesures (en secondes)
max_time_without_stop = 200  # Temps maximum sans arrêt avant alerte (en secondes)
stop_times = []
last_stop_time = None
arrets_duree = []
defaillance = 0

for _ in range(2):
    # Récupérer la puissance actuelle depuis la base de données
    query = "SELECT puissance FROM sensor ORDER BY ttime DESC LIMIT 1"
    result = pd.read_sql(query, engine)
    current_time = time.time()
    
    if not result.empty:
        current_power = result.iloc[0]['puissance']
        print(f"puissance actuelle: {current_power}")

        # Insérer l'état de la machine dans la table 'etat'
        if current_power < power_threshold:
            print("La machine est en arret")
            etat_value = 0
        else:
            print("La machine est en marche")
            etat_value = 1

        insert_etat = etat_table.insert().values(timestamp=current_time, etat=etat_value)
        with engine.connect() as connection:
            connection.execute(insert_etat)
    else:
        print("No power data available.")
        continue  # Passer à la prochaine itération si aucune donnée n'est disponible

    # Vérifier si la puissance est en dessous du seuil
    if current_power < power_threshold:
        current_time = time.time()
        if last_stop_time is not None:
            interval = current_time - last_stop_time
            stop_times.append(interval)
            stop_times = stop_times[-10:]  # Garder seulement les 10 derniers intervalles
            print(f"Stop detected: {interval:.2f} secondes.")
        last_stop_time = current_time

    # Calculer l'intervalle moyen entre les arrêts
    if len(stop_times) >= 1:
        average_interval = np.mean(stop_times)
        print(f"Average interval: {average_interval:.2f} secondes.")
        
        # Vérifier s'il y a une alerte basée sur l'intervalle moyen
        time_since_last_stop = time.time() - last_stop_time
        print("Dernier arret depuis:", time_since_last_stop, " secondes.")
        
        if time_since_last_stop > alert_interval * average_interval:
            print("Alerte: L'intervalle entre les arrêts est plus long que d'habitude!")

    # Vérifier s'il n'y a pas eu d'arrêt pendant trop longtemps
    if last_stop_time is not None and (time.time() - last_stop_time) > max_time_without_stop:
        print("Alerte: Aucun arrêt détecté pendant une période prolongée!")

puissance = data['puissance']
    
# Analyser les variations de puissance
variations_puissance = np.diff(puissance)
arrets = 0
total_arrets = 0  # Total des arrêts

for variation in variations_puissance:
    if variation <= 0:
        arrets += 1
    else:
        if arrets > 0:
            total_arrets += 1
            arrets_duree.append(arrets * intervalle_temps)
            if arrets >= 6:  # Si plus de 6 intervalles, considérer comme une défaillance
                defaillance += 1
        arrets = 0

# Inclure le dernier arrêt s'il y a un arrêt en cours à la fin des données
if arrets > 0:
    total_arrets += 1
    arrets_duree.append(arrets * intervalle_temps)
    if arrets >= 6:
        defaillance += 1

# Calculer le pourcentage de défaillance
if total_arrets > 0:
    pourcentage_defaillance = (defaillance / total_arrets) * 100
else:
    pourcentage_defaillance = 0

print("Pourcentage de défaillance:", pourcentage_defaillance, "%")

# Insérer le pourcentage de défaillance dans la table 'defaillance'
insert_defaillance = defaillance_table.insert().values(timestamp=current_time, pourcentage=pourcentage_defaillance)
with engine.connect() as connection:
    connection.execute(insert_defaillance)

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
