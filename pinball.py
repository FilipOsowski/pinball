"""Very simple breakout clone. A circle shape serves as the paddle, then
breakable bricks constructed of Poly-shapes.
The code showcases several pymunk concepts such as elasitcity, impulses,
constant object speed, joints, collision handlers and post step callbacks.
"""

import math, sys, random
import os

import pygame
from pygame.locals import *
from pygame.color import *

import pymunk
from pymunk import Vec2d
import pymunk.pygame_util

width, height = 600, 600

collision_types = {
    "ball": 1,
    "brick": 2,
    "bottom": 3,
    "player": 4,
}


def spawn_ball(space, position, direction):
    ball_body = pymunk.Body(1, pymunk.inf)
    ball_body.position = position

    ball_shape = pymunk.Circle(ball_body, 5)
    ball_shape.color = THECOLORS["green"]
    ball_shape.elasticity = 1.0
    ball_shape.collision_type = collision_types["ball"]

    ball_body.apply_impulse_at_local_point(Vec2d(direction))

    # Keep ball velocity at a static value
    def constant_velocity(body, gravity, damping, dt):
        body.velocity = body.velocity.normalized() * 400

    ball_body.velocity_func = constant_velocity

    space.add(ball_body, ball_shape)


def setup_level(space):
    # Remove balls and bricks
    # for s in space.shapes[:]:
    #     if s.body.body_type == pymunk.Body.DYNAMIC and s.body not in [player_body]:
    #         space.remove(s.body, s)

    # Spawn a ball for the player to have something to play with
    spawn_ball(space, (0, 40), random.choice([(1, 10), (-1, 10)]))

def main():
    ### PyGame init
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()
    running = True
    font = pygame.font.SysFont("Arial", 16)
    ### Physics stuff
    space = pymunk.Space()
    space.gravity = 0.0, -1450.0
    draw_options = pymunk.pygame_util.DrawOptions(screen)

    ### Game area
    # walls - the left-top-right walls
    static_lines = [pymunk.Segment(space.static_body, (50, 100), (50, 550), 2)
        , pymunk.Segment(space.static_body, (50, 550), (550, 550), 2)
        , pymunk.Segment(space.static_body, (550, 550), (550, 100), 2)
        ,pymunk.Segment(space.static_body, (50, 100), (225, 50), 2)
        , pymunk.Segment(space.static_body, (550, 100), (375, 50), 2)
                    ]
    for line in static_lines:
        line.color = THECOLORS['lightgray']
        line.elasticity = 1.0

    space.add(static_lines)

    # bottom - a sensor that removes anything touching it



    def remove_first(arbiter, space, data):
        ball_shape = arbiter.shapes[0]
        space.remove(ball_shape, ball_shape.body)
        return True

    h = space.add_collision_handler(
        collision_types["ball"],
        collision_types["bottom"])
    h.begin = remove_first

    ### Player ship
    # player_body = pymunk.Body(500, pymunk.inf)
    # player_body.position = 300, 100
    #
    # player_shape = pymunk.Segment(player_body, (-50, 0), (50, 0), 8)
    # player_shape.color = THECOLORS["red"]
    # player_shape.elasticity = 1.0
    # player_shape.collision_type = collision_types["player"]

    def pre_solve(arbiter, space, data):
        # We want to update the collision normal to make the bounce direction
        # dependent of where on the paddle the ball hits. Note that this
        # calculation isn't perfect, but just a quick example.
        set_ = arbiter.contact_point_set
        if len(set_.points) > 0:
            player_shape = arbiter.shapes[0]
            width = (player_shape.b - player_shape.a).x
            delta = (player_shape.body.position - set_.points[0].point_a.x).x
            normal = Vec2d(0, 1).rotated(delta / width / 2)
            set_.normal = normal
            set_.points[0].distance = 0
        arbiter.contact_point_set = set_
        return True

    h = space.add_collision_handler(
        collision_types["player"],
        collision_types["ball"])
    h.pre_solve = pre_solve

    # restrict movement of player to a straigt line
    # move_joint = pymunk.GrooveJoint(space.static_body, player_body, (100, 100), (500, 100), (0, 0))
    # space.add(player_body, player_shape, move_joint)
    global state
    # # Start game
    setup_level(space)

    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN and (event.key in [K_ESCAPE, K_q]):
                running = False
            elif event.type == KEYDOWN and event.key == K_p:
                pygame.image.save(screen, "breakout.png")

            elif event.type == KEYDOWN and event.key == K_SPACE:
                  spawn_ball(space,  (300, 50), random.choice([(1, 10), (-1, 10)]))

        # if event.type == KEYDOWN and event.key == K_LEFT:
          #       # player_body.velocity = (-600, 0)
          #       print
          #   elif event.type == KEYUP and event.key == K_LEFT:
          #       # player_body.velocity = 0, 0
          #       print
          #
          #   elif event.type == KEYDOWN and event.key == K_RIGHT:
          #       # player_body.velocity = (600, 0)
          #   elif event.type == KEYUP and event.key == K_RIGHT:
          #       # player_body.velocity = 0, 0
          #
          #   elif event.type == KEYDOWN and event.key == K_r:
          #       # setup_level(space, player_body)
          #   elif event.type == KEYDOWN and event.key == K_SPACE:
          #       # spawn_ball(space, player_body.position + (0, 40), random.choice([(1, 10), (-1, 10)]))

        ## Clear screen
        screen.fill(THECOLORS["black"])

        ### Draw stuff
        space.debug_draw(draw_options)

        state = []
        for x in space.shapes:
            s = "%s %s %s" % (x, x.body.position, x.body.velocity)
            state.append(s)

        ### Update physics
        fps = 60
        dt = 1. / fps
        space.step(dt)

        ### Info and flip screen
        screen.blit(font.render("fps: " + str(clock.get_fps()), 1, THECOLORS["white"]), (0, 0))
        screen.blit(font.render("Move with left/right arrows, space to spawn a ball", 1, THECOLORS["darkgrey"]),
                    (5, height - 35))
        screen.blit(font.render("Press R to reset, ESC or Q to quit", 1, THECOLORS["darkgrey"])
                    , (5, height - 20))

        pygame.display.flip()
        clock.tick(fps)


if __name__ == '__main__':
    sys.exit(main())
