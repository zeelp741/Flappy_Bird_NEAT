import pygame
import neat
import time
import os
import random
pygame.font.init()



WIN_WIDTH = 500
WIN_HEIGHT = 800

gen  = 0

BIRD_IMAGES = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))),pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))),pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]
PIPE_IMAGES = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMAGES = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BACKGROUND_IMAGES = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "background.png")))

FONT = pygame.font.SysFont("comicsans", 50)


class Bird:
    IMAGES = BIRD_IMAGES
    ROTATION_MAX = 25
    ROTATION_VELOCITY = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
      self.x = x
      self.y = y
      self.tilt = 0
      self.tick_count = 0
      self.velocity = 0
      self.height = self.y
      self.image_count = 0
      self.image = self.IMAGES[0]

    def jump(self):
        self.velocity = -10.5
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1
        displacement = self.velocity * self.tick_count + 1.5 * self.tick_count ** 2

        if displacement >= 16:
            displacement = 16

        if displacement < 0:
            displacement -= 2

        self.y = self.y + displacement

        if displacement < 0 or self.y < self.height + 50:
            if self.tilt < self.ROTATION_MAX:
                self.tilt = self.ROTATION_MAX
        else:
            if self.tilt > -90:
                self.tilt -= self.ROTATION_VELOCITY

    def draw(self, win):
        self.image_count += 1

        if self.image_count < self.ANIMATION_TIME:
            self.img = self.IMAGES[0]
        elif self.image_count < self.ANIMATION_TIME*2:
            self.img = self.IMAGES[1]
        elif self.image_count < self.ANIMATION_TIME*3:
            self.img = self.IMAGES[2]
        elif self.image_count < self.ANIMATION_TIME*4:
            self.img = self.IMAGES[1]
        elif self.image_count < self.ANIMATION_TIME*4 + 1:
            self.img = self.IMAGES[0]
            self.image_count = 0

        if self.tilt <= -80:
            self.img = self.IMAGES[1]
            self.image_count = self.ANIMATION_TIME*2

        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center = self.img.get_rect(topleft = (self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.image)

class Pipe:
    GAP = 200
    VELOCITY = 5

    def __init__(self, x):
        self.x = x
        self.height = 0

        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMAGES, False, True)
        self.PIPE_BOTTOM = PIPE_IMAGES

        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(40, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.VELOCITY

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        if t_point or b_point:
            return True
        
        return False

class GROUND:
    VELOCITY = 5
    WIDTH = BASE_IMAGES.get_width()
    IMAGE = BASE_IMAGES

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VELOCITY
        self.x2 -= self.VELOCITY

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH
    
    def draw(self, win):
        win.blit(self.IMAGE, (self.x1, self.y))
        win.blit(self.IMAGE, (self.x2, self.y))





def draw_windows(win, birds, pipes, ground, score, gen):
    win.blit(BACKGROUND_IMAGES, (0,0))

    for pipe in pipes:
        pipe.draw(win)

    text = FONT.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    text = FONT.render("Gen: " + str(gen), 1, (255, 255, 255))
    win.blit(text, (10, 10))
    
    ground.draw(win)
    for bird in birds:
        bird.draw(win)
    pygame.display.update()

 
def main(genomes, config):
    global gen
    nets = []
    ge = []
    birds = []

    gen += 1

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230, 350))
        g.fitness = 0
        ge.append(g)



    ground = GROUND(730)
    pipes = [Pipe(600)]

    score = 0


    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()
    run = True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
            keys = pygame.key.get_pressed()
            # if keys[pygame.K_SPACE]:
            #     bird.jump()
            
            if keys[pygame.K_ESCAPE]:
                run = False
                pygame.quit()
                quit()

        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1
        else:
            run = False
            break

        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1

            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))
            if output[0] > 0.5:
                bird.jump()

        
        add_pipe = False
        rem = []

        for pipe in pipes:
            for x, bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[x].fitness -= 1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)

                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True
            
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)


            pipe.move()

        if add_pipe:
            score += 1
            for g in ge:
                g.fitness += 5
            pipes.append(Pipe(600))

        for r in rem:
            pipes.remove(r)

        for x, bird in enumerate(birds):
            if bird.y + bird.image.get_height() >= 730 or bird.y < 0 :
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)


        bird.move()
        ground.move()
        draw_windows(win, birds, pipes, ground, score, gen)



def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,neat.DefaultSpeciesSet, neat.DefaultStagnation,config_path)

    population = neat.Population(config)

    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    winner = population.run(main, 50)




if __name__=="__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-neat.txt')
    run(config_path)



    



