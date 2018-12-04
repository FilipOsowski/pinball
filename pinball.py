import sys, random

import pygame
from pygame.locals import *
from pygame.color import *

import pymunk
from pymunk import Vec2d
import pymunk.pygame_util

width, height = 700, 900

collision_types = {
    "ball": 1,
    "bumper": 2,
    "out_of_bounds": 3,
    "powerup": 4,
    "trans1":5,
    "trans2":6
}


def flipyv(v):
    return int(v.x), int(-v.y + 600)

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

def add_powerup(space,color,position): #adds circular power ups that affect ball differently upon impact
    pow=pymunk.Circle(space.static_body,15)
    pow.body.position= position
    pow.collision_type = collision_types["powerup"]
    pow.color = color
    space.add(pow)
def add_powerup_collision_handler(space):#collision between ball and powerup
    def remove_pow(arbiter, space, data):
        circ= arbiter.shapes[0]
        ball = arbiter.shapes[1]
        if (circ.color == THECOLORS["blue"]):#makes ball go faster
            print("fast")
            space.remove(ball.body,ball)
            spawn_ball(space,ball.body.position,ball.body.velocity*2)
            #ball.body.velocity*=2
        elif (circ.color == THECOLORS["red"]):#adds new ball in screen and makes ball go faster
            print("both")
           # ball.body.velocity/=5
            spawn_ball(space, (random.randint(50, 550), 500), (random.randint(-100, 100), random.randint(-100, 100)))
            space.remove(ball.body, ball)
            spawn_ball(space, ball.body.position, ball.body.velocity * 2)
            #ball.body.velocity*=3
        else:#adds new ball in screen
            print("new")
            spawn_ball(space, (random.randint(50, 550), 500), (random.randint(-100, 100), random.randint(-100, 100)))
        print(ball.body.velocity)
        space.remove(circ)
    h = space.add_collision_handler(collision_types["powerup"],collision_types["ball"])
    h.separate = remove_pow

def add_transport(space,posStart,posEnd,posStart2,posEnd2): #adds segments that transport ball across the layout
    trans = pymunk.Segment(space.static_body, posStart, posEnd, 5)     #segment on left
    trans.body.position.x = posStart[0]
    trans.collision_type = collision_types["trans1"]
    trans.color = THECOLORS["green"]

    trans2 = pymunk.Segment(space.static_body, posStart2, posEnd2, 5)     #segment on right
    trans2.body.position.x = posStart2[0]
    trans2.collision_type = collision_types["trans2"]
    trans2.color = THECOLORS["green"]
    space.add(trans,trans2)

    def move_ball_left(arbiter, space, data):    #changes ball's position to the left, after collision with the right segment
        print("left")
        ball = arbiter.shapes[0]
        space.remove(ball.body, ball)#removes ball from space
        spawn_ball(space, (trans.body.position.x + 5, ball.body.position.y),ball.body.velocity * -1)#spawns ball in again with new velocity and in the left position
    def move_ball_right(arbiter, space, data):  #changes ball's position to the right, after collision with the left segment
        print("right")
        ball = arbiter.shapes[0]
        space.remove(ball.body,ball)
        spawn_ball(space,(trans.body.position.x + (posStart2[0] - abs(posStart[0])) - 5, ball.body.position.y),ball.body.velocity*-1)#spawns ball in again with new velocity and in the right position
    h = space.add_collision_handler(#adds collision betweel ball and left transport
        collision_types["ball"],
        collision_types["trans1"])
    h.separate = move_ball_right
    h2 = space.add_collision_handler(#adds collision betweel ball and right transport
        collision_types["ball"],
        collision_types["trans2"])
    h2.separate = move_ball_left
    return trans,trans2
def gen_rail(space,pInit,pFin):#generates series of short line segments to give impression of a curve
    rail = []
    distX = (pFin[0]-pInit[0])
    distY=(pFin[1]-pInit[1])
    pX= pInit[0]
    pY= pInit[1]
    tot = 23
    for num in range(tot):
        rail.append(pymunk.Segment(space.static_body, (pX,pY),(pX+(distX/tot),pY+(distY/tot)+((tot/2)-num)*3),6))
        pX+=distX/tot
        pY+=distY/tot
        pY+=((tot/2)-num)*3
    for line in rail:
        line.color = THECOLORS['lightgray']
        line.elasticity = 0.21
        space.add(line)
    return rail

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

    add_powerup_collision_handler(space)   #adds power up obstacles that change ball
    add_powerup(space,THECOLORS["red"],(300,400))
    add_powerup(space, THECOLORS["blue"], (475, 350))
    add_powerup(space, THECOLORS["yellow"], (100, 150))

    add_transport(space,(-50,50),(-50,100),(450,50),(450,100))      #adds transport segments that move ball
def add_out_of_bounds_collision_handler(space):
    def begin(arbiter, space, data):
        ball_shape = arbiter.shapes[0]
        space.remove(ball_shape, ball_shape.body)
        return True

    h = space.add_collision_handler(
        collision_types["ball"],
        collision_types["out_of_bounds"])
    h.begin = begin

spring_segment_body = None
def add_spring(space):

    spring_anchor_body = pymunk.Body(body_type = pymunk.Body.STATIC)
    spring_anchor_body.position = (590, 50)
    spring_ground = pymunk.Segment(spring_anchor_body, (-40, 0), (40, 0), 3)
    body = pymunk.Body(10, 1000000000000000000000000000000000000)
    body.position = (580, 100)
    l1 = pymunk.Segment(body, (-18.6, 0), (18.6, 0), 20)

#615,350
    rest_length = 300
    rest_length = 100
    stiffness = 3000
    damping = 150
    r = pymunk.DampedSpring(body, spring_anchor_body, (0, 0), (0, 0), rest_length, stiffness, damping)

    space.add(l1, body, spring_anchor_body, spring_ground, r)
    return r


def add_boundaries(space):
    static_lines = [pymunk.Segment(space.static_body, (50, 100), (50, 700), 4),
                    #pymunk.Segment(space.static_body, (50, 850), (630, 850), 4),
                    pymunk.Segment(space.static_body, (565, 650), (565, 50), 4),
                    pymunk.Segment(space.static_body, (50, 100), (225, 50), 4),
                    pymunk.Segment(space.static_body, (550, 100), (375, 50), 4),
                    pymunk.Segment(space.static_body, (550, 650), (550, 50), 4),
                    pymunk.Segment(space.static_body, (550, 450), (565, 450), 4),
                    pymunk.Segment(space.static_body, (615, 678), (615, 50), 4),
                    pymunk.Segment(space.static_body, (630, 678), (630, 50), 4),
                    #pymunk.Segment(space.static_body, (550, 850), (615, 700), 4),
                    ]
    gen_rail(space, (50, 700), (633, 678))
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


spring_anchor = None

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
    spring = add_spring(space)
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
                spring.rest_length = 10
            elif event.type == KEYUP and event.key == K_SPACE:
                spring.rest_length = 150
            elif event.type == pygame.MOUSEBUTTONUP:
                def normalize_vector(a, b):
                    v = [b[0] - a[0], b[1] - a[1]]
                    r = (v[0] ** 2 + v[1] ** 2) ** (1 / 2)
                    v = [v[0] / r, v[1] / r]
                    return v

                pos = flipyv(Vec2d(event.pos))

                direction = normalize_vector((615, 400), pos)
                strength = 5
                print("DIRECTION IS")
                print(direction)
                direction = map(lambda x: x * strength, direction)
                spawn_ball(space, (615, 400), direction)

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
    yval = 100
    sys.exit(main())