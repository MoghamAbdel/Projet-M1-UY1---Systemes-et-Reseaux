import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import socket
import struct
import threading
import csv
import time
import sys
import os
from datetime import datetime
from pytz import timezone
import pygame
import time
import os
import socket
import pygame
import time

import pygame
import time
import os

# Couleurs
COULEURS = {
    'ROUGE': (255, 0, 0),
    'BLANC': (255, 255, 255),
    'BLEU': (0, 75, 255)
}

# Paramètres de la fenêtre
LARGEUR, HAUTEUR = 1280, 690

# Paramètres de la barre de chargement
BARRE_LARGEUR, BARRE_HAUTEUR = 60, 30
CHARGEMENT_TOTAL = 1218

# Fonction de chargement de l'application
def chargement_application():
    pygame.init()
    pygame.display.set_caption("SERVEUR")

    fenetre = pygame.display.set_mode((LARGEUR, HAUTEUR), pygame.DOUBLEBUF)
    horloge = pygame.time.Clock()

    barre_chargement = pygame.Rect(0, HAUTEUR - BARRE_HAUTEUR, BARRE_LARGEUR, BARRE_HAUTEUR)

    police = pygame.font.SysFont("Arial", 30, bold=True)
    texte_chargement = police.render("Chargement de l'application...", True, COULEURS['BLEU'])
    texte_pourcentage = None

    while barre_chargement.width <= LARGEUR:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        fenetre.fill(COULEURS['BLANC'])

        barre_chargement.width += LARGEUR // CHARGEMENT_TOTAL
        fenetre.blit(texte_chargement, (LARGEUR // 2 - texte_chargement.get_width() // 2, HAUTEUR - 60))

        pourcentage = (barre_chargement.width / LARGEUR) * 100
        texte_pourcentage = police.render(f"{int(pourcentage)}%", True, COULEURS['BLEU'])
        fenetre.blit(texte_pourcentage, (10, HAUTEUR - 60))

        pygame.draw.rect(fenetre, COULEURS['ROUGE'], barre_chargement)
        pygame.display.flip()

        if barre_chargement.width == BARRE_LARGEUR:
            time.sleep(2)  # Simulation du chargement du serveur

        horloge.tick(60)

    pygame.quit()
    os.system("connexion.py")

# Point d'entrée du programme
if __name__ == "__main__":
    chargement_application()

MAX_CLIENTS = 10
MAX_FILENAME = 256
MAX_BUFFER_SIZE = 1024

class ClientInfo:
    def __init__(self):
        self.ip = ""
        self.port = 0
        self.files = []
        self.file_count = 0
        self.connection_time = ""

class ClientList:
    def __init__(self):
        self.clients = []
        self.client_count = 0

def addClient(client_list, ip, port):
    if client_list.client_count < MAX_CLIENTS:
        client = ClientInfo()
        client.ip = ip
        client.port = port
        client.file_count = 0
        client_list.clients.append(client)
        client_list.client_count += 1

def addFile(client_list, client_index, filename):
    if 0 <= client_index < client_list.client_count:
        client = client_list.clients[client_index]
        if client.file_count < MAX_FILENAME:
            client.files.append(filename)
            client.file_count += 1
            saveClientList("client_list.csv", client_list)  # Enregistrer la liste des clients après chaque ajout de fichier

def saveClientList(filename, client_list):
    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Fichier", "Adresse IP", "Numéro de port", "Date et heure de connexion"])
        for client in client_list.clients:
            for filename in client.files:
                writer.writerow([filename, client.ip, client.port, client.connection_time])

def logOperation(operation):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    log_message = "[{}] {}".format(timestamp, operation)
    print(log_message)  # Afficher le message de log
    with open("server_log.txt", "a") as logFile:
        logFile.write(log_message + "\n")  # Écrire le message de log dans le fichier

def handleClient(client_socket, client_list):
    buffer = bytearray(MAX_BUFFER_SIZE)

    # Recevoir la liste des fichiers partagés par le client
    file_count_data = client_socket.recv(4)
    file_count = struct.unpack('i', file_count_data[:4])[0]

    for _ in range(file_count):
        filename_length_data = client_socket.recv(4)
        filename_length = struct.unpack('i', filename_length_data[:4])[0]

        filename = client_socket.recv(filename_length).decode()
        addFile(client_list, client_list.client_count - 1, filename)

    # Sauvegarder la liste des clients dans un fichier CSV (déplacé dans la fonction addFile)

    print("Informations enregistrées avec succès.")

    # Afficher la liste des fichiers partagés par le client
    client = client_list.clients[client_list.client_count - 1]
    print("Fichiers partagés par le client {}:{} :".format(client.ip, client.port))
    for file in client.files:
        print(file)

    # Log de l'opération
    operation = "Client {}:{} a partagé des fichiers".format(client.ip, client.port)
    logOperation(operation)
    operation = "Client {}:{} Opération de partage de fichiers terminée".format(client.ip, client.port)
    logOperation(operation)
    operation = "Client {}:{} Client déconnecté".format(client.ip, client.port)
    logOperation(operation)
    operation = "Client {}:{} Attente d'une nouvelle connexion".format(client.ip, client.port)
    logOperation(operation)

    # Fermer la connexion avec le client
    client_socket.close()

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('', 1234)

    client_list = ClientList()

    # Création du socket
    try:
        server_socket.bind(server_address)
    except socket.error as e:
        print("Erreur lors de la liaison du socket:", str(e))
        return

    # Mettre le serveur en écoute
    server_socket.listen(MAX_CLIENTS)
    print("Serveur en attente de connexions...")

    while True:
        # Accepter une connexion entrante
        client_socket, client_address = server_socket.accept()
        client_ip, client_port = client_address

        print("Nouvelle connexion acceptée : IP = {}, Port = {}".format(client_ip, client_port))
        logOperation("IP = {}, Port = {}".format(client_ip, client_port))

        # Ajouter le client à la liste des clients connectés
        addClient(client_list, client_ip, client_port)

        # Enregistrer la date et l'heure de connexion du client
        client_list.clients[client_list.client_count - 1].connection_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        # Afficher la date et l'heure de connexion du client
        print("Date et heure de connexion du client : {}".format(client_list.clients[client_list.client_count - 1].connection_time))
        logOperation("Date et heure de connexion du client : {}".format(client_list.clients[client_list.client_count - 1].connection_time))

        # Créer un thread pour gérer la connexion avec le client
        thread = threading.Thread(target=handleClient, args=(client_socket, client_list))
        thread.start()

def create_interface():
    window = tk.Tk()
    window.title("Serveur")
    window.geometry("500x400")


    # Logo
    logo_image_path = os.path.join(os.path.dirname(__file__), "logo.png")
    if os.path.exists(logo_image_path):
        logo_image = tk.PhotoImage(file=logo_image_path)
        logo_label = tk.Label(window, image=logo_image)
        logo_label.pack(pady=10)

    # Titre
    title_label = tk.Label(window, text="Serveur", font=("Arial", 16))
    title_label.pack()

    log_text = ScrolledText(window)
    log_text.pack(expand=True, fill='both')

    status_bar = tk.Label(window, text="Statut : Déconnecté", bd=1, relief=tk.SUNKEN, anchor=tk.W)
    status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    toolbar = tk.Frame(window, bd=1, relief=tk.RAISED)
    toolbar.pack(side=tk.TOP, fill=tk.X)

    def redirect_print_to_text_widget():
        class PrintRedirector:
            def __init__(self, widget):
                self.widget = widget

            def write(self, text):
                self.widget.insert('end', text)
                self.widget.see('end')

            def flush(self):
                pass  # Ajouter une méthode flush vide

        sys.stdout = PrintRedirector(log_text)

    redirect_print_to_text_widget()

    def updateClock():
        current_time = datetime.now(timezone('Europe/Paris')).strftime("%Y-%m-%d %H:%M:%S")
        status_bar.config(text="Statut : Connecté | Heure actuelle : {}".format(current_time))
        window.after(1000, updateClock)

    def start_server_thread():
        start_server_thread = threading.Thread(target=start_server)
        start_server_thread.daemon = True
        start_server_thread.start()

    def showLogs():
        with open("server_log.txt", "r") as log_file:
            logs = log_file.read()
            log_text.delete('1.0', tk.END)
            log_text.insert(tk.END, logs)

    logs_button = ttk.Button(toolbar, text="Afficher les logs", command=showLogs)
    logs_button.pack(side=tk.LEFT, padx=5, pady=5)

    def play_sound():
        pygame.mixer.init()
        pygame.mixer.music.load("sound.mp3")
        pygame.mixer.music.play()

    def stop_sound_clicked():
        stop_sound()

    def stop_sound():
        pygame.mixer.music.stop()

    play_sound_button = tk.Button(toolbar, text="Jouer un son", command=play_sound)
    play_sound_button.pack(side=tk.LEFT)

    stop_sound_button = tk.Button(toolbar, text="Arrêter le son", command=stop_sound_clicked)
    stop_sound_button.pack(side=tk.LEFT)

    def start_server_clicked():
        start_server_button.config(state=tk.DISABLED)
        status_bar.config(text="Statut : Connecté | En attente de connexions...", bg="blue", fg="white")

        start_server_thread()

    start_server_button = tk.Button(toolbar, text="Démarrer le serveur", command=start_server_clicked)
    start_server_button.pack(side=tk.LEFT)

    quit_button = tk.Button(toolbar, text="Quitter", command=window.quit)
    quit_button.pack(side=tk.RIGHT)

    updateClock()
    window.mainloop()

create_interface()

