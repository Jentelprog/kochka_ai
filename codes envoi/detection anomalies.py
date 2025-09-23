import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sqlalchemy
import mysql.connector
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVC
from sklearn.cluster import DBSCAN
from sklearn.metrics import classification_report

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

consommation = data['puissance']

# Obtenir l'indice du maximum de consommation
pic_de_puissance = max(consommation)
indice_pic_de_puissance = consommation.idxmax()

sorted_consommation = consommation.sort_values(ascending=False)
deuxieme_max = sorted_consommation.iloc[1]
indice_deuxieme_max = sorted_consommation.index[1]

# Créer un modèle Isolation Forest
model = IsolationForest(contamination=0.005)
model.fit(consommation.values.reshape(-1, 1))

# Prédire les anomalies dans les données de consommation
anomalies = model.predict(consommation.values.reshape(-1, 1))

# Filtrer les indices des anomalies détectées
indices_anomalies = [i for i, x in enumerate(anomalies) if x == -1]

# Afficher les points de défaillance sur le graphique
plt.scatter(indices_anomalies, consommation.iloc[indices_anomalies], color='green', label='Défaillance détectée')

# Création du graphique
plt.plot(consommation, label='Consommation')
plt.axhline(y=deuxieme_max, color='red', linestyle='--', label='Max puissance')
plt.axhline(y=400, color='red', label='Marge puissance')
plt.scatter(indice_pic_de_puissance, pic_de_puissance, color='red', label='Pic de demarrage')
plt.xlabel('Temps')
plt.ylabel('Consommation')
plt.title('Courbe de consommation avec pic de puissance')
plt.legend()
plt.grid(True)
plt.show()

# Calcul de la moyenne mobile sur une fenêtre de 5 points
moyenne_mobile = consommation.rolling(window=5).mean()

# Calcul de l'écart-type mobile sur une fenêtre de 5 points
ecart_type_mobile = consommation.rolling(window=5).std()

# Calcul des valeurs maximales et minimales mobiles sur une fenêtre de 5 points
max_mobile = consommation.rolling(window=5).max()
min_mobile = consommation.rolling(window=5).min()

# Calcul du nombre de pics au-dessus d'un seuil de 300 dans chaque fenêtre de 5 points
seuil = 300
nb_pics = consommation.rolling(window=5).apply(lambda x: np.sum(x > seuil))

# Visualisation des caractéristiques
plt.figure(figsize=(10, 6))
plt.plot(consommation, label='Consommation')
plt.plot(moyenne_mobile, label='Moyenne mobile')
plt.plot(ecart_type_mobile, label='Écart-type mobile')
#plt.plot(max_mobile, label='Max mobile')
#plt.plot(min_mobile, label='Min mobile')
plt.plot(nb_pics, label='Nombre de pics')
plt.xlabel('Temps')
plt.ylabel('Consommation')
plt.title('Caractéristiques de la consommation')
plt.legend()
plt.grid(True)
plt.show()

