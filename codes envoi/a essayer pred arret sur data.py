# -*- coding: utf-8 -*-
"""
Created on Sun May 26 17:42:54 2024

@author: eya
"""

import numpy as np
import pandas as pd
import mysql.connector
import sqlalchemy
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import time
import datetime

password = "Ilyes/148639527"

# Établir la connexion à la base de données
conn = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password=password,
    database="optinergie"
)

engine = sqlalchemy.create_engine(f"mysql+mysqlconnector://root:{password}@localhost/optinergie")


# Récupérer les données de la table depuis la base de données
query = "SELECT * FROM sensor"
data = pd.read_sql(query, engine)
data['ttime'] = pd.to_datetime(data['ttime'])

# Détecter les arrêts en fonction du courant
power_threshold = 0  # Exemple de seuil de courant pour détecter les arrêts
data['stop'] = (data['courant'] <= power_threshold).astype(int)

# Ajouter une colonne avec les intervalles de temps entre les arrêts
data['time_since_last_stop'] = (data['ttime'] - data['ttime'].shift()).fillna(pd.Timedelta(seconds=0)).dt.total_seconds()
data['time_to_next_stop'] = data['stop'][::-1].cumsum()[::-1].shift(-1, fill_value=0).astype(int)

# Filtrer les données pour obtenir les intervalles de temps entre les arrêts uniquement
stop_intervals = data[data['stop'] == 1]['time_since_last_stop'].reset_index(drop=True)

# Créer des séquences pour le modèle
sequence_length = 20  # Nombre de précédents arrêts utilisés pour prédire le prochain
X = []
y = []

for i in range(len(stop_intervals) - sequence_length):
    X.append(stop_intervals[i:i+sequence_length].values)
    y.append(stop_intervals[i+sequence_length])

X = np.array(X)
y = np.array(y)

# Diviser les données en ensembles d'entraînement et de test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Entraîner un modèle de régression (Random Forest Regressor dans cet exemple)
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Faire des prédictions sur l'ensemble de test
y_pred = model.predict(X_test)

# Évaluer le modèle
mse = mean_squared_error(y_test, y_pred)
print(f'Mean Squared Error: {mse}')

# Vérifier si la machine est en marche avant de faire une prédiction
etat_courant_query = "SELECT courant FROM sensor ORDER BY ttime DESC LIMIT 1"
etat_courant_data = pd.read_sql(etat_courant_query, engine)
etat_courant = etat_courant_data['courant'].iloc[0]

if etat_courant >= power_threshold:
    # Faire une prédiction pour le prochain arrêt basé sur les derniers arrêts
    last_sequence = stop_intervals[-sequence_length:].values.reshape(1, -1)
    predicted_time_to_next_stop = model.predict(last_sequence)
    predicted_time_to_next_stop_minute = predicted_time_to_next_stop / 60

    print(f'Un arret en theorie apres: {predicted_time_to_next_stop[0]} secondes')
    print(f'En minute= {predicted_time_to_next_stop_minute[0]} ')

    # Convertir predicted_time_to_next_stop en un objet timedelta
    time_to_wait = predicted_time_to_next_stop[0]

    # Boucle pour vérifier périodiquement l'état de la machine
    start_time = time.time()
    while time.time() - start_time < time_to_wait:
        etat_courant_data = pd.read_sql(etat_courant_query, engine)
        etat_courant = etat_courant_data['courant'].iloc[0]
        if etat_courant <= power_threshold:
            print("La machine s'est arrêtée.")
            break
        time.sleep(1)

    print(f"Arrêt théorique dans {time_to_wait} secondes.")
else:
    print("La machine est actuellement arrêtée.")


plt.figure(figsize=(10, 6))
plt.plot(stop_intervals.index, stop_intervals, label='Actual Intervals Between Stops', color='blue')
plt.axvline(x=len(stop_intervals), color='red', linestyle='--', label='Prediction Point')
plt.scatter(len(stop_intervals), predicted_time_to_next_stop, color='red', marker='x', s=100, label='Predicted Next Stop Interval')
plt.xlabel('Index')
plt.ylabel('Time Since Last Stop (seconds)')
plt.title('Prediction of Time Until Next Stop')
plt.legend()
plt.show()
