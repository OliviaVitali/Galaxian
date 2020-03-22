#!/usr/bin/env python3

import pygame
import random
import sys
import math

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
        self.image = pygame.image.load('../playerShip1_blue.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (60, 60))
        #self.image = pygame.Surface((500, 10))
        #self.image.fill((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.x = 375 #determines starting location of ship icon on screen
        self.rect.y = 570

    def draw(self, screen):
        screen.blit(self.image, self.rect) #draws image on screen of player icon only

class Block(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('../ufoBlue.png')
        self.image = pygame.transform.scale(self.image, (40,40))
        #self.image = pygame.Surface((100, 50))
        #sets blocks to random colors
        self.color = ( random.randint(0, 255), random.randint(0, 255), random.randint(0, 255) )
        #self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.offset = 0

    #method to detect collision between paddle and enemy
    #def update(self, paddle):

class Ball(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((10, 10))
        pygame.draw.circle(self.image, (0, 0, 0), (5, 5), 5)
        self.rect = self.image.get_rect()
        self.rect.x = 400
        self.rect.y = 560
        self.vector = [ 0, 0 ]
        self.thud_sound = pygame.mixer.Sound('assets/thud.wav')

    def update(self, game, blocks, paddle):
        if self.rect.x < 1 or self.rect.x > 795: #checks for out of bounds values
            self.vector[0] *= -1
        #removes ball from play if it moves past the top of the window
        if self.rect.y < 0:
            #self.vector[1] *= -1
            game.balls.remove(self)
        #removes ball from play if it moves past the paddle
        #if self.rect.y > paddle.rect.y + 20:
         #   game.balls.remove(self)
            #pygame.event.post(game.new_life_event)
        hitObject = pygame.sprite.spritecollideany(self, blocks)
        if hitObject:
            self.thud_sound.play()
            self.vector[0] *= -1.1
            self.vector[1] *= -1.1
            hitObject.kill()
            game.numDead += 1
            game.score += 1
        if pygame.sprite.collide_rect(self, paddle):
            self.vector[1] *= -1.2
            self.vector[0] += random.random()
            if random.randint(0,1) == 1:
                self.vector[0] *= -1
        #If we want to only shoot straigh, uncomment next line
        #self.rect.x += self.vector[0]
        self.rect.y += self.vector[1]

class Game:
    def __init__(self):
        pygame.init()
        pygame.key.set_repeat(50)
        #uncommenet music when done
        #pygame.mixer.music.load('assets/loop.wav')
        #pygame.mixer.music.play(-1)
        self.numDead = 0
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((800, 600)) #creates the screen with size 800 height x 600 width
        pygame.display.set_caption("Space Invaders!"); #added line to change window title
        #creates an icon for the window
        icon = pygame.image.load('../playerShip1_blue.png')
        pygame.display.set_icon(icon)
        self.balls = pygame.sprite.Group()
        self.balls.add(Ball())
        self.paddle = Paddle()
        self.new_life_event = pygame.event.Event(pygame.USEREVENT + 1)
        self.blocks = pygame.sprite.Group()
        self.overlay = Overlay()
        #screen is inside the game scope
        self.screen.fill((43, 68, 140))
        self.ready = True 
        self.score = 0
        self.lives = 5
        self.enemyDirctionDown = True

        #creates target blocks 2 x 2 in block formation
        for i in range(0, 2 ):
            for j in range(0, 4):
                block = Block()
                block.rect.x = j * 100 + 200
                block.rect.y = i * 50 + 100
                self.blocks.add(block)

    def run(self):
        #created offset that ships are allowed to move
        offset = 1
        self.done = False
        while not self.done: #game will continue to run until 'done' flag is true
            self.screen.fill((43, 68, 140)) #changed background color

            #When you kill 8 enemies, you're done and you've won
            if (8 == self.numDead):
                self.numDead += 1
                self.done = True

            #moves enemy ships
            for block in self.blocks:
                if (offset % 300 < 150 ):
                    block.rect.x +=1 #moves ships left for half the time
                else:
                    block.rect.x -= 1 #moves ships right for the other half of game time
                #advances enemies down every 50 loops
                if (offset % 50 == 0):
                    if (self.enemyDirctionDown):
                        block.rect.y += 1

                if (offset % 1000 == 0):
                    self.enemyDirctionDown = False
                if (offset % 2000 == 0):
                    self.enemyDirctionDown = True
            offset += 1
            #loops all events from user
            for event in pygame.event.get(): #every user input, mouse movement etc is an event
                if event.type == self.new_life_event.type:
                    self.screen.fill((255, 255, 255)) #flashes when player looses a life
                    self.lives -= 1
                    if self.lives > 0: #player must have 0 or more lives
                        ball = Ball()
                        ball.rect.x = self.paddle.rect.x + 25
                        self.balls.add(ball)
                        self.ready = True
                    else:
                        pygame.quit() #exits the program
                        sys.exit(0)
                if event.type == pygame.QUIT:
                    self.done = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        self.lives += 1
                        ball = Ball()
                        ball.vector = [ - random.randint(1, 10), -1 ]
                        self.balls.add(ball)
                    if event.key == pygame.K_SPACE and self.ready:
                        self.balls.sprites()[0].vector = [ -1, -1 ]
                        self.ready = False
                    if event.key == pygame.K_LEFT:
                        self.paddle.rect.x -= 5
                        if self.paddle.rect.x <= 0:
                            self.paddle.rect.x = 0
                    if event.key == pygame.K_RIGHT:
                        self.paddle.rect.x += 5
                        if self.paddle.rect.x >= 750:
                            self.paddle.rect.x = 750
                if self.ready:
                    self.balls.sprites()[0].rect.x = self.paddle.rect.x + 25

            self.balls.update(self, self.blocks, self.paddle)
            self.overlay.update(self.score, self.lives)
            self.blocks.update()
            #draws objects on screen
            self.balls.draw(self.screen)
            self.paddle.draw(self.screen)
            self.blocks.draw(self.screen)
            self.overlay.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(60)


class Intro(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        #not sure what this does
        self.image = pygame.Surface((800, 220))
        self.font = pygame.font.Font('freesansbold.ttf', 96)
        self.text = self.font.render('Breakout!', True, (0, 0, 0))
        self.rect = self.image.get_rect()
        self.image.blit(self.text, self.rect) #draws image of 'text' on screen

    def draw(self, screen):
        screen.blit(self.text, (0, 0)) #draws text on screen

#main function: loads game
if __name__ == "__main__":
    game = Game()
    game.run()
