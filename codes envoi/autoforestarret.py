# -*- coding: utf-8 -*-
"""
Created on Sun May 26 14:36:09 2024

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
from sklearn.model_selection import RandomizedSearchCV

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
data['ttime'] = pd.to_datetime(data['ttime'])

# Détecter les arrêts en fonction du courant
courant_threshold = 0  # Exemple de seuil de courant pour détecter les arrêts
data['stop'] = (data['courant'] <= courant_threshold).astype(int)

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

# Définir la grille d'hyperparamètres à rechercher
param_dist = {
    'n_estimators': [50, 100, 200],
    'max_features': ['auto', 'sqrt', 'log2'],
    'max_depth': [10, 20, 30, None],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4],
    'bootstrap': [True, False]
}

# Créer le modèle RandomForestRegressor
rf = RandomForestRegressor(random_state=42)

# Recherche aléatoire des hyperparamètres
rf_random = RandomizedSearchCV(estimator=rf, param_distributions=param_dist, n_iter=100, cv=3, verbose=2, random_state=42, n_jobs=-1)
rf_random.fit(X_train, y_train)

# Meilleurs hyperparamètres
print(f'Best Hyperparameters: {rf_random.best_params_}')

# Utiliser les meilleurs hyperparamètres pour entraîner le modèle final
best_rf = rf_random.best_estimator_
best_rf.fit(X_train, y_train)

# Faire des prédictions sur l'ensemble de test
y_pred = best_rf.predict(X_test)

# Évaluer le modèle
mse = mean_squared_error(y_test, y_pred)
print(f'Mean Squared Error: {mse}')

# Afficher les prédictions et les valeurs réelles pour visualisation
plt.figure(figsize=(10, 5))
plt.plot(y_test, label='Actual', color='blue')
plt.plot(y_pred, label='Predicted', color='red')
plt.xlabel('Sample index')
plt.ylabel('Time to next stop')
plt.legend()
plt.title('Actual vs Predicted Time to Next Stop')
plt.show()

# Faire une prédiction pour le prochain arrêt basé sur les derniers arrêts
last_sequence = stop_intervals[-sequence_length:].values.reshape(1, -1)
predicted_time_to_next_stop = best_rf.predict(last_sequence)
print(f'Un arret en theorie apres: {predicted_time_to_next_stop[0]} secondes')
