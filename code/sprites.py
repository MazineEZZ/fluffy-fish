import pygame
from settings import *
from random import choice, randint

class BG(pygame.sprite.Sprite):
    def __init__(self, groups, scale_factor):
        super().__init__(groups)
        self.sprite_type = "background"

        # Image
        bg_image = pygame.image.load("graphics/environment/Sea.png").convert()

        # Image scaling
        bg_width, bg_height = bg_image.get_width() * scale_factor, bg_image.get_height() * scale_factor
        full_sized_bg = pygame.transform.scale(bg_image, (bg_width, bg_height))

        # Image logic
        self.image = pygame.Surface((bg_width * 2, bg_height))
        self.image.blit(full_sized_bg, (0, 0))
        self.image.blit(full_sized_bg, (bg_width, 0))

        # position
        self.rect = self.image.get_rect(topleft=(0,0))
        self.pos = pygame.math.Vector2(self.rect.topleft)

    def update(self, dt, speed=None):
        self.pos.x -= 280 * dt
        if self.rect.centerx <= 0:
            self.pos.x = 0
        self.rect.x = round(self.pos.x)
    
class Ground(pygame.sprite.Sprite):
    def __init__(self, groups, scale_factor):
        super().__init__(groups)
        self.sprite_type = "ground"

        # Image
        ground_surf = pygame.image.load("graphics/environment/Sea_ground.png").convert_alpha()
        self.image = pygame.transform.scale(ground_surf, pygame.math.Vector2(ground_surf.get_size()) * scale_factor)

        # Position
        self.rect = self.image.get_rect(bottomleft=(0, HEIGHT))
        self.pos = pygame.math.Vector2(self.rect.topleft)

        # Mask
        self.mask = pygame.mask.from_surface(self.image)
    
    def update(self, dt, speed):
        self.pos.x -= 340 * dt
        if self.rect.x + self.rect.w - WIDTH <= 0:
            self.pos.x = 0
        self.rect.x = round(self.pos.x)

class Fish(pygame.sprite.Sprite):
    def __init__(self, groups, scale_factor, skins):
        super().__init__(groups)
        self.sprite_type = "fish"
        self.skins = skins
        self.scale_factor = scale_factor

        # Image
        self.import_frames()
        self.frame_index = 0
        self.image = self.frames[self.frame_index]

        # Rect
        self.rect = self.image.get_rect(midleft=(WIDTH/20, HEIGHT/2))
        self.pos = pygame.math.Vector2(self.rect.topleft)

        # Movement
        self.gravity = 600
        self.direction = 0

        # Mask
        self.mask = pygame.mask.from_surface(self.image)

        # Sound
        self.jump_sound = pygame.mixer.Sound('sounds/Jump_sound.wav')
        self.jump_sound.set_volume(0.2)

    def import_frames(self):
        self.frames = []
        for i in range(3):
            surf = pygame.image.load(f"graphics/fish/fish {i}.png")
            scaled_surf = pygame.transform.scale(surf, pygame.math.Vector2(surf.get_size()) * self.scale_factor)
            self.frames.append(scaled_surf)
    
    def applied_gravity(self, dt):
        self.direction += self.gravity * dt
        self.pos.y += self.direction * dt
        self.rect.y = round(self.pos.y)
    
    def jump(self, volume_sound):
        self.direction = -300
        self.jump_sound.set_volume(volume_sound)
        self.jump_sound.play()

    def animate(self, dt):
        self.frame_index += 15 * dt
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

    def rotate(self):
        rotated_plane = pygame.transform.rotozoom(self.image, -self.direction * 0.09, 1).convert_alpha()
        self.image = rotated_plane
        self.mask = pygame.mask.from_surface(self.image)

    def change_skins(self):
        for i in range(len(self.skins)):
            if self.skins[i]:
                skin = pygame.image.load(f"graphics/fish/skins/Skin {i}.png")
                self.skin = pygame.transform.scale(skin, pygame.math.Vector2(skin.get_width(), skin.get_height()) * self.scale_factor)

        self.image.blit(self.skin, (0, 0))

    def update(self, dt, speed):
        self.applied_gravity(dt)
        self.animate(dt)
        self.change_skins()
        self.rotate()

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, groups, scale_factor):
        super().__init__(groups)
        self.sprite_type = "obstacle"
        self.passed = False

        # Image
        orientation = choice(('up', 'down'))
        surf = pygame.image.load(f'graphics/obstacles/{choice((0, 1))}.png').convert_alpha()
        self.image = pygame.transform.scale(surf, pygame.math.Vector2(surf.get_size()) * scale_factor)
        
        # Image flipping
        x = WIDTH + randint(40, 100)
        if orientation == 'up':
            y = HEIGHT + randint(10, 50)
            self.rect = self.image.get_rect(midbottom=(x, 5 + HEIGHT))
        else:
            y = 0 + randint(-50, -10)
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect = self.image.get_rect(midtop=(x, -5))
        
        # Position
        self.pos = pygame.math.Vector2(self.rect.topleft)

        # Mask
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt, speed):
        self.pos.x -= speed * dt
        self.rect.x = round(self.pos.x)
        if self.rect.right <= -self.image.get_width() - 20:
            self.kill()

class Menu(pygame.sprite.Sprite):
    def __init__(self, groups, scale_factor):
        super().__init__(groups)
        # Image
        self.import_frames(scale_factor)
        self.frame_index = 0
        self.image = self.frames[self.frame_index]

        # Rect
        self.rect = self.image.get_rect(center=(WIDTH/2, HEIGHT/2))

    def import_frames(self, scale_factor):
        self.frames = []
        for i in range(7):
            surf = pygame.image.load(f"graphics/ui/Menu/menu {i}.png")
            scaled_surf = pygame.transform.scale(surf, pygame.math.Vector2(surf.get_size()) * scale_factor)
            self.frames.append(scaled_surf)

    def animate(self, dt):
        self.frame_index += 15 * dt
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

    def update(self, dt):
        self.animate(dt)

class Button:
    def __init__(self, name, x_pos, y_pos, width, height, picture_path, scale_factor):
        # Image & Rect
        picture = pygame.image.load(picture_path).convert_alpha()
        self.image = pygame.transform.scale(picture, pygame.math.Vector2(picture.get_width(), picture.get_height()) * scale_factor)
        self.rect = self.image.get_rect(center=(x_pos, y_pos))

        # General info
        self.name = name
    
    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Coins(pygame.sprite.Sprite):
    def __init__(self, groups, scale_factor):
        super().__init__(groups)
        self.sprite_type = "coin"
        self.passed = False

        # Image
        self.image = pygame.image.load("graphics/obtainables/coin.png")
        
        # Image flipping
        y = randint(200, HEIGHT-200)
        x = randint(HEIGHT-75, HEIGHT-50)
        self.rect = self.image.get_rect(midtop=(x, y))
        
        # Position
        self.pos = pygame.math.Vector2(self.rect.topleft)

        # Mask
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt, speed):
        self.pos.x -= speed * dt
        self.rect.x = round(self.pos.x)
        if self.rect.right <= -self.image.get_width() - 20:
            self.kill()
