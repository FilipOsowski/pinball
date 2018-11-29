import sys, random

import pygame
from pygame.locals import *
from pygame.color import *

import pymunk
from pymunk import Vec2d
import pymunk.pygame_util

width, height = 600, 600

collision_types = {
    "ball": 1,
    "bumper": 2,
    "out_of_bounds": 3
}


def add_bumper(space, location, radius):
    body = pymunk.Body(body_type=pymunk.Body.STATIC)

    body.position = location

    shape = pymunk.Circle(body, radius)
    shape.collision_type = collision_types["bumper"]

    space.add(body, shape)


def add_bumper_collision_handler(space):
    ch = space.add_collision_handler(collision_types["ball"], collision_types["bumper"])

    def normalized_vector_between(a, b):
        v = [b.position[0] - a.position[0], b.position[1] - a.position[1]]
        r = (v[0] ** 2 + v[1] ** 2) ** (1 / 2)
        v = [v[0] / r, v[1] / r]
        return v

    def post_solve(arbiter, space, data):
        bumper_body = arbiter.shapes[1].body
        ball_body = arbiter.shapes[0].body

        strength_of_bumper = 20
        impulse = normalized_vector_between(bumper_body, ball_body)
        impulse = [impulse[0] * strength_of_bumper, impulse[1] * strength_of_bumper]

        ball_body.apply_impulse_at_world_point(impulse, (ball_body.position[0], ball_body.position[1]))

    ch.post_solve = post_solve


def spawn_ball(space, position, direction):
    ball_body = pymunk.Body(1, pymunk.inf)
    ball_body.position = position
    ball_shape = pymunk.Circle(ball_body, 10)

    ball_shape.color = THECOLORS["green"]
    ball_shape.elasticity = 0.95
    ball_shape.collision_type = collision_types["ball"]

    ball_body.apply_impulse_at_local_point(Vec2d(direction))

    # Keep ball velocity at a static value
    space.add(ball_body, ball_shape)


def setup_level(space):
    # Spawn a ball for the player to have something to play with
    spawn_ball(space, (random.randint(50, 550), 500), (random.randint(-100, 100), random.randint(-100, 100)))

    # Adds bottom and upper boundaries
    add_boundaries(space)

    # Adds collision handler for the ball to be removed if it touches any of the red lines
    add_out_of_bounds_collision_handler(space)

    add_bumper_collision_handler(space)  # Add a collision handler for bumpers to work properly
    add_bumper(space, (200, 300), 20)  # Add a bumper with position and radius
    add_bumper(space, (400, 300), 20)


def add_out_of_bounds_collision_handler(space):
    def begin(arbiter, space, data):
        ball_shape = arbiter.shapes[0]
        space.remove(ball_shape, ball_shape.body)
        return True

    h = space.add_collision_handler(
        collision_types["ball"],
        collision_types["out_of_bounds"])
    h.begin = begin

def add_boundaries(space):
    static_lines = [pymunk.Segment(space.static_body, (50, 100), (50, 550), 4),
                    pymunk.Segment(space.static_body, (50, 550), (550, 550), 4),
                    pymunk.Segment(space.static_body, (550, 550), (550, 100), 4),
                    pymunk.Segment(space.static_body, (50, 100), (225, 50), 4),
                    pymunk.Segment(space.static_body, (550, 100), (375, 50), 4)]

    for line in static_lines:
        line.color = THECOLORS['lightgray']
        line.elasticity = 0.95

    out_of_bounds_area = [pymunk.Segment(space.static_body, (225, 0), (375, 0), 4),
                          pymunk.Segment(space.static_body, (225, 0), (225, 45), 4),
                          pymunk.Segment(space.static_body, (375, 0), (375, 45), 4)]

    for line in out_of_bounds_area:
        line.collision_type = collision_types["out_of_bounds"]
        line.color = THECOLORS["red"]


    static_lines.append(out_of_bounds_area)
    space.add(static_lines)


def main():
    # PyGame init
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()
    running = True
    font = pygame.font.SysFont("Arial", 16)

    # Physics stuff
    space = pymunk.Space()
    space.gravity = (0, -500)
    draw_options = pymunk.pygame_util.DrawOptions(screen)

    global state
    # Start game
    setup_level(space)

    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN and (event.key in [K_ESCAPE, K_q]):
                running = False
            elif event.type == KEYDOWN and event.key == K_SPACE:
                spawn_ball(space, (random.randint(50, 550), 500),
                           (random.randint(-100, 100), random.randint(-100, 100)))

        # Clear screen
        screen.fill(THECOLORS["black"])

        # Draw stuff
        space.debug_draw(draw_options)

        state = []
        for x in space.shapes:
            s = "%s %s %s" % (x, x.body.position, x.body.velocity)
            state.append(s)

        # Update physics
        fps = 60
        dt = 1. / fps
        space.step(dt)

        # Info and flip screen
        screen.blit(font.render("fps: " + str(clock.get_fps()), 1, THECOLORS["white"]), (0, 0))

        pygame.display.flip()
        clock.tick(fps)


if __name__ == '__main__':
    sys.exit(main())
