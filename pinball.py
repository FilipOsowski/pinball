import sys
import random
import math
import pygame
import pymunk
import pymunk.pygame_util
import Animator

from pygame.locals import *
from pygame.color import *
from pymunk import Vec2d

line_color = (49, 62, 80)
spring_color = (112, 193, 179)
paddle_color = (242, 95, 92)
bumper_color = (255, 224, 102)
transport_color = (74, 86, 104)
screen_color = (80, 81, 79)
ball_color = (237, 247, 246)

width, height = 680, 910
score = 0
lives = []
numLives = 2
transport_coordinates = [(58, 300), (58, 600), (541, 300), (541, 600)]
fan_shape, fan_base_shape = None, None
fan_bounds = (100, 500)
animators = []
gameDisplay = pygame.display.set_mode((680, 910))
clock = pygame.time.Clock()

collision_types = {
    "ball": 1,
    "bumper": 2,
    "out_of_bounds": 3,
    "powerup": 4,
    "trans1": 5,
    "trans2": 6,
    "fan": 7,
    "block":8
}
pow_timewait= {#adjust all values to -1 if you want to stop power ups from appearing
    "blue": 100,
    "red": 0,
    "yellow": 120

}

black = (0,0,0)


def add_bumper(space, location, radius):
    body = pymunk.Body(body_type=pymunk.Body.STATIC)
    body.position = location

    shape = pymunk.Circle(body, radius)
    shape.collision_type = collision_types["bumper"]
    shape.color = bumper_color

    space.add(body, shape)

def text_objects(text, font):
    textSurface = font.render(text, True, black)
    return textSurface, textSurface.get_rect()

def add_bumper_collision_handler(space):
    ch = space.add_collision_handler(collision_types["ball"],
                                     collision_types["bumper"])

    def normalized_vector_between(a, b):
        v = [b.position[0] - a.position[0], b.position[1] - a.position[1]]
        r = (v[0]**2 + v[1]**2)**(1 / 2)
        v = [v[0] / r, v[1] / r]
        return v

    def post_solve(arbiter, space, data):
        bumper_body = arbiter.shapes[1].body
        ball_body = arbiter.shapes[0].body

        radius = arbiter.shapes[1].radius
        pos = bumper_body.position
        screen = pygame.display.get_surface()

        def animate(percentage_complete):
            s = pygame.Surface((52, 52))
            s.set_colorkey((0, 0, 0))
            s.set_alpha(255 * (1 - percentage_complete))
            # pygame.draw.circle(s, (233, 255, 166), (int(pos.x), int(height - pos.y)), int(radius))
            pygame.draw.circle(s, (233, 255, 166), (26, 26), int(radius))
            screen.blit(s, (int(pos.x - radius), int(height - pos.y - radius)))


        animators.append(Animator.Animator(30, animate))

        strength_of_bumper = 20
        impulse = normalized_vector_between(bumper_body, ball_body)
        impulse = [
            impulse[0] * strength_of_bumper, impulse[1] * strength_of_bumper
        ]
        global score
        score += 1000
        ball_body.apply_impulse_at_world_point(
            impulse, (ball_body.position[0], ball_body.position[1]))

    ch.post_solve = post_solve


def add_powerup(space,color,position): #adds circular power ups that affect ball differently upon impact
    body = pymunk.Body(body_type=pymunk.Body.STATIC)
    pow=pymunk.Circle(body,10)
    pow.sensor = True
