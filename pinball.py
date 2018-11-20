import pygame
import pymunk
import pymunk.pygame_util
import random
import sys


pygame.init()

screen = pygame.display.set_mode((1000, 1000))  # The screen things are displayed in with a resolution of 1000 by 1000

clock = pygame.time.Clock()

draw_options = pymunk.pygame_util.DrawOptions(screen)  # Sets up pymunk/pygame so that it will automatically draw objects

space = pymunk.Space()  # This is where pymunk "holds" its objects (shapes, rigid bodies, etc)
space.gravity = (0, 0)  # The gravity of the space, in (x, y) coordinates
# (0, 0) means that there is no gravity

frames_per_second = 3  # You can mess around with this value


def add_ball(space):
    mass = 1
    radius = 20

    body = pymunk.Body()  # The body of the ball holds its mass, moment of inertia, and position, among other things

    body.mass = mass
    body.moment = pymunk.moment_for_circle(mass, 0, radius)
    body.position = (500, 500)

    x_velocity = random.randint(-200, 200)
    y_velocity = random.randint(-200, 200)
    body.velocity = (x_velocity, y_velocity)  # You can set an object's velocity

    shape = pymunk.Circle(body, radius)  # The shape is what is drawn on the display

    shape.friction = 0.5  # You can set a shape's friction
    shape.elasticity = 0.5  # You can set a shape's elasticity (1 is perfectly elastic, 0 is perfectly inelastic)

    space.add(body, shape)
    return shape


def main():
    while True:  # This is the while loop in which the game/simulation is played
        for event in pygame.event.get():  # This is where you detect key presses
            if event.type == pygame.QUIT:
                sys.exit(0)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                print("You pressed space and added a ball")
                add_ball(space)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                print("Quitting the game")
                pygame.quit()

        space.debug_draw(draw_options)  # Pymunk actually tells pygame to draw its objects
        space.step(1/frames_per_second)  # Pymunk moves time forward by 1/fps in the simulation

        pygame.display.flip()  # Pygame display is updated
        screen.fill((255, 255, 255))  # Fills the screen with the color white

        clock.tick(frames_per_second)
