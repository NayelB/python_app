import pygame
import time
import random

# Initialiser Pygame
pygame.init()

# Définir les dimensions de la fenêtre de jeu
display_width = 1200
display_height = 720

# Définir les couleurs
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
gray = (50, 50, 50)

# Charger les images de la voiture, des obstacles (voitures et camions) et les redimensionner
carImg = pygame.image.load('car.png')
carImg_lights = pygame.image.load('car_lights.png')  # Image des phares
carImg = pygame.transform.scale(carImg, (112, 225))  # Augmenter la taille de la voiture de 50%
carImg_lights = pygame.transform.scale(carImg_lights, (112, 225))  # Redimensionner l'image des phares
car_width = carImg.get_rect().width
car_height = carImg.get_rect().height

obstacle_images = [
    pygame.transform.scale(pygame.image.load('obstacle_car.png'), (112, 225)),  # Augmenter la taille de l'obstacle voiture
    pygame.transform.scale(pygame.image.load('obstacle_truck.png'), (180, 360))  # Augmenter la taille de l'obstacle camion
]

# Charger et redimensionner les images des arbres et des panneaux de signalisation
treeImg = pygame.transform.scale(pygame.image.load('tree.png'), (75, 150))
signImg = pygame.transform.scale(pygame.image.load('sign.png'), (75, 150))

# Créer la fenêtre de jeu
gameDisplay = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('Course en voiture')

# Définir l'horloge pour contrôler la vitesse du jeu
clock = pygame.time.Clock()

# Variables pour le compteur de vitesse et le régime moteur
speed = 0
rpm = 0