#    pow.density = 1.225
    pow.body.position= position
    pow.collision_type = collision_types["powerup"]
    pow.color = color
    space.add(pow,body)
    if color == THECOLORS["red"]:#once powerups are displayed sets dictionary value to -1
        pow_timewait["red"]= -1
    if color == THECOLORS["yellow"]:
        pow_timewait["yellow"]=-1
    if color ==THECOLORS["blue"]:
        pow_timewait["blue"]=-1

    radius = pow.radius
    screen = pygame.display.get_surface()
    pos = body.position
    multiplier = 4

    def animate(percentage_complete):
        s = pygame.Surface((radius * multiplier * 2, radius * multiplier * 2))
        s.set_colorkey((0, 0, 0))
        s.set_alpha(255 * (1 - (percentage_complete % 1)))
        pygame.draw.circle(s, color, (int(radius) * multiplier, int(radius) * multiplier), int(radius * (1 + multiplier/2 * (percentage_complete % 1))), 2)
        screen.blit(s, (int(pos.x - multiplier * radius), int(height - pos.y - multiplier * radius)))

    def custom_is_done():
        if pow in space.shapes:
            return False
        return True

    custom_animator = Animator.Animator(45, animate)
    custom_animator.is_done = custom_is_done

    animators.append(custom_animator)


def add_powerup_collision_handler(space):  # collision between ball and powerup
    def remove_pow(arbiter, space, data):
        circ = arbiter.shapes[0]
        ball = arbiter.shapes[1]
        if circ.color == THECOLORS["blue"]:  # Adjusts gravity of the game
            print("fast")
            wait=150
            color ="blue"
            def normalized_vector_between(a, b):
                v = [b.position[0] - a.position[0], b.position[1] - a.position[1]]
                r = (v[0] ** 2 + v[1] ** 2) ** (1 / 2)
                v = [v[0] / r, v[1] / r]
                return v

            bumper_body = arbiter.shapes[0].body
            ball_body = arbiter.shapes[1].body
            strength_of_bumper = 5
            impulse = normalized_vector_between(bumper_body, ball_body)
            impulse = [impulse[0] * strength_of_bumper, impulse[1] * strength_of_bumper]
            print("IMPULSE IS")
            print(impulse)

            # ball_body.apply_impulse_at_world_point(impulse, (ball_body.position[0], ball_body.position[1]))
            v = ball_body.velocity
            # ball_body.velocity = (v[0] * 1.5, v[1] * 1.5)
            if space.gravity == (0,-100):
                space.gravity = (0,-600)
            else:
                space.gravity = (0, -100)

        elif (circ.color == THECOLORS["red"]):  # adds new ball in screen and makes ball go faster
            print("both")
            color = "red"
            def normalized_vector_between(a, b):
                v = [b.position[0] - a.position[0], b.position[1] - a.position[1]]
                r = (v[0] ** 2 + v[1] ** 2) ** (1 / 2)
                v = [v[0] / r, v[1] / r]
                return v

            bumper_body = arbiter.shapes[0].body
            ball_body = arbiter.shapes[1].body

            strength_of_bumper = 5
            impulse = normalized_vector_between(bumper_body, ball_body)
            impulse = [impulse[0] * strength_of_bumper, impulse[1] * strength_of_bumper]

            ball_body.apply_impulse_at_world_point(impulse, (ball_body.position[0], ball_body.position[1]))
            wait=600
            spawn_ball(space, (random.randint(50, 550), 500), (random.randint(-100, 100), random.randint(-100, 100)))
        else:  # adds new ball in screen
            color="yellow"
            print("new")
            wait= 250
            spawn_ball(space, (random.randint(50, 550), 500), (random.randint(-100, 100), random.randint(-100, 100)))
        print(ball.body.velocity)
        pow_timewait[color]=wait
        space.remove(circ, circ.body)

        return False

        #respawn_powerup(color, space)

    h = space.add_collision_handler(collision_types["powerup"], collision_types["ball"])
    h.begin = remove_pow
def check_powerup(space):#checks to see if powerups are displaying
    for color in pow_timewait:
        if color=="blue":
            pos= (random.randint(100,475), random.randint(120,300))
        elif color == "red":
            pos= (random.randint(175,425),random.randint(500,725))
        elif color=="yellow":
            pos=(random.randint(75,150), 450)
        if pow_timewait[color]==0:#displays powerups again after time has passed
            add_powerup(space,THECOLORS[color],pos)
        elif pow_timewait[color]>0:#if they've been hit, counts down the time until they will reappear
            pow_timewait[color]-=1

