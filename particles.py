import pygame
import sys
import numpy as np
from random import randint

class Object(pygame.sprite.Sprite):
    def __init__(self, img=None):
        super().__init__()
        self.image = self.load_image(img).convert_alpha()
        self.rect = self.image.get_rect()


    def draw(self, display, pos):
        display.blit(self.image, (self.rect[0] - pos[0], self.rect[1] - pos[1]))#, special_flags=pygame.BLEND_ALPHA_SDL2 )
        #print(type(self))
    def load_image(self, name=None):
        if name!=None:
            image = pygame.image.load('E:/Programmieren/_GameDev/GameMechs/Assets/' + name)
        else:
            image = pygame.image.load('E:/Programmieren/_GameDev/GameMechs/Assets/red.png')
        return image
    def set_image(self, img):
        self.image = img.convert_alpha()
        self.rect = self.image.get_rect()


grav_vec = np.array([0,1])


class Particle(Object):
    def __init__(self, pos, img=None, vel=np.zeros(2)):
        super().__init__(img)
        self.lifetime = 50 + randint(-5, 5)
        self.fadeout = self.lifetime * 0.2
        self.fade_steps = 255//self.fadeout
        self.oppacity = 255
        self.left = self.lifetime
        self.vel = (np.random.rand(2)-0.5 + vel) * 20
        self.pos = np.array((float(pos[0]),float(pos[1])))
        #self.vel = self.vel / np.linalg.norm(self.vel)
        self.despawn = False

    def update(self):
        m = 20
        s = 10
        self.vel += grav_vec
        if self.vel[0] > m:
            self.vel[0] = m
        if self.vel[1] > m:
            self.vel[1] = m
        #self.vel = self.vel / np.linalg.norm(self.vel)
        #print(f" self.rect.y {(self.rect.y)}, self.vel[1]{self.vel[1]}, int() {int(self.rect.y + self.vel[1])}")

        self.pos += self.vel
        self.rect.x = int(self.pos[0])
        self.rect.y = int(self.pos[1])

        self.left -= 1
        #print(self.left)
        if self.left < self.fadeout:
            self.oppacity -= self.fade_steps
            self.image.set_alpha(self.oppacity)
        if self.left < 0:
            self.despawn = True

    def __del__(self):
        pass

class Firework(Particle):
    def __init__(self, pos, img='dummyRocket.png', color='red', direction=0):
        super().__init__(pos, img)
        self.image = pygame.transform.rotate(self.image, direction*40)
        self.lifetime = 50
        self.left = self.lifetime
        self.vel = np.array((0.,0.))
        self.dir = np.array((np.sin(direction), np.cos(direction)))
        self.pos = pos
        self.eh = 400 + randint(-200, 200)
        self.spark_offset =np.array((16, 20))
        #self.pos = np.array((float(pos[0]),float(pos[1])))
        #self.vel = self.vel / np.linalg.norm(self.vel)
        self.despawn = False
        self.visible = True
        self.state = 1 # 0:starting, 1:rising, 2:explosion
        self.part_img = color + '.png'

    def draw(self, display, pos):
        if self.visible:
            display.blit(self.image, (self.rect[0] - pos[0], self.rect[1] - pos[1]))#, special_flags=pygame.BLEND_ALPHA_SDL2 )

    def update(self, part_man):
        #print(self.pos)

        if self.state == 1:
            self.pos += self.vel
            self.vel -= self.dir
            #self.pos[1] -= 10
            self.rect.y = int(self.pos[1])
            self.rect.x = int(self.pos[0])
            part_man.add_particle(Particle(self.pos+self.spark_offset, img='spark2x2.png', vel=np.array((0, 1))))
            if self.pos[1] < self.eh:
                self.state = 2
                self.visible = False
                for _ in range(20):
                    #part_man.add_particle(Particle(self.pos, img=self.part_img, vel=np.array((0,-0.7))))
                    part_man.add_particle(Particle(self.pos, img=self.part_img, vel=self.vel/40))
                self.despawn = True



