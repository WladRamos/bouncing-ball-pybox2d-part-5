from pygame import Vector2

from Ball import Ball
from Ring import Ring
from Sounds import sounds
from utils import utils
import random


class Game:
    def __init__(self):
        self.center = Vector2(utils.width / 2, utils.height / 2)
        self.ball = Ball(Vector2(utils.width / 2, utils.height / 2), 1, (255, 255, 255))
        self.particles = []
        self.rings = []

        radius = 5
        numRings = 16
        rotateSpeed = 0.5

        # **Decidir aleatoriamente se as cores mudam com o tempo ou permanecem fixas**
        self.dynamic_colors = random.choice([True, False])

        # **Definir cores iniciais e finais aleatórias**
        self.start_hue = random.random()  # Matiz inicial aleatória (0 a 1)
        self.end_hue = random.random()  # Matiz final aleatória (0 a 1)

        for i in range(numRings):
            # **Interpolação do matiz (hue)**
            hue = self.start_hue + (self.end_hue - self.start_hue) * (i / numRings)
            hue = hue % 1  # Garante que esteja no intervalo válido de matiz (0 a 1)

            ring = Ring(self.center, radius, rotateSpeed, 50, hue, self.dynamic_colors)

            radius += 1.4
            rotateSpeed *= 1.1

            self.rings.append(ring)


    def update(self):
        utils.world.Step(1.0 / 60.0, 6, 2)
        if utils.contactListener:
            for bodyA,bodyB in utils.contactListener.collisions:
                sounds.play()
                break
            utils.contactListener.collisions = []

        if len(self.rings) > 0:
            if self.center.distance_to(self.ball.getPos()) > self.rings[0].radius * 10:
                self.rings[0].destroyFlag = True
                utils.world.DestroyBody(self.rings[0].body)

        for ring in self.rings:
            if ring.destroyFlag:
                self.particles += ring.spawParticles()
                self.rings.remove(ring)
                sounds.playDestroySound()


        for exp in self.particles:
            exp.update()
            if len(exp.particles) == 0:
                self.particles.remove(exp)

    def draw(self):
        for ring in self.rings:
            ring.draw()
        self.ball.draw()

        for exp in self.particles:
            exp.draw()