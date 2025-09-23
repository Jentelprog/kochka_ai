# -*- coding: utf-8 -*-
"""
Created on Sat May 11 13:18:25 2024

@author: eya
"""
import pandas as pd
import sqlalchemy
import mysql.connector
from sklearn.model_selection import train_test_split
from sklearn.ensemble import IsolationForest
from sklearn.metrics import roc_curve, precision_recall_curve, auc
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

# Récupérer les données de la table depuis la base de données
query = "SELECT * FROM sensor"
data = pd.read_sql(query, engine)

# Diviser les données en caractéristiques (X) et étiquettes (y)
X = data['ttime']
y = data['puissance']

# Diviser les données en ensembles d'entraînement et de test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialiser le modèle Isolation Forest
model = IsolationForest(contamination=0.1, random_state=42)

# Entraîner le modèle
model.fit(X_train.to_numpy().reshape(-1, 1))  # Reshape nécessaire car IsolationForest attend des données en 2D

# Prédire les anomalies sur l'ensemble de test
y_pred = model.predict(X_test.to_numpy().reshape(-1, 1))  # Reshape nécessaire

# Calculer les scores de décision pour les courbes ROC et PR
decision_scores = model.decision_function(X_test.to_numpy().reshape(-1, 1))  # Reshape nécessaire


# Calculer la courbe ROC
fpr, tpr, _ = roc_curve(y_test, decision_scores)
roc_auc = auc(fpr, tpr)

# Tracer la courbe ROC
plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, color='blue', lw=2, label='ROC curve (area = %0.2f)' % roc_auc)
plt.plot([0, 1], [0, 1], color='gray', linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic (ROC) Curve')
plt.legend(loc="lower right")
plt.show()

# Calculer la courbe PR
precision, recall, _ = precision_recall_curve(y_test, decision_scores)

# Tracer la courbe PR
plt.figure(figsize=(8, 6))
plt.plot(recall, precision, color='red', lw=2, label='Precision-Recall curve')
plt.xlabel('Recall')
plt.ylabel('Precision')
plt.title('Precision-Recall Curve')
plt.legend(loc="lower left")
plt.show()
