import pygame
import random
import math
from settings import *

vec = pygame.math.Vector2


class Enemy:
    def __init__(self, app, pos, number):
        self.app = app
        self.grid_pos = pos
        self.starting_pos = [pos.x, pos.y]
        self.pix_pos = self.get_pix_pos()
        self.radius = int(self.app.cell_width//2.3)
        self.number = number
        self.colour = self.set_colour()
        self.direction = vec(0, 0)
        self.personality = self.set_personality()
        self.target = None
        self.speed = self.set_speed()
        self.corner = False
        self.grid = [[0 for x in range(28)] for x in range(30)]
        for cell in self.app.walls:
            if cell.x < 28 and cell.y < 30:
                self.grid[int(cell.y)][int(cell.x)] = 1
        self.past_direction = vec(0,0)

    def update(self):
        self.target = self.set_target()
        if self.target != self.grid_pos:
            self.pix_pos += self.direction * self.speed
            if self.time_to_move():
                self.move()

        # Setting grid position in reference to pix position
        self.grid_pos[0] = (self.pix_pos[0]-TOP_BOTTOM_BUFFER +
                            self.app.cell_width//2)//self.app.cell_width+1
        self.grid_pos[1] = (self.pix_pos[1]-TOP_BOTTOM_BUFFER +
                            self.app.cell_height//2)//self.app.cell_height+1

    def draw(self):
        pygame.draw.circle(self.app.screen, self.colour,
                           (int(self.pix_pos.x), int(self.pix_pos.y)), self.radius)

    def set_speed(self):
        if self.personality in ["speedy", "not_scared", "random"]:
            speed = 2
        else:
            speed = 1
        return speed

    def set_target(self):
        #print("self: " + str(self.app.player.grid_pos))
        if self.personality == "speedy":
            return self.app.player.grid_pos
        elif self.personality == "fast":
            if math.sqrt(math.pow((self.app.player.grid_pos[0] - self.grid_pos[0]), 2) + math.pow((self.app.player.grid_pos[1] - self.grid_pos[1]), 2)) < 5:
                return self.app.player.grid_pos
            else:
                vect = None
                if self.app.player.direction == vec(1, 0):
                    #print("Right: " + str(vec((self.app.player.grid_pos[0] + 2) % (COLS - 2) + 1, self.app.player.grid_pos[1])))
                    vect =  vec((self.app.player.grid_pos[0] + 2) % (COLS - 2) + 1, self.app.player.grid_pos[1])
                elif self.app.player.direction == vec(-1, 0):
                    #print("Left: " + str(vec((self.app.player.grid_pos[0] - 2) % (COLS - 2) + 1, self.app.player.grid_pos[1])))
                    vect = vec((self.app.player.grid_pos[0] - 2) % (COLS - 2) - 1, self.app.player.grid_pos[1])
                elif self.app.player.direction == vec(0, 1):
                    #print("Down: " + str(vec(self.app.player.grid_pos[0], (self.app.player.grid_pos[1] + 2) % (ROWS - 1) + 1)))
                    vect = vec(self.app.player.grid_pos[0], (self.app.player.grid_pos[1] + 2) % (ROWS - 1))
                else:
                    #print("Up: " + str(vec(self.app.player.grid_pos[0], (self.app.player.grid_pos[1] - 2) % (ROWS - 1) + 1)))
                    vect = vec(self.app.player.grid_pos[0], (self.app.player.grid_pos[1] - 2) % (ROWS - 1))
                if(self.grid[int(vect[1])][int(vect[0])] == 1):
                    return self.app.player.grid_pos
                else:
                    return vect
        elif self.personality == "not_scared":
            if math.sqrt(math.pow((self.app.player.grid_pos[0] - self.grid_pos[0]), 2) + math.pow((self.app.player.grid_pos[1] - self.grid_pos[1]), 2)) < 3:
                self.personality = "scared"
                self.corner = False
            else:
                return self.app.player.grid_pos
        if self.personality == "scared":
            gridpos0 = self.grid_pos[0]
            gridpos1 = self.grid_pos[1]
            if (gridpos0 == 1 and gridpos1 == 1) or (gridpos0 == 1 and gridpos1 == ROWS - 1) or (gridpos0 == COLS - 2 and gridpos1 == 1) or (gridpos0 == COLS - 2 and gridpos1 == ROWS - 1):
                self.personality = "not_scared"
                return self.app.player.grid_pos
            else:
                if(not self.corner):
                    self.corner = True
                    if self.app.player.grid_pos[0] > COLS//2 and self.app.player.grid_pos[1] > ROWS//2:
                        return vec(1, 1)
                    if self.app.player.grid_pos[0] > COLS//2 and self.app.player.grid_pos[1] < ROWS//2:
                        return vec(1, ROWS-1)
                    if self.app.player.grid_pos[0] < COLS//2 and self.app.player.grid_pos[1] > ROWS//2:
                        return vec(COLS-2, 1)
                    else:
                        return vec(COLS-2, ROWS-1)
                else:
                    return self.target
            

    def time_to_move(self):
        if int(self.pix_pos.x+TOP_BOTTOM_BUFFER//2) % self.app.cell_width == 0:
            if self.direction == vec(1, 0) or self.direction == vec(-1, 0) or self.direction == vec(0, 0):
                return True
        if int(self.pix_pos.y+TOP_BOTTOM_BUFFER//2) % self.app.cell_height == 0:
            if self.direction == vec(0, 1) or self.direction == vec(0, -1) or self.direction == vec(0, 0):
                return True
        return False

    def move(self):
        if self.direction == vec(1, 0) or self.direction == vec(-1, 0):
            if (self.grid_pos[1] + 1 >= len(self.grid) or  self.grid[int(self.grid_pos[1] + 1)][int(self.grid_pos[0])]) == 1 and (self.grid_pos[1] - 1 < 0 or self.grid[int(self.grid_pos[1] - 1)][int(self.grid_pos[0])] == 1):
                return
        else:
            if (self.grid_pos[0] + 1 >= len(self.grid[0]) or self.grid[int(self.grid_pos[1])][int(self.grid_pos[0] + 1)] == 1) and (self.grid_pos[0] - 1 < 0 or self.grid[int(self.grid_pos[1])][int(self.grid_pos[0] - 1)] == 1):
                return
        if self.personality == "random":
            self.direction = self.get_random_direction()
        if self.personality == "fast":
            self.direction = self.get_path_direction(self.target)
        if self.personality == "speedy":
            self.direction = self.get_path_direction(self.target)
        if self.personality == "scared":
            self.direction = self.get_path_direction(self.target)
        if self.personality == "not_scared":
            self.direction = self.get_path_direction(self.target)
        
        if (-self.direction[0]) == self.past_direction[0] and (-self.direction[1]) == self.past_direction[1]:
            self.direction = self.past_direction
        else:
            self.past_direction = self.direction

        contdir = 0
        while (self.grid_pos[1] + self.direction[1] >= len(self.grid)) or (self.grid_pos[0] + self.direction[0] >= len(self.grid[0])) or (self.grid_pos[1] + self.direction[1] < 0) or (self.grid_pos[0] + self.direction[0] < 0) or self.grid[int(self.grid_pos[1] + self.direction[1])][int(self.grid_pos[0] + self.direction[0])] == 1:
            if contdir == 0:
                self.direction = vec(1,0)
            elif contdir == 1:
                self.direction = vec(0,1)
            elif contdir == 2:
                self.direction = vec(-1,0)
            else:
                self.direction = vec(0,-1)
            contdir += 1


    def get_path_direction(self, target):
        next_cell = self.find_next_cell_in_path(target)
        xdir = next_cell[0] - self.grid_pos[0]
        ydir = next_cell[1] - self.grid_pos[1]
        return vec(xdir, ydir)

    def find_next_cell_in_path(self, target):
        path = self.BFS([int(self.grid_pos.x), int(self.grid_pos.y)], [
                        int(target[0]), int(target[1])])
        return path[1]

    def BFS(self, start, target):
        queue = [start]
        path = []
        visited = []
        visited.append(vec(self.grid_pos[0] - self.direction[0], self.grid_pos[1] - self.direction[1]))
        while queue:
            current = queue[0]
            queue.remove(queue[0])
            visited.append(current)
            if current == target:
                break
            else:
                neighbours = [[0, -1], [1, 0], [0, 1], [-1, 0]]
                for neighbour in neighbours:
                    if neighbour[0]+current[0] >= 0 and neighbour[0] + current[0] < len(self.grid[0]):
                        if neighbour[1]+current[1] >= 0 and neighbour[1] + current[1] < len(self.grid):
                            next_cell = [neighbour[0] + current[0], neighbour[1] + current[1]]
                            if next_cell not in visited:
                                if self.grid[next_cell[1]][next_cell[0]] != 1:
                                    queue.append(next_cell)
                                    path.append({"Current": current, "Next": next_cell})
        shortest = [target]
        while target != start:
            for step in path:
                if step["Next"] == target:
                    target = step["Current"]
                    shortest.insert(0, step["Current"])
        return shortest

    def get_random_direction(self):
        while True:
            number = random.randint(-2, 1)
            if number == -2:
                x_dir, y_dir = 1, 0
            elif number == -1:
                x_dir, y_dir = 0, 1
            elif number == 0:
                x_dir, y_dir = -1, 0
            else:
                x_dir, y_dir = 0, -1
            next_pos = vec(self.grid_pos.x + x_dir, self.grid_pos.y + y_dir)
            if next_pos not in self.app.walls:
                break
        return vec(x_dir, y_dir)

    def get_pix_pos(self):
        return vec((self.grid_pos.x*self.app.cell_width)+TOP_BOTTOM_BUFFER//2+self.app.cell_width//2,
                   (self.grid_pos.y*self.app.cell_height)+TOP_BOTTOM_BUFFER//2 +
                   self.app.cell_height//2)

    def set_colour(self):
        if self.number == 0:
            return (43, 78, 203)
        if self.number == 1:
            return (197, 200, 27)
        if self.number == 2:
            return (189, 29, 29)
        if self.number == 3:
            return (215, 159, 33)

    def set_personality(self):
        if self.number == 0:
            return "speedy"
        elif self.number == 1:
            return "fast"
        elif self.number == 2:
            return "random"
        else:
            return "not_scared"
