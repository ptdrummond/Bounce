'''
MIT License

Copyright (c) 2016 Paul T Drummond

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Simple traversal platformer 
Jump on a blue box to bounce off of it.
Red platforms can be walked on and jumped from.
Reach the gold box to advance a level and +100 points

Fall and you die -10 points

@author: Paul T Drummond
'''

import sys
import pygame
from pygame.locals import *
from random import randint
from math import sqrt

#initialize window and constants
size = width, height = 1280, 720
black = 0, 0, 0 #background color
red = 255,0,0 #platform and wall color
blue = 0,0,255 #enemy color
green = 0,255,0 #player color
gold = 255,215,0 #goal color

FRAMERATE = 60 #frames/second
METER = (height/72) #size of a meter relative to screen unit m
LEVELSPEED = METER #horizontal speed of player movement and camera units: m*(1/s)=m/s
MAX_X_VELOCITY = LEVELSPEED * 3
JUMP_VEL = 2.3*METER #speed players jump at units: m*(1/s)=m/s
GRAVITY = 10*(METER)/FRAMERATE #gravity increment unit: (m/s)*(1/s)=m/(s^2)
MAX_Y_VELOCITY = JUMP_VEL*2 #terminal velocity

FALL_DAMAGE = 1 #damage from falling off the screen

LEVEL = 1 #current game level
MAX_LEVELS = 4 #number of levels in game

MAX_HEALTH = 1
CHEAT_MODE = False #allows infinite jump to test traversal and background scrolling

screen = pygame.display.set_mode(size)

timer = pygame.time.Clock() #timer for the game update

#initialize pygame mixer and load level 1 song
#pygame.mixer.init()
#pygame.mixer.music.load("Audio\\Game1.ogg")
#pygame.mixer.music.play(-1)