def add_transport(
        space, posStart, posEnd, posStart2,
        posEnd2):  # adds segments that transport ball across the layout
    body = pymunk.Body(body_type=pymunk.Body.STATIC)
    trans = pymunk.Segment(body, posStart, posEnd, 7)  # segment on left
    trans.collision_type = collision_types["trans1"]
    trans.color = transport_color
    trans.sensor = True
    body2 = pymunk.Body(body_type=pymunk.Body.STATIC)
    trans2 = pymunk.Segment(body2, posStart2, posEnd2, 7)  # segment on right
    trans2.collision_type = collision_types["trans2"]
    trans2.color = transport_color
    trans2.sensor = True
    space.add(trans, trans2)

    def move_ball_left(
            arbiter, space, data
    ):  # changes ball's position to the left, after collision with the right segment
        global score
        score += 500
        ball = arbiter.shapes[0]
        space.remove(ball.body, ball)  # removes ball from space
        spawn_ball(
            space, (posStart[0] + 20, ball.body.position.y), ball.body.velocity
        )  # spawns ball in again with new velocity and in the left position

        screen = pygame.display.get_surface()

        def animate(percentage_complete):
            s = pygame.Surface((14, 300))
            s.fill((142, 150, 163))
            s.set_alpha(255 * (1 - percentage_complete))
            print("ALPHA IS")
            print(s.get_alpha())
            screen.blit(s, (transport_coordinates[1][0] - 5,
                                        height - transport_coordinates[1][1]))
        animators.append(Animator.Animator(20, animate))

        return False

    def move_ball_right(
            arbiter, space, data
    ):  # changes ball's position to the right, after collision with the left segment
        global score
        score += 500
        ball = arbiter.shapes[0]
        space.remove(ball.body, ball)
        spawn_ball(
            space, (posStart2[0] - 20, ball.body.position.y),
            ball.body.velocity
        )  # spawns ball in again with new velocity and in the right position

        screen = pygame.display.get_surface()

        def animate(percentage_complete):
            s = pygame.Surface((14, 300))
            s.fill((142, 150, 163))
            s.set_alpha(255 * (1 - percentage_complete))
            print("ALPHA IS")
            print(s.get_alpha())
            screen.blit(s, (transport_coordinates[3][0] - 5,
                            height - transport_coordinates[3][1]))
        animators.append(Animator.Animator(20, animate))

        return False

    h = space.add_collision_handler(  # adds collision betweel ball and left transport
        collision_types["ball"], collision_types["trans1"])
    h.begin = move_ball_right
    h2 = space.add_collision_handler(  # adds collision betweel ball and right transport
        collision_types["ball"], collision_types["trans2"])
    h2.begin = move_ball_left
    return trans, trans2


def gen_rail(
        space, pInit, pFin
):  # generates series of short line segments to give impression of a curve
    rail = []
    distX = (pFin[0] - pInit[0])
    distY = (pFin[1] - pInit[1])
    pX = pInit[0]
    pY = pInit[1]
    tot = 23
    for num in range(tot):
        rail.append(
            pymunk.Segment(space.static_body, (pX, pY),
                           (pX + (distX / tot), pY + (distY / tot) +
                            ((tot / 2) - num) * 3), 15))
        pX += distX / tot
        pY += distY / tot
        pY += ((tot / 2) - num) * 3
    for line in rail:
        line.color = line_color
        line.elasticity = 0.21
        space.add(line)
    return rail


def spawn_ball(space, position, direction):
    ball_body = pymunk.Body(1.2, pymunk.inf)
    ball_body.position = position
    ball_shape = pymunk.Circle(ball_body, 13)

    ball_shape.color = ball_color
    ball_shape.elasticity = 0.5
    ball_shape.collision_type = collision_types["ball"]

    ball_body.apply_impulse_at_local_point(Vec2d(direction))

    # Keep ball velocity at a static value
    space.add(ball_body, ball_shape)
    return ball_body

