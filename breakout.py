#!/usr/bin/env python3

import pygame
import random
import sys

class Overlay(pygame.sprite.Sprite):
    def __init__(self):
        # Equivalent statements:
        #pygame.sprite.Sprite.__init__(self)
        super(pygame.sprite.Sprite, self).__init__()
        self.image = pygame.Surface((800, 20))
        #self.image.fill((0, 0, 0))
        self.rect = self.image.get_rect()
        self.font = pygame.font.Font('freesansbold.ttf', 18)
        self.render('Score: 0        Lives: 5')
        
    def render(self, text):
        self.text = self.font.render(text, True, (0, 0, 0))
        self.image.blit(self.text, self.rect)
    
    def draw(self, screen):
        screen.blit(self.text, (0, 0))

    def update(self, score, lives):
        self.render('Score: ' + str(score) + '        Lives: ' + str(lives))

class Paddle(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        #makes image for paddle the blue spaceship
        self.image = pygame.image.load('playerShip1_blue.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (60, 60))
        #self.image = pygame.Surface((500, 10))
        #self.image.fill((0, 0, 0))
        self.rect = self.image.get_rect() #creates a rectangle for the ship to reference
        self.rect.x = 375 #determines starting location of ship icon on screen
        self.rect.y = 570

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Block(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('ufoBlue.png') #by default, we use the blue ship
        self.image = pygame.transform.scale(self.image, (40,40))
        #self.image = pygame.Surface((100, 50))
        #sets blocks to random colors
        #self.color = ( random.randint(0, 255), random.randint(0, 255), random.randint(0, 255) )
        #self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.numHitsLeft =  1 #number of hits til death
    #changes ships color to red
    def changeRed(self):
            self.image = pygame.image.load('ufoRed.png')
            self.image = pygame.transform.scale(self.image, (40, 40))
    #changes ship's color to blue
    def changeBlue(self):
        self.image = pygame.image.load('ufoBlue.png')
        self.image = pygame.transform.scale(self.image, (40, 40))


class Ball(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((10, 10))
        pygame.draw.circle(self.image, (255, 0, 0), (5, 5), 5)
        self.rect = self.image.get_rect()
        self.rect.x = 400
        self.rect.y = 560
        self.vector = [ 0, 0 ]
        self.thud_sound = pygame.mixer.Sound('assets/thud.wav')

    def update(self, game, blocks, paddle):
        if self.rect.x < 1 or self.rect.x > 795:
            self.vector[0] *= -1 #changes direction of bullet
        if self.rect.y < 1: #removes balls that pass beyond top of screen
            self.kill()
        if self.rect.y > paddle.rect.y + 20: #balls fall below screen
            game.balls.remove(self) #removes ball
            pygame.event.post(game.new_life_event) #takes player's life
        hitObject = pygame.sprite.spritecollideany(self, blocks)
        if hitObject:
            self.thud_sound.play()
            self.vector[0] *= 0
            self.vector[1] *= -1.1
            hitObject.kill()
            self.kill() #removes ball from play when collision occurs
            pygame.event.post(game.new_ball_event)

            #ToDo connect to ready to refire
            game.score += 1
        if pygame.sprite.collide_rect(self, paddle):
            pygame.event.post(game.new_ball_event)
            self.vector[1] *= -1.2
            #self.vector[0] += random.random()
            self.vector[0] = 0
            if random.randint(0,1) == 1:
                self.vector[0] *= -1
        self.rect.x += self.vector[0]
        self.rect.y += self.vector[1]

class Game:
    def __init__(self):
        pygame.init()
        pygame.key.set_repeat(50)
        #pygame.mixer.music.load('assets/loop.wav') #TODO uncomment when ready to submit
        #pygame.mixer.music.play(-1)
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((800, 600))
        self.balls = pygame.sprite.Group()
        self.balls.add(Ball())
        self.paddle = Paddle()
        self.new_life_event = pygame.event.Event(pygame.USEREVENT + 1)
        self.new_ball_event = pygame.event.Event(pygame.USEREVENT + 2) #creates a new ball
        self.enemy_shoots_event = pygame.event.Event(pygame.USEREVENT +3) #enemy fires at user
        self.blocks = pygame.sprite.Group()
        self.overlay = Overlay()
        self.screen.fill((255, 255, 255))
        self.ready = True 
        self.score = 0
        self.lives = 5
        for i in range(0, 2):
            for j in range(0, 4):
                block = Block()
                block.rect.x = j * 100 + 100 + j * 50
                block.rect.y = i * 50 + 100 + i * 20
                self.blocks.add(block)
        self.offset = 1 #keeps track of timing in game
        self.numDead = 0 # number of dead enemies

    def run(self):
        self.done = False
        while not self.done:
            # When you kill 8 enemies, you're done and you've won
            if (8 == self.numDead):
                self.numDead += 1  # extra security to prevent infinite loop
                self.done = True

            # moves enemy ships
            for block in self.blocks:
                # moves ships left for half the time
                if (self.offset % 300 < 150):
                    block.rect.x += 1
                else: # moves ships right for the other half of game time
                    block.rect.x -= 1
                # advances enemies down every 50 loops
                if (self.offset % 150 == 0):
                    block.rect.y += 2
                #randomly fires bullets
                if self.offset % random.randint(100, 300) < random.randint(1, 8) and block.rect.x % random.randint(10, 20) == 0:
                    #change color to red
                    block.changeRed()
                    #add 'fire at player' event
                    ball = Ball()
                    ball.rect.x = block.rect.x + 50
                    ball.rect.y = block.rect.y + 50
                    ball.vector = [random.randint(1, 2), 1]
                    self.balls.add(ball)

                #changes color back to blue after firing
                if self.offset % 40 == 0:
                    block.changeBlue()
            self.offset += 1

            self.screen.fill((43 +self.lives * 10, 60 + self.lives *10, 120+ self.lives *10))
            for event in pygame.event.get():
                #player looses a life
                if event.type == self.new_life_event.type:
                    self.lives -= 1
                    if self.lives > 0:
                        self.screen.fill((255, 255, 255)) #flashes you you loose a life
                        ball = Ball()
                        ball.rect.x = self.paddle.rect.x + 25
                        self.balls.add(ball)
                        self.ready = True
                    else:
                        pygame.quit()
                        sys.exit(0)
                #player quits
                if event.type == pygame.QUIT:
                    self.done = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        self.lives += 1
                        ball = Ball()
                        ball.vector = [ - random.randint(1, 10), -1 ]
                        self.balls.add(ball)
                    #enemy fires at player event
                    #if event.type == self.enemy_shoots_event:
                        #print( "here")


                    #player presses spacebar to fire
                    if event.key == pygame.K_SPACE and self.ready:
                        self.balls.sprites()[0].vector = [ 0, -1 ] #shoots in a straigt line
                        self.ready = False
                        #speed of bullets fired.  Increases speed as player gets closer to death
                    elif (self.offset %10-self.lives == 0 and event.key == pygame.K_SPACE): #shoots in spurts.
                        ball = Ball()
                        ball.rect.x = self.paddle.rect.x + 26
                        ball.vector = [0, -1 ]
                        self.balls.add(ball)
                    if event.key == pygame.K_LEFT:
                        self.paddle.rect.x -= 5 + self.lives #speed of paddle
                        if self.paddle.rect.x <= 0:
                            self.paddle.rect.x = 0
                    if event.key == pygame.K_RIGHT:
                        self.paddle.rect.x += 5 + self.lives #speed of paddle
                        if self.paddle.rect.x >= 750:
                            self.paddle.rect.x = 750
                if self.ready:
                    self.balls.sprites()[0].rect.x = self.paddle.rect.x + 25
            
            self.balls.update(self, self.blocks, self.paddle)
            self.overlay.update(self.score, self.lives)
            self.blocks.update()
            self.balls.draw(self.screen)
            self.paddle.draw(self.screen)
            self.blocks.draw(self.screen)
            self.overlay.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(60)

class Intro(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((800, 120))
        self.font = pygame.font.Font('freesansbold.ttf', 96)
        self.text = self.font.render('Breakout!', True, (0, 0, 0))
        self.rect = self.image.get_rect()
        self.image.blit(self.text, self.rect)

    def draw(self, screen):
        screen.blit(self.text, (0, 0))

if __name__ == "__main__":
    game = Game()
    game.run()
