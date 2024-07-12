import pygame
import random
import sys

# Initialisation de Pygame
pygame.init()

# Dimensions de l'écran
screen_width = 1024
screen_height = 768

# Couleurs
black = (0, 0, 0)
white = (255, 255, 255)
green = (0, 255, 0)
red = (255, 0, 0)

# Configuration de l'écran
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Space Invaders")

# Charger les images
player_img = pygame.image.load("player.png")
enemy_img = pygame.image.load("enemy.png")
bullet_img = pygame.image.load("bullet.png")
laser_img = pygame.image.load("laser.png")
background_img = pygame.image.load("background.png")
boss_img = pygame.image.load("boss.png")
boss2_img = pygame.image.load("boss2.png")
heart_img = pygame.image.load("heart.png")

# Redimensionner les images si nécessaire
player_img = pygame.transform.scale(player_img, (60, 60))
enemy_img = pygame.transform.scale(enemy_img, (50, 50))
bullet_img = pygame.transform.scale(bullet_img, (10, 20))
laser_img = pygame.transform.scale(laser_img, (10, 20))
background_img = pygame.transform.scale(background_img, (screen_width, screen_height))
boss_img = pygame.transform.scale(boss_img, (200, 200))
boss2_img = pygame.transform.scale(boss2_img, (200, 200))
heart_img = pygame.transform.scale(heart_img, (30, 30))

# Classe Joueur
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect()
        self.rect.centerx = screen_width // 2
        self.rect.bottom = screen_height - 10
        self.speed = 5
        self.health = 3

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > screen_width:
            self.rect.right = screen_width

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)

    def take_damage(self):
        self.health -= 1

    def get_health(self):
        return self.health

# Classe Ennemi
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = enemy_img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speedx = 1

    def update(self):
        self.rect.x += self.speedx
        if self.rect.left < 0 or self.rect.right > screen_width:
            self.speedx = -self.speedx
            self.rect.y += 20

        if random.random() < 0.001:  # Probabilité réduite à 0.1%
            self.shoot()

    def shoot(self):
        laser = Laser(self.rect.centerx, self.rect.bottom)
        all_sprites.add(laser)
        lasers.add(laser)

# Classe Boss
class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y, img, health):
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speedx = 1
        self.health = health
        self.max_health = health

    def update(self):
        self.rect.x += self.speedx
        if self.rect.left < 0 or self.rect.right > screen_width:
            self.speedx = -self.speedx
            self.rect.y += 20

        if random.random() < 0.002:  # Probabilité réduite à 0.2%
            self.shoot()

    def shoot(self):
        laser = Laser(self.rect.centerx, self.rect.bottom)
        all_sprites.add(laser)
        lasers.add(laser)

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.kill()

    def draw_health_bar(self):
        if self.health > 0:
            pygame.draw.rect(screen, red, (self.rect.x, self.rect.y - 20, self.rect.width, 10))
            pygame.draw.rect(screen, green, (self.rect.x, self.rect.y - 20, self.rect.width * (self.health / self.max_health), 10))

# Classe Bullet
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

# Classe Laser
class Laser(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = laser_img
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y
        self.speedy = 10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > screen_height:
            self.kill()

# Initialisation des groupes de sprites
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
lasers = pygame.sprite.Group()
boss_group = pygame.sprite.Group()

# Création du joueur
player = Player()
all_sprites.add(player)

# Score
score = 0
font = pygame.font.SysFont(None, 36)

# Fonction pour afficher le score
def draw_text(surf, text, size, x, y, color=white):
    font = pygame.font.Font(pygame.font.match_font('arial'), size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.topleft = (x, y)
    surf.blit(text_surface, text_rect)

# Fonction pour créer une vague d'ennemis
def create_enemies():
    for row in range(3):  # 3 lignes d'ennemis
        for col in range(10):  # 10 ennemis par ligne
            enemy = Enemy(50 + col * 80, 50 + row * 60)
            all_sprites.add(enemy)
            enemies.add(enemy)

# Fonction pour afficher "Game Over"
def show_game_over_screen():
    screen.blit(background_img, (0, 0))
    draw_text(screen, "GAME OVER", 96, screen_width // 2 - 150, screen_height // 2 - 50, red)
    draw_text(screen, f"Score: {score}", 48, screen_width // 2 - 100, screen_height // 2 + 50, white)
    pygame.display.flip()
    pygame.time.delay(3000)  # Pause de 3 secondes avant de quitter
    reset_game()

# Fonction pour afficher "Press any key to start"
def show_start_screen():
    screen.blit(background_img, (0, 0))
    draw_text(screen, "Press any key to start", 36, screen_width // 2 - 120, screen_height // 2, white)
    pygame.display.flip()
    waiting_for_key()

# Fonction pour attendre l'appui d'une touche avant de démarrer
def waiting_for_key():
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                waiting = False

# Fonction pour redémarrer le jeu
def reset_game():
    global score, next_wave, boss1_spawned, boss2_spawned
    all_sprites.empty()
    enemies.empty()
    bullets.empty()
    lasers.empty()
    player.rect.centerx = screen_width // 2
    player.rect.bottom = screen_height - 10
    player.health = 3
    all_sprites.add(player)
    score = 0
    next_wave = True
    boss1_spawned = False
    boss2_spawned = False
    show_start_screen()

# Compte à rebours
def show_countdown():
    for i in range(3, 0, -1):
        screen.blit(background_img, (0, 0))
        draw_text(screen, f"{i}", 96, screen_width // 2 - 20, screen_height // 2 - 50, red)
        pygame.display.flip()
        pygame.time.delay(1000)

# Boucle principale
running = True
paused = False
clock = pygame.time.Clock()
next_wave = True
boss1_spawned = False
boss2_spawned = False

show_start_screen()
show_countdown()

while running:
    # Gestion des événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                paused = not paused
            elif event.key == pygame.K_r:
                reset_game()
            elif event.key == pygame.K_SPACE:
                player.shoot()

    if not paused:
        # Mise à jour des sprites
        all_sprites.update()

        # Vérifier si le joueur est touché par un laser ennemi
        hits = pygame.sprite.spritecollide(player, lasers, True)
        if hits:
            player.take_damage()

        # Vérifier les collisions des balles avec les ennemis
        hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
        for hit in hits:
            score += 400

        # Vérifier les collisions des balles avec les boss
        if boss1_spawned:
            hits = pygame.sprite.spritecollide(boss, bullets, True)
            for hit in hits:
                boss.take_damage(10)
                score += 400

        if boss2_spawned:
            hits = pygame.sprite.spritecollide(boss2, bullets, True)
            for hit in hits:
                boss2.take_damage(10)
                score += 400

        # Vérifier si le joueur n'a plus de vie
        if player.get_health() <= 0:
            show_game_over_screen()

        # Vérifier les conditions pour faire apparaître les boss
        if score >= 5000 and not boss1_spawned:
            boss = Boss(screen_width // 2 - 100, 50, boss_img, 1000)
            all_sprites.add(boss)
            boss_group.add(boss)
            boss1_spawned = True
        elif score >= 10000 and not boss2_spawned:
            boss2 = Boss(screen_width // 2 - 100, 50, boss2_img, 1500)
            all_sprites.add(boss2)
            boss_group.add(boss2)
            boss2_spawned = True

        # Si un boss est apparu, vérifier s'il a été éliminé
        if boss1_spawned and boss.health <= 0:
            boss1_spawned = False
            next_wave = True
            boss.kill()
        elif boss2_spawned and boss2.health <= 0:
            boss2_spawned = False
            next_wave = True
            boss2.kill()

        # Si une vague d'ennemis est terminée, créer une nouvelle vague
        if next_wave and not (boss1_spawned or boss2_spawned):
            create_enemies()
            next_wave = False

    # Affichage à l'écran
    screen.blit(background_img, (0, 0))
    all_sprites.draw(screen)
    draw_text(screen, f"Score: {score}", 36, 10, 10, white)

    # Affichage des vies du joueur
    for i in range(player.get_health()):
        screen.blit(heart_img, (screen_width - 40 - i * 40, 10))

    # Affichage de la barre de vie du boss
    if boss1_spawned and boss.health > 0:
        boss.draw_health_bar()
    if boss2_spawned and boss2.health > 0:
        boss2.draw_health_bar()

    # Pause
    if paused:
        draw_text(screen, "PAUSE", 48, screen_width // 2 - 80, screen_height // 2 - 25, red)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
