import pygame
from pygame import Vector2
import math
import intersection_tests
from ble_controller import M5StickGameController
import numpy

# variables that you may want to modify
TIME_PER_LEVEL = 20
PLATFORM_WIDTH = 400
OBJECT_RADIUS = 10
BALL_RADIUS = 20

USE_M5STICK = True # set True if BLE M5Stick controller is available
M5STICK_NAME = "M5StickCPlus-Kyle"

# helper object to hold the falling object
class FallingObject:
    def __init__(self,pos):
        self.position = pos
        self.velocity = Vector2(0,0)
        self.radius = OBJECT_RADIUS
    def move(self,dt):
        self.position += self.velocity*dt
        self.velocity += gravity*dt

if USE_M5STICK:
    m5stick = M5StickGameController(M5STICK_NAME)

pygame.init()
# set up the screen
screen_width, screen_height = 600, 800
screen = pygame.display.set_mode((screen_width, screen_height),pygame.SCALED|pygame.RESIZABLE,vsync=1)
font = pygame.font.Font(None, 36)

# timing variables
clock = pygame.time.Clock()
tick_rate = 60
dt = 0
rng =  numpy.random.default_rng() # random number generator

# game state variables
game_over = False
running = True

gravity = Vector2(0,600) # up is down
ball_pos = Vector2(screen_width/2,0) #start at top
ball_vel = Vector2(0,0) #no motion to start
ball_mass = 1 # empirical
ball_radius = BALL_RADIUS
ball_color = (255,0,0)

platform_center_pos = Vector2(screen_width/2, screen_height-100) 
platform_color = (0,255,0)
platform_width = PLATFORM_WIDTH
platform_tilt_angle = 0

difficulty = 1 # will influence the number of objects dropped
level_timer = 0 # used to determine when the difficulty increases
object_timer = 0 # used to determine when to drop an object

falling_objects:list[FallingObject] = []

while running:
    # we always clear the screen and deal with window close events
    screen.fill((0,0,0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    keys = pygame.key.get_pressed() # also get the pressed keys
    
    # we have 3 main states, not connected, not game over, and game over

    if USE_M5STICK and not m5stick.connected:
        # draw a message to the screen that you are waiting
        text_surface = font.render(f"Waiting for M5Stick Connection", True, (255,255,255)) 
        r = text_surface.get_rect()
        r.center = (screen_width/2,screen_height/2)
        screen.blit(text_surface,r) 

    elif not game_over:
        
        # handle input
        platform_tilt_input = 0
        if keys[pygame.K_LEFT]:
            platform_tilt_input =-.03
        elif keys[pygame.K_RIGHT]:
            platform_tilt_input = .03

        if USE_M5STICK and m5stick.connected:
            platform_tilt_angle = platform_tilt_angle*.9+m5stick.acc[1]*.1 # this is a basic exponential filter to smooth the tilt input
        else:
            platform_tilt_angle += platform_tilt_input

        # compute information about the platform pose based on the tilt angle
        platform_right = Vector2(math.cos(platform_tilt_angle),math.sin(platform_tilt_angle))
        platform_normal = Vector2(-platform_right.y,platform_right.x)
        platform_left_pos = platform_center_pos - platform_right*platform_width/2
        platform_right_pos=  platform_center_pos + platform_right*platform_width/2

        # simulate timers
        level_timer += dt
        object_timer += dt
        if level_timer > TIME_PER_LEVEL:
            level_timer = 0
            difficulty += 1
        
        if object_timer > 1 + 1/difficulty: # difficulty is every 2 seconds to start, and then goes down
            object_timer = 0
            left_most = screen_width/2-platform_width/2
            falling_objects.append(FallingObject(Vector2(left_most + rng.random()*platform_width,0)))

        # simulate ball motion and object motion
        ball_acc = gravity 
        ball_vel += ball_acc*dt
        ball_new_pos = ball_pos + ball_vel*dt
        ball_displacement = ball_new_pos - ball_pos
        for o in falling_objects:
            o.move(dt)
            # deal with objects hitting the ball
            if intersection_tests.check_intersect_circle_circle(ball_new_pos,ball_radius,o.position,o.radius):
                game_over = True

        # deal with floor/side intersections and adjust pos and vel accordingly.  Bounce off the sides by reversing the x velocity
        if ball_new_pos.y > screen_height: # ball hit the floor
            game_over = True
        if ball_new_pos.x > screen_width:
            ball_new_pos.x = screen_width
            ball_vel.x = -ball_vel.x
        if ball_new_pos.x < 0:
            ball_new_pos.x = 0
            ball_vel.x = -ball_vel.x

        # now handle the intersection with the platform.  basically, if the ball intersects the platform, it needs to move along the platform normal.  This is also its new velocity
        platform_force = Vector2(0,0)
        intersection = intersection_tests.check_intersect_circle_segment(ball_new_pos,ball_radius,platform_left_pos,platform_right_pos)
        if intersection:
            ball_platform = ball_new_pos - platform_center_pos
            penetration_depth = ball_radius + ball_platform.dot(platform_normal)
            movement_delta = - penetration_depth*platform_normal
            ball_new_pos += movement_delta # move out so that the ball is no longer penetrating
            ball_vel = ball_vel - 1*ball_vel.dot(platform_normal)*platform_normal
        
        ball_pos = ball_new_pos # we are finally ready to accept the new position

        # draw the ball (I like drawing it a different color when on the platform)
        pygame.draw.circle(screen,ball_color if not intersection else (0,0,255),ball_pos,ball_radius)
        
        # draw the platform as a basic line
        pygame.draw.line(screen,platform_color,platform_left_pos,platform_right_pos)

        # draw all falling objects
        for o in falling_objects:
            pygame.draw.circle(screen,(0,255,255),o.position,o.radius)
        
        # draw the level on the screen
        text_surface = font.render(f"Level {difficulty}", True, (255,255,255)) 
        screen.blit(text_surface,text_surface.get_rect()) 
        
    else:
        #draw our game over message, and instructions to reset
        text_surface = font.render(f"Game Over! Hit R to Restart", True, (255,255,255)) 
        r = text_surface.get_rect()
        r.center = (screen_width/2,screen_height/2)
        screen.blit(text_surface,r) 
        if keys[pygame.K_r]: # a simple reset (would be good to put this all in a class, so it wasn't repetitive)
            game_over = False
            level_timer = 0
            object_timer = 0
            ball_pos = Vector2(screen_width/2,-100) #start at top
            ball_vel = Vector2(0,0) #no motion to start     
            platform_tilt_angle = 0
            falling_objects = []
            
    # we always tick the clock and flip the display
    dt = clock.tick(tick_rate)/1000
    pygame.display.flip()

# the window was closed, clean up
pygame.quit()
if USE_M5STICK:
    m5stick.close() # this quits the thread