# Définir les positions des voies en tenant compte de la largeur de la voiture
lanes = [200, 400, 600, 800, 1000]
lane_width = lanes[1] - lanes[0]
lane_centers = [lane + lane_width // 2 for lane in lanes]

# Fonction pour afficher la voiture avec les phares
def car(x, y, lights_on):
    if lights_on:
        gameDisplay.blit(carImg_lights, (x, y))
    else:
        gameDisplay.blit(carImg, (x, y))

# Fonction pour afficher les obstacles
def draw_obstacle(obstacle, obx, oby):
    gameDisplay.blit(obstacle, (obx, oby))

# Fonction pour afficher les arbres
def draw_tree(tx, ty):
    gameDisplay.blit(treeImg, (tx, ty))

# Fonction pour afficher les panneaux de signalisation
def draw_sign(sx, sy):
    gameDisplay.blit(signImg, (sx, sy))

# Fonction pour afficher le texte des objets
def text_objects(text, font):
    textSurface = font.render(text, True, black)
    return textSurface, textSurface.get_rect()

# Fonction pour afficher un message sur l'écran
def message_display(text):
    largeText = pygame.font.Font('freesansbold.ttf', 115)
    TextSurf, TextRect = text_objects(text, largeText)
    TextRect.center = ((display_width / 2), (display_height / 2))
    gameDisplay.blit(TextSurf, TextRect)
    pygame.display.update()
    time.sleep(2)
    game_loop()

# Fonction pour afficher le message de crash
def crash():
    message_display('Vous avez crashé!')

# Fonction pour afficher le score
def show_score(count):
    font = pygame.font.SysFont(None, 25)
    text = font.render(f"Score: {count}", True, black)
    gameDisplay.blit(text, (10, 10))  # Affichage du score en haut à gauche

# Fonction pour afficher la vitesse
def show_speed(speed):
    font = pygame.font.SysFont(None, 25)
    text = font.render(f"Vitesse: {speed} km/h", True, black)
    gameDisplay.blit(text, (20, display_height - 40))

# Fonction pour afficher le régime moteur
def show_rpm(rpm):
    font = pygame.font.SysFont(None, 25)
    text = font.render(f"Régime: {rpm} RPM", True, black)
    gameDisplay.blit(text, (20, display_height - 20))

# Fonction pour vérifier la collision entre deux obstacles
def check_collision(ob1, ob2):
    return ob1.colliderect(ob2)

# Fonction pour créer une liste d'obstacles en fonction de la difficulté
def create_obstacles(difficulty):
    obstacles = []
    num_obstacles = 0
    obstacle_speed = 0

    if difficulty == 'easy':
        num_obstacles = 2
        obstacle_speed = 5
    elif difficulty == 'medium':
        num_obstacles = 4
        obstacle_speed = 7
    elif difficulty == 'hard':
        num_obstacles = 6
        obstacle_speed = 9

    for _ in range(num_obstacles):
        ob_type = random.choice(obstacle_images)
        ob_width = ob_type.get_rect().width
        ob_height = ob_type.get_rect().height
        ob_startx = random.choice(lane_centers) - ob_width // 2
        ob_starty = random.randrange(-3000, -600)
        obstacles.append({
            'image': ob_type,
            'rect': pygame.Rect(ob_startx, ob_starty, ob_width, ob_height),
            'speed': obstacle_speed
        })

    return obstacles

# Fonction principale du jeu
def game_loop():
    x = lane_centers[1] - car_width // 2  # Commencer dans la deuxième voie
    y = (display_height * 0.8)
    x_change = 0
    y_change = 0

    # Initialisation de la vitesse à zéro
    speed = 0
    
    # Sélection de la difficulté et création des obstacles en fonction
    difficulty = game_intro()
    obstacles = create_obstacles(difficulty)

    score = 0
    lights_on = False  # État des phares

    # Positions initiales pour les arbres et les panneaux
    tree_positions = [[random.randrange(0, 120), random.randrange(-900, 0)] for _ in range(5)] + [[random.randrange(1080, display_width), random.randrange(-900, 0)] for _ in range(5)]
    sign_positions = [[random.randrange(1080, display_width), random.randrange(-900, 0)] for _ in range(2)]

    # Variables pour le calcul de la vitesse
    start_time = time.time()  # Temps de départ
    distance_traveled = 0     # Distance parcourue par la voiture

    # Variables pour le régime moteur
    rpm = 0
    acceleration = 0.1  # Exemple de valeur d'accélération

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    x_change = -5
                elif event.key == pygame.K_RIGHT:
                    x_change = 5
                elif event.key == pygame.K_UP:
                    y_change = -5
                elif event.key == pygame.K_DOWN:
                    y_change = 5
                elif event.key == pygame.K_SPACE:
                    lights_on = not lights_on  # Inverser l'état des phares

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    x_change = 0
                if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    y_change = 0

        x += x_change
        y += y_change

        # Garder la voiture dans les voies
        if x < lanes[0]:
            x = lanes[0]
        elif x + car_width > lanes[-1] + lane_width:
            x = lanes[-1] + lane_width - car_width

        gameDisplay.fill(gray)  # Fond de la route

        # Dessiner les bordures
        pygame.draw.rect(gameDisplay, green, [0, 0, 150, display_height])  # Bordure gauche
        pygame.draw.rect(gameDisplay, green, [1050, 0, 150, display_height])  # Bordure droite

        # Dessiner les lignes des voies
        for lane in lanes:
            pygame.draw.line(gameDisplay, white, (lane, 0), (lane, display_height), 5)

        # Dessiner les arbres et les panneaux
        for pos in tree_positions:
            draw_tree(pos[0], pos[1])
            pos[1] += 7  # Faire défiler les arbres
            if pos[1] > display_height:
                pos[1] = random.randrange(-900, 0)  # Réinitialiser la position de l'arbre

        for pos in sign_positions:
            draw_sign(pos[0], pos[1])
            pos[1] += 7  # Faire défiler les panneaux
            if pos[1] > display_height:
                pos[1] = random.randrange(-900, 0)  # Réinitialiser la position du panneau

        # Vérifier les collisions entre la voiture et les obstacles
        car_rect = pygame.Rect(x, y, car_width, car_height)
        for ob in obstacles:
            if check_collision(car_rect, ob['rect']):
                crash()

        # Mettre à jour la distance parcourue pour calculer la vitesse
        distance_traveled += abs(x_change) + abs(y_change)

        # Calculer la vitesse en km/h (par exemple)
        elapsed_time = time.time() - start_time
        if elapsed_time > 0:
            speed = int(distance_traveled / elapsed_time * 3.6)  # Conversion m/s en km/h (3.6)

        # Mettre à jour le régime moteur en fonction de la vitesse actuelle
        if speed > 0:
            rpm = int(speed * 100)  # Exemple de calcul simplifié du régime moteur en fonction de la vitesse

        # Afficher les éléments du jeu
        for ob in obstacles:
            draw_obstacle(ob['image'], ob['rect'].x, ob['rect'].y)
            ob['rect'].y += ob['speed']  # Vitesse des obstacles
            if ob['rect'].y > display_height:
                ob['rect'].x = random.choice(lane_centers) - ob['rect'].width // 2
                ob['rect'].y = random.randrange(-3000, -600)

        car(x, y, lights_on)
        
        # Vérifier si la voiture a dépassé un obstacle
        for ob in obstacles:
            if ob['rect'].y > display_height and ob['rect'].y < display_height + ob['speed']:
                score += 1

        show_score(score)
        show_speed(speed)
        show_rpm(rpm)

        pygame.display.update()
        clock.tick(60)

# Fonction pour afficher le menu d'introduction
def game_intro():
    intro = True
    speed = 7  # Vitesse par défaut

    while intro:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse = pygame.mouse.get_pos()
                if 250 < mouse[0] < 450 and 400 < mouse[1] < 500:
                    return 'easy'
                elif 500 < mouse[0] < 700 and 400 < mouse[1] < 500:
                    return 'medium'
                elif 750 < mouse[0] < 950 and 400 < mouse[1] < 500:
                    return 'hard'

        gameDisplay.fill(gray)
        largeText = pygame.font.Font('freesansbold.ttf', 115)
        TextSurf, TextRect = text_objects("Course en voiture", largeText)
        TextRect.center = ((display_width / 2), (display_height / 2 - 100))
        gameDisplay.blit(TextSurf, TextRect)

        mouse = pygame.mouse.get_pos()

        # Boutons pour sélectionner la difficulté
        button("Facile", 250, 400, 200, 100, green, black)
        button("Moyen", 500, 400, 200, 100, red, black)
        button("Difficile", 750, 400, 200, 100, red, black)

        pygame.display.update()
        clock.tick(15)

# Fonction pour dessiner des boutons
def button(msg, x, y, w, h, ic, ac):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    if x + w > mouse[0] > x and y + h > mouse[1] > y:
        pygame.draw.rect(gameDisplay, ac, (x, y, w, h))
        if click[0] == 1:
            return True
    else:
        pygame.draw.rect(gameDisplay, ic, (x, y, w, h))

    smallText = pygame.font.Font("freesansbold.ttf", 20)
    textSurf, textRect = text_objects(msg, smallText)
    textRect.center = ((x + (w / 2)), (y + (h / 2)))
    gameDisplay.blit(textSurf, textRect)

    return False

# Démarrer le jeu
game_intro()
game_loop()
pygame.quit()
quit()
