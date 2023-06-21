
import os
import socket
import struct
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
from tkinter import ttk
import subprocess
from pathlib import Path
import threading
import os
import pygame
import time


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


MAX_FILENAME = 256
MAX_BUFFER_SIZE = 1024
SERVER_PORT = 12345
SERVER_IP = "127.0.0.1"


class Client:
    def __init__(self, filename="", ip="", port=0):
        self.filename = filename
        self.ip = ip
        self.port = port


def share_files(client_socket):
    directory = filedialog.askdirectory(title="Partager des fichiers", initialdir="/")
    if not directory:
        return

    # Récupérer la liste des fichiers dans le répertoire
    filenames = os.listdir(directory)
    file_count = len(filenames)
    file_count_data = struct.pack('i', file_count)
    client_socket.sendall(file_count_data)

    # Envoyer la liste des fichiers au serveur
    for filename in filenames:
        filename_length = len(filename)
        client_socket.send(struct.pack("i", filename_length))
        client_socket.send(filename.encode())

    messagebox.showinfo("Partage réussi", "Les fichiers ont été partagés avec succès.")

     # Afficher la liste des fichiers partagés
    file_list_window = tk.Toplevel()
    file_list_window.title("Liste des fichiers partagés")
    file_list_window.geometry("500x900")

    file_list_label = tk.Label(file_list_window, text="Liste des fichiers partagés:")
    file_list_label.pack(pady=10)

    file_list_text = tk.Text(file_list_window, wrap="word")
    file_list_text.pack(expand=True, fill="both")

    for i, filename in enumerate(filenames):
        file_list_text.insert(tk.END, "{}. {}\n".format(i + 1, filename))

    file_list_text.config(state="disabled")


