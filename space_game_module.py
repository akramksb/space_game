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

colors = [(30,30,255), (30,255,30), (255,30,30), (255,200,30), (30,255,200)]

# variables
space = [[0, 0], space_width, space_height]
rockets = []    # moving objects
new_rocket = []
planets = []    # fixed objects
arrows = [0, 0, 0, 0]
mouse = [0, 0, 0]
mouse_pos = [0,0]
zoom = [0, 0]

# usefull functions
def set_camera(o, h):
    space[0] = list(o)
    space[2] = h
    space[1] = space[2]*(width/height)
def modify_camera(d_o, d_h):
    if space[2] + d_h <= 0: return 0
    d_w = d_h*(width/height)
    d_o = vect_add(d_o, (-d_w/2, -d_h/2))
    set_camera(vect_add(space[0],d_o), space[2] + d_h)

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
def grav_forces_norm(dist, mP, time_step=1):
    return G*(time_step**2)*mP/(dist)**2
def grav_forces_vect(rocket_p, planet_p, mP, time_step=1):
    vect_r_p = (planet_p[0]-rocket_p[0], planet_p[1]-rocket_p[1])
    unit_vect_r_p = vect_mult(1/vect_norm(vect_r_p) ,vect_r_p)
    dist = get_distance(rocket_p, planet_p)
    return vect_mult(grav_forces_norm(dist,mP,time_step), unit_vect_r_p)
def map_distance(real_dist, real_dist_0=space[2], map_dist_0=height):
    map_dist = (real_dist/real_dist_0) * map_dist_0
    return map_dist
def map_coord(real_coord, origin, real_dist_0=space[2], map_dist_0=height):
    map_coord = ( map_distance(real_coord[0]-origin[0], real_dist_0, map_dist_0),
        map_distance(real_coord[1]-origin[1], real_dist_0, map_dist_0))
    return map_coord
def real_distance(map_dist, real_dist_0=space[2], map_dist_0=height):
    real_dist = (map_dist/map_dist_0) * real_dist_0
    return real_dist
def real_coord(map_coord, origin, real_dist_0=space[2], map_dist_0=height):
    real_coord = ( real_distance(map_coord[0], real_dist_0, map_dist_0)+origin[0],
        real_distance(map_coord[1], real_dist_0, map_dist_0)+origin[1])
    return real_coord

def collid(rocket):
    for planet in planets:
        if rocket == planet: continue
        if get_distance(rocket.pos, planet.pos) <= planet.r+rocket.r:
            return True
    return False


class Planet:
    def __init__(self, mass, position, radius):
        self.m = mass
        self.pos = position
        self.r = radius
        self.vel = (0,0)
        self.acc = (0,0)
    def next_pos(self, planets, time_step=1):
        self.pos = vect_add(
            self.pos,
            self.vel
        )
        self.acc = (0, 0)
        for planet in planets:
            if planet == self:
                continue
            self.acc = vect_add(
                self.acc,
                grav_forces_vect(self.pos, planet.pos,  planet.m, time_step)
            )
        self.vel = vect_add(self.vel, self.acc)
    def draw(self, screen):
        pos = round_vect(map_coord(self.pos, space[0], space[2], height))
        radius = round(map_distance(self.r, space[2], height))
        pygame.draw.circle(screen, gray, pos, radius+2)
        pygame.draw.circle(screen, orange, pos, radius)

class Rocket:
    def __init__(self, mass, position=(0, 0), velocity=(0, 0), acceleration=(0, 0), radius=10_000):
        self.m = mass
        self.pos = position
        self.vel = velocity
        self.acc = acceleration
        self.r = radius
        self.path = []
    def next_pos(self, planets, time_step=1):
        self.pos = vect_add(
            self.pos,
            self.vel
        )
        self.acc = (0, 0)
        for planet in planets:
            self.acc = vect_add(
                self.acc,
                grav_forces_vect(self.pos, planet.pos,  planet.m, time_step)
            )
        self.vel = vect_add(self.vel, self.acc)

    def predict(self, screen, lenght=9):
        time_step = 1    # lower -> less accuracy
        pos_0 = self.pos
        vel_0 = self.vel
        self.vel = vect_mult(time_step ,self.vel)
        for i in range(lenght*4):
            self.next_pos(planets, time_step)
            if i%8==0: self.draw_p(screen)
            if collid(self): break
        self.pos = pos_0
        self.vel = vel_0

    def draw(self, screen):
        pos = round_vect(map_coord(self.pos, space[0], space[2], height))
        radius = round(map_distance(self.r, space[2], height))
        pygame.draw.circle(screen, white, pos, radius+2)
        pygame.draw.circle(screen, gray, pos, radius)
    def draw_p(self, screen):
        pos = round_vect(map_coord(self.pos, space[0], space[2], height))
        radius = 2
        # radius = round(map_distance(self.r, space[2], height) * 0.7 )
        pygame.draw.circle(screen, (30, 30, 255), pos, radius)


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

    def Draw(self, screen, color = None):
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


def write_text(screen, text, position, color, fontSize=None):           # change font to 'freesansbold.ttf'
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

def place_planet(coord=None, mass = 80 * 10**15):
    if mouse[2] == 1:
        mouse[2] = 0
        coord = real_coord(mouse_pos, space[0], space[2], height)
        for i in range(len(planets)):
            if get_distance(coord, planets[i].pos) <= planets[i].r:
                del planets[i]
                return 0
        P = Planet(mass, coord, 1_000)
        if not collid(P):
            planets.append(P)

def place_rocket(screen):
    if mouse[0] == 1:
        if not new_rocket:
            # mouse[0] = 0
            start_pos = real_coord(mouse_pos, space[0], space[2], height)
            R =  Rocket(100, start_pos, radius=25)
            if not collid(R):
                new_rocket.append(R)
        else:
            mouse_pos[:] = list(pygame.mouse.get_pos())
            end_pos = real_coord(mouse_pos, space[0], space[2], height)
            velFactor = 400/space[2]  # constant -1/40
            new_rocket[0].vel = vect_mult(-velFactor, vect_add(end_pos, vect_mult(-1, new_rocket[0].pos) ))
            new_rocket[0].draw(screen)
            new_rocket[0].predict(screen, 90)

    if mouse[0]==0 and new_rocket:
        rockets.append(new_rocket[0])
        del new_rocket[0]

        



def read_inputs():
    for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP: arrows[0] = 1
                if event.key == pygame.K_DOWN: arrows[1] = 1
                if event.key == pygame.K_RIGHT: arrows[2] = 1
                if event.key == pygame.K_LEFT: arrows[3] = 1
                if event.key == pygame.K_i: zoom[0] = 1
                if event.key == pygame.K_o: zoom[1] = 1
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    arrows[0] = 0
                if event.key == pygame.K_DOWN:
                    arrows[1] = 0
                if event.key == pygame.K_RIGHT:
                    arrows[2] = 0
                if event.key == pygame.K_LEFT:
                    arrows[3] = 0
                if event.key == pygame.K_i:
                    zoom[0] = 0
                if event.key == pygame.K_o:
                    zoom[1] = 0
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse[:] = list(pygame.mouse.get_pressed())
                mouse_pos[:] = list(pygame.mouse.get_pos())
            if event.type == pygame.MOUSEBUTTONUP: mouse[:] = list(pygame.mouse.get_pressed())
