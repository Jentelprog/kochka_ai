# -*- coding: utf-8 -*-
"""
Created on Sun May 12 17:38:15 2024

@author: eya
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

# Charger les données
# Supposons que vous avez un DataFrame 'data' avec une colonne 'puissance' contenant les valeurs de puissance
# Assurez-vous que votre DataFrame a une colonne de dates ou d'index temporel
# data = pd.read_csv('votre_fichier.csv', parse_dates=['timestamp'], index_col='timestamp')

# Par souci de simplicité, générons des données de puissance aléatoires pour l'exemple
np.random.seed(0)
dates = pd.date_range(start='2024-01-01', end='2024-05-01', freq='H')
power_values = np.random.normal(loc=100, scale=20, size=len(dates))
data = pd.DataFrame({'timestamp': dates, 'puissance': power_values})
data.set_index('timestamp', inplace=True)

# Normalisation des données
scaler = MinMaxScaler()
data['puissance_norm'] = scaler.fit_transform(data[['puissance']])

# Préparation des données pour l'entrainement
sequence_length = 24  # Longueur de la séquence d'entrée (par exemple, 24 heures)
X, y = [], []
for i in range(len(data) - sequence_length):
    X.append(data['puissance_norm'].iloc[i:i+sequence_length])
    y.append(data['puissance_norm'].iloc[i+sequence_length])
X = np.array(X)
y = np.array(y)

# Diviser les données en ensembles d'entraînement et de test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

# Créer le modèle LSTM
model = Sequential([
    LSTM(units=50, input_shape=(X.shape[1], 1)),
    Dense(units=1)
])

# Compiler le modèle
model.compile(optimizer='adam', loss='mean_squared_error')

# Entraîner le modèle
model.fit(X_train.reshape(-1, sequence_length, 1), y_train, epochs=50, batch_size=32, verbose=2)

# Évaluer le modèle
loss = model.evaluate(X_test.reshape(-1, sequence_length, 1), y_test)
print('Test Loss:', loss)

# Faire des prédictions
predictions = model.predict(X_test.reshape(-1, sequence_length, 1))
predictions = scaler.inverse_transform(predictions)  # Revenir à l'échelle originale des données

# Tracer les prédictions
plt.plot(predictions, label='Prédictions')
plt.plot(scaler.inverse_transform(y_test.reshape(-1, 1)), label='Valeurs réelles')
plt.legend()
plt.show()
