import pygame, sys, json, math
from sprites import BG, Ground, Fish, Obstacle, Menu, Button, Coins
from settings import *

class Game:
    def __init__(self):

        # Pygame initialization
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode(SIZE)
        self.clock = pygame.time.Clock()
        self.active = False # Status of the Game
        pygame.display.set_caption("Fluffy Fish")
        pygame.display.set_icon(pygame.image.load("graphics/Icon/Fish_Icon.png").convert_alpha())

        # Sprite group
        self.all_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()
        self.coin_sprites = pygame.sprite.Group()

        # Scale factor
        bg_height = pygame.image.load('graphics/environment/Sea.png').get_height()
        self.scale_factor = HEIGHT/bg_height # For scaling the images

        ## Sprite setup
        BG(self.all_sprites, self.scale_factor)
        Ground([self.all_sprites, self.collision_sprites], self.scale_factor * 1.5)
        self.fish = Fish(self.all_sprites, self.scale_factor * 2, [True])
        self.difficulty_speed = 400

        # Background_sprite
        self.background_sprite = pygame.sprite.Group()
        for i in range(len(self.all_sprites)):
            if self.all_sprites.sprites()[i].sprite_type == "background":
                self.background_sprite.add(self.all_sprites.sprites()[i])

        # Timer
        self.obstacle_timer = pygame.USEREVENT + 1
        pygame.time.set_timer(self.obstacle_timer, 1400)

        # Text
        try:
            self.Bfont = pygame.font.Font("graphics/font/04B_30__.ttf", 50)
            self.font = pygame.font.Font("graphics/font/04B_30__.ttf", 30)
            self.Sfont = pygame.font.Font("graphics/font/04B_30__.ttf", 20)
        except:
            self.Bfont = pygame.font.Font("Arial", 50)
            self.font = pygame.font.Font("Arial", 30)
            self.Sfont = pygame.font.SysFont("Arial", 20)

        self.points = 0
        self.score = 0

        # Read the file and check the high_score
        try:
            with open("code/high_score.json") as high_score_file:
                self.high_score = json.load(high_score_file) 
        except:
            self.high_score = 0

        # Read the coins file and check the coins score
        try:
            with open("code/coins_score.json") as coins_file:
                self.coins = json.load(coins_file) 
        except:
            self.coins = 0

        self.obstacle_passed = False

        # Menu
        self.menu = pygame.sprite.GroupSingle()
        Menu(self.menu, self.scale_factor/1.1)

        # Souns
        self.hurt_sound = pygame.mixer.Sound("sounds/Hurt_sound.mp3")
        self.powerup = pygame.mixer.Sound("sounds/Powerup_sound.mp3")
        self.volume = 0.1
        self.volume_sound = 0.1

        # Skins
        self.equipped_skin = [True, False, False, False] # Equipped skin
        self.skin_value = [0, 100, 200, 300]
        self.skins_list = []
        
        for i in range(1, len(self.equipped_skin)):
            skin = pygame.image.load(f"graphics/fish/skins/Skin {i}.png").convert_alpha()
            skin = pygame.transform.scale(skin, pygame.math.Vector2(skin.get_width(), skin.get_height()) * self.scale_factor)
            skin_rect = skin.get_rect(topleft=(WIDTH/2 - skin.get_width()/2 + 30, 0))
            self.skins_list.append((skin, skin_rect, self.skin_value[i]))

        self.owned_skins = {}
        for i in range(len(self.skins_list)):
            self.owned_skins[i] = False

    def store_screen(self):        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.menu_screen(True)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    for index, skin in enumerate(self.skins_list):
                        mouse_sprite = pygame.sprite.Sprite()
                        mouse_sprite.image = pygame.Surface((1, 1))
                        mouse_sprite.rect = pygame.Rect(event.pos[0], event.pos[1], 1, 1)

                        temp_skin = pygame.sprite.Sprite()
                        temp_skin.image = skin[0]
                        temp_skin.rect = skin[1]

                        if pygame.sprite.collide_mask(mouse_sprite, temp_skin):
                            if not self.owned_skins[index]:
                                if self.coins >= skin[2]:
                                    self.coins -= skin[2]

                                    with open("code/coins_score.json", "w") as coins_file:
                                        json.dump(self.coins, coins_file)

                                    for i in range(len(self.equipped_skin)):
                                        self.equipped_skin[i] = False
                                    self.equipped_skin[index+1] = True
                                    self.owned_skins[index] = True
                                else:
                                    print("not enough money!")
                            else:
                                for i in range(len(self.equipped_skin)):
                                    self.equipped_skin[i] = False
                                self.equipped_skin[index+1] = True
                                self.owned_skins[index] = True

            # Background
            self.screen.fill("#2569a6")
            pygame.draw.rect(self.screen, "#144774", [0, 0, WIDTH, HEIGHT/10])
            pygame.draw.rect(self.screen, "#195489", [0, HEIGHT/10, WIDTH, 10])
            music_text = self.Bfont.render("Store", True, WHITE)
            music_text = self.screen.blit(music_text, (WIDTH/2-music_text.get_width()/2, (HEIGHT/10)/2-music_text.get_height()/2))

            # Skins
            y = HEIGHT/10 + 50
            for i, skin in enumerate(self.skins_list):
                skin[1].y = y

                text = self.Sfont.render(f"{skin[2]}", True, BLACK)
                text_rect = text.get_rect()
                text_rect.x = skin[1].x + skin[1].w/2 - text.get_width()
                text_rect.y = skin[1].y + skin[1].h/2 - text.get_height()

                self.screen.blit(text, text_rect)
                if self.owned_skins[i]:
                    pygame.draw.line(self.screen, RED, (text_rect.x, text_rect.y), (text_rect.x + text_rect.w, text_rect.y + text_rect.h), 5)

                if self.equipped_skin[1+i]:
                    checkmark = pygame.image.load("graphics/fish/skins/Checkmark.png").convert_alpha()
                    self.screen.blit(checkmark, (skin[1].x + skin[1].w/2 , skin[1].y + skin[1].h/2 - checkmark.get_height()))

                self.screen.blit(skin[0], skin[1])
                y += 150

            pygame.mixer.music.set_volume(self.volume)
            pygame.display.update()

    def settings_screen(self):
        class Slider:
            def __init__(self, x, y, width, height, color):
                self.rect = pygame.Rect(x, y, width, height)
                self.color = color

            def draw(self, screen, border_radius, color):
                pygame.draw.rect(screen, self.color, self.rect, 0, border_radius)
                pygame.draw.rect(screen, color, pygame.Rect(self.rect.x+5, self.rect.y+ 7.5, self.rect.w-10, self.rect.h/4), 0, border_radius)

        # Knob class
        class Knob(Slider):
            def __init__(self, x, y, width, height, color):
                super().__init__(x, y, width, height, color)
                self.dragging = False

            def draw(self, screen, border_radius, color):
                pygame.draw.rect(screen, self.color, self.rect, 0, border_radius)
                pygame.draw.rect(screen, color, pygame.Rect(self.rect.x+5, self.rect.y+ 5, self.rect.w-10, self.rect.h/2+2.5), 0, border_radius)

            def move_x(self, pos, slider_rect):
                mouse_x = max(slider_rect.x-self.rect.w/2, min(slider_rect.x + slider_rect.w - self.rect.w + self.rect.w/2, pos[0]))
                self.rect.x = mouse_x

            def sound_value(self, slider_rect):
                value = ((self.rect.x + self.rect.w/2 - slider_rect.x)/(slider_rect.w))*100
                sound_value = value/100
                return sound_value

        # Knob info
        knob_width, knob_height = 25, 25

        slider_width, slider_height = 300, 20
        change_x, change_y = 0, -150
        slider_x, slider_y = (WIDTH/2-slider_width/2) + change_x, (HEIGHT/2-slider_height/2) + change_y

        sliders = []
        slider_type =  ["volume", "sound"]

        for i in range(2):
            slider = Slider(slider_x, slider_y, slider_width, slider_height, "#dcae81")
            if slider_type[i] == "volume":
                knob = Knob(slider_x + (slider_width * self.volume) - knob_width/2, slider_y + slider_height/2 - knob_height/2, knob_width, knob_height, "#997653")
            elif slider_type[i] == "sound":
                knob = Knob(slider_x + (slider_width * self.volume_sound) - knob_width/2, slider_y + slider_height/2 - knob_height/2, knob_width, knob_height, "#997653")
            sliders.append([slider, knob, slider_type[i]])
            slider_y += 100

        while True:
            dt = self.clock.tick(FPS) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.menu_screen(True)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    for slider in sliders:
                        if slider[1].rect.collidepoint(event.pos):
                            slider[1].dragging = True
                        else:
                            slider[1].dragging = False
                if event.type == pygame.MOUSEMOTION:
                    for slider in sliders:
                        Left_click = pygame.mouse.get_pressed()[0]
                        if slider[1].dragging and Left_click:
                            slider[1].move_x(event.pos, slider[0].rect)

            self.screen.fill("#2569a6")
            pygame.draw.rect(self.screen, "#144774", [0, 0, WIDTH, HEIGHT/10])
            pygame.draw.rect(self.screen, "#195489", [0, HEIGHT/10, WIDTH, 10])
            music_text = self.Bfont.render("Music", True, WHITE)
            music_text = self.screen.blit(music_text, (WIDTH/2-music_text.get_width()/2, (HEIGHT/10)/2-music_text.get_height()/2))

            for slider in sliders:
                # Volume
                if slider[2] == slider_type[0]:
                    volume_text = self.Sfont.render(f"{round(self.volume*100)}", True, BLACK)
                    self.screen.blit(volume_text, (WIDTH-75, slider[1].rect.y))
                    self.volume = slider[1].sound_value(slider[0].rect)
                
                # Volume sound
                if slider[2] == slider_type[1]:
                    volume_text = self.Sfont.render(f"{round(self.volume_sound*100)}", True, BLACK)
                    self.screen.blit(volume_text, (WIDTH-75, slider[1].rect.y))
                    self.volume_sound = slider[1].sound_value(slider[0].rect)

                slider[0].draw(self.screen, int(slider_width/10), "#bd9065")
                slider[1].draw(self.screen, int(knob_width/2), "white")

            pygame.mixer.music.set_volume(self.volume)

            pygame.display.update()

    def menu_screen(self, play_music=False):
        # Music
        if not play_music:
            pygame.mixer.music.load("music/MenuScreen_Music.mp3")
            while pygame.mixer.music.get_busy(): # Loads the music a lot faster
                pygame.time.Clock().tick(10)
        if not play_music:
            pygame.mixer.music.play(loops=-1)
        pygame.mixer.music.set_volume(self.volume)

        # Text, scaling and resizing info
        text_surf = pygame.image.load("graphics/ui/Text.png")

        angle = 0
        rotation_direction = 1
        rotation_speed = 0.2
        max_rotation_angle = 5
        scaling_factor = 1.15
        scaling_factor = 1
        scaling_direction = 1

        # Buttons
        button_name = {"play": 0,
                       "options": 1,
                       "store":2,
                       "exit": 3}

        for i, key in enumerate(button_name.keys()):
            button_name[key] = "graphics/ui/Buttons/button {}.png".format(i)

        buttons = []
        button_x = 250
        for key in button_name.keys():
            button = Button(key, WIDTH/2, button_x, 150, 50, button_name[key], self.scale_factor * 1.7)
            button_x += 125
            buttons.append(button)

        while True:
            dt = self.clock.tick(FPS) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for button in buttons:
                        if button.rect.collidepoint(event.pos):
                            if button.name == "play":
                                self.play_screen()
                            if button.name == "options":
                                self.settings_screen()
                            if button.name == "store":
                                self.store_screen()
                            if button.name == "exit":
                                pygame.quit()
                                sys.exit()
                if event.type == pygame.MOUSEMOTION:
                    for button in buttons:
                        if button.rect.collidepoint(event.pos):
                            pass

            ### Menu Game Logic
            self.screen.fill(BLACK)
            
            # Bakcground
            self.background_sprite.draw(self.screen)
            self.background_sprite.update(dt)

            # Buttons
            for button in buttons:
                button.draw(self.screen) # Continue on making the menu --

            ## resizing and scaling the text
            angle += rotation_speed * rotation_direction
            scaling_factor = 1 + 0.17 * math.sin(pygame.time.get_ticks() / 500) * scaling_direction * 0.9

            if scaling_factor >= 1.2:
                scaling_direction = -1
            elif scaling_factor <= 0.8:
                scaling_direction = 1

            if angle > max_rotation_angle or angle < -max_rotation_angle:
                rotation_direction = -rotation_direction

            scaled_factor = max(0.8, min(1.2, scaling_factor))
            rotated_text = pygame.transform.rotozoom(text_surf, angle, scaled_factor)
            rotated_text_rect = rotated_text.get_rect(center=(WIDTH/2, 100))

            self.screen.blit(rotated_text, rotated_text_rect)

            # Displaying the coin text
            coin_text = self.font.render(f"Coins: {self.coins}", True, BLACK)
            self.screen.blit(coin_text, (WIDTH-10-coin_text.get_width(), 10))

            pygame.display.update()

    def play_screen(self):
        # Music
        pygame.mixer.music.load("music/MainScreen_Music.mp3")
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.music.play(loops=-1)
        pygame.mixer.music.set_volume(self.volume)

        def collisions():
            if pygame.sprite.spritecollide(self.fish, self.collision_sprites, False, pygame.sprite.collide_mask)\
            or self.fish.rect.top <= 0:
                # Kills all the obstacles sprites
                for sprite in self.collision_sprites.sprites():
                    if sprite.sprite_type == "obstacle":
                        sprite.kill()

                self.hurt_sound.play()
                self.active = False
                self.fish.kill()

            # Checks for the score
            for obstacle in self.collision_sprites.sprites():
                if obstacle.rect.right < self.fish.rect.right and not self.obstacle_passed:
                    if obstacle.sprite_type == "obstacle":
                        obstacle.passed = True
                        self.points += 1
                else:
                    if obstacle.sprite_type == "obstacle":
                        obstacle.passed = False


            for coin in self.coin_sprites.sprites():
                if self.fish.rect.colliderect(coin.rect):
                    if pygame.sprite.collide_mask(self.fish, coin):
                        coin.kill()
                        self.coins += 1
                        self.powerup.set_volume(self.volume_sound)
                        self.powerup.play()
                        with open("code/coins_score.json", "w") as coins_file:
                            json.dump(self.coins, coins_file)

        def calculating__displaying_score(score): # __ means and _ means a space
            # Calculating the score
            self.score += self.points / 93
            self.points = 0

            # Calculating the High_score
            if self.score > self.high_score:
                self.high_score = self.score
                with open("code/high_score.json", "w") as high_score_file:
                    json.dump(self.high_score, high_score_file)

            # Score
            score_surf = self.font.render(f"{round(self.score)}", True, "Black")
            score_rect = score_surf.get_rect(midtop=(WIDTH/2,HEIGHT/20))

            # High_score
            high_score_surf = self.font.render(f"High Score: {round(self.high_score)}", True, "Black")
            high_score_rect = high_score_surf.get_rect(midtop=(WIDTH/2, HEIGHT/20))

            # Check the status
            if self.active:
                self.screen.blit(score_surf, score_rect)
            else:
                score_surf = self.font.render(f"Score: {round(self.score)}", True, "Black")
                score_rect = score_surf.get_rect(midtop=(WIDTH/2,HEIGHT/20))
                self.fish.kill()
                self.screen.blit(score_surf, (score_rect.x, HEIGHT/2 + self.menu.sprites()[0].rect.h/1.5))
                self.screen.blit(high_score_surf, (high_score_rect.x, HEIGHT/2 - self.menu.sprites()[0].rect.h/1.5 - high_score_rect.h))
                self.difficulty_speed = 400

        while True:
            self.hurt_sound.set_volume(self.volume_sound)
            # Delta time
            dt = self.clock.tick(FPS) / 1000

            # Checking the events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    with open("code/high_score.json", "w") as high_score_file:
                        json.dump(self.high_score, high_score_file)

                    with open("code/coins_score.json", "w") as coins_file:
                        json.dump(self.coins, coins_file)
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.active: 
                        self.fish.jump(self.volume_sound)
                    else:
                        self.points = 0
                        self.score = 0
                        self.fish = Fish(self.all_sprites, self.scale_factor / 2.5, self.equipped_skin)
                        self.active = True

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if self.active:
                            self.fish.jump(self.volume_sound)
                    if event.key == pygame.K_ESCAPE:
                        self.active = False
                        self.menu_screen()

                if event.type == self.obstacle_timer and self.active:
                    Obstacle([self.all_sprites, self.collision_sprites], self.scale_factor)
                    Coins([self.all_sprites, self.coin_sprites], self.scale_factor)
                    self.difficulty_speed += 5

            ## Main Game logic
            self.screen.fill("black")
            self.all_sprites.draw(self.screen)
            self.all_sprites.update(dt, self.difficulty_speed)
            calculating__displaying_score(self.score)

            if self.active:
                collisions()
            else:
                self.menu.draw(self.screen)
                self.menu.update(dt)

            pygame.display.update()

if __name__ == "__main__":
    game = Game()
    game.menu_screen()
