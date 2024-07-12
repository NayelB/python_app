import pygame
import random
import time

pygame.init()

# Couleurs
NOIR = (0, 0, 0)
BLANC = (255, 255, 255)
VERT = (0, 255, 0)
ROUGE = (255, 0, 0)

# Dimensions de l'écran
LARGEUR = 800
HAUTEUR = 600
ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("Jeu de Plateforme")

# Police de caractère
font = pygame.font.SysFont(None, 48)

class Joueur(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 50))
        self.image.fill(VERT)
        self.rect = self.image.get_rect()
        self.rect.x = 50
        self.rect.y = HAUTEUR - 60
        self.vitesse_y = 0

    def sauter(self):
        self.rect.y -= 1
        if self.rect.bottom >= HAUTEUR - 10:  # Vérifie si le joueur est sur le sol
            self.vitesse_y = -15

    def update(self):
        self.vitesse_y += 1  # Gravité
        self.rect.y += self.vitesse_y
        if self.rect.bottom > HAUTEUR - 10:  # Empêche le joueur de tomber à travers le sol
            self.rect.bottom = HAUTEUR - 10
            self.vitesse_y = 0

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, largeur, hauteur):
        super().__init__()
        self.image = pygame.Surface((largeur, hauteur))
        self.image.fill(ROUGE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self, vitesse_defilement):
        self.rect.x -= vitesse_defilement

def afficher_texte(texte, x, y):
    texte_surface = font.render(texte, True, BLANC)
    texte_rect = texte_surface.get_rect()
    texte_rect.center = (x, y)
    ecran.blit(texte_surface, texte_rect)

# ... (Suite du code dans la prochaine réponse)


