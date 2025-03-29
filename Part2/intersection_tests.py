import pygame
import math

def check_intersect_circle_segment(circle_center: pygame.Vector2, radius: float,
                                    p1: pygame.Vector2, p2: pygame.Vector2) -> bool:

    v1_2 = (p2 - p1)  # Vector from p1 to p2
    u1_2 = v1_2.normalize() # unit vector
    c = circle_center - p1 # Vector from p1 to the circle center
    t = c.dot(u1_2) # this is how far the projection is of c onto the unit vector
    if t < -radius: # off the left side, quick no
        return False
    if t > v1_2.magnitude() + radius: # off the right side, quick no
        return False
    p = p1 + u1_2*t # it's somewhere in between, we need to get the point
    if (circle_center - p).magnitude() > radius: # and check the distance to this point
        return False
    return True

def check_intersect_circle_circle(c1: pygame.Vector2, r1: float, c2: pygame.Vector2, r2: float) -> bool:
    return (c2-c1).magnitude() < (r1+r2) # distance less than the sum of the radii