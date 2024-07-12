import pygame
import random
from PIL import Image

# Initialiser Pygame
pygame.init()

# Constantes du jeu
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_WIDTH = 50  # Largeur du joueur
PLAYER_HEIGHT = 70  # Hauteur du joueur
GRAVITY = 0.5
JUMP_STRENGTH = 10
DOUBLE_JUMP_STRENGTH = 7  # Force de double saut réduite
SPEED = 5
OBSTACLE_GAP = 800
PLATFORM_GAP = 1000
TRAMPOLINE_ACTIVATION_HEIGHT = 10

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Fonction pour charger les frames du GIF
def load_gif_frames(filename):
    frames = []
    gif = Image.open(filename)
    for frame in range(0, gif.n_frames):
        gif.seek(frame)
        frame_image = gif.convert("RGBA")
        frame_data = frame_image.tobytes("raw", "RGBA")
        frame_surface = pygame.image.fromstring(frame_data, frame_image.size, "RGBA")
        frames.append(pygame.transform.scale(frame_surface, (PLAYER_WIDTH, PLAYER_HEIGHT)))
    return frames

# Classe pour le joueur
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.frames = load_gif_frames('run.gif')
        self.image = self.frames[0]  # Définir l'image initiale du joueur à la première frame du GIF
        self.rect = self.image.get_rect()
        self.rect.x = 100
        self.rect.y = SCREEN_HEIGHT - PLAYER_HEIGHT
        self.change_y = 0
        self.is_jumping = False
        self.can_double_jump = True  # Indique si le joueur peut effectuer un double saut
        self.frame_index = 0  # Indice de la frame actuelle pour l'animation
        self.animation_speed = 5  # Vitesse de l'animation
        self.animation_counter = 0  # Compteur pour gérer la vitesse de l'animation

    def update(self):
        self.calc_grav()
        self.rect.y += self.change_y

        if self.rect.y >= SCREEN_HEIGHT - PLAYER_HEIGHT:
            self.rect.y = SCREEN_HEIGHT - PLAYER_HEIGHT
            self.is_jumping = False
            self.can_double_jump = True  # Réinitialiser la possibilité de double saut

        # Gérer l'animation
        self.animation_counter += 1
        if self.animation_counter >= self.animation_speed:
            self.animation_counter = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.image = self.frames[self.frame_index]

    def calc_grav(self):
        if self.change_y == 0:
            self.change_y = 1
        else:
            self.change_y += GRAVITY

    def jump(self):
        if not self.is_jumping:
            self.change_y = -JUMP_STRENGTH
            self.is_jumping = True
        elif self.can_double_jump:
            self.change_y = -DOUBLE_JUMP_STRENGTH
            self.can_double_jump = False  # Marquer que le double saut a été utilisé

# Classe de base pour les plateformes
class Platform(pygame.sprite.Sprite):
    def __init__(self, width, height):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(BLACK)
        self.rect = self.image.get_rect()
        self.rect.y = random.randint(150, SCREEN_HEIGHT - 100)
        self.rect.width = width
        self.rect.height = height

    def update(self):
        self.rect.x -= SPEED
        if self.rect.right < 0:
            self.kill()

# Classe pour les obstacles
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.y = SCREEN_HEIGHT - self.rect.height
        self.rect.x = SCREEN_WIDTH

    def update(self):
        self.rect.x -= SPEED
        if self.rect.right < 0:
            self.kill()

