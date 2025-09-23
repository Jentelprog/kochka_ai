# -*- coding: utf-8 -*-
"""
Created on Thu May 16 12:51:22 2024

@author: eya
"""

import numpy as np
import pandas as pd
import sqlalchemy
import mysql.connector
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import tensorflow as tf

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
puissance = data['puissance'].values

# Normalisation des données
scaler = MinMaxScaler(feature_range=(0, 1))
puissance = scaler.fit_transform(puissance.reshape(-1, 1)).reshape(-1)

# Préparation des données pour le modèle LSTM
sequence_length = 10  # Longueur de la séquence temporelle
X, y = [], []
for i in range(len(puissance) - sequence_length):
    X.append(puissance[i:i+sequence_length])
    y.append(puissance[i+sequence_length])

X = np.array(X)
y = np.array(y)

# Division des données en ensembles d'entraînement et de test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Redimensionnement pour être compatible avec l'entrée LSTM (nombre d'échantillons, longueur de la séquence, nombre de caractéristiques)
X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))

# Création du modèle LSTM
model = tf.keras.Sequential()
model.add(tf.keras.layers.LSTM(50, input_shape=(X_train.shape[1], 1)))
model.add(tf.keras.layers.Dense(1))
model.compile(optimizer='adam', loss='mse')

# Entraînement du modèle
model.fit(X_train, y_train, epochs=100, batch_size=32, verbose=1)

# Évaluation du modèle
loss = model.evaluate(X_test, y_test, verbose=0)
print("Loss:", loss)

# Prédiction pour le prochain intervalle de temps
prochaine_prediction_arret = model.predict(np.array([X_test[-1]]))