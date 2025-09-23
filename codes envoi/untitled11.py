# -*- coding: utf-8 -*-
"""
Created on Fri May 10 20:05:29 2024

@author: eya
"""

import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import sqlalchemy
import seaborn as sns
import pmdarima as pm
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.model_selection import train_test_split
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.stattools import adfuller
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

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


# Calcul de l'IQR
Q1 = data['puissance'].quantile(0.25)
Q3 = data['puissance'].quantile(0.75)
IQR = Q3 - Q1

# Détection des valeurs aberrantes
outliers = (data['puissance'] < Q1 - 1.5 * IQR) | (data['puissance'] > Q3 + 1.5 * IQR)

# Supprimer les valeurs aberrantes
data_clean = data[~outliers]

# Remplacer les valeurs aberrantes par la médiane
median_fill = data_clean['puissance'].median()
data.loc[outliers, 'puissance'] = median_fill

####################################


# Rééchantillonnage des données à une fréquence horaire
data_clean['ttime'] = pd.to_datetime(data_clean['ttime'])  # si la colonne 'ttime' est de type datetime
data_clean.set_index('ttime', inplace=True)  # Définir 'ttime' comme index
data_resampled = data_clean.resample('H').mean()  # Rééchantillonner les données à une fréquence horaire en prenant la moyenne
data_resampled.fillna(data_resampled.mean(), inplace=True)  # Remplir les valeurs manquantes avec la moyenne


# Ajustement du modèle ARIMA à l'aide de toutes vos données disponibles
model = ARIMA(data_resampled['puissance'], order=(10, 0, 16))  # Exemple : ARIMA(p,d,q) avec p=11, d=0, q=14
model_fit = model.fit()

# Faire des prédictions sur de nouvelles données (par exemple, les 24 prochaines heures)
forecast_steps = 24
forecast = model_fit.forecast(steps=forecast_steps)

# Convertir la colonne timestamp en type datetime
last_timestamp = data_resampled.index[-1]
timestamps = pd.date_range(start=last_timestamp, periods=forecast_steps + 1, freq='H')[1:]

# Tracer les prédictions
plt.figure(figsize=(10, 6))
plt.plot(data_resampled.index, data_resampled['puissance'], label='Données historiques', color='blue')
plt.plot(timestamps, forecast, label='Prédictions', color='red')
plt.title('Prédictions de la consommation électrique pour les 24 prochaines heures')
plt.xlabel('Date et heure')
plt.ylabel('Consommation électrique')
plt.legend()
plt.grid(True)
plt.show()
# Créer une table pour stocker les prédictions
create_table_query = """
CREATE TABLE IF NOT EXISTS new_predictions (
    timestamp DATETIME PRIMARY KEY,
    prediction FLOAT
)
"""
cursor = conn.cursor()
cursor.execute(create_table_query)

# Insérer les prédictions dans la table
for i, prediction in enumerate(forecast, start=1):
    # Calculer le timestamp pour la prédiction
    timestamp = data_resampled.index[-1] + pd.Timedelta(hours=i)
    # Formatage de la date et de l'heure au format MySQL
    timestamp_mysql = timestamp.strftime('%Y-%m-%d %H:%M:%S')
    # Requête SQL d'insertion
    insert_query = "INSERT INTO new_predictions (timestamp, prediction) VALUES (%s, %s)"
    # Exécution de la requête
    cursor.execute(insert_query, (timestamp_mysql, prediction))

# Valider les modifications dans la base de données
conn.commit()

# Fermer le curseur et la connexion
cursor.close()
conn.close()