# Classe pour les trampolines
class Trampoline(pygame.sprite.Sprite):
    def __init__(self, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.y = SCREEN_HEIGHT - self.rect.height
        self.rect.x = SCREEN_WIDTH

    def update(self):
        self.rect.x -= SPEED
        if self.rect.right < 0:
            self.kill()

# Classe pour le jeu principal
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Jeu de Plateforme")
        self.clock = pygame.time.Clock()
        self.running = True
        self.paused = False

        # Chargement et redimensionnement de l'image Game Over
        self.game_over_image = pygame.image.load('darksouls.jpg').convert()
        self.game_over_image = pygame.transform.scale(self.game_over_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Chargement et redimensionnement de l'image de fond du jeu
        self.background_image = pygame.image.load('ori.jpg').convert()
        self.background_image = pygame.transform.scale(self.background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

        # Chargement de l'image du trampoline avec transparence
        self.trampoline_image = pygame.image.load('bumper.png').convert_alpha()
        self.trampoline_image = pygame.transform.scale(self.trampoline_image, (50, 50))  # Redimensionner selon les besoins

        # Chargement de l'image des obstacles avec transparence
        self.obstacle_image = pygame.image.load('pokey.png').convert_alpha()
        self.obstacle_image = pygame.transform.scale(self.obstacle_image, (50, 50))  # Redimensionner selon les besoins

        self.all_sprites = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.trampolines = pygame.sprite.Group()

        self.player = Player()
        self.all_sprites.add(self.player)

        self.last_obstacle_time = pygame.time.get_ticks()
        self.last_platform_time = pygame.time.get_ticks()
        self.last_trampoline_time = pygame.time.get_ticks()

        self.distance = 0
        self.font = pygame.font.Font(None, 36)

    def reset(self):
        self.all_sprites.empty()
        self.obstacles.empty()
        self.platforms.empty()
        self.trampolines.empty()

        self.player = Player()
        self.all_sprites.add(self.player)

        self.last_obstacle_time = pygame.time.get_ticks()
        self.last_platform_time = pygame.time.get_ticks()
        self.last_trampoline_time = pygame.time.get_ticks()

        self.distance = 0
        self.paused = False

    def spawn_obstacle(self):
        obstacle = Obstacle(self.obstacle_image)
        if not pygame.sprite.spritecollideany(obstacle, self.trampolines):  # Vérifier si la position est libre de trampolines
            self.all_sprites.add(obstacle)
            self.obstacles.add(obstacle)

    def spawn_platform(self):
        platform = Platform(random.randint(50, 150), random.randint(5, 10))
        platform.rect.x = SCREEN_WIDTH
        self.all_sprites.add(platform)
        self.platforms.add(platform)

    def spawn_trampoline(self):
        trampoline = Trampoline(self.trampoline_image)
        if not pygame.sprite.spritecollideany(trampoline, self.obstacles):  # Vérifier si la position est libre d'obstacles
            self.all_sprites.add(trampoline)
            self.trampolines.add(trampoline)

    def run(self):
        while self.running:
            self.events()
            if not self.paused:
                self.update()
                self.draw()
                self.clock.tick(60)
                self.distance += SPEED / 10
                self.spawn_obstacles_with_gap()
                self.spawn_platforms_with_gap()
                self.spawn_trampolines_with_gap()
            else:
                self.draw_pause_menu()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.player.jump()
                elif event.key == pygame.K_p:
                    self.paused = True

    def update(self):
        self.all_sprites.update()

        # Gestion des collisions avec les obstacles
        obstacle_hits = pygame.sprite.spritecollide(self.player, self.obstacles, False)
        if obstacle_hits:
            self.game_over()

        # Gestion des collisions avec les plateformes
        platform_hits = pygame.sprite.spritecollide(self.player, self.platforms, False)
        if platform_hits:
            platform = platform_hits[0]
            self.player.rect.y = platform.rect.top - PLAYER_HEIGHT
            self.player.change_y = 0
            self.player.is_jumping = False
            self.player.can_double_jump = True  # Réinitialiser la possibilité de double saut sur une plateforme

        # Gestion des collisions avec les trampolines
        trampoline_hits = pygame.sprite.spritecollide(self.player, self.trampolines, False)
        if trampoline_hits:
            trampoline = trampoline_hits[0]
            if self.player.rect.bottom < trampoline.rect.centery:  # Sauter sur le trampoline
                self.player.rect.bottom = trampoline.rect.top
                self.player.change_y = -JUMP_STRENGTH * 1.5
                self.player.can_double_jump = True  # Réinitialiser la possibilité de double saut

    def draw(self):
        self.screen.blit(self.background_image, (0, 0))  # Dessiner l'image de fond
        self.all_sprites.draw(self.screen)
        distance_text = self.font.render(f"Distance: {int(self.distance)}", 1, BLACK)
        self.screen.blit(distance_text, (10, 10))
        pygame.display.flip()

    def draw_pause_menu(self):
        self.screen.fill(WHITE)
        font = pygame.font.Font(None, 74)
        text = font.render("Pause", 1, BLACK)
        self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))

        font = pygame.font.Font(None, 36)
        continue_text = font.render("Appuyez sur P pour continuer", 1, BLACK)
        restart_text = font.render("Appuyez sur R pour recommencer", 1, BLACK)
        quit_text = font.render("Appuyez sur Q pour quitter", 1, BLACK)

        self.screen.blit(continue_text, (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 100))
        self.screen.blit(quit_text, (SCREEN_WIDTH // 2 - quit_text.get_width() // 2, SCREEN_HEIGHT // 2 + 150))

        pygame.display.flip()

        self.pause_events()

    def pause_events(self):
        while self.paused:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.paused = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        self.paused = False
                    elif event.key == pygame.K_r:
                        self.reset()
                    elif event.key == pygame.K_q:
                        self.running = False
                        self.paused = False

    def game_over(self):
        self.screen.blit(self.game_over_image, (0, 0))  # Afficher l'image Game Over en arrière-plan

        font = pygame.font.Font(None, 74)
        text = font.render("Game Over", 1, WHITE)  # Texte en blanc
        self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))

        score_text = self.font.render(f"Score final: {int(self.distance)}", 1, WHITE)  # Score en blanc
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 + text.get_height()))

        restart_text = self.font.render("Appuyez sur R pour recommencer", 1, WHITE)  # Texte en blanc
        quit_text = self.font.render("Appuyez sur Q pour quitter", 1, WHITE)  # Texte en blanc

        self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + text.get_height() + 50))
        self.screen.blit(quit_text, (SCREEN_WIDTH // 2 - quit_text.get_width() // 2, SCREEN_HEIGHT // 2 + text.get_height() + 100))

        pygame.display.flip()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.reset()
                        return
                    elif event.key == pygame.K_q:
                        self.running = False
                        return

    def spawn_obstacles_with_gap(self):
        now = pygame.time.get_ticks()
        if now - self.last_obstacle_time > OBSTACLE_GAP:
            self.last_obstacle_time = now
            self.spawn_obstacle()

    def spawn_platforms_with_gap(self):
        now = pygame.time.get_ticks()
        if now - self.last_platform_time > PLATFORM_GAP:
            self.last_platform_time = now
            self.spawn_platform()

    def spawn_trampolines_with_gap(self):
        now = pygame.time.get_ticks()
        if now - self.last_trampoline_time > PLATFORM_GAP * 2:  # Changer la fréquence d'apparition des trampolines
            self.last_trampoline_time = now
            self.spawn_trampoline()

# Fonction principale pour démarrer le jeu
def main():
    game = Game()
    game.run()

    pygame.quit()

if __name__ == "__main__":
    main()


