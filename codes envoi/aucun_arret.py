# -*- coding: utf-8 -*-
"""
Created on Thu May 23 13:19:43 2024

@author: eya
"""
import numpy as np
import pandas as pd
import mysql.connector
import sqlalchemy
import time

# Mock time.time() for testing
class MockTime:
    def __init__(self, start_time):
        self.current_time = start_time
    
    def time(self):
        return self.current_time
    
    def advance(self, seconds):
        self.current_time += seconds

mock_time = MockTime(start_time=1621251216.0)  # Arbitrary start time

# Configuration
power_threshold = 10.0  # Seuil de puissance pour détecter un arrêt (par exemple, en watts)
alert_interval = 1.5    # Facteur multiplicatif pour déclencher une alerte
max_time_without_stop = 200  # Temps maximum sans arrêt avant alerte (en secondes)
stop_times = []
last_stop_time = mock_time.time() - 100  # Simulate a last stop 100 seconds ago
average_interval = 50  # Simulate an average interval of 50 seconds

# Simulate current power below threshold (machine is stopped)
current_power = 5.0
if current_power < power_threshold:
    print("La machine est en arrêt")
    current_time = mock_time.time()
    if last_stop_time is not None:
        interval = current_time - last_stop_time
        stop_times.append(interval)
        stop_times = stop_times[-10:]  # Garder seulement les 10 derniers intervalles
        print(f"Stop detected: {interval:.2f} secondes.")
    last_stop_time = current_time
else:
    print("La machine est en marche")

# Check time since last stop and trigger alerts if necessary
time_since_last_stop = mock_time.time() - last_stop_time
print("Dernier arrêt depuis:", time_since_last_stop, " secondes.")

if time_since_last_stop > alert_interval * average_interval:
    print("Alerte: L'intervalle entre les arrêts est plus long que d'habitude!")

# Simulate no stop for too long
mock_time.advance(201)  # Advance time by 201 seconds

if last_stop_time is not None and (mock_time.time() - last_stop_time) > max_time_without_stop:
    print("Alerte: Aucun arrêt détecté pendant une période prolongée!")

