# -*- coding: utf-8 -*-
"""
Created on Tue May 21 12:44:46 2024

@author: eya
"""

import numpy as np
import pandas as pd
import mysql.connector
import sqlalchemy
import time


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



class MachineMonitor:
    def __init__(self, power_threshold, alert_interval):
        self.power_threshold = power_threshold
        self.alert_interval = alert_interval
        self.stop_times = []
        self.last_stop_time = None

    def check_power(self, current_power):
        """Check the current power and update stop times if a stop is detected.""" 
        if current_power < self.power_threshold:
            current_time = time.time()
            if self.last_stop_time is not None:
                interval = current_time - self.last_stop_time
                self.stop_times.append(interval)
                self.stop_times = self.stop_times[-10:]  # Keep only the last 10 intervals
            self.last_stop_time = current_time

    def get_average_interval(self):
        """Calculate the average interval between stops."""
        if len(self.stop_times) < 2:
            return None
        return np.mean(self.stop_times)

    def check_for_alert(self):
        """Check if the current interval is longer than the average and alert if needed."""
        if len(self.stop_times) < 2:
            return None
        average_interval = self.get_average_interval()
        if average_interval is not None and (time.time() - self.last_stop_time) > self.alert_interval * average_interval:
            print("Alerte: L'intervalle entre les arrêts est plus long que d'habitude!")

# Configuration
power_threshold = 10.0  # Seuil de puissance pour détecter un arrêt (par exemple, en watts)
alert_interval = 1.5    # Facteur multiplicatif pour déclencher une alerte

# Création de l'objet de surveillance
monitor = MachineMonitor(power_threshold, alert_interval)

# Simuler la lecture de la puissance de la machine (à remplacer par votre propre méthode de lecture)
def get_current_power():
    """Retrieve the latest power reading from the database."""
    query = "SELECT puissance FROM sensor ORDER BY ttime DESC LIMIT 1"
    result = pd.read_sql(query, engine)
    if not result.empty:
        return result.iloc[0]['puissance']
    return None


# Boucle de surveillance (à exécuter dans un thread séparé ou de manière asynchrone dans une vraie application)

current_power = get_current_power()
print(current_power)
if current_power is not None:
        monitor.check_power(current_power)
        monitor.check_for_alert()
else:
  print("No power data available.")
  time.sleep(1)  # Attendre 1 seconde avant de lire à nouveau la puissance (ajuster selon vos besoins)