def add_paddles(space):
    pointer_body = pymunk.Body(body_type=pymunk.Body.STATIC)
    pointer_body.position = 202, 60
    pointer_body2 = pymunk.Body(body_type=pymunk.Body.STATIC)
    pointer_body2.position = 398, 60

    # ps_1 = [(20, 0), (0, 0), (5, 80), (15, 80), ]
    ps_1 = [(10, 0), (20, 5), (0, 5), (5, 80), (15, 80), (12, 2), (18, 3), (8, 3), (2, 2), (5, 3)]
    ps_2 = [(20, -5), (0, -5), (5, -80), (15, -80), (10, 0), (12, -2), (18, -3), (8, -3), (2, -2), (5, -3)]

    moment_1 = pymunk.moment_for_poly(1, ps_1)
    paddle_body_1 = pymunk.Body(9999, moment_1)
    paddle_body_1.angle = -3 * math.pi / 4
    paddle_body_1.position = pointer_body.position
    paddle_shape_1 = pymunk.Poly(paddle_body_1, ps_1)
    paddle_shape_1.elasticity = 0.1
    paddle_shape_1.color = paddle_color

    moment_2 = pymunk.moment_for_poly(1, ps_2)
    paddle_body_2 = pymunk.Body(9999, moment_2)
    paddle_body_2.angle = 3 * math.pi / 4
    paddle_body_2.position = pointer_body2.position
    paddle_shape_2 = pymunk.Poly(paddle_body_2, ps_2)
    paddle_shape_2.elasticity = 0.1
    paddle_shape_2.color = paddle_color

    rest_angle = 3 * math.pi / 5
    rest_angle2 = -8 * math.pi / 5
    stiffness = 20000000
    damping = 21000 * 20
    pinjoint = pymunk.constraint.PinJoint(pointer_body, paddle_body_1)
    pinjoint2 = pymunk.constraint.PinJoint(pointer_body2, paddle_body_2)
    rotary_spring = pymunk.constraint.DampedRotarySpring(
        pointer_body, paddle_body_1, rest_angle, stiffness, damping)
    rotary_spring2 = pymunk.constraint.DampedRotarySpring(
        pointer_body2, paddle_body_2, rest_angle2, stiffness, damping)

    space.add(paddle_body_1, paddle_shape_1, rotary_spring, pinjoint)
    space.add(paddle_body_2, paddle_shape_2, rotary_spring2, pinjoint2)
    return rotary_spring, rotary_spring2



def setup_level(space):
    # Adds bottom and upper boundaries
    add_boundaries(space)

    positions = [(25, 825), (65, 825), (105, 825)]
    for x in range(3):
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        body.position = positions[x]
        shape = pymunk.Circle(body, 15)
        shape.color = THECOLORS["red"]
        space.add(shape, body)
        lives.append(shape)

    # Adds collision handler for the ball to be removed if it touches any of the red lines
    add_out_of_bounds_collision_handler(space)

    add_bumper_collision_handler(
        space)  # Add a collision handler for bumpers to work properly
    add_bumper(space, (150, 300), 26)  # Add a bumper with position and radius
    add_bumper(space, (450, 300), 26)
    add_bumper(space, (150, 600), 26)
    add_bumper(space, (450, 600), 26)
    add_bumper(space, (300, 450), 26)
    add_powerup_collision_handler(space)  # adds power up obstacles that change ball
    # add_powerup(space,THECOLORS["red"],(random.randint(250,400),random.randint(500,700)))
    # add_powerup(space, THECOLORS["blue"], (random.randint(400,500), random.randint(80,150)))
    # add_powerup(space, THECOLORS["yellow"], (150, random.randint(100,600)))
    check_powerup(space)#displays powerups, (if you dont want them displayed, set pow_timewait values to -1

    add_transport(
        space, transport_coordinates[0], transport_coordinates[1],
        transport_coordinates[2],
        transport_coordinates[3])  # adds transport segments that move ball

    global fan_shape, fan_base_shape
    fan_shape, fan_base_shape = add_fan(space=space, fan_width=50, fan_height=300, position=(300, 175), speed=50, bounds=(75, 480))


