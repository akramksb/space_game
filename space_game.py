from space_game_module import *
import pygame, sys

# init
pygame.init()
S = pygame.Surface((32, 32))
S.fill(white)
pygame.display.set_icon(S)
pygame.display.set_caption("Space Game")
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()


def main():
    # set_camera((6_371_000,-1_371_000), 6_371_000)
    # planets.append(Planet( 5.972*10**24, (space_width/2, space_height/2), 6_371_000 ))
    # rockets.append(Rocket(440_000, (space_width/2, space_height/2-6_371_000-408_000 ), (7_650,0), (0,0)))
    set_camera((0,0), 14_000)
    # planets.append(Planet(100 * 10**15, (space[1]/2, space[2]/2), 2_000))
    # rockets.append(Rocket(440_000, (1_000, 1_000), (0, 15), radius=100))
    # rockets.append(Rocket(440_000, (1_000, 1_000), (0, 20), radius=100))
    # rockets.append(Rocket(440_000, (space[1]/2, space[2]/2-3_000), (-50, 0), radius=100))
    # rockets.append(Rocket(440_000, (space[1]/2+2_500, space[2]/2-3_000), (24, 28), radius=100))
    # rockets.append(Rocket(440_000, (0.7*space[1], 0.9*space[2]), (19, -10), radius=100))
    frame = 0
    crash = False
    while not crash:
        start = pygame.time.get_ticks()
        screen.fill(black)
        read_inputs()
        place_planet()
        place_rocket(screen)
        # controle camera
        step = 0.01 * space[2]
        zoom_step = 0.01 * space[2]
        modify_camera(vect_mult(step, ( arrows[2]-arrows[3], arrows[1]-arrows[0] )),
            zoom_step * ( zoom[0]-zoom[1] ))
        #-----------------------------------

        for planet in planets:
            planet.draw(screen)
        
        i = -1
        for rocket in rockets:
            i+=1
            #to draw only visible rockets
            #if get_distance(rocket.pos, vect_add(space[0],(0.5*space[1],0.5*space[2]) )) < space[1]//2:
            #    rocket.draw(screen)
            rocket.draw(screen)
            if not collid(rocket):
                rocket.next_pos(planets)
            else:
                del rockets[rockets.index(rocket)]

        #-------------------------------------------------
        frame += 1
        clock.tick(FPS)
        # ellapsed = pygame.time.get_ticks() - start
        # fps = int(1000/ellapsed)
        # write_text(f"{fps} fps", (50,20), white)
        pygame.display.flip()


if __name__ == "__main__":
    main()