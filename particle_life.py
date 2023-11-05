import pygame
from buttons import *
import random
import math
from settings import *
import numpy as np
import json



class ParticleLife():
    def __init__(self):



        self.particle_n = 600
        self.setup()
        self.build_ui()
        self.loop_time = 10000
        self.last_loop_time = pygame.time.get_ticks() - self.loop_time

        self.click_time = 200
        self.last_click_time = pygame.time.get_ticks() - self.click_time

        self.save_loop = False
        self.random_loop = False

        self.font = pygame.font.Font(None, 16)


    def setup(self):

        self.yellows_pos = []
        self.yellows_v = []

        self.reds_pos = []
        self.reds_v = []

        self.greens_pos = []
        self.greens_v = []

        n = self.particle_n / 3
        for i in range(int(n)):
            pos = (random.randint(50, 550), random.randint(50, 550))
            self.yellows_pos.append([pos[0], pos[1]])
            self.yellows_v.append([0, 0])

            pos = (random.randint(50, 550), random.randint(50, 550))
            self.reds_pos.append([pos[0], pos[1]])
            self.reds_v.append([0, 0])

            pos = (random.randint(50, 550), random.randint(50, 550))
            self.greens_pos.append([pos[0], pos[1]])
            self.greens_v.append([0, 0])

        self.yellows_pos = np.array(self.yellows_pos)
        self.yellows_v = np.array(self.yellows_v)

        self.reds_pos = np.array(self.reds_pos)
        self.reds_v = np.array(self.reds_v)

        self.greens_pos = np.array(self.greens_pos)
        self.greens_v = np.array(self.greens_v)


    def build_ui(self):
        self.sliders = [
            Slider((750, 50), (100, 10), 0.5, 0, 2, 'yellow'),
            Slider((750, 70), (100, 10), 0.5, 0, 2, 'red'),
            Slider((750, 90), (100, 10), 0.5, 0, 2, 'green'),

            Slider((750, 130), (100, 10), 0.5, 0, 2, 'red'),
            Slider((750, 150), (100, 10), 0.5, 0, 2, 'yellow'),
            Slider((750, 170), (100, 10), 0.5, 0, 2, 'green'),

            Slider((750, 210), (100, 10), 0.5, 0, 2, 'green'),
            Slider((750, 230), (100, 10), 0.5, 0, 2, 'yellow'),
            Slider((750, 250), (100, 10), 0.5, 0, 2, 'red'),

            Slider((750, 280), (100, 10), 0.5, 0, 2, 'purple'),
        ]

        self.buttons = [
            Button((750, 300), (75, 20), 'respawn'),
            Button((750, 330), (60, 20), 'save'),
            Button((700, 330), (40, 20), 'load'),
            Button((700, 390), (80, 20), 'loop saves'),
            Button((700, 420), (80, 20), 'loop rand.')
        ]

        self.text_boxes = [
            TextBox((770, 360), (50, 20)),
            TextBox((700, 360), (50, 20)),
            TextBox((700, 300), (40, 15))
        ]


    def input(self):
        mouse_pres = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        current_time = pygame.time.get_ticks()

        if current_time - self.last_click_time >= self.click_time and mouse_pres[0]:

            # slider input
            for slider in self.sliders:
                if slider.container_rect.collidepoint(mouse_pos):
                    slider.move_slider(mouse_pos)
            # text box click
                for text_box in self.text_boxes:
                    if text_box.rect.collidepoint(mouse_pos):
                        text_box.active = True
                    elif mouse_pos[0]:
                        text_box.active = False


            # button input
            # respawn
            if self.buttons[0].button_rect.collidepoint(mouse_pos):
                self.particle_n = int(self.text_boxes[2].text)
                self.setup()
            # save
            elif self.buttons[1].button_rect.collidepoint(mouse_pos):
                self.saveSettings()
            # load
            elif self.buttons[2].button_rect.collidepoint(mouse_pos):
                self.loadSettings()
            # save loop
            elif self.buttons[3].button_rect.collidepoint(mouse_pos):
                current_time = pygame.time.get_ticks()
                if current_time - self.last_click_time >= self.click_time:
                    if not self.save_loop:
                        self.save_loop = True
                        self.buttons[3].color = 'green'
                        self.random_loop = False
                        self.buttons[4].color = 'grey'

                    else:
                        self.save_loop = False
                        self.buttons[3].color = 'grey'

            # rand loop
            elif self.buttons[4].button_rect.collidepoint(mouse_pos):
                current_time = pygame.time.get_ticks()
                if current_time - self.last_click_time >= self.click_time:
                    if not self.random_loop:
                        self.random_loop = True
                        self.buttons[4].color = 'green'
                        self.save_loop = False
                        self.buttons[3].color = 'grey'
                    else:
                        self.random_loop = False
                        self.buttons[4].color = 'grey'


            self.last_click_time = current_time


    def rule(self, particles1_pos, particles1_v, particles2_pos, g):
        a = particles1_pos
        av = particles1_v
        b = particles2_pos

        # Calculate the distance squared
        d_squared = np.sum((a[:, np.newaxis] - b) ** 2, axis=2)
        d = np.sqrt(d_squared)


        # Optimize the calculation of F
        with np.errstate(divide='ignore', invalid='ignore'):
            F = np.where(d > 80, 0, g / d)

        F[np.isinf(F)] = 0  # Handle division by zero resulting in inf
        F[np.isnan(F)] = 0  # Handle NaN values
        F += np.where(d < 5, 2 / d, 0)



        # Calculate the total force using np.nansum
        total_force = np.nansum(F[:, :, np.newaxis] * (a[:, np.newaxis] - b), axis=1)

        # Update the velocity
        av = (av + total_force) * self.velocity_vac

        # Update the positions of 'a' and keep them within [0, 500] range
        av[(a <= 50) | (a >= 550)] *= -2
        # av[(a >= 550)] = 50
        # av[(a <= 50)] = 550
        #
        # a[(a <= 50)] = 550
        # a[(a >= 550)] = 50

        a = np.clip(a + av, 50, 550)

        return a


    def referenceRule(self, particles1, particles2, g):
        for i in range(len(particles1)):
            fx = 0
            fy = 0
            for j in range(len(particles2)):
                a = particles1[i]
                b = particles2[j]
                dx = a.x - b.x
                dy = a.y - b.y
                d = math.sqrt(dx*dx + dy*dy)
                if d > 0 and d < 80:
                    F = g * 1/d
                    fx += (F * dx)
                    fy += (F * dy)

                a.vx = (a.vx + fx) * 0.8
                a.vy = (a.vy + fy) * 0.8
                a.x += a.vx
                a.y += a.vy

                if a.x <= 50 or a.x >= 550:
                    a.vx *= -2
                if a.y <= 50 or a.y >= 550:
                    a.vy *= -2


    def randomSaves(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_loop_time >= self.loop_time:

            if 1 == random.randint(1,4):
                self.setup()

            with open('saved_settings.json', 'r') as save_file:
                data = json.load(save_file)
                l = len(data)
                r = random.randint(0, l)
                c = 0
                for name in data:
                    if name == '':
                        pass


                    elif c == r:
                        self.save_text_render = self.font.render(f'save: {str(name)}', True, 'white')
                        self.loadSettings(name=name)
                        self.last_loop_time = current_time
                        break
                    c +=1


    def randomLoop(self):

        current_time = pygame.time.get_ticks()
        if current_time - self.last_loop_time >= self.loop_time:


            if 1 == random.randint(1,4):
                self.setup()

            self.sliders[0].calculate_button_centerx(random.uniform(-0.500, 0.500))
            self.sliders[1].calculate_button_centerx(random.uniform(-0.500, 0.500))
            self.sliders[2].calculate_button_centerx(random.uniform(-0.500, 0.500))

            self.sliders[3].calculate_button_centerx(random.uniform(-0.500, 0.500))
            self.sliders[4].calculate_button_centerx(random.uniform(-0.500, 0.500))
            self.sliders[5].calculate_button_centerx(random.uniform(-0.500, 0.500))

            self.sliders[6].calculate_button_centerx(random.uniform(-0.500, 0.500))
            self.sliders[7].calculate_button_centerx(random.uniform(-0.500, 0.500))
            self.sliders[8].calculate_button_centerx(random.uniform(-0.500, 0.500))

            self.sliders[9].calculate_button_centerx(random.uniform(0.1, 1.000))

            self.last_loop_time = current_time

    def saveSettings(self):
        settings = {
                'yy': self.yy,
                'yr': self.yr,
                'yg': self.yg,

                'rr': self.rr,
                'ry': self.ry,
                'rg': self.rg,

                'gg': self.gg,
                'gy': self.gy,
                'gr': self.gr,

                'g': self.velocity_vac
        }
        with open('saved_settings.json', 'r') as save_file:
            data = json.load(save_file)

            data[self.text_boxes[0].text] = settings

        with open('saved_settings.json', 'w') as save_file:
            json.dump(data, save_file)

    def loadSettings(self, name=None):

        with open('saved_settings.json', 'r') as save_file:
            data = json.load(save_file)
            if name == None:
                save = data[self.text_boxes[0].text]
            else:
                save = data[name]
            self.sliders[0].calculate_button_centerx(save['yy'])
            self.sliders[1].calculate_button_centerx(save['yr'])
            self.sliders[2].calculate_button_centerx(save['yg'])

            self.sliders[3].calculate_button_centerx(save['rr'])
            self.sliders[4].calculate_button_centerx(save['ry'])
            self.sliders[5].calculate_button_centerx(save['rg'])

            self.sliders[6].calculate_button_centerx(save['gg'])
            self.sliders[7].calculate_button_centerx(save['gy'])
            self.sliders[8].calculate_button_centerx(save['gr'])

            self.sliders[9].calculate_button_centerx(save['g'])

    def update(self, events):

        if self.save_loop:
            self.randomSaves()

        elif self.random_loop:
            self.randomLoop()

        for box in self.text_boxes:
            box.input(events)

        self.yy = self.sliders[0].get_value()
        self.yr = self.sliders[1].get_value()
        self.yg = self.sliders[2].get_value()

        self.rr = self.sliders[3].get_value()
        self.ry = self.sliders[4].get_value()
        self.rg = self.sliders[5].get_value()

        self.gg = self.sliders[6].get_value()
        self.gy = self.sliders[7].get_value()
        self.gr = self.sliders[8].get_value()

        self.velocity_vac = self.sliders[9].get_value()

        self.yellows_pos = self.rule(self.yellows_pos, self.yellows_v, self.yellows_pos, self.yy)
        self.yellows_pos = self.rule(self.yellows_pos, self.yellows_v, self.reds_pos, self.yr)
        self.yellows_pos = self.rule(self.yellows_pos, self.yellows_v, self.greens_pos, self.yg)

        self.reds_pos = self.rule(self.reds_pos, self.reds_v, self.reds_pos, self.rr)
        self.reds_pos = self.rule(self.reds_pos, self.reds_v, self.yellows_pos, self.ry)
        self.reds_pos = self.rule(self.reds_pos, self.reds_v, self.greens_pos, self.rg)

        self.greens_pos = self.rule(self.greens_pos, self.greens_v, self.greens_pos, self.gg)
        self.greens_pos = self.rule(self.greens_pos, self.greens_v, self.yellows_pos, self.gy)
        self.greens_pos = self.rule(self.greens_pos, self.greens_v, self.reds_pos, self.gr)




    def draw(self, screen):
        screen.fill(BLACK)

        for i in self.yellows_pos:
            pygame.draw.circle(screen, YELLOW, i, 2)
        for i in self.reds_pos:
            pygame.draw.circle(screen, RED, i, 2)
        for i in self.greens_pos:
            pygame.draw.circle(screen, GREEN, i, 2)

        for slider in self.sliders:
            slider.draw(screen)

        for button in self.buttons:
            button.draw(screen)

        for text_box in self.text_boxes:
            text_box.draw(screen)

        if self.save_loop:
            screen.blit(self.save_text_render, (250, 25))




    def run(self, screen, events):
        self.input()
        self.update(events)
        self.draw(screen)