def add_out_of_bounds_collision_handler(space):
    def begin(arbiter, space, data):
        ball_shape = arbiter.shapes[0]
        space.remove(ball_shape, ball_shape.body)
        global numLives
        if numLives > -1:

            space.remove(lives[numLives])
            numLives -= 1

        return True

    h = space.add_collision_handler(collision_types["ball"],
                                    collision_types["out_of_bounds"])
    h.begin = begin


def add_spring(space):
    spring_anchor_body = pymunk.Body(body_type=pymunk.Body.STATIC)
    spring_anchor_body.position = (590, 108)
    spring_ground = pymunk.Segment(spring_anchor_body, (-40, 0), (40, 0), 3)
    body = pymunk.Body(10, 1000000000000000000000000000000000000)
    body.position = (580, 158)
    spring_top = pymunk.Poly.create_box(body, (40, 30))
    spring_top.color = spring_color

    rest_length = 100
    stiffness = 3000
    damping = 150
    dampened_spring = pymunk.DampedSpring(body, spring_anchor_body, (0, 0),
                                          (0, 0), rest_length, stiffness,
                                          damping)

    space.add(spring_top, body, spring_anchor_body, spring_ground,
              dampened_spring)
    return dampened_spring


def add_fan(space, fan_width, fan_height, position, speed, bounds):
    global fan_bounds
    fan_bounds = bounds

    fan_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
    fan_body.position = position
    fan_body.velocity = (speed, 0)
    fan_shape = pymunk.Poly(fan_body, [(fan_width, fan_height), (fan_width, 0), (0, 0), (0, fan_height)])
    fan_shape.collision_type = collision_types["fan"]
    fan_shape.sensor = True

    fan_base_width = fan_width
    fan_base_height = 15
    fan_base_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
    fan_base_body.position = (fan_body.position[0], fan_body.position[1] - fan_base_height)
    fan_base_body.velocity = (speed, 0)
    fan_base_shape = pymunk.Poly(fan_base_body, [(fan_base_width, fan_base_height), (fan_base_width, 0), (0, 0), (0, fan_base_height)])

    ch = space.add_collision_handler(collision_types["ball"], collision_types["fan"])

    global fan_surface
    fan_surface = pygame.Surface((fan_width, fan_height))
    fan_surface.fill(THECOLORS["red"])
    fan_surface.set_alpha(60)

    def pre_solve(arbiter, space, data):
        ball_body = arbiter.shapes[0].body
        ball_body.apply_force_at_local_point((0, 3000), (0, 0))
        return False

    ch.pre_solve = pre_solve

    space.add(fan_body, fan_shape, fan_base_body, fan_base_shape)

    return fan_shape, fan_base_shape
def spawn_block(space):
    body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
    body.position = (558,587)
    body.velocity = (100,0)
    # body_width = 22
    # body_height =125
    #block= pymunk.Poly(body,(557,525),(557,650),22)#height of 125 at all times
    block = pymunk.Poly.create_box(body,(44,125))  # height of 125 at all times
    block.color = line_color
    block.collision_type=collision_types["block"]
    #print(block.body.position.y)
    space.add(body,block)
    return block

# (550,775) to (550,500)
def check_block(block_up,block,ball_body):
    #print(block.body.position)
    if block_up is False and block.body.position[1]>587:
      #  print("going down")
        block.body.velocity=(0,-1000)
    if block_up is True and block.body.position[1]<712:
       # print("going up")
        if ball_body.position[1]>=725:
            block.body.velocity=(0,300)
    if (block_up is False and block.body.position[1]<=587) or (block_up is True and block.body.position[1]>=712):
        block.body.velocity=(0,0)

def add_boundaries(space):
    radius = 15
    static_lines = [
        pymunk.Segment(space.static_body, (50, 100), (185, 53), radius),
        pymunk.Segment(space.static_body, (550, 100), (415, 53), radius),
        pymunk.Segment(space.static_body, (50, 100), (50, 700), radius),
        pymunk.Segment(space.static_body, (565, 650), (565, 50), radius),
        pymunk.Segment(space.static_body, (550, 650), (550, 50), radius),
        pymunk.Segment(space.static_body, (550, 450), (565, 450), radius),
        pymunk.Segment(space.static_body, (640, 678), (640, 50), radius),
        pymunk.Segment(space.static_body, (630, 678), (630, 50), radius),
    ]

    gen_rail(space, (50, 700), (633, 678))
    for line in static_lines:
        line.color = line_color
        line.elasticity = 0.5

    static_lines[0].elasticity = 0.2
    static_lines[1].elasticity = 0.2

    out_of_bounds_area = [
        pymunk.Segment(space.static_body, (0, -20), (1000, -20), 4)
    ]

    for line in out_of_bounds_area:
        line.collision_type = collision_types["out_of_bounds"]
        line.color = THECOLORS["red"]
        line.sensor = True

    static_lines.append(out_of_bounds_area)
    space.add(static_lines)


spring_anchor = None


def change_fan_direction():
    global fan_shape, fan_base_shape

    v = fan_shape.body.velocity[0]

    if (fan_shape.body.position[0] < fan_bounds[0] and v < 0) or (fan_shape.body.position[0] > fan_bounds[1] and v > 0):
        fan_shape.body.velocity = (v * -1, 0)
        fan_base_shape.body.velocity = (v * -1, 0)


def draw(space):
    draw_options = pymunk.pygame_util.DrawOptions(pygame.display.get_surface())

    if fan_shape.body.position[0] > fan_bounds[1] or fan_shape.body.position[0] < fan_bounds[0]:
        change_fan_direction()

    for shape in space.shapes:

        color = THECOLORS["lightgray"]
        try:
            color = shape.color
        except AttributeError:
            pass

        if type(shape) == pymunk.shapes.Circle:
            pymunk.pygame_util.DrawOptions.draw_circle(
                draw_options, shape.body.position, shape.body.angle,
                shape.radius, color, color)
        elif type(shape) == pymunk.shapes.Segment:
            pymunk.pygame_util.DrawOptions.draw_fat_segment(
                draw_options, shape.a, shape.b, shape.radius, color, color)

        elif type(shape) == pymunk.shapes.Poly:
            # if shape.collision_type == collision_types["block"]:
            #     pygame.display.get_surface().blit(fan_surface, (shape.body.position[0], height - 125 - shape.body.position[1]))
            if not shape.collision_type == collision_types["fan"]:
                position = shape.body.position
                local_vertices = shape.get_vertices()
                world_vertices = []
                for vertex in local_vertices:
                    new_vertex = pymunk.vec2d.Vec2d(vertex[0], vertex[1])
                    new_vertex.rotate(shape.body.angle)
                    new_vertex.x += position[0]
                    new_vertex.y += position[1]
                    world_vertices.append(new_vertex)
                pymunk.pygame_util.DrawOptions.draw_polygon(
                    draw_options, world_vertices, shape.radius, color, color)

            else:
                fan_height = shape.get_vertices()[3][1]
                pygame.display.get_surface().blit(fan_surface, (shape.body.position[0], height - fan_height - shape.body.position[1]))

    for a in animators:
        if a.is_done():
            animators.remove(a)
        else:
            a.animate()
def game_intro():
    intro = True

    while intro:
        for event in pygame.event.get():
            print(event)
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        gameDisplay.fill(THECOLORS['whitesmoke'])
        largeText = pygame.font.Font('freesansbold.ttf', 205)
        TextSurf, TextRect = text_objects("Pinball", largeText)
        TextRect.center = ((680 / 2), (910 / 2))
        gameDisplay.blit(TextSurf, TextRect)
        pygame.display.update()
        clock.tick(15)


def main():
    # PyGame init
    pygame.init()
    started = False
    global numLives
    numLives = 2
    gameOver = False

    screen = pygame.display.set_mode((width, height), RESIZABLE)
    clock = pygame.time.Clock()
    running = True

    # Display some text
    font = pygame.font.SysFont("Arial", 30)
    text = ""
    score = 0

    # Physics stuff
    space = pymunk.Space()
    space.gravity = (0, -600)
    space.damping = 0.9

    transport_surface = pygame.Surface((14, 300))
    intro = pygame.Surface((680, 910))

    intro.fill(transport_color)
    transport_surface.fill(transport_color)

    spring = add_spring(space)
    block_up = False
    block = spawn_block(space)
    rotary_spring, rotary_spring2 = add_paddles(space)

    image = pygame.image.load("background.jpg")

    # Start game
    setup_level(space)
    temp_ballbody = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
    while running:
        global score
        global gameOver
        check_powerup(space)
        check_block(block_up, block,temp_ballbody)
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN and (event.key in [K_ESCAPE, K_q]):
                running = False
            elif event.type == KEYDOWN and event.key == K_SPACE:
                block_up=False
                #check_block(block_up, block,temp_ballbody)
                spring.rest_length = 10
                temp_ballbody=spawn_ball(space, (600, 300), (0, 0))

            elif event.type == KEYUP and event.key == K_SPACE:
                spring.rest_length = 150

                block_up=True
                #check_block(block_up, block,temp_ballbody)

            if event.type == KEYDOWN and event.key == K_LEFT:
                rotary_spring.rest_angle = math.pi / 5
            if event.type == KEYUP and event.key == K_LEFT:
                rotary_spring.rest_angle = 3 * math.pi / 5
            if event.type == KEYDOWN and event.key == K_RIGHT:
                rotary_spring2.rest_angle = -6 * math.pi / 5
            if event.type == KEYUP and event.key == K_RIGHT:
                rotary_spring2.rest_angle = -8 * math.pi / 5
            if event.type == MOUSEBUTTONDOWN:
                started = True
                if gameOver:
                    gameOver = False
                    numLives=2
                    space.add(lives[0])
                    space.add(lives[1])
                    space.add(lives[2])
                    score = 0

        if numLives <= -1:
            gameOver = True

        # Clear screen
        screen.fill(screen_color)

        # Draw stuff

        # Update physics
        fps = 60
        step = 1. / fps

        for x in range(5):
            space.step(step / 5)

        # Info and flip screen
        screen.blit(image, (0, 0))
        largeText = pygame.font.Font('freesansbold.ttf', 205)

        screen.blit(
            font.render("fps: " + str(clock.get_fps()), 1, THECOLORS["white"]),
            (0, height - 25))
        screen.blit(
            font.render("Score: " + str(score), 1, THECOLORS["white"]), (0, 0))
        draw(space)

        screen.blit(transport_surface, (transport_coordinates[1][0] - 5,
                                        height - transport_coordinates[1][1]))
        screen.blit(transport_surface, (transport_coordinates[3][0] - 5,
                                        height - transport_coordinates[3][1]))
        draw(space)
        if not started :
            screen.blit(intro, (0,0))
            screen.blit(font.render("Pinball ", 1, THECOLORS["white"]), (300, 455))
        if gameOver:
            screen.blit(intro, (0, 0))
            screen.blit(font.render("Game Over", 1, THECOLORS["white"]), (300, 455))
            screen.blit(font.render("Score:  " + str(score), 1, THECOLORS["white"]), (300, 490))

        pygame.display.flip()
        clock.tick(fps)


if __name__ == '__main__':
    sys.exit(main())
