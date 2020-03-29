import pygame
import numpy as np
import sys
import copy
import gym

from gym import spaces
from settings import *
from player_class import *
from enemy_class import *


pygame.init()
vec = pygame.math.Vector2

# Constants
N_DISCRETE_ACTIONS = 4  # Nothing, up, down, left, right
EMPTY = 0
WALL = 1
COIN = 2
PLAYER = 3
ENEMY = 4

# ACT_NOTHING = 0
ACT_UP = 0
ACT_DOWN = 1
ACT_LEFT = 2
ACT_RIGHT = 3


class App(gym.Env):
    def __init__(self):
        super(App, self).__init__()
        self.screen = None
        self.clock = pygame.time.Clock()

        self.action_space = spaces.Discrete(N_DISCRETE_ACTIONS)
        self.observation_space = spaces.Box(
            # low=0, high=4, shape=(4,), dtype=np.uint8)
            low=0, high=4, shape=(COLS*ROWS + 2,), dtype=np.uint8)
        # low=0, high=max(COLS, ROWS), shape=(10,), dtype=np.uint8)

        self.done = False
        self.running = True
        self.state = 'playing'
        self.cell_width = MAZE_WIDTH//COLS
        self.cell_height = MAZE_HEIGHT//ROWS
        self.walls = []
        self.coins = []
        self.enemies = []
        self.e_pos = []
        self.p_pos = None

        self.grid = np.zeros((COLS, ROWS), dtype=int)
        # print(self.grid)

        self.load()
        self.player = Player(self, vec(self.p_pos))
        self.make_enemies()

        self.time_elapsed = 0
        self.old_score = 0
        # self.run()

    def run(self):
        while self.running:
            if self.state == 'start':
                self.start_events()
                self.start_update()
                self.start_draw()
            elif self.state == 'playing':
                self.action = ACT_NOTHING
                # self.playing_events()
                # self.step(self.action)
                # self.playing_update()
                # self.playing_draw()
            elif self.state == 'game over':
                self.game_over_events()
                self.game_over_update()
                self.game_over_draw()
            else:
                self.running = False
            # self.clock.tick(FPS)

            # pygame.time.wait(1)
        pygame.quit()
        sys.exit()

    def gen_obs(self):
        """obs = []

        obs.append(self.player.grid_pos[0])
        obs.append(self.player.grid_pos[1])

        for e in self.enemies:
            obs.append(e.grid_pos[0])
            obs.append(e.grid_pos[1])

        obs = np.array(obs, dtype=int)
        # print("Shape:", obs.shape)#

        # np.concatenate(obs, )
        print("Shape:", self.grid.shape)

        n_grid = self.grid.flatten()
        # print("Shape:", n_grid.shape)
        obs = np.append(obs, n_grid)
        # print("Shape:", obs.shape)"""

        # n_grid = n_grid.reshape((ROWS, COLS, 1))
        # print("Shape:", n_grid.shape)
        # print("Grid Shape:", n_grid.shape)
        # print("Obs Space Shape:", self.observation_space.shape)

        px = int(self.player.grid_pos[0])
        py = int(self.player.grid_pos[1])

        n_grid = np.copy(self.grid).flatten()
        n_grid = np.append([px, py], n_grid)
        #print("Shape:", n_grid.shape)

        # return n_grid
        # up = self.grid[px][py + 1]
        # down = self.grid[px][py - 1]
        # left = self.grid[px + 1][py]
        # right = self.grid[px - 1][py]

        return n_grid

############################ HELPER FUNCTIONS ##################################

    def draw_text(self, words, screen, pos, size, colour, font_name, centered=False):
        font = pygame.font.SysFont(font_name, size)
        text = font.render(words, False, colour)
        text_size = text.get_size()
        if centered:
            pos[0] = pos[0]-text_size[0]//2
            pos[1] = pos[1]-text_size[1]//2
        screen.blit(text, pos)

    def load(self):
        self.background = pygame.image.load('maze.png')
        self.background = pygame.transform.scale(
            self.background, (MAZE_WIDTH, MAZE_HEIGHT))

        # Opening walls file
        # Creating walls list with co-ords of walls
        # stored as  a vector
        with open("walls.txt", 'r') as file:
            for yidx, line in enumerate(file):
                for xidx, char in enumerate(line):
                    if char == "1":
                        self.walls.append(vec(xidx, yidx))
                        self.grid[xidx, yidx] = WALL
                    elif char == "C":
                        self.coins.append(vec(xidx, yidx))
                        self.grid[xidx, yidx] = COIN
                    elif char == "P":
                        self.p_pos = [xidx, yidx]
                    elif char in ["2", "3", "4", "5"]:
                        self.e_pos.append([xidx, yidx])
                    elif char == "B":
                        pygame.draw.rect(self.background, BLACK, (xidx*self.cell_width, yidx*self.cell_height,
                                                                  self.cell_width, self.cell_height))

    def make_enemies(self):
        for idx, pos in enumerate(self.e_pos):
            self.enemies.append(Enemy(self, vec(pos), idx))

    def draw_grid(self):
        for x in range(WIDTH//self.cell_width):
            pygame.draw.line(self.background, GREY, (x*self.cell_width, 0),
                             (x*self.cell_width, HEIGHT))
        for x in range(HEIGHT//self.cell_height):
            pygame.draw.line(self.background, GREY, (0, x*self.cell_height),
                             (WIDTH, x*self.cell_height))
        # for coin in self.coins:
        #     pygame.draw.rect(self.background, (167, 179, 34), (coin.x*self.cell_width,
        #                                                        coin.y*self.cell_height, self.cell_width, self.cell_height))

    def reset(self):
        # print("Score:", self.player.current_score)
        self.done = False
        self.time_elapsed = 0

        self.player.lives = 3
        self.player.current_score = 0
        self.player.grid_pos = vec(self.player.starting_pos)
        self.player.pix_pos = self.player.get_pix_pos()
        self.player.direction *= 0
        for enemy in self.enemies:
            enemy.grid_pos = vec(enemy.starting_pos)
            enemy.pix_pos = enemy.get_pix_pos()
            enemy.direction *= 0

        self.coins = []
        with open("walls.txt", 'r') as file:
            for yidx, line in enumerate(file):
                for xidx, char in enumerate(line):
                    if char == 'C':
                        self.coins.append(vec(xidx, yidx))
                        self.grid[xidx, yidx] = COIN

        self.state = "playing"
        obs = self.gen_obs()
        # print("OBS SHAPE:", obs.shape)
        return obs


########################### INTRO FUNCTIONS ####################################

    def start_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.state = 'playing'

    def start_update(self):
        pass

    def start_draw(self):
        self.screen.fill(BLACK)
        self.draw_text('PUSH SPACE BAR', self.screen, [
                       WIDTH//2, HEIGHT//2-50], START_TEXT_SIZE, (170, 132, 58), START_FONT, centered=True)
        self.draw_text('1 PLAYER ONLY', self.screen, [
                       WIDTH//2, HEIGHT//2+50], START_TEXT_SIZE, (44, 167, 198), START_FONT, centered=True)
        self.draw_text('HIGH SCORE', self.screen, [4, 0],
                       START_TEXT_SIZE, (255, 255, 255), START_FONT)
        pygame.display.update()

########################### PLAYING FUNCTIONS ##################################
    def print_state(self):
        # print(self.walls)
        # print(self.coins)
        for x in range(0, COLS):
            for y in range(0, ROWS):
                print(int(self.grid[x, y]), end="")
            print()

    def print_obs(self):
        obs = self.gen_obs()

        for x in range(0, COLS):
            for y in range(0, ROWS):
                print(int(obs[y + (COLS*x)]), end="")
            print()

    def step(self, action):
        # self.clock.tick(FPS)
        # self.action = ACT_NOTHING
        # self.playing_events()
        # self.step(self.action)
        # self.playing_update()

        # self.playing_draw()
        self.playing_events()
        self.time_elapsed += 1

        if self.time_elapsed >= TIMESTEPS:
            self.done = True

        # Execute one time step within the environment
        if action == ACT_LEFT:
            self.player.move(vec(-1, 0))
        if action == ACT_RIGHT:
            self.player.move(vec(1, 0))
        if action == ACT_UP:
            self.player.move(vec(0, -1))
        if action == ACT_DOWN:
            # self.print_state()
            self.player.move(vec(0, 1))

        self.playing_update()

        if self.done == True:
            print("Score: ", self.player.current_score)

        reward = self.player.current_score - self.old_score
        self.old_score = self.player.current_score

        return self.gen_obs(), reward, self.done, {}

    def playing_events(self):
        no_action = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    # self.print_state()
                    self.print_obs()

                # exit()
            """if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.step(ACT_LEFT)
                    no_action = False
                if event.key == pygame.K_RIGHT:
                    self.step(ACT_RIGHT)
                    no_action = False
                if event.key == pygame.K_UP:
                    self.step(ACT_UP)
                    no_action = False
                if event.key == pygame.K_DOWN:
                    self.print_state()
                    self.step(ACT_DOWN)
                    no_action = False

        if no_action:
            self.step(ACT_NOTHING)
        """

    def playing_update(self):
        self.player.update()
        for enemy in self.enemies:
            enemy.update()

        for enemy in self.enemies:
            if enemy.grid_pos == self.player.grid_pos:
                self.remove_life()

    def playing_draw(self):
        self.screen.fill(BLACK)
        self.screen.blit(
            self.background, (TOP_BOTTOM_BUFFER//2, TOP_BOTTOM_BUFFER//2))
        self.draw_coins()
        # self.draw_grid()
        self.draw_text('CURRENT SCORE: {}'.format(self.player.current_score),
                       self.screen, [60, 0], 18, WHITE, START_FONT)
        self.draw_text('HIGH SCORE: 0', self.screen, [
                       WIDTH//2+60, 0], 18, WHITE, START_FONT)
        self.player.draw()
        for enemy in self.enemies:
            enemy.draw()
        pygame.display.update()

    def remove_life(self):
        """self.player.lives -= 1
        if self.player.lives == 0:
            self.state = "game over"
        else:
            self.player.grid_pos = vec(self.player.starting_pos)
            self.player.pix_pos = self.player.get_pix_pos()
            self.player.direction *= 0
            for enemy in self.enemies:
                enemy.grid_pos = vec(enemy.starting_pos)
                enemy.pix_pos = enemy.get_pix_pos()
                enemy.direction *= 0"""
        self.done = True

    def draw_coins(self):
        for coin in self.coins:
            pygame.draw.circle(self.screen, (124, 123, 7),
                               (int(coin.x*self.cell_width)+self.cell_width//2+TOP_BOTTOM_BUFFER//2,
                                int(coin.y*self.cell_height)+self.cell_height//2+TOP_BOTTOM_BUFFER//2), 5)

########################### GAME OVER FUNCTIONS ################################

    def game_over_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.reset()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False

    def game_over_update(self):
        pass

    def game_over_draw(self):
        self.screen.fill(BLACK)
        quit_text = "Press the escape button to QUIT"
        again_text = "Press SPACE bar to PLAY AGAIN"
        self.draw_text("GAME OVER", self.screen, [
                       WIDTH//2, 100],  52, RED, "arial", centered=True)
        self.draw_text(again_text, self.screen, [
                       WIDTH//2, HEIGHT//2],  36, (190, 190, 190), "arial", centered=True)
        self.draw_text(quit_text, self.screen, [
                       WIDTH//2, HEIGHT//1.5],  36, (190, 190, 190), "arial", centered=True)
        pygame.display.update()

    def render(self, mode='human', close=False):
        if self.screen == None:
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT))

        if self.clock == None:
            self.clock = pygame.time.Clock()

        self.playing_draw()

    def close(self):
        pygame.quit()
