import os
import sys
import csv
import time
from datetime import datetime
from pytz import timezone
import socket
import struct
import threading
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

import pygame

# Déclaration des couleurs
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 75, 255)
BACKGROUND_COLOR = (220, 220, 220)  # Couleur de fond améliorée

def main():
    # Variables nécessaires
    largeur, hauteur = 1280, 690
    horloge = 0
    chargement_total = 1218

    pygame.init()  # Initialisation de pygame
    pygame.display.set_caption("SERVEUR")  # Nom de la fenêtre
    info = pygame.display.set_mode((largeur, hauteur), pygame.DOUBLEBUF)  # Taille de la fenêtre

    # Chargement du son de chargement
    pygame.mixer.init()
    pygame.mixer.music.load("sound.mp3")  # Remplacez "sound.mp3" par le chemin de votre fichier audio
    pygame.mixer.music.set_volume(0.5)

    # Chargement de l'animation en arrière-plan
    animation_images = []
    for i in range(1, 7):
        image_path = f"/home/tsango/Bureau/Tsango_Edou_Benjamin_19M2400/VERSION_PYTHON1/image/logo.png"  # Remplacez "animation_{i}.png" par le chemin de vos images d'animation
        image = pygame.image.load(image_path).convert_alpha()
        animation_images.append(image)

    animation_index = 0
    animation_delay = 100  # Délai entre chaque image de l'animation (en millisecondes)
    animation_timer = pygame.time.get_ticks()

    # Création de la barre de chargement
    ma_barre = pygame.Rect(0, hauteur - 30, 60, 30)

    # Chargement de la police
    font_path = pygame.font.match_font("Arial")  # Chemin de la police de caractères Arial
    arial_police = pygame.font.Font(font_path, 30)

    # Lancement de la musique de chargement
    pygame.mixer.music.play(-1)  # -1 pour la répétition en boucle

    # Mise en place de l'animation de chargement
    while horloge <= chargement_total:
        time.sleep(0.001)
        info.fill(BACKGROUND_COLOR)  # Utilisation de la couleur de fond améliorée

        # Animation en arrière-plan
        if pygame.time.get_ticks() - animation_timer > animation_delay:
            animation_index = (animation_index + 1) % len(animation_images)
            animation_timer = pygame.time.get_ticks()

        animation_image = animation_images[animation_index]
        animation_rect = animation_image.get_rect(center=(largeur // 2, hauteur // 2))
        info.blit(animation_image, animation_rect)

        # Calcul du dégradé de couleur
        pourcentage = horloge / chargement_total
        r = int((1 - pourcentage) * BLUE[0] + pourcentage * RED[0])
        g = int((1 - pourcentage) * BLUE[1] + pourcentage * RED[1])
        b = int((1 - pourcentage) * BLUE[2] + pourcentage * RED[2])
        color_gradient = (r, g, b)

        ma_barre.width = pourcentage * (largeur - 60)
        text_progression = arial_police.render(f"Chargement : {int(pourcentage * 100)}%", True, color_gradient)
        info.blit(text_progression, [510, hauteur - 60])
        pygame.draw.rect(info, RED, ma_barre)

        pygame.display.flip()

        if horloge == 0:
            # Simulation du chargement du serveur
            time.sleep(2)  # Temps d'attente de 2 secondes pour simuler le chargement

        horloge += 1

    # Arrêt de la musique de chargement
    pygame.mixer.music.stop()

    pygame.quit()  # Fermeture de la fenêtre
    os.system("connexion.py")  # Lancement de la fonction de gestion du mode administrateur

if __name__ == "__main__":
    main()

