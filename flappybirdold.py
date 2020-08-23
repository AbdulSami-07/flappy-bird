import random
import sys # To exit the game
import pygame
from pygame.locals import *
import time

#Global var for the game

FPS = 32
SCREENWIDTH = 289
SCREENHEIGHT = 511
SCREEN = pygame.display.set_mode((SCREENWIDTH,SCREENHEIGHT)) # Making the game screen
GROUNDY = SCREENHEIGHT * 0.8
GAME_SPRITES = {}
GAME_SOUNDS = {}
PLAYER = 'gallery/sprites/bird.png'
BACKGROUND = './gallery/sprites/background.png'
PIPE = 'gallery/sprites/pipe.png'
FONT = 'gallery/fonts/OpenSans-Bold.ttf'
def welcomeScreen():
    """
    It shows the welcome screen in the game
    """
    playerx = int(SCREENWIDTH/2 - 20)
    playery = int((SCREENHEIGHT - GAME_SPRITES['player'].get_height())/2 + 50)
    messagex = int((SCREENWIDTH - GAME_SPRITES['message'].get_width())/2)
    messagey = int(SCREENHEIGHT*0.13)
    basex = 0
    while True:
        for event in pygame.event.get():
            # event.type == QUIT if someone click on x button.
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

            elif event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                return

        else:
                SCREEN.blit(GAME_SPRITES['background'],(0,0))
                SCREEN.blit(GAME_SPRITES['player'],(playerx,playery))
                SCREEN.blit(GAME_SPRITES['message'],(messagex,messagey))
                SCREEN.blit(GAME_SPRITES['base'],(basex,GROUNDY))
                pygame.display.update()
                FPSCLOCK.tick(FPS)


def mainGame():
    score = 0
    playerx = int(SCREENWIDTH/5)
    playery = int(SCREENHEIGHT/6)
    basex = 0

    #Creating 2 new pipes
    newPipe1 = getRandomPipe()
    newPipe2 = getRandomPipe()

    # List of upperPipe 
    upperPipes = [
        {'x': SCREENWIDTH + 150 , 'y': newPipe1[0]['y']},
        {'x': SCREENWIDTH + 150 + SCREENWIDTH/2 ,'y': newPipe2[0]['y']}
    ]
    # List of lowerPipe
    lowerPipes = [
        {'x': SCREENWIDTH + 150 , 'y': newPipe1[1]['y']},
        {'x': SCREENWIDTH + 150 + SCREENWIDTH/2 ,'y': newPipe2[1]['y']}
    ]

    pipeVelX = -4
    playerVelY = -9
    playerMaxVelY = 10
    playerAccY = 1

    playerFlapAccv = -8 # Velocity due to flapping
    playerFlapped = False # True when flapping

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.key == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if playery > 0:
                    playerVelY = playerFlapAccv
                    playerFlapped = True
                    GAME_SOUNDS['wing'].play()

            if event.type == KEYDOWN and event.key == K_p:
                pause()

        # Checking for collision
        crashBool = isCollide(playerx, playery, upperPipes , lowerPipes)
        if crashBool:
            gameOver = pygame.font.Font(FONT,36)
            gameOverText = gameOver.render("GameOver",True,(235,0,0))
            gameOverRect = gameOverText.get_rect()
            gameOverRect.left,gameOverRect.top = 50 ,SCREENHEIGHT/4
            SCREEN.blit(gameOverText,gameOverRect)
            pygame.display.update()
            FPSCLOCK.tick(FPS)
            pygame.time.delay(1000)
            return

        # Score Logic
        playerMidPos = playerx + GAME_SPRITES['player'].get_width()/2
        for pipe in upperPipes:
            pipeMidPos = pipe['x'] + GAME_SPRITES['pipe'][0].get_width()/2
            if pipeMidPos<= playerMidPos < pipeMidPos + 5:
                score += 1
                GAME_SOUNDS['point'].play()

        if playerVelY < playerMaxVelY and not playerFlapped:
            playerVelY += playerAccY

        if playerFlapped:
            playerFlapped = False

        playerHeight = GAME_SPRITES['player'].get_height()
        playery = playery + min(playerVelY, GROUNDY - playery - playerHeight)
        
        # move pipes to the left 
        for upperPipe , lowerPipe in zip(upperPipes,lowerPipes):
            upperPipe['x'] += pipeVelX
            lowerPipe['x'] += pipeVelX
            

        #Add a new pipe
        if 0<upperPipes[0]['x']<5:
            newpipe = getRandomPipe()
            upperPipes.append(newpipe[0])
            lowerPipes.append(newpipe[1])

        # if the pipe is out of the screen , remove it
        if upperPipes[0]['x'] < -GAME_SPRITES['pipe'][0].get_width():
            upperPipes.pop(0)
            lowerPipes.pop(0)

        SCREEN.blit(GAME_SPRITES['background'],(0,0))
        for upperPipe , lowerPipe in zip(upperPipes,lowerPipes):
            SCREEN.blit(GAME_SPRITES['pipe'][0] ,(upperPipe['x'],upperPipe['y']))
            SCREEN.blit(GAME_SPRITES['pipe'][1] ,(lowerPipe['x'],lowerPipe['y']))

        SCREEN.blit(GAME_SPRITES['base'],(basex,GROUNDY))
        SCREEN.blit(GAME_SPRITES['player'],(playerx,playery))
        myScoreDigits = [int(x) for x in list(str(score))]
        width = 0
        for digits in myScoreDigits:
            width += GAME_SPRITES['numbers'][digits].get_width()

        xoffset = (SCREENWIDTH - width)/2

        for digit in myScoreDigits:
            SCREEN.blit(GAME_SPRITES['numbers'][digit],(xoffset,SCREENHEIGHT*0.13))
            xoffset += GAME_SPRITES['numbers'][digit].get_width()

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def getRandomPipe():

    pipeHeight = GAME_SPRITES['pipe'][0].get_height()
    offset = SCREENHEIGHT/3
    y2 = offset + random.randrange(0,int(SCREENHEIGHT - GAME_SPRITES['base'].get_height() - 1.2*offset))
    pipeX = SCREENWIDTH + 10
    y1 = pipeHeight - y2 + offset
    pipe = [
        {'x':pipeX, 'y':-y1}, # Upper Pipe
        {'x':pipeX,'y':y2} # Lower Pipe
    ]
    return pipe


def isCollide(playerx, playery, upperPipes, lowerPipes):
    if playery> GROUNDY - 25  or playery<0:
        GAME_SOUNDS['hit'].play()
        return True
    
    for pipe in upperPipes:
        pipeHeight = GAME_SPRITES['pipe'][0].get_height()
        if(playery < pipeHeight + pipe['y'] and abs(playerx - pipe['x'] -10) < GAME_SPRITES['pipe'][0].get_width()):
            GAME_SOUNDS['hit'].play()
            return True

    for pipe in lowerPipes:
        if (playery + GAME_SPRITES['player'].get_height() > pipe['y']) and abs(playerx - pipe['x'] -10) < GAME_SPRITES['pipe'][0].get_width():
            GAME_SOUNDS['hit'].play()
            return True

    return False


def pause():
    pause_state = True

    while pause_state:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and (event.key == K_ESCAPE or event.key == K_q)):
                pygame.quit()
                sys.exit()

            elif event.type == KEYDOWN and (event.key == K_c or event.key == K_UP):
                pause_state = False
                return 

            else:
                pause_font = pygame.font.Font(FONT,19)
                # Creating text surface object
                pause_text = pause_font.render("PAUSED, Q=quit or C=continue",True,(0,0,0))
                # Creating rect for text surface object
                pause_rect = pause_text.get_rect()
                pause_rect.top , pause_rect.left = SCREENHEIGHT//2 , pause_rect.left + 5
                
                SCREEN.blit(pause_text,pause_rect)
                pygame.display.update()
                FPSCLOCK.tick(FPS)


if __name__ == "__main__":
    pygame.init() # To initiallize all modules.
    FPSCLOCK = pygame.time.Clock()
    pygame.display.set_caption('Flappy Birds by Sami')
    GAME_SPRITES['numbers'] = (
        pygame.image.load('gallery/sprites/0.png').convert_alpha(),
        pygame.image.load('gallery/sprites/1.png').convert_alpha(),
        pygame.image.load('gallery/sprites/2.png').convert_alpha(),
        pygame.image.load('gallery/sprites/3.png').convert_alpha(),
        pygame.image.load('gallery/sprites/4.png').convert_alpha(),
        pygame.image.load('gallery/sprites/5.png').convert_alpha(),
        pygame.image.load('gallery/sprites/6.png').convert_alpha(),
        pygame.image.load('gallery/sprites/7.png').convert_alpha(),
        pygame.image.load('gallery/sprites/8.png').convert_alpha(),
        pygame.image.load('gallery/sprites/9.png').convert_alpha()
    )
    GAME_SPRITES['message'] = pygame.image.load('gallery/sprites/message.png').convert_alpha()
    GAME_SPRITES['base'] = pygame.image.load('gallery/sprites/base.png').convert_alpha()
    GAME_SPRITES['pipe'] = (
        pygame.transform.rotate(pygame.image.load(PIPE).convert_alpha(),180),
        # To rotate the pipe image
        pygame.image.load(PIPE)
    )
    GAME_SPRITES['background'] = pygame.image.load(BACKGROUND).convert_alpha()
    GAME_SPRITES['player'] = pygame.image.load(PLAYER).convert_alpha()

    GAME_SOUNDS['die'] = pygame.mixer.Sound('gallery/audio/die.wav')
    GAME_SOUNDS['point'] = pygame.mixer.Sound('gallery/audio/point.wav')
    GAME_SOUNDS['swoosh'] = pygame.mixer.Sound('gallery/audio/swoosh.wav')
    GAME_SOUNDS['wing'] = pygame.mixer.Sound('gallery/audio/wing.wav')
    GAME_SOUNDS['hit'] = pygame.mixer.Sound('gallery/audio/hit.wav')


    while True:
        welcomeScreen()
        mainGame()

