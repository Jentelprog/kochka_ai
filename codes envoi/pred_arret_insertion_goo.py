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

# Créer la table 'predictions' si elle n'existe pas
create_table_query = """
CREATE TABLE IF NOT EXISTS predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    etat INT,
    predicted_time_to_next_stop FLOAT
)
"""
with engine.connect() as conn_engine:
    conn_engine.execute(create_table_query)

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

# Faire une prédiction pour le prochain arrêt basé sur les derniers arrêts
last_sequence = stop_intervals[-sequence_length:].values.reshape(1, -1)
predicted_time_to_next_stop = model.predict(last_sequence)
predicted_time_to_next_stop_minute = (predicted_time_to_next_stop / 60)

print(f'Un arret en theorie apres: {predicted_time_to_next_stop[0]} secondes')
print(f'En minute= {predicted_time_to_next_stop_minute[0]} ')

# Convertir predicted_time_to_next_stop en un objet timedelta
time_to_wait = datetime.timedelta(seconds=float(predicted_time_to_next_stop[0]))

# Attendre le temps prédit jusqu'au prochain arrêt
time.sleep(time_to_wait.total_seconds())

etat_courant_query = "SELECT courant FROM sensor ORDER BY ttime DESC LIMIT 1"
etat_courant_data = pd.read_sql(etat_courant_query, engine)

# Extraire la valeur de l'état du courant à partir du DataFrame retourné par la requête
etat_courant = etat_courant_data['courant'].iloc[0]
if etat_courant <= power_threshold:
    etat = 0
else:
    etat = 1
print("courant=", etat_courant, "means", etat)

# Enregistrer les valeurs dans la table predictions
insert_query = """
INSERT INTO predictions (etat, predicted_time_to_next_stop) VALUES (%s, %s)
"""
cursor = conn.cursor()
cursor.execute(insert_query, (etat, float(predicted_time_to_next_stop[0])))
conn.commit()

# Fermer le curseur et la connexion
cursor.close()
conn.close()

