# -*- coding: utf-8 -*-
"""
Created on Tue May 21 14:30:48 2024

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
    password="Ilyes/148639527",
    database="optinergie"
)

# Connect to MySQL
password = "Ilyes/148639527"
# Créer le moteur SQLAlchemy
engine = sqlalchemy.create_engine(f"mysql+mysqlconnector://root:{password}@localhost/optinergie")


# Récupérer les données de la table depuis la base de données
query = "SELECT * FROM sensor"
data = pd.read_sql(query, engine)


class MachineMonitor:
    def __init__(self, power_threshold, alert_interval, intervalle_temps=1):
        self.power_threshold = power_threshold
        self.alert_interval = alert_interval
        self.intervalle_temps = intervalle_temps
        self.stop_times = []
        self.last_stop_time = None
        self.arrets_duree = []
        self.defaillance = 0

    def check_power(self, current_power):
        """Check the current power and update stop times if a stop is detected."""
        print(f"Checking power: {current_power}")
        if current_power < self.power_threshold:
            print(f"Power {current_power} is below threshold {self.power_threshold}.")
            current_time = time.time()
            if self.last_stop_time is not None:
                interval = current_time - self.last_stop_time
                self.stop_times.append(interval)
                self.stop_times = self.stop_times[-10:]  # Keep only the last 10 intervals
                print(f"Stop detected. Interval: {interval:.2f} seconds.")
            self.last_stop_time = current_time
        else:
            print(f"Power {current_power} is above threshold {self.power_threshold}.")

    def get_average_interval(self):
        """Calculate the average interval between stops."""
        if len(self.stop_times) < 2:
            print("Not enough stop times to calculate average interval.")
            return None
        average_interval = np.mean(self.stop_times)
        print(f"Average interval: {average_interval:.2f} seconds.")
        return average_interval

    def check_for_alert(self):
        """Check if the current interval is longer than the average and alert if needed."""
        if len(self.stop_times) < 2:
            return
        average_interval = self.get_average_interval()
        if average_interval is not None and (time.time() - self.last_stop_time) > self.alert_interval * average_interval:
            print("Alerte: L'intervalle entre les arrêts est plus long que d'habitude!")

    def detect_stops_and_failures(self, variations_puissance):
        """Detect stops and calculate durations and failures."""
        arrets = 0
        for variation in variations_puissance:
            if variation <= 0:
                arrets += 1
            else:
                if arrets > 0:
                    self.arrets_duree.append(arrets * self.intervalle_temps)
                    if arrets >= 6:  # If stops >= 6, trigger the failure
                        self.defaillance += 1
                arrets = 0

    def analyze_power(self, puissance):
        """Analyze power variations."""
        variations_puissance = np.diff(puissance)
        self.detect_stops_and_failures(variations_puissance)

        # Afficher la durée des arrêts
        print("Durée des arrêts (en intervalles de temps):", self.arrets_duree)

        # Calcul du pourcentage de défaillance
        if len(self.arrets_duree) > 0:
            pourcentage_defaillance = (self.defaillance / len(self.arrets_duree)) * 100
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

        # Vérification s'il y a une alerte
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


# Configuration
power_threshold = 10.0  # Seuil de puissance pour détecter un arrêt (par exemple, en watts)
alert_interval = 1.5    # Facteur multiplicatif pour déclencher une alerte

# Création de l'objet de surveillance
monitor = MachineMonitor(power_threshold, alert_interval)


def get_current_power():
    """Retrieve the latest power reading from the database."""
    query = "SELECT puissance FROM sensor ORDER BY ttime DESC LIMIT 1"
    result = pd.read_sql(query, engine)
    if not result.empty:
        power = result.iloc[0]['puissance']
        print(f"Current power: {power}")
        return power
    else:
        print("No power data available.")
    return None


def get_power_data():
    """Retrieve all power readings from the database."""
    query = "SELECT puissance FROM sensor"
    data = pd.read_sql(query, engine)
    return data['puissance']


# Boucle de surveillance (à exécuter dans un thread séparé ou de manière asynchrone dans une vraie application)
while True:
    current_power = get_current_power()
    if current_power is not None:
        monitor.check_power(current_power)
        monitor.check_for_alert()
    else:
        print("No power data available to check.")
    
    # Récupérer toutes les données de puissance pour analyse
    puissance = get_power_data()
    monitor.analyze_power(puissance)

    time.sleep(60)  # Attendre 60 secondes avant de lire à nouveau les données pour l'analyse (ajuster selon vos besoins)