class ParticleManger:
    def __init__(self,):
        self.particles = []
        self.emitters = []
        self.counter_p = 0
        self.counter_e = 0

    def add_particle(self, particle):
        self.particles.append(particle)
        self.counter_p += 1
    def add_emitter(self, emitter):
        self.emitters.append(emitter)
        self.counter_e += 1
    def print_info(self):
        print('parts: ', self.counter_p, ',\temis: ', self.counter_e)
    def get_info(self):
        return (self.counter_p, self.counter_e)
    def get_info_str(self):
        return f'parts: {str(self.counter_p).ljust(10)}emis: {self.counter_e}'

    def update_parts(self, display):
        for index, p in enumerate(self.particles):
            p.update()
            p.draw(display, (0,0))

            # dummy collision
            # if p.rect.x < 0 or p.rect.x > w:
            #     p.vel[0] *= -1
            # if p.rect.y < 0 or p.rect.y > h:
            #     p.vel[1] *= -1

            if p.despawn:
                del self.particles[index]
                self.counter_p -= 1

    def update_ems(self, display):
        for index, e in enumerate(self.emitters):
            e.update(self)
            e.draw(display, (0,0))

            if e.despawn:
                del self.emitters[index]
                self.counter_e -= 1


def render_text_multiline(textfont, string_list, color=(255, 255, 255), antialias=True):
    surf_list = []
    x=0
    y=0
    for string in string_list:
        rendered = textfont.render(string, antialias, color)
        surf_list.append(rendered)
        size = rendered.get_size()
        if size[0] > x:
            x = size[0]
        y += size[1]
        print(f'x:{x}, y:{y}')
    surf = pygame.surface.Surface((x, y))
    offset = 0
    for s in surf_list:
        surf.blit(s, (0, offset))
        offset += s.get_size()[1]
    return surf




if __name__ == "__main__":
    print("running Particle test")
    pygame.init()
    w, h = 1280,940
    screen = pygame.display.set_mode((w, h))
    selection_active = False
    #p = []
    #p.append(Particle((0., 0.)))
    bg_color = pygame.Color('black')
    tick_counter = 0
    clock = pygame.time.Clock()
    particle_manager = ParticleManger()
    particle_manager.add_emitter(Firework((600,800)))
    #actiontype = 1
    pygame.font.init()  # you have to call this at the start,
                        # if you want to use this module.
    font = pygame.font.SysFont('Comic Sans MS', 30)
    info_text_surface = font.render('Some Text', True, (255, 255, 255))
    #print(info_text_surface)
    slow_tick = 0

    render_layer_1 = pygame.surface.Surface((w, h))
    render_layer_1.set_alpha(200)
    render_layer_2 = pygame.surface.Surface((w, h))
    render_layer_2.set_colorkey(bg_color)
    bg = pygame.surface.Surface((w, h))
    bg.fill(bg_color)
    firework_color = 'red'
    firework_x_movement = True


    while True:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print('Programm wird beendet.')
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_1:
                    firework_color = 'red'
                if event.key == pygame.K_2:
                    firework_color = 'orange'
                if event.key == pygame.K_3:
                    firework_color = 'pink'
                if event.key == pygame.K_4:
                    firework_color = 'purple'
                if event.key == pygame.K_5:
                    firework_color = 'lightblue'

        if pygame.mouse.get_pressed(num_buttons=3)[0]:  # left mouse button
            selection_active = True
            s_pos = pygame.mouse.get_pos()
        else:
            selection_active = False

        if selection_active:
            if firework_x_movement:
                particle_manager.add_emitter(Firework(s_pos, color=firework_color, direction=randint(-10,10)/10/np.pi))
            else:
                particle_manager.add_emitter(Firework(s_pos, color=firework_color))
            #for i in range (10):
            #    particle_manager.add_particle(Particle(s_pos))
                #p.append(Particle(s_pos))

        # slow tick
        # Todo: use as Event
        if tick_counter % 10 == 0:
            #slow_tick=0
            info_text = [f'FPS: {int(clock.get_fps())}', particle_manager.get_info_str()]
            info_text_surface = render_text_multiline(font, info_text)
            info_text_surface.set_colorkey((0,0,0))




        #print(clock.get_fps())
        #particle_manager.print_info()

        screen.fill(bg_color)

        render_layer_1.blit(render_layer_2, (0, 0))
        particle_manager.update_parts(render_layer_1)
        render_layer_2.fill(bg_color)
        render_layer_2.blit(render_layer_1, (0, 0))

        particle_manager.update_ems(screen)
        #render_layer_1.blit(screen, (0, 0))
        #particle_manager.update(render_layer_1)
        #render_layer_1.set_alpha(200)
        #render_layer_2.blit(render_layer_1, (0, 0))
        #render_layer_2.set_alpha(100)
        #render_layer_1.set_alpha(255)


        screen.blit(render_layer_2, (0, 0), special_flags=pygame.BLEND_RGBA_ADD )
        screen.blit(info_text_surface, (0, 0))

        pygame.display.flip()
        tick_counter += 1