class Entity(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

class goal(Entity):
    def __init__(self,x,y):
        Entity.__init__(self)
        self.x = x
        self.y = y  
        self.rect = pygame.Rect(self.x,self.y,4*METER,4*METER)
        
    def disp(self):
        self.rect.topleft = (self.x,self.y)
        pygame.draw.rect(screen,gold,self.rect,0)    

#character bounces off of these blocks        
class bounce(Entity):
    def __init__(self,x,y,m): #x,y starting coords, m is which mode it moves in (0-4)
        Entity.__init__(self)
        self.x = x
        self.y = y
        self.x0 = x #origin, used for when scrolling side to side
        self.y0 = y
        self.xvel = 0
        self.yvel = 0
        self.rect = pygame.Rect(self.x,self.y,3*METER,2*METER)
        pygame.draw.rect(screen,blue,self.rect,0)
        self.type = m #integer: 0=stationary; 1=moves side to side; 2=moves vertically; 3=moves diagonal /; 4=moves diagonal \
        if(self.type == 1 or self.type == 3 or self.type == 4):
            self.xvel = 0.5*LEVELSPEED
        if(self.type == 2 or self.type == 4):
            self.yvel = 0.5*LEVELSPEED
        if(self.type == 3):
            self.yvel = -0.5*LEVELSPEED
        
    def update(self):
        self.x += self.xvel
        self.y += self.yvel
        if(not self.type == 0):
            if((self.x > self.x0+(12*METER)) or (self.x < self.x0-(12*METER))): #reverse direction if it reaches its own bounds
                self.xvel *= -1
            if((self.y > self.y0+(12*METER)) or (self.y < self.y0-(12*METER))):
                self.yvel *= -1
                
        
    def disp(self):
        self.rect.topleft = (self.x,self.y)
        pygame.draw.rect(screen,blue,self.rect,0)

#platforms and walls should all be stationary
class block(Entity):
    def __init__(self,x,y,w,h): #x,y coords and width,height, as these are used for walls and platforms
        Entity.__init__(self)
        self.rect = pygame.Rect(x,y,w,h)
        pygame.draw.rect(screen,red,self.rect,0)
        self.x = x
        self.y = y
        
    def disp(self):
        self.rect.topleft = (self.x,self.y)
        pygame.draw.rect(screen,red,self.rect,0)

#determines level layout, decides where to place blocks
class levelLayout():
    def __init__(self,levelnum):
        #self.platforms = [block(METER,5*METER,4*METER,height),block(METER,5*METER,width-2*METER,4*METER),block(width-5*METER,5*METER,4*METER,height)]
        self.spawn = block(12*METER,height-(12*METER),12*METER,5*METER) #spawn platform
        #self.platforms.append(self.spawn)
        self.platforms = [self.spawn]
        if(levelnum == 1):
            #set platform locations
            
            self.platforms.append(block((36*METER),height-(12*METER),12*METER,5*METER))
            self.platforms.append(block((108*METER),height-(12*METER),12*METER,5*METER))
            self.platforms.append(block((80*METER),height-(40*METER),12*METER,5*METER))
            self.platforms.append(block((20*METER),height-(40*METER),10*METER,4*METER))
            #set bounceblock locations
            #bounce type: 0=stationary; 1=moves side to side; 2=moves vertically; 3=moves diagonal /; 4=moves diagonal \
            self.bounceblocks = [bounce(76*METER,height-16*METER,0)]
            self.bounceblocks.append(bounce(104*METER,height-24*METER,3))
            self.bounceblocks.append(bounce(104*METER,height-35*METER,0))
            self.bounceblocks.append(bounce(55*METER,height-40*METER,1))
            #set goal location
            self.end = goal(20*METER,height-44*METER)
        elif(levelnum ==2):
            
            self.platforms.append(block((108*METER),height-(12*METER),12*METER,5*METER))
            
            self.bounceblocks = [bounce(40*METER,height-16*METER,0)]
            self.bounceblocks.append(bounce(60*METER,height-28*METER,2))
            self.bounceblocks.append(bounce(80*METER,height-36*METER,4))
            
            self.end = goal(116*METER,height-16*METER)
        elif(levelnum ==3):
            
            self.platforms.append(block((108*METER),height-50*METER,12*METER,5*METER))
            self.platforms.append(block((34*METER),height-(46*METER),10*METER,4*METER))
            self.platforms.append(block((108*METER),height-(12*METER),12*METER,5*METER))
            
            self.bounceblocks = [bounce(60*METER,height-36*METER,1)]
            self.bounceblocks.append(bounce(30*METER,height-30*METER,4))
            self.bounceblocks.append(bounce(96*METER,height-28*METER,2))
            
            self.end = goal(116*METER,height-54*METER)
        elif(levelnum ==4):
            
            self.platforms.append(block((104*METER),height-(12*METER),16*METER,5*METER))
            
            self.bounceblocks = [bounce(40*METER,height-16*METER,0)]
            self.bounceblocks.append(bounce(50*METER,height-30*METER,0))
            self.bounceblocks.append(bounce(84*METER,height-20*METER,0))
            self.bounceblocks.append(bounce(60*METER,height-40*METER,0))
            
            self.bounceblocks.append(bounce(96*METER,height-26*METER,2))
            self.bounceblocks.append(bounce(99*METER,height-26*METER,2))
            self.bounceblocks.append(bounce(102*METER,height-26*METER,2))
            self.bounceblocks.append(bounce(105*METER,height-26*METER,2))
            self.bounceblocks.append(bounce(108*METER,height-26*METER,2))
            self.bounceblocks.append(bounce(111*METER,height-26*METER,2))
            self.bounceblocks.append(bounce(114*METER,height-26*METER,2))
            self.bounceblocks.append(bounce(117*METER,height-26*METER,2))
            
            self.end = goal(116*METER,height-16*METER)
            
        
    def update(self):
        for i in self.bounceblocks:
            i.update()
        
    def disp(self):
        for i in self.platforms:
            i.disp()
        for i in self.bounceblocks:
            i.disp()
        self.end.disp()


layout = levelLayout(LEVEL)

        
class player(Entity):
    def __init__(self):
        Entity.__init__(self)
        self.xvel = 0
        self.yvel = 0
        self.x = layout.spawn.x
        self.y = layout.spawn.y-3*METER
        self.x0 = self.x #for spawn in current level
        self.y0 = self.y
        self.onground = False
        self.score = 0
        self.health = MAX_HEALTH
        self.reachedgoal = False
        
        self.rect = pygame.Rect(self.x,self.y,3*METER,3*METER)
        pygame.draw.rect(screen,green,self.rect,0)
        
    #parameters are the controls, booleans indicating
    #whether they were pressed on that frame
    #remember if player1 is dead center, background pans when moving right
    def update(self, left, right, jump):    
        
        if(left): #Player moves freely of the background left
            self.xvel = -LEVELSPEED
        elif(right):
            self.xvel = LEVELSPEED
        if(jump and self.onground):
            self.yvel = -JUMP_VEL
            self.onground = False
            
        if not self.onground:
            self.yvel += GRAVITY #acceleration in the air
            if self.yvel > MAX_Y_VELOCITY:
                self.yvel = MAX_Y_VELOCITY
        
        if(CHEAT_MODE):
            if(jump):
                self.yvel = -JUMP_VEL #allow air jumps with cheat
                
        if not(left or right):#decelerate horizontally
            if self.xvel > 0: #if moving right
                self.xvel-=7 #decrement closer to zero
                if self.xvel < 0: #overshot
                    self.xvel = 0 #zero out
            elif self.xvel < 0: #if moving left
                self.xvel += 7 #increment closer to zero
                if self.xvel > 0: #overshot
                    self.xvel = 0 #zero out
                    
                    
        self.x += self.xvel #move horizontally        
        
        self.collision(self.xvel,0)#horizontal collision check values for checking platforms
        
        self.y += self.yvel #move vertically
        
        self.onground = False #doesnt matter if we are or not    
        
        self.collision(0,self.yvel) #collision will make it right. values for checking platforms
        
        
        if(self.y > 720): #Fell off the screen
            self.damage()
            #or call endgame routine here, break main while loop and start over etc
            
    #resets player position to current level's spawn point
    def respawn(self):
        self.y = self.y0
        self.x = self.x0
        self.yvel = 0
    #inflicts damage on the player and respawns them
    def damage(self):
        #respawn
        if(self.health>0):#else:
            self.health -= FALL_DAMAGE
        self.score -= 10
        self.respawn()           
    
    
            
    #detects collision based on coordinates of objects
    def collisiondetect(self,x1,y1,w1,h1,x2,y2,w2,h2):
        if(x2+w2>=x1>=x2) and (y2+h2>=y1>=y2):
            return True
        elif(x2+w2>=x1+w1>=x2) and (y2+h2>=y1>=y2):
            return True
        elif(x2+w2>=x1>=x2) and (y2+h2>=y1+h1>=y2):
            return True
        elif(x2+w2>=x1+w1>=x2) and (y2+h2>=y1+h1>=y2):
            return True
        else:
            return False
        
        
    def collision(self,xvel,yvel): 
        for i in layout.platforms:
        #start checks if hit the platform first, so the player can be protected by not dying from hitting the bottom of a platform an enemy sits on
            temp = i
            
            if pygame.sprite.collide_rect(self,temp):
                #check certain "hitzones" combined with position and current velocity
                        
                if xvel > 0 and self.x < temp.rect.left: #was moving right
                    if self.x+self.rect.width >= temp.rect.left: #moving right so check if on right side
                        self.x = temp.rect.left - self.rect.width#has collided right reset x value to left
                                        
                if xvel < 0 and self.rect.right > temp.rect.right: #was moving left
                    if self.x <= temp.rect.right: #check left side of player and right side of object
                        self.x = temp.rect.right #has collided left reset x value to right
                                       
                if yvel > 0 and self.rect.right > temp.rect.left and self.rect.left < temp.rect.right: #was falling (hit ground)
                    if self.y+self.rect.height >= temp.rect.top: #position check
                        self.y = temp.rect.top - self.rect.height #has collided down reset y value to ground
                        self.onground = True
                        #self.doublejump = True #re-enable double jump ability
                        #self.lastgroundy = self.y
                        self.yvel = 0
                                  
                if yvel < 0 and self.rect.right > temp.rect.left and self.rect.left < temp.rect.right: #was jumping (hit ceiling)
                    if self.y <= temp.rect.bottom:
                        self.y = temp.rect.bottom #has collided up reset y value to bottom of obstacle
                #by here yvel must be 0, check if youre off the edge and fall
                if self.onground and (self.x > temp.rect.right or self.rect.right < temp.rect.left):
                    self.yvel += GRAVITY
        #done checking platforms ######################################################################
        for i in layout.bounceblocks:
            temp = i
            if pygame.sprite.collide_rect(self,temp):
                if yvel > 0:
                    if self.y+self.rect.height >= temp.rect.top:
                        self.yvel = -1*JUMP_VEL
        #done checking bounceblocks#####################################################################
        
        #check if we hit the goal block
        if pygame.sprite.collide_rect(self,layout.end):
            self.reachedgoal = True
            #self.respawn()
        
    def disp(self):
        
        #self.rect.topleft = (self.x,self.y)
        #screen.blit(screen,self.rect)
        self.rect.topleft = (self.x,self.y)
        pygame.draw.rect(screen,green,self.rect,0)
        
        #distancetext=font.render("Distance:"+str(self.distance), 1,(0,255,0))
        #screen.blit(distancetext, (self.jumpbuttonrect.right+50, 20))
        scoretext=font.render("Score: "+str(self.score)+"         Level: "+str(LEVEL)+"/"+str(MAX_LEVELS)+"     Song: ---    A:Left  D:Right    SPACEBAR:Jump", 1,(255,0,0))
        screen.blit(scoretext,(20,20))

#set control booleans
left = False
right = False
jump = False
player1 = player()

pygame.font.init()
font=pygame.font.Font(None,30)

bg_rect = pygame.Rect(0,0,width,height)
pygame.draw.rect(screen,black,bg_rect,0)

quit_game = False
while not quit_game: #start level
        
        
        for event in pygame.event.get():
            #if event.type == pygame.QUIT:
            #    sys.exit()
            if event.type == KEYDOWN:#set keydown booleans here
                if(event.key==K_d): #move right
                    right = True
                if(event.key==K_a): #move left
                    left = True
                if(event.key==K_SPACE): #j key for jump
                    jump = True
                if(event.key == K_ESCAPE):
                    quit_game = True
                    #sys.exit()
                if(event.key == K_r):
                    player1.reachedgoal = True
            elif event.type == KEYUP:#set keyup booleans here
                if(event.key==K_d):
                    right = False
                if(event.key == K_a):
                    left = False
                if(event.key == K_SPACE):
                    jump = False
                
        #keys set, update player location and attributes
        timer.tick(FRAMERATE) 
        
        #display the background
        pygame.draw.rect(screen,black,bg_rect,0)
        
        #update player position, collision, and attributes
        layout.update() #update level movements (if any)
        player1.update(left,right,jump)
        
        if(player1.reachedgoal):
            LEVEL += 1
            if(LEVEL > MAX_LEVELS):
                LEVEL = 1
            layout = levelLayout(LEVEL)
            #player1 = player()
            player1.respawn()
            player1.score += 100
            player1.reachedgoal = False
            
            #pygame.mixer.music.stop()
            #if(LEVEL == 1):
            #    pygame.mixer.music.load("Audio\\Game1.ogg")
            #elif(LEVEL == 2):
            #    pygame.mixer.music.load("Audio\\Game2.ogg")
            #elif(LEVEL == 3):
            #    pygame.mixer.music.load("Audio\\Game3.ogg")
            #elif(LEVEL == 4):
            #    pygame.mixer.music.load("Audio\\Game4.ogg")
            #pygame.mixer.music.play(-1)
            
        #display level elements and player
        layout.disp()
        player1.disp()
        
        pygame.display.flip()
        
#pygame.mixer.stop()
sys.exit()