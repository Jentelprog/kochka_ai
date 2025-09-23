# -*- coding: utf-8 -*-
"""
Created on Sun May 12 17:50:35 2024

@author: eya
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error

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

# Décomposer les données en ensembles d'entraînement et de test
train_size = int(len(data) * 0.8)
train, test = data.iloc[:train_size], data.iloc[train_size:]

# Entraîner le modèle ARIMA
model = ARIMA(train['puissance'], order=(2,0,10)) # Modifier l'ordre selon votre choix
model_fit = model.fit()

# Faire des prédictions
predictions = model_fit.forecast(steps=len(test))

# Calculer l'erreur quadratique moyenne (RMSE)
rmse = np.sqrt(mean_squared_error(test['puissance'], predictions))
print('Test RMSE:', rmse)

# Tracer les prédictions
plt.plot(test.index, predictions, color='red', label='Prédictions')
plt.plot(test.index, test['puissance'], color='blue', label='Valeurs réelles')
plt.legend()
plt.show()