def search_files(client_socket, keyword):
    search_command = "grep -w '{}' client_list.csv | cut -d ',' -f 1,2,3 | sort".format(keyword)

    # Ouvrir un processus en lecture pour exécuter la commande
    pipe = subprocess.Popen(search_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, _ = pipe.communicate()

    clients = []
    output_lines = output.decode().split("\n")
    for line in output_lines:
        parts = line.strip().split(",")
        if len(parts) == 3:
            client = Client(parts[0], parts[1], int(parts[2]))
            clients.append(client)

    if len(clients) > 0:
        result_window = tk.Toplevel()
        result_window.title("Résultats de recherche")
        result_window.geometry("400x300")

        result_label = tk.Label(result_window, text="Résultats de recherche pour le mot-clé '{}':".format(keyword))
        result_label.pack(pady=10)

        result_text = tk.Text(result_window, wrap="word")
        result_text.pack(expand=True, fill="both")

        for i, client in enumerate(clients):
            result_text.insert(tk.END, "Client {}:\n".format(i + 1))
            result_text.insert(tk.END, "  Nom du fichier : {}\n".format(client.filename))
            result_text.insert(tk.END, "  Adresse IP : {}\n".format(client.ip))
            result_text.insert(tk.END, "  Port : {}\n".format(client.port))
            result_text.insert(tk.END, "----------------------------------------------\n")

        result_text.config(state="disabled")
    else:
        messagebox.showinfo("Résultats de recherche", "Aucun résultat trouvé pour le mot-clé '{}'.".format(keyword))


def download_file_socket(filename, ip, port):
    download_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_addr = (ip, port)

    try:
        download_sock.connect(server_addr)
    except Exception as e:
        messagebox.showerror("Erreur de connexion", "Impossible de se connecter au client pour le téléchargement.")
        return

    # Envoyer le nom du fichier à télécharger au serveur
    download_sock.send(filename.encode())
    
    # Recevoir le message d'erreur s'il y a lieu
    # error_message = download_sock.recv(MAX_BUFFER_SIZE).decode()
    # if error_message:
    #     messagebox.showinfo("Erreur", error_message)
    #     download_sock.close()
    #     return

    # Réception du fichier
    save_path = Path("downloads") / filename
    with save_path.open("wb") as file:
        while True:
            buffer = download_sock.recv(MAX_BUFFER_SIZE)
            if not buffer:
                break
            file.write(buffer)

    # Recevoir le message de succès
    success_message = download_sock.recv(MAX_BUFFER_SIZE).decode()
    if success_message:
        messagebox.showinfo("Téléchargement réussi", success_message)
    else:
        messagebox.showinfo("Téléchargement réussi", "Le fichier a été téléchargé avec succès.")
    
    download_sock.close()

    # Ouvrir le répertoire contenant le fichier téléchargé
    folder_path = save_path.parent
    if folder_path.exists() and folder_path.is_dir():
        if os.name == "nt":
            subprocess.Popen(f'explorer "{folder_path}"')
        else:
            subprocess.Popen(["xdg-open", folder_path])
    else:
        messagebox.showerror("Erreur", "Impossible d'ouvrir le dossier de téléchargement.")


# Code du serveur
PORT_PEER = 4444
IP_PEER = ""
MAX_BUFFER_SIZE = 2048

import os

def share_data():
    server_fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_fd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_fd.bind((IP_PEER, PORT_PEER))
    server_fd.listen(3)

    print("Le serveur est prêt à recevoir des demandes de téléchargement...")

    while True:
        new_socket, client_addr = server_fd.accept()
        print("Connexion établie avec le client {}:{}".format(client_addr[0], client_addr[1]))

        filename = new_socket.recv(MAX_BUFFER_SIZE).decode()
        if not filename:
            print("Erreur : Nom de fichier non reçu.")
            new_socket.close()
            continue

        if not os.path.isfile(filename):
            message = "Erreur : le fichier demandé est introuvable.".encode()
            new_socket.sendall(message)
            print("Le fichier  {}  est introuvable.".format(filename))
            new_socket.close()
            continue

        with open(filename, "rb") as file:
            while True:
                data = file.read(MAX_BUFFER_SIZE)
                if not data:
                    break
                new_socket.sendall(data)

        print("Le fichier {} a été envoyé avec succès.".format(filename))
        response = "Le fichier {} a été téléchargé avec succès.".format(filename)
        new_socket.sendall(response.encode())

        new_socket.close()


def display_logs():
    log_file_path = "server_log.txt"
    if not os.path.isfile(log_file_path):
        messagebox.showerror("Erreur", "Impossible d'ouvrir le fichier de logs.")
        return

    with open(log_file_path, "r") as log_file:
        log_content = log_file.read()

    log_window = tk.Toplevel()
    log_window.title("Logs du serveur")
    log_window.geometry("800x600")

    log_text = tk.Text(log_window, wrap="word")
    log_text.pack(expand=True, fill="both")

    log_text.insert(tk.END, log_content)
    log_text.config(state="disabled")


def main():
    
     # Creation du thread pour executer share_data
    share_data_thread = threading.Thread(target=share_data)
    share_data_thread.daemon = True
    share_data_thread.start()
    
    root = tk.Tk()
    root.title("Client de partage de fichiers")
    root.geometry("800x800")

    # Titre du programme
    title_label = tk.Label(root, text="Client de partage de fichiers", font=("Arial", 16, "bold"))
    title_label.pack(pady=10)

    # Widget central
    central_widget = ttk.Frame(root)
    central_widget.pack(expand=True, fill="both")

    # Display area
    display_frame = ttk.Frame(central_widget)
    display_frame.pack(expand=True, fill="both")

    # Liste des fichiers partagés
    shared_files_canvas = tk.Canvas(display_frame, bg="white")
    shared_files_canvas.pack(expand=True, fill="both")

    shared_files_frame = ttk.Frame(shared_files_canvas)
    shared_files_frame.pack(expand=True, fill="both")

    shared_files_scrollbar = ttk.Scrollbar(display_frame, orient="vertical", command=shared_files_canvas.yview)
    shared_files_scrollbar.pack(side=tk.RIGHT, fill="y")

    shared_files_canvas.configure(yscrollcommand=shared_files_scrollbar.set)
    shared_files_canvas.bind('<Configure>', lambda e: shared_files_canvas.configure(scrollregion=shared_files_canvas.bbox("all")))
    shared_files_canvas.create_window((0, 0), window=shared_files_frame, anchor="nw")

    # Fonctions d'actions
    def share_files_action():
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_addr = (SERVER_IP, SERVER_PORT)

        try:
            client_socket.connect(server_addr)
        except Exception as e:
            messagebox.showerror("Erreur de connexion", "Impossible de se connecter au serveur.")
            return

        share_files(client_socket)
        client_socket.close()

    def search_files_action():
        keyword = simpledialog.askstring("Rechercher des fichiers", "Entrez le mot-clé de recherche:")
        if keyword:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_addr = (SERVER_IP, SERVER_PORT)

            try:
                client_socket.connect(server_addr)
            except Exception as e:
                messagebox.showerror("Erreur de connexion", "Impossible de se connecter au serveur.")
                return

            search_files(client_socket, keyword)
            client_socket.close()

    def download_file_action():
        filename = simpledialog.askstring("Télécharger un fichier", "Entrez le nom du fichier à télécharger:")
        ip = simpledialog.askstring("Télécharger un fichier", "Entrez l'adresse IP du client propriétaire du fichier:")
        port = simpledialog.askinteger("Télécharger un fichier", "Entrez le port du client propriétaire du fichier:")

        if filename and ip and port:
            download_file_socket(filename, ip, port)


    def display_logs_action():
        display_logs()

    def exit_client():
        root.destroy()

    # Barre de menu verticale
    menu_bar = tk.Menu(root)
    menu_bar.config(background="blue")

    file_menu = tk.Menu(menu_bar, tearoff=0)
    file_menu.add_command(label="Partager des fichiers", command=share_files_action)
    file_menu.add_separator()
    file_menu.add_command(label="Quitter", command=exit_client)

    search_menu = tk.Menu(menu_bar, tearoff=0)
    search_menu.add_command(label="Rechercher des fichiers", command=search_files_action)

    download_menu = tk.Menu(menu_bar, tearoff=0)
    download_menu.add_command(label="Télécharger un fichier", command=download_file_action)

    log_menu = tk.Menu(menu_bar, tearoff=0)
    log_menu.add_command(label="Afficher les logs", command=display_logs_action)

    menu_bar.add_cascade(label="Fichier", menu=file_menu)
    menu_bar.add_cascade(label="Recherche", menu=search_menu)
    menu_bar.add_cascade(label="Téléchargement", menu=download_menu)
    menu_bar.add_cascade(label="Logs", menu=log_menu)

    root.config(menu=menu_bar)

    # Cadre des boutons
    button_frame = ttk.Frame(display_frame)
    button_frame.pack(pady=10)

    share_button = ttk.Button(button_frame, text="Partager des fichiers", command=share_files_action)
    share_button.grid(row=0, column=0, padx=10)

    search_button = ttk.Button(button_frame, text="Rechercher des fichiers", command=search_files_action)
    search_button.grid(row=0, column=1, padx=10)

    download_button = ttk.Button(button_frame, text="Télécharger un fichier", command=download_file_action)
    download_button.grid(row=0, column=2, padx=10)

    log_button = ttk.Button(button_frame, text="Afficher les logs", command=display_logs_action)
    log_button.grid(row=0, column=3, padx=10)

    # Pied de page
    footer_label = ttk.Label(root, text="© 2023 MonClient. Tous droits réservés.", font=("Arial", 10))
    footer_label.pack(side=tk.BOTTOM, pady=10)

    root.mainloop()


if __name__ == "__main__":
    main()

