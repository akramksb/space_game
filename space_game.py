import numpy as np
import pygame, sys

# constants
FPS = 120
G = 6.67430 * 10**(-11) # N·m2·kg-2 
time_step = 1
width = 1000
height = 600
space_height = 6_371_000*2 + 408_000*2 + 1_100_000
space_width = space_height*(width/height)

white = (255,255,255)
gray = (130,130,130)
black = (0,0,0)
orange = (255, 126,70)


# variables
space = [[0, 0], space_width, space_height]
rockets = []    # moving objects
planets = []    # fixed objects
keys = [0, 0, 0, 0]
zoom = [0, 0]

# init
pygame.init()
S = pygame.Surface((32, 32))
S.fill(white)
pygame.display.set_icon(S)
pygame.display.set_caption("Space Game")
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

# usefull functions
def set_space(o, h):
    space[0] = list(o)
    space[2] = h
    space[1] = space[2]*(width/height)
def modify_space(d_o, d_h):
    d_w = d_h*(width/height)
    d_o = vect_add(d_o, (-d_w/2, -d_h/2))
    set_space(vect_add(space[0],d_o), space[2] + d_h)

def vect_add(v1, v2):
    return (v1[0]+v2[0], v1[1]+v2[1])
def vect_norm(v):
    return (v[0]**2 + v[1]**2)**0.5
def vect_mult(k, v):
    return (k*v[0], k*v[1])
def round_vect(v):
    return (round(v[0]), round(v[1]))

def get_distance(p1, p2):
    return ((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)**0.5
def grav_forces_norm(dist, mP):
    return G*(time_step**2)*mP/(dist)**2
def grav_forces_vect(rocket_p, planet_p, mP):
    vect_r_p = (planet_p[0]-rocket_p[0], planet_p[1]-rocket_p[1])
    unit_vect_r_p = vect_mult(1/vect_norm(vect_r_p) ,vect_r_p)
    dist = get_distance(rocket_p, planet_p)
    return vect_mult(grav_forces_norm(dist,mP), unit_vect_r_p)
def map_distance(real_dist, real_dist_0=space[2], map_dist_0=height):
    map_dist = (real_dist/real_dist_0) * map_dist_0
    return map_dist
def map_coord(real_coord, origin, real_dist_0=space[2], map_dist_0=height):
    map_coord = ( map_distance(real_coord[0]-origin[0], real_dist_0, map_dist_0),
        map_distance(real_coord[1]-origin[1], real_dist_0, map_dist_0))
    return map_coord

def collid(rocket):
    for planet in planets:
        if get_distance(rocket.pos, planet.pos) <= planet.r:
            return True
    return False

class Planet:
    def __init__(self, mass, position, radius):
        self.m = mass
        self.pos = position
        self.r = radius
    def draw(self):
        pos = round_vect(map_coord(self.pos, space[0], space[2], height))
        radius = round(map_distance(self.r, space[2], height))
        pygame.draw.circle(screen, gray, pos, radius+2)
        pygame.draw.circle(screen, orange, pos, radius)

class Rocket:
    def __init__(self, mass, position=(0, 0), velocity=(0, 0), acceleration=(0, 0), radius=10_000):
        self.m = mass
        self.pos = position
        self.vel = vect_mult(time_step, velocity)
        self.acc = acceleration
        self.radius = radius
    def next_pos(self, planets):
        self.pos = vect_add(
            self.pos,
            self.vel
        )
        self.acc = (0, 0)
        for planet in planets:
            self.acc = vect_add(
                self.acc,
                grav_forces_vect(self.pos, planet.pos,  planet.m)
            )
        self.vel = vect_add(self.vel, self.acc)

    def draw(self):
        pos = round_vect(map_coord(self.pos, space[0], space[2], height))
        radius = round(map_distance(self.radius, space[2], height))
        pygame.draw.circle(screen, white, pos, radius+2)
        pygame.draw.circle(screen, gray, pos, radius)
    def draw_p(self):
        pos = round_vect(map_coord(self.pos, space[0], space[2], height))
        pygame.draw.circle(screen, (30, 30, 255), pos, 2)


class bar:
    def __init__(self, pos=(100,100), width=150, height=8, percent=0.5, valRange=(0,255)):
        '''Arguments Help'''
        self.valRange = valRange
        self.pos = pos
        self.width = width
        self.height = height
        self.percent = percent
        self.clicked = False
        
    def IsHover(self, mousePos):
        ans = ( self.pos[0]-self.width/2 < mousePos[0] < self.pos[0]+self.width/2 ) \
            and ( self.pos[1]-self.height/2 < mousePos[1] < self.pos[1]+self.height/2 )
        return ans

    def GetPercent(self, mouseClick, mousePos):
        '''GetPalue Help'''
        if mouseClick and self.IsHover(mousePos):
            self.clicked = True
        elif not mouseClick:
            self.clicked = False
        if self.clicked:
            mp = mousePos[0]
            if mp >= self.pos[0]+self.width/2:
                self.percent = 1
            elif mp <= self.pos[0]-self.width/2:
                self.percent = 0
            else:
                self.percent = (mp - self.pos[0] + self.width/2) / self.width
        return self.percent

    def GetValue(self):
        return self.percent*(self.valRange[1]-self.valRange[0]) + self.valRange[0]

    def Draw(self, color = None):
        darkColor = (120, 120, 120)
        lightColor = (240, 240, 240)
        if color == 'red':
            darkColor = (140, 20, 20)
            lightColor = (240, 30, 30)
        elif color == 'green':
            darkColor = (20, 120, 20)
            lightColor = (30, 240, 30)
        elif color == 'blue':
            darkColor = (20, 20, 120)
            lightColor = (30, 30, 240)

        leftBorder = self.pos[0] - self.width//2
        pygame.draw.rect(screen, lightColor,\
            [(leftBorder, self.pos[1] - 2), (self.width, 4)])
        pygame.draw.rect(screen, darkColor,\
            [(leftBorder, self.pos[1] - 2),(self.width, 4)],1)

        distance = self.percent * self.width
        pygame.draw.rect(screen, lightColor,\
            [(leftBorder + distance - 2, self.pos[1] - self.height//2), (4, self.height)])
        pygame.draw.rect(screen, darkColor,\
            [(leftBorder + distance - 2, self.pos[1] - self.height//2), (4, self.height)],1)


def write_text(text, position, color, fontSize=None):           # change font to 'freesansbold.ttf'
    if fontSize:
        font = pygame.font.Font('freesansbold.ttf', fontSize)
    else:
        font = pygame.font.Font('freesansbold.ttf', 18)
    text = font.render(text, True, color) 
    textRect = text.get_rect()
    textRect.center = position
    screen.blit(text, textRect)


def predict(rocket):
    time_step = 0.3
    def grav_forces_norm(dist, mP):
        return G*(time_step**2)*mP/(dist)**2
    pos_0 = rocket.pos
    vel_0 = rocket.vel
    rocket.vel = vect_mult(time_step, rocket.vel)
    for i in range(200):
        rocket.next_pos(planets)
        if i%20==0 : rocket.draw_p()
    rocket.pos = pos_0
    rocket.vel = vel_0



def read_inputs():
    for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    keys[0] = 1
                if event.key == pygame.K_DOWN:
                    keys[1] = 1
                if event.key == pygame.K_RIGHT:
                    keys[2] = 1
                if event.key == pygame.K_LEFT:
                    keys[3] = 1
                if event.key == pygame.K_i:
                    zoom[0] = 1
                if event.key == pygame.K_o:
                    zoom[1] = 1
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    keys[0] = 0
                if event.key == pygame.K_DOWN:
                    keys[1] = 0
                if event.key == pygame.K_RIGHT:
                    keys[2] = 0
                if event.key == pygame.K_LEFT:
                    keys[3] = 0
                if event.key == pygame.K_i:
                    zoom[0] = 0
                if event.key == pygame.K_o:
                    zoom[1] = 0

colors = [(30,30,255), (30,255,30), (255,30,30), (255,200,30), (30,255,200)]
def main():
    paths = []
    # set_space((6_371_000,-1_371_000), 6_371_000)
    # planets.append(Planet( 5.972*10**24, (space_width/2, space_height/2), 6_371_000 ))
    # rockets.append(Rocket(440_000, (space_width/2, space_height/2-6_371_000-408_000 ), (7_650,0), (0,0)))
    set_space((0,0), 14_000)
    planets.append(Planet(100 * 10**15, (space[1]/2, space[2]/2), 2_000))
    rockets.append(Rocket(440_000, (1_000, 1_000), (0, 15), radius=100))
    rockets.append(Rocket(440_000, (1_000, 1_000), (0, 20), radius=100))
    rockets.append(Rocket(440_000, (space[1]/2, space[2]/2-3_000), (-50, 0), radius=100))
    rockets.append(Rocket(440_000, (space[1]/2+2_500, space[2]/2-3_000), (24, 28), radius=100))
    rockets.append(Rocket(440_000, (0.7*space[1], 0.9*space[2]), (19, -10), radius=100))
    paths.append([])
    paths.append([])
    paths.append([])
    paths.append([])
    paths.append([])
    frame = 0
    step = 0.01 * space[2]
    zoom_step = 0.01 * space[2]
    crash = False
    while not crash:
        start = pygame.time.get_ticks()
        read_inputs()

        # o = vect_add(space[0],\
        #     vect_mult(step, ( keys[2]-keys[3], keys[1]-keys[0] ))
        #     )
        # h = space[2] + zoom_step * ( zoom[0]-zoom[1] )

        modify_space(vect_mult(step, ( keys[2]-keys[3], keys[1]-keys[0] )),
            zoom_step * ( zoom[0]-zoom[1] ))

        screen.fill(black)
        for planet in planets:
            planet.draw()
        frame += 1
        i = -1
        for path in paths:
            i+=1
            for j in range(len(path)):
                pos = path[j]
                last_pos = pos
                if j != 0:
                    last_pos = path[j-1]
                l_p = round_vect(map_coord(last_pos, space[0], space[2], height))
                p = round_vect(map_coord(pos, space[0], space[2], height))
                pygame.draw.circle(screen, colors[i], p, 2)
                pygame.draw.line(screen,colors[i],l_p,p,4)
        i = -1
        for rocket in rockets:
            i+=1
            if not collid(rocket):
                #predict(rocket)
                rocket.next_pos(planets)
                if frame%4 == 0 :
                    paths[i].append(rocket.pos)
                    if frame >= FPS*1.3:
                        paths[i] = paths[i][1:]
            rocket.draw()

        if frame >= FPS*8 :
            print(len(paths[0]))

        #-------------------------------------------------
        clock.tick(FPS)
        ellapsed = pygame.time.get_ticks() - start
        # fps = int(1000/ellapsed)
        # write_text(f"{fps} fps", (50,20), white)
        pygame.display.flip()

if __name__ == "__main__":
    main()