import pygame

Vs = 5.0  # Source voltage (Volts)
R = 2000  # Resistance (Ohms)
C = 0.001  # Capacitance (Farads)
Q = 0.0  # Initial charge on capacitor (Coulombs)

running = True
# Pygame setup
pygame.init()
screen = pygame.display.set_mode((800,600),flags = pygame.SCALED | pygame.RESIZABLE,vsync=1)
clock = pygame.time.Clock()
dt = 0
font = pygame.font.Font(None, 36)

while running:
    screen.fill((0,0,0)) # clear to black
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    charging = pygame.key.get_pressed()[pygame.K_c] # one way to do it, the other way is to listen to down/up events
    if charging:
        I = (Vs-Q/C)/R  
    else:
        I = (-Q/C)/R  

    Q += I * dt
    Vc = Q / C

    # draw the voltage value in the top left
    text_surface = font.render(f"Vc = {Vc:.2f} volts", True, (255,255,255)) # this gives a surface
    screen.blit(text_surface,(0,0)) # which we have to blit to the screen

    # draw a rectangle centered, half the size of the screen that fills up to the height if it reaches the charging voltage
    rect_height = int((Vc / Vs) * screen.get_height())
    rect_width = screen.get_width()/2
    # top, left is 0,0, so we need to flip the y coordinates
    r = pygame.Rect(screen.get_width()/2-rect_width/2,screen.get_height()-rect_height,rect_width,rect_height)
    pygame.draw.rect(screen, (255,0,0), r)

    pygame.display.flip()
    dt = clock.tick(60)/1000 

pygame.quit()
