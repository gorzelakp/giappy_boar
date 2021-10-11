import pygame
import sys
import random

from datetime import datetime

from utils import (DEFAULT_GRAVITY, RES_X, RES_Y, FONT_PATH, FLOOR_PATH, PRESS_SPACE_PATH,
                   SPAWN_PIPE_DELAY, WELCOME_PATH, FLAP_SOUND, DEATH_SOUND, SCORE_SOUND, 
                   STARTING_POS_X, STARTING_POS_Y, JUMP_VALUE, PIPE_SPEED, BIRD_FLAP_DELAY,
                   FONT_COLOR)

class GiappyBoar:
    def __init__(self):

        pygame.init()

        self.gravity = DEFAULT_GRAVITY

        self.bird_movement = 0
        self.score = 0
        self.high_score = 0
        self.bird_index = 0
        self.floor_x_pos = 0

        self.pipe_list =  []
        self.pipe_heights = [400, 600, 800]

        self.game_active = True
        self.can_score = True

        self.clock = pygame.time.Clock()
        self.game_font = pygame.font.Font(FONT_PATH, 40)

    # TODO: PRZENIEŚĆ I PRZEROBIĆ TE TE FUNKCJE
    def draw_floor(self):
        self.game_surface.blit(self.floor_surface, (self.floor_x_pos, RES_Y-150))
        self.game_surface.blit(self.floor_surface, (self.floor_x_pos + RES_X, RES_Y-150)) 

    def create_pipe(self):
        random_pipe_pos = random.choice(self.pipe_heights)
        bottom_pipe = self.pipe_surface.get_rect(midtop = (RES_Y-300, random_pipe_pos))
        top_pipe = self.pipe_surface.get_rect(midbottom = (RES_Y-300, random_pipe_pos - 300))

        return bottom_pipe, top_pipe

    def move_pipes(self):
        for pipe in self.pipe_list:
            pipe.centerx -= PIPE_SPEED
        visible_pipes = [pipe for pipe in self.pipe_list if pipe.right > -50]
        return visible_pipes

    def draw_pipes(self):
        for pipe in self.pipe_list:
            if pipe.bottom >= RES_Y:
                self.game_surface.blit(self.pipe_surface, pipe)
            else:
                flip_pipe = pygame.transform.flip(self.pipe_surface, False, True)
                self.game_surface.blit(flip_pipe, pipe)

    def check_collision(self):
        for pipe in self.pipe_list:
            if self.bird_rect.colliderect(pipe):
                self.death_sound.play()
                self.can_score = True
                return False
        if self.bird_rect.top <= -100 or self.bird_rect.bottom >= 900:
            self.death_sound.play()
            self.can_score = True
            return False
        return True

    def rotate_bird(self):
        return pygame.transform.rotate(self.bird_surface, -self.bird_movement * 3)

    def bird_animation(self):
        new_bird = self.bird_frames[self.bird_index]
        new_bird_rect = new_bird.get_rect(center = (STARTING_POS_X, self.bird_rect.centery))
        return new_bird, new_bird_rect

    def score_display(self, game_state):
        if game_state == 'main_game':
            score_surface = self.game_font.render(str(int(self.score)), True, FONT_COLOR)
            score_rect = score_surface.get_rect(center = (288, 100))
            self.game_surface.blit(score_surface, score_rect)
        elif game_state == 'game_over':
            score_surface = self.game_font.render(f'Wynik: {int(self.score)}', True, FONT_COLOR)
            score_rect = score_surface.get_rect(center = (288, 100))
            self.game_surface.blit(score_surface, score_rect)

            high_score_surface = self.game_font.render(f'Top: {int(self.high_score)}', True, FONT_COLOR)
            high_score_rect = high_score_surface.get_rect(center = (288, 850))
            self.game_surface.blit(high_score_surface, high_score_rect)

    def update_score(self):
        if self.score > self.high_score:
            self.high_score = self.score
        return self.high_score

    def pipe_score_check(self):        
        if self.pipe_list:
            for pipe in self.pipe_list:
                if 95 < pipe.centerx < 105 and self.can_score:
                    self.score += 1
                    self.score_sound.play()
                    self.can_score = False
                if pipe.centerx < 0:
                    self.can_score = True

    def load_correct_assets(self):
        if datetime.utcnow().hour < 18:
            self.BG_PATH = 'assets/background-day.png'
            self.PIPE_PATH = 'assets/pipe-green.png'
        else:
            self.BG_PATH = 'assets/background-night.png'
            self.PIPE_PATH = 'assets/pipe-red.png'

    ########################################################################################################

    def init_surfaces(self):
        self.game_surface = pygame.display.set_mode((RES_X, RES_Y))

        self.load_correct_assets()
        self.bg_surface = pygame.transform.scale2x(pygame.image.load(self.BG_PATH).convert())
        self.pipe_surface = pygame.transform.scale2x(pygame.image.load(self.PIPE_PATH))

        self.floor_surface = pygame.transform.scale2x(pygame.image.load(FLOOR_PATH).convert())

        self.welcome_surface = pygame.image.load(WELCOME_PATH).convert_alpha()
        self.welcome_rect = self.welcome_surface.get_rect(center = (RES_X/2, RES_Y/2-100))

        self.press_space_surface = pygame.image.load(PRESS_SPACE_PATH).convert_alpha()
        self.press_space_rect = self.press_space_surface.get_rect(center = (RES_X/2, RES_Y/2))

        # ZMIENIC
        bird_downflap = pygame.transform.scale2x(pygame.image.load('assets/1.png').convert_alpha())
        bird_midflap = pygame.transform.scale2x(pygame.image.load('assets/2.png').convert_alpha())
        bird_upflap = pygame.transform.scale2x(pygame.image.load('assets/3.png').convert_alpha())
        self.bird_frames = [bird_downflap, bird_midflap, bird_upflap]
        self.bird_surface = self.bird_frames[self.bird_index]
        self.bird_rect = self.bird_surface.get_rect(center = (STARTING_POS_X, STARTING_POS_Y))

    def init_player_events_and_timers(self):
        self.SPAWNPIPE = pygame.USEREVENT
        self.BIRDFLAP = pygame.USEREVENT + 1

        pygame.time.set_timer(self.BIRDFLAP, BIRD_FLAP_DELAY)
        pygame.time.set_timer(self.SPAWNPIPE, SPAWN_PIPE_DELAY)

    def init_sounds(self):
        self.flap_sound = pygame.mixer.Sound(FLAP_SOUND)
        self.death_sound = pygame.mixer.Sound(DEATH_SOUND)
        self.score_sound = pygame.mixer.Sound(SCORE_SOUND)

    def perform_jump(self):
        self.bird_movement = 0 
        self.bird_movement -= JUMP_VALUE 
        self.flap_sound.play()

    def restart_game_after_death(self):
        self.game_active = True
        self.pipe_list.clear()
        self.bird_rect.center = (STARTING_POS_X, STARTING_POS_Y)
        self.bird_movement = 0
        self.score = 0

    def hanle_game_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and self.game_active:
                    self.perform_jump()
                if event.key == pygame.K_SPACE and not self.game_active:
                    self.restart_game_after_death()
            if event.type == self.SPAWNPIPE:
                self.pipe_list.extend(self.create_pipe())
            if event.type == self.BIRDFLAP:
                if self.bird_index < 2:
                    self.bird_index += 1
                else:
                    self.bird_index = 0
                self.bird_surface, self.bird_rect = self.bird_animation()

    def handle_current_situation(self):
        self.game_surface.blit(self.bg_surface, (0, 0))

        if self.game_active:
            self.bird_movement += self.gravity
            rotated_bird = self.rotate_bird()
            self.bird_rect.centery += self.bird_movement
            self.game_surface.blit(rotated_bird, self.bird_rect)
            self.game_active = self.check_collision()

            # Pipes
            self.pipe_list = self.move_pipes()
            self.draw_pipes()

            # Score
            self.pipe_score_check()
            self.score_display('main_game')
        else:
            self.game_surface.blit(self.welcome_surface, self.welcome_rect)
            self.game_surface.blit(self.press_space_surface, self.press_space_rect)
            self.high_score = self.update_score()
            self.score_display('game_over')

        # Floor
        self.floor_x_pos -= 1
        self.draw_floor()
        if self.floor_x_pos <= -RES_X:
            self.floor_x_pos = 0

        pygame.display.update()
        self.clock.tick(120)

    def init_main_loop(self):
        while True:
            self.hanle_game_events()
            self.handle_current_situation()
                
    def run(self):
        self.init_surfaces()
        self.init_player_events_and_timers()
        self.init_sounds()
        self.init_main_loop()


giappy_boar = GiappyBoar()
giappy_boar.run()
