

# -*- coding: utf-8 -*-
"""
Created on Thu May  2 12:43:10 2024

@author: eya
"""
import mysql.connector
import sqlalchemy
import pandas as pd

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
query = "SELECT puissance FROM sensor ORDER BY id DESC LIMIT 1"
data = pd.read_sql(query, engine)


# Créer le curseur pour exécuter les requêtes SQL
curseur = conn.cursor()

# Création de la table aslema_table si elle n'existe pas déjà
curseur.execute('''CREATE TABLE IF NOT EXISTS etat_RB (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    RB INT
                    )''')

# Initialiser la valeur du seuil
x = 5

# Initialiser la valeur du relais
r = 0

# Initialiser la variable de sauvegarde de la base de relais
# Exécuter une requête SQL pour récupérer la dernière valeur de RB à partir de la table aslema_table
curseur.execute("SELECT RB FROM etat_RB ORDER BY id DESC LIMIT 1")
derniere_valeur_RB = curseur.fetchone()[0]  # Récupérer la dernière valeur de RB

# Utiliser la dernière valeur de RB
RB = derniere_valeur_RB
# Liste pour stocker les valeurs de RB
RB_liste = []

# Boucle pour exécuter le processus cinq fois

    # Utiliser la dernière valeur de puissance
p = data.loc[0, 'puissance']


    # Mettre à jour le relais en fonction des valeurs de seuil et de puissance
if p > x:
    r = 1
else:
    r = 0
    
    # Afficher la valeur mise à jour du relais
print("La valeur du relais est :", r)
 
    # Vérifier si la valeur du relais a changé depuis la dernière itération
if RB != r:
        RB = r
        print("La valeur data base de relais est :", RB)
        RB_liste.append(RB)

# Insertion des valeurs de RB 
for valeur in RB_liste:
    curseur.execute("INSERT INTO etat_RB (RB) VALUES (%s)", (valeur,))

# Valider les modifications et fermer la connexion
conn.commit()
conn.close()
