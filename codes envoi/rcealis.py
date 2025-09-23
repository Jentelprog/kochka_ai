# -*- coding: utf-8 -*-
"""
Created on Thu May  2 12:43:10 2024

@author: eya
"""
import mysql.connector
import sqlalchemy

# Connexion à la base de données MySQL
connexion = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Azerty1234",
    database="testt"
)

# Créer la chaîne de connexion SQLAlchemy
connexion_str = 'mysql+mysqlconnector://root:Azerty1234@localhost/testt'

# Créer le moteur SQLAlchemy
engine = sqlalchemy.create_engine(connexion_str)
curseur = connexion.cursor()

# Création de la table aslema_table si elle n'existe pas déjà
curseur.execute('''CREATE TABLE IF NOT EXISTS aslema_table (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    RB INT
                    )''')

# Initialiser la valeur du relais
r = 0
# Initialiser la variable de sauvegarde de la base de relais
RB = 0

# Liste pour stocker les valeurs de RB
RB_liste = []

# Boucle pour exécuter le processus cinq fois

    # Demander à l'utilisateur de saisir les valeurs de seuil et de puissance
x = 650
p = 60000

    # Réinitialiser la valeur du relais à 0 à chaque itération
r = 0

    # Mettre à jour le relais en fonction des valeurs de seuil et de puissance
if p > x:
    r = 1
    print("La valeur du relais est :", r)
 
    # Vérifier si la valeur du relais a changé depuis la dernière itération
if RB != r:
    RB = r
    print("La valeur data base de relais est :", RB)
    RB_liste.append(RB)

# Insertion des valeurs de RB dans la table RB_table
for valeur in RB_liste:
    curseur.execute("INSERT INTO aslema_table (RB) VALUES (%s)", (valeur,))

# Valider les modifications et fermer la connexion
connexion.commit()
connexion.close()