"""

# Tracer le graphique de l'Autocorrélation (ACF)
plt.figure(figsize=(12, 6))
plot_acf(data_resampled['puissance'], lags=50)  # Lags : nombre de décalages à inclure dans le calcul de l'ACF
plt.title('Autocorrélation (ACF)')
plt.xlabel('Décalages')
plt.ylabel('Corrélation')
plt.grid(True)
plt.show()

# Tracer le graphique de l'Autocorrélation partielle (PACF)
plt.figure(figsize=(12, 6))
plot_pacf(data_resampled['puissance'], lags=22)  # Lags : nombre de décalages à inclure dans le calcul de la PACF
plt.title('Autocorrélation partielle (PACF)')
plt.xlabel('Décalages')
plt.ylabel('Corrélation partielle')
plt.grid(True)
plt.show()


# Fonction pour effectuer le test de Dickey-Fuller augmenté
def test_stationarity(timeseries):
    # Calcul des statistiques de test
    result = adfuller(timeseries)
    print('Test Statistique:', result[0])
    print('p-value:', result[1])
    print('Valeurs Critiques:')
    for key, value in result[4].items():
        print('\t{}: {}'.format(key, value))

    # Interprétation des résultats
    print('\nRésultats du test de stationnarité de Dickey-Fuller augmenté:')
    if result[1] <= 0.05:
        print("La série temporelle est stationnaire (rejeter l'hypothèse nulle)")
    else:
        print("La série temporelle n'est pas stationnaire (ne pas rejeter l'hypothèse nulle)")

# Appliquer le test de stationnarité à votre série temporelle
test_stationarity(data_resampled['puissance'])


# Fonction pour visualiser la série temporelle et les résultats du test de Dickey-Fuller augmenté
def plot_stationarity(timeseries):
    # Tracé de la série temporelle
    plt.figure(figsize=(12, 6))
    plt.plot(timeseries, color='blue')
    plt.title('Série Temporelle de Puissance Électrique')
    plt.xlabel('Date')
    plt.ylabel('Puissance')
    plt.grid(True)
    plt.show()

    # Test de stationnarité
    result = adfuller(timeseries)
    print('\nRésultats du test de stationnarité de Dickey-Fuller augmenté:')
    print('Test Statistique:', result[0])
    print('p-value:', result[1])
    print('Valeurs Critiques:')
    for key, value in result[4].items():
        print('\t{}: {}'.format(key, value))

    # Interprétation des résultats
    if result[1] <= 0.05:
        print("\nLa série temporelle est stationnaire (rejeter l'hypothèse nulle)")
    else:
        print("\nLa série temporelle n'est pas stationnaire (ne pas rejeter l'hypothèse nulle)")

# Appliquer la fonction à votre série temporelle
plot_stationarity(data_resampled['puissance'])




# Séparation des données en ensembles d'entraînement et de test (par exemple, en utilisant les 80% premières observations pour l'entraînement)
train_size = int(len(data_resampled) * 0.8)
train_data = data_resampled.iloc[:train_size]
test_data = data_resampled.iloc[train_size:]

# Appliquer le test de stationnarité à l'ensemble d'entraînement
test_stationarity(train_data['puissance'])


####################

# Appliquer le modèle ARIMA à l'ensemble d'entraînement
model = ARIMA(train_data['puissance'], order=(11, 0, 14))
model_fit = model.fit()

print(model_fit.summary())



# Prédictions sur l'ensemble d'entraînement
train_predictions = model_fit.predict(start=train_data.index[0], end=train_data.index[-1])

# Prédictions sur l'ensemble de test
test_predictions = model_fit.predict(start=test_data.index[0], end=test_data.index[-1])

# Tracer les prédictions et les données réelles avec les courbes collées
plt.figure(figsize=(10, 6))
plt.plot(train_data.index, train_data['puissance'], label='Ensemble d\'entraînement', color='blue')
plt.plot(test_data.index, test_data['puissance'], label='Ensemble de test (réel)', color='blue', linestyle='--')
plt.plot(train_predictions.index, train_predictions, label='Prédictions (Entraînement)', color='red')
plt.plot(test_predictions.index, test_predictions, label='Prédictions (Test)', color='green')

# Définir les limites des axes x et y pour une continuité visuelle
plt.xlim(train_data.index[0], test_data.index[-1])
plt.ylim(min(train_data['puissance'].min(), test_data['puissance'].min()), max(train_data['puissance'].max(), test_data['puissance'].max()))

plt.xlabel('Date')
plt.ylabel('Puissance')
plt.title('Prédictions du modèle ARIMA')
plt.legend()
plt.show()
# Mesures de performance sur l'ensemble d'entraînement
train_mae = mean_absolute_error(train_data['puissance'], train_predictions)
train_mse = mean_squared_error(train_data['puissance'], train_predictions)
train_rmse = mean_squared_error(train_data['puissance'], train_predictions, squared=False)
train_r2 = r2_score(train_data['puissance'], train_predictions)

# Mesures de performance sur l'ensemble de test
test_mae = mean_absolute_error(test_data['puissance'], test_predictions)
test_mse = mean_squared_error(test_data['puissance'], test_predictions)
test_rmse = mean_squared_error(test_data['puissance'], test_predictions, squared=False)
test_r2 = r2_score(test_data['puissance'], test_predictions)

# Créer un DataFrame pour afficher les mesures de performance
performance_df = pd.DataFrame({
    'Métrique': ['MAE', 'MSE', 'RMSE', 'R²'],
    'Ensemble d\'entraînement': [train_mae, train_mse, train_rmse, train_r2],
    'Ensemble de test': [test_mae, test_mse, test_rmse, test_r2]
})

print(performance_df)




# Visualisation des résidus
model_fit.plot_diagnostics(figsize=(12, 8))
plt.show()

#### RESIDUS

# Récupérer les résidus du modèle ARIMA
residuals = model_fit.resid

# Tracer les graphiques ACF et PACF des résidus
fig, axes = plt.subplots(1, 2, figsize=(12, 4))
plot_acf(residuals, ax=axes[0], lags=20)
plot_pacf(residuals, ax=axes[1], lags=20)
plt.show()

# Faire des prévisions
forecast_steps = 24  # Prévoir les prochaines 24 heures
forecast = model_fit.forecast(steps=forecast_steps)

# Afficher les prévisions
plt.plot(data_resampled.index[-50:], data_resampled['puissance'].tail(50), label='Données historiques')
plt.plot(pd.date_range(start=data_resampled.index[-1], periods=forecast_steps, freq='H'), forecast, label='Prévisions')
plt.title('Prévisions de la consommation électrique')
plt.xlabel('Date et heure')
plt.ylabel('Consommation électrique')
plt.legend()
plt.show()




"""

"""
# Ajustement du modèle ARIMA
model = ARIMA(data_resampled['puissance'], order=(5,1,0))  # Exemple : ARIMA(p,d,q) avec p=5, d=1, q=0
model_fit = model.fit()

# Afficher les paramètres du modèle ARIMA
print(model_fit.summary())

# Visualisation des résidus
model_fit.plot_diagnostics(figsize=(12, 8))
plt.show()

# Faire des prévisions
forecast_steps = 24  # Prévoir les prochaines 24 heures
forecast = model_fit.forecast(steps=forecast_steps)

# Afficher les prévisions
plt.plot(data_resampled.index[-50:], data_resampled['puissance'].tail(50), label='Données historiques')
plt.plot(pd.date_range(start=data_resampled.index[-1], periods=forecast_steps, freq='H'), forecast, label='Prévisions')
plt.title('Prévisions de la consommation électrique')
plt.xlabel('Date et heure')
plt.ylabel('Consommation électrique')
plt.legend()
plt.show()
"""
