#!/usr/bin/env python3

import pygame
import random
import sys

#handles text Overlay placed on screen
class Overlay(pygame.sprite.Sprite):
    def __init__(self):
        # Equivalent statements:
        #pygame.sprite.Sprite.__init__(self)
        super(pygame.sprite.Sprite, self).__init__()
        self.image = pygame.Surface((800, 20))
        #self.image.fill((0, 0, 0))
        self.rect = self.image.get_rect()
        self.font = pygame.font.Font('freesansbold.ttf', 18)
        # score, lives, and Enemies killed  the player can see banner
        self.render('Score: 0        Lives: 5       Enemy Killed: 0')

    #renders text on screen for player (not on screen yet)
    def render(self, text):
        self.text = self.font.render(text, True, (0, 0, 0))
        self.image.blit(self.text, self.rect)

    #draws the overlay onto the screen
    def draw(self, screen):
        screen.blit(self.text, (0, 0))

    #when the variables passed in change, we need to update our rendered object
    def update(self, score, lives, numDead):
        self.render('Score: ' + str(score) + '        Lives: ' + str(lives) + '     Enemy Killed: '+ str(numDead))

#This is the player's ship
#It starts center bottom of the screen and can move along the x axis only
class Paddle(pygame.sprite.Sprite):
    #constructor
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        #makes image for paddle the blue spaceship
        self.image = pygame.image.load('playerShip1_blue.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (60, 60))
        #creates a rectangle for the ship to reference
        self.rect = self.image.get_rect()
        # determines starting location of ship icon on screen
        self.rect.x = 375
        self.rect.y = 570

    #draws the object on the screen
    def draw(self, screen):
        screen.blit(self.image, self.rect)

#This is the enemy ship class repurposed from a different project (breakout)
class Block(pygame.sprite.Sprite):
    #constructor
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('ufoBlue.png') #by default, we use the blue ship
        self.image = pygame.transform.scale(self.image, (40,40))
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


#bullets fired in game
class Ball(pygame.sprite.Sprite):
    #constructor
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((10, 10))
        pygame.draw.circle(self.image, (0, 0, 0), (5, 5), 5)
        self.rect = self.image.get_rect()
        self.rect.x = 400
        self.rect.y = 560
        self.vector = [ 0, 0 ]
        self.thud_sound = pygame.mixer.Sound('assets/thud.wav')
    #handles collisions and movement of object
    def update(self, game, blocks, paddle):
        #kills non-moving balls
        if self.vector[0] == 0 and self.vector[1] == 0:
            self.kill()
        #checks boundaries
        if self.rect.x < 1 or self.rect.x > 795:
            self.vector[0] *= -1 #changes direction of bullet
        if self.rect.y < 1: #removes balls that pass beyond top of screen
            self.kill()
        if self.rect.y > paddle.rect.y + 20: #balls fall below screen
            game.balls.remove(self) #removes ball

        hitObject = pygame.sprite.spritecollideany(self, blocks)
        if hitObject: #ships can hit ships
            if self.vector[1] <=0:
                self.thud_sound.play()
                self.vector[0] *= 0
                self.vector[1] *= -1.1
                hitObject.kill()
                self.kill() #removes ball from play when collision occurs
                game.numDead += 1 #adds to "death toll"
                pygame.event.post(game.new_ball_event)
                game.score += 1
        if pygame.sprite.collide_rect(self, paddle):
            #bounces bullet
            pygame.event.post(game.new_life_event)
            #self.vector[1] *= -1.2
            self.vector[0] += random.random()
            self.vector[0] = 0
            self.kill()
            #if random.randint(0,1) == 1:
                #self.vector[0] *= -1
        self.rect.x += self.vector[0]
        self.rect.y += self.vector[1]

class Game:
    #constructor
    def __init__(self):
        pygame.init()
        pygame.key.set_repeat(50)
        pygame.mixer.music.load('assets/loop.wav') #music for game
        pygame.mixer.music.play(-1)
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((800, 600))
        self.balls = pygame.sprite.Group()
        self.balls.add(Ball())
        self.paddle = Paddle()
        self.new_life_event = pygame.event.Event(pygame.USEREVENT + 1)
        self.new_ball_event = pygame.event.Event(pygame.USEREVENT + 2) #creates a new ball
        self.blocks = pygame.sprite.Group()
        self.overlay = Overlay()
        self.screen.fill((255, 255, 255))
        self.ready = True #determines player firing bullets
        self.HanShotFirst = False #if player has fired their weapon
        self.score = 0
        self.lives = 5
        #blocks are added to the game
        for i in range(0, 2):
            for j in range(0, 4):
                block = Block()
                block.rect.x = j * 100 + 100 + j * 50
                block.rect.y = i * 50 + 100 + i * 20
                self.blocks.add(block)
        self.offset = 1 #keeps track of timing in game
        self.numDead = 0 # number of dead enemies
    #game logic
    def run(self):
        self.done = False
        while not self.done:
            #Extra Feature
            # If you wait to kill enemies, you will get a bonus
            if 2 > self.numDead and self.offset %2700 == 0:
                self.score += 30

            # moves enemy ships
            for block in self.blocks:
                #Extra Feature: enemy attacks together
                #first shot for enemy
                #will have entire fleet shoot you at once
                #the higher your score, the less frequently this happens
                if self.offset == 1 or self. offset % ((self.score +1)* 200) == 0:
                    ball = Ball()
                    ball.rect.x = block.rect.x + 50
                    ball.rect.y = block.rect.y + 50
                    ball.vector = [random.randint(1, 2), 1]
                    self.balls.add(ball)
                # moves ships left for half the time
                if (self.offset % 300 < 150):
                    block.rect.x += 1
                else: # moves ships right for the other half of game time
                    block.rect.x -= 1
                # advances enemies down every 50 loops
                if (self.offset % 150 == 0):
                    block.rect.y += 2
                #randomly fires bullets after giving user a chance to fire
                if (self.offset % random.randint(100, 300) < random.randint(2, 9) and block.rect.x % random.randint(10, 20) == 0) or self.offset <1:
                    #Extra Feature: color change enemy ships
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
            self.offset += 1 #counter used for timing in game incremented

            #Extra feature: screen gets lighter as you die!
            self.screen.fill((250 -self.lives * 5, 200 - self.lives *5, 200 - self.lives * 5))
            for event in pygame.event.get():
                #player looses a life
                if event.type == self.new_life_event.type:
                    self.lives -= 1
                    if self.lives > 0:
                        #Extra Feature: game flashes when you loose a life
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
                        self.HanShotFirst = True
                        self.lives += 1
                        ball = Ball()
                        ball.vector = [ - random.randint(1, 10), -1 ]
                        self.balls.add(ball)
                    #Extra Feature: score for lives
                    #player can lower score for a extra life
                    if event.key == pygame.K_s:
                        if self.score > 3:
                            self.score -= 2
                            self.lives += 1
                    #player presses spacebar to fire
                    if event.key == pygame.K_SPACE and self.ready:
                        self.HanShotFirst = True
                        self.balls.sprites()[0].vector = [ 0, -1 ] #shoots in a straight line
                        self.ready = False
                        #speed of bullets fired.  Increases speed as player gets closer to death
                    elif (self.offset %10-self.lives == 0 and event.key == pygame.K_SPACE): #shoots in spurts.
                        self.HanShotFirst = True
                        ball = Ball()
                        ball.rect.x = self.paddle.rect.x + 26
                        ball.vector = [0, -1 ]
                        self.balls.sprites()[0].vector = [0,-1]
                        self.balls.add(ball)

                    #Extra Feature: When you loose life, you ship gets faster
                    if event.key == pygame.K_LEFT:
                        self.paddle.rect.x -= 12 - self.lives #speed of paddle
                        if self.paddle.rect.x <= 0:
                            self.paddle.rect.x = 0
                    if event.key == pygame.K_RIGHT:
                        self.paddle.rect.x += 12 - self.lives #speed of paddle
                        if self.paddle.rect.x >= 750:
                            self.paddle.rect.x = 750
                if self.ready and self.HanShotFirst:
                    self.balls.sprites()[0].rect.x = self.paddle.rect.x + 25

            #Extra Feature: Han Shot First
            #We all know Han DIDN'T shoot first,
            #if the player gets hit before they shoot, they get extra points and more lives
            if not(self.HanShotFirst) and 5 > self.lives:
                self.score += 2
                self.lives += 2

            self.balls.update(self, self.blocks, self.paddle)
            self.overlay.update(self.score, self.lives, self.numDead)
            self.blocks.update()
            self.balls.draw(self.screen)
            self.paddle.draw(self.screen)
            self.blocks.draw(self.screen)
            self.overlay.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(60)

#intro
class Intro(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((800, 120))
        self.font = pygame.font.Font('freesansbold.ttf', 96)
        self.text = self.font.render('GALAXIAN! By Olivia Vitali', True, (0, 0, 0))
        self.rect = self.image.get_rect()
        self.image.blit(self.text, self.rect)

    def draw(self, screen):
        screen.blit(self.text, (0, 0))

#entry point for program
if __name__ == "__main__":
    game = Game()
    game.run()
