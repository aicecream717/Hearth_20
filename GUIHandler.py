'''
Created on Apr 8, 2020

@author: shan.jiang
'''
import pygame,math,os,random,database
import inputbox,time,pygame.font,fontlib
from pygame.locals import *
from numpy import sign
from math import sqrt




def get_image(img_path,scale):
    try:
        image_source=pygame.image.load(img_path).convert_alpha()
    except:
        image_source=pygame.image.load("images/secret.png").convert_alpha()
    
    return pygame.transform.scale(image_source, scale)

'''screen and colors'''   
x = 100
y = 30
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x,y)

SCREEN_WIDTH = 1720
SCREEN_HEIGHT = 960
WHITE = (255, 255, 255)
BLACK = (1,     1,   1)
RED   = (255,   0,   0)
RED2   = (242,   166,   22)
GREEN = (0,   255,   0)
BLUE  = (0,    0,  255)
PINK  = (255, 170, 170)
ORANGE= (255, 153, 51)

FPS = 60
    
# -pygame init -
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

'''background related images'''
background = pygame.transform.scale(pygame.image.load('images/background.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
background_dark = pygame.transform.scale(pygame.image.load('images/background_dark.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT)) 
draft_background = pygame.transform.scale(pygame.image.load('images/background.png').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
pick_hero_background=pygame.transform.scale(pygame.image.load('images/choose_your_hero.png').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
button=pygame.transform.scale(pygame.image.load('images/button.png').convert_alpha(), (250, 100))
rope=pygame.transform.scale(pygame.image.load('images/rope.png').convert_alpha(), (1160,200))
ropefire=pygame.transform.scale(pygame.image.load('images/ropefire.png').convert_alpha(), (80,80))
explode=pygame.transform.scale(pygame.image.load('images/explode.png').convert_alpha(), (80,80))
        
    
'''card related images'''
cost_background=pygame.transform.scale(pygame.image.load('images/mana_crystal.png').convert_alpha(),(30,30))
atk_background=pygame.transform.scale(pygame.image.load('images/atk_background.png').convert_alpha(),(30,30))
hp_background=pygame.transform.scale(pygame.image.load('images/hp_background.png').convert_alpha(),(30,30))
cost_background_zoom=pygame.transform.scale(pygame.image.load('images/mana_crystal.png').convert_alpha(),(50,50))
atk_background_zoom=pygame.transform.scale(pygame.image.load('images/atk_background.png').convert_alpha(),(50,50))
hp_background_zoom=pygame.transform.scale(pygame.image.load('images/hp_background.png').convert_alpha(),(50,50))
cost_background_red=pygame.transform.scale(pygame.image.load('images/hp_background.png').convert_alpha(),(30,30))

taunt_image = get_image("images/taunt3.png",(130,177))
divine_shield_image = get_image("images/divine_shield.png",(160,177)) 
windfury_image = get_image("images/windfury.png",(130,177))
elusive_image = get_image("images/elusive.png",(100,133))
enrage_image = get_image("images/enrage.png",(100,135))
spell_damage_boost_image = get_image("images/spell_damage_boost.png",(100,177))
stealth_image = get_image("images/stealth.png",(156,210))
poisonous_image = get_image("images/poisonous.png",(35,35))
freeze_image = get_image('images/frozen.png', (103,128))
lifesteal_image = get_image('images/lifesteal.png', (35,35))
deathrattle_image = get_image("images/deathrattle.png",(35,35))
inspire_image = get_image("images/inspire.png",(30,35))
inspire2_image = get_image("images/inspire2.png",(30,35))
trigger_image = get_image("images/trigger.png",(25,35))
trigger2_image = get_image("images/trigger2.png",(25,35))
overkill_image = get_image("images/overkill.png",(60,70))  
arrow_image = get_image("images/snipe.png",(120,120))
hero_power_disabled_image  = get_image("images/disabled_hero_power.png",(108,148))
ephemeral_image = get_image("images/ephemeral.png",(103,141))
immune_image = get_image("images/immune.png",(180,207))
reborn_image = get_image("images/reborn.png",(180,177))
corrupted_image = get_image("images/shadow_word.png",(180,177))
silence_image = get_image("images/silence.png",(180,180))
dormant_image = get_image("images/dormant.png",(130,177))

'''hero related images'''
mana_crystal_image      = get_image('images/mana_crystal.png', (22,22))
lock_image              = get_image('images/lock.png', (22,22))
shield_image            = get_image('images/Shield_Grey.png', (44,44))
hero_freeze_image       = get_image('images/frozen.png', (170,236))
hero_stealth_image      = get_image("images/stealth.png",(240,260)) 
hero_immune_image       = get_image("images/immune.png",(240,260))
hero_elusive_image      = get_image("images/elusive.png",(180,200))        
        
#Preparing number images
bigfont = pygame.font.Font(None, 300)
numbers={WHITE:{},GREEN:{},RED2:{},RED:{}}
for color in numbers.keys():
    for i in range(200):
        text_img=fontlib.textOutline(bigfont, str(i-100), color, BLACK)
        numbers[color][i-100]=text_img


class BoardObject:
    def __init__(self,img,rect=(0,0),owner=""):
        self.image=img
        self.rect = pygame.rect.Rect(rect[0],rect[1],img.get_width(),img.get_height())
        self.owner=owner
        self.location=self.rect.x,self.rect.y
        
    def isCard(self):
        return False
    
    def isHero(self):
        return False
    


def get_rect(x,y,width,height):
    rect=pygame.rect.Rect(x,y,width,height)
    return rect

def blit_at_center(image,target):
    target_center=target.rect.x+target.image.get_width()/2-image.get_width()/2,target.rect.y+target.image.get_height()/2-image.get_height()/2
    screen.blit(image,target_center)
    return target_center

def get_center(target,image): # Get the right rect left upper corner if image is to be blit on target
    return target.rect.x+target.image.get_width()/2-image.get_width()/2,target.rect.y+target.image.get_height()/2-image.get_height()/2
  
def get_landed_board_area(card):
    if card.owner.side==1: #main player
        if 0<=card.rect.x<=SCREEN_WIDTH-card.mini_image.get_width() and card.rect.y<=SCREEN_HEIGHT*8/16:
            return "Opponent"
        elif 0<=card.rect.x<=SCREEN_WIDTH-card.mini_image.get_width() and SCREEN_HEIGHT*8/16<card.rect.y<=SCREEN_HEIGHT*12/16:
            return "Board"
        elif 0<=card.rect.x<=SCREEN_WIDTH-card.mini_image.get_width() and SCREEN_HEIGHT*12/16<card.rect.y<=SCREEN_HEIGHT:
            return "Hand"
    elif card.owner.side==-1: # opponent player
        if 0<=card.rect.x<=SCREEN_WIDTH-card.mini_image.get_width() and SCREEN_HEIGHT*8/16<=card.rect.y<=SCREEN_HEIGHT:
            return "Opponent"
        elif 0<=card.rect.x<=SCREEN_WIDTH-card.mini_image.get_width() and SCREEN_HEIGHT*4/16<=card.rect.y<SCREEN_HEIGHT*8/16:
            return "Board"
        elif 0<=card.rect.x<=SCREEN_WIDTH-card.mini_image.get_width() and 0<=card.rect.y<SCREEN_HEIGHT*4/16:
            return "Hand"
    return "Other"

def show_arrow(player):
    pygame.draw.line(screen, RED, player.rect.center, player.mouse_pos, 5)
    
def show_text(message="",size=80,location=(300,320),color=WHITE,outline=BLACK,flip=False,pause=0):
    bigfont = pygame.font.Font(None, size)
    text_img=fontlib.textOutline(bigfont, message, color, outline)
    screen.blit(text_img,location)
    if flip:
        pygame.display.flip()
        time.sleep(float(pause))
        
def show_number(number=0,size=80,location=(300,320),color=WHITE,flip=False,pause=0):  
    num_digits=len(str(number))
    text_img=pygame.transform.scale(numbers[color][number],(int(0.5*size*num_digits),int(0.5*size*1.5)))
    screen.blit(text_img,location)
    if flip:
        pygame.display.flip()
        time.sleep(float(pause))
                
def blit_alpha(target, source, location, opacity):
        x = location[0]
        y = location[1]
        temp = pygame.Surface((source.get_width(), source.get_height())).convert()
        temp.blit(target, (-x, -y))
        temp.blit(source, (0, 0))
        temp.set_alpha(opacity)        
        target.blit(temp, location)

def white_out(card):
    whiteout=pygame.transform.scale(pygame.image.load('images/whiteout.jpg').convert(),(card.big_image.get_width(),card.big_image.get_height()))
    for k in range(30):
        whiteout.set_alpha(k*0.5)
        screen.blit(whiteout,card.location)
        pygame.display.flip()
        time.sleep(0.01)

def flash_out(cards):
    whiteout=pygame.transform.scale(pygame.image.load('images/flash_out.png').convert(),(cards[0].big_image.get_width(),cards[0].big_image.get_height()))
    for k in range(30):
        whiteout.set_alpha((29-k)*0.5)
        for card in cards:
            screen.blit(whiteout,card.location)
        pygame.display.flip()
        time.sleep(0.01)
                                        
def get_player(entity):
    if hasattr(entity,'owner'):
        return entity.owner
    elif hasattr(entity,'hero_power'):
        return entity
    else:
        return None
    '''
    if entity.isCard():
        player=entity.owner
    elif entity.isHero():
        player=entity
    else:
        player=entity.owner
        
    return player
    '''
       
def sort_minions_animation(minions):
    num_of_minions=len(minions)
    space=50
    if num_of_minions>0:
        card_width=minions[0].image.get_width()
        left_x=SCREEN_WIDTH/2-num_of_minions/2*(card_width+space)+space/2
        offset=0
        y={-1:SCREEN_HEIGHT/4+45,1:SCREEN_HEIGHT/2}[minions[0].owner.side]
        for minion in minions:
            minion.rect=get_rect(left_x+offset, y,minion.image.get_width(),minion.image.get_height())
            minion.location=minion.rect.x,minion.rect.y
            offset+=(card_width+space)     
           
def sort_hand_animation(player):
    handsize=len(player.hand)
    if(handsize!=0):
        card_width=player.hand[0].image.get_width()
    else:
        card_width=85
    space=20-handsize*2
    left_x=SCREEN_WIDTH/2-handsize/2*(card_width+space/2)+space/2-350

    offset=0
    y={-1:5,1:820}[player.side]
        
    for card in player.hand:
        card.rect=pygame.rect.Rect(left_x+offset, y, card.image.get_width(), card.image.get_height())
        card.location=(card.rect.x,card.rect.y)
        offset+=(card.image.get_width()+space)
    
    #Trigger on add to hand effect if any
    for card in player.hand:
        player.board.activate_triggered_effects('add to hand',card)
        
def trigger_quest_animation(quest):
    show_board(quest.owner.board,exclude=[quest],flip=False)
    if quest.counter>quest.goal:
        quest.counter=quest.goal
    show_text(str(quest.counter)+"/"+str(quest.goal), size=25, location=(quest.rect.x,quest.rect.y), color=WHITE, outline=BLACK, flip=True, pause=0.5)

def trigger_dormant_animation(minion):
    show_board(minion.owner.board,flip=False)
    show_text(str(minion.dormant_counter)+"/"+str(minion.dormant_cap), size=25, location=(minion.rect.x+30,minion.rect.y), color=ORANGE, outline=BLACK, flip=True, pause=0.7)

def awake_animation(minion):
    #zoom_up_animation(minion.image, minion, minion.location, speed=10, max_size=250)
    show_board(minion.owner.board,flip=False)
    buff_animation(minion)

    
def sort_triggerables_animation(triggerables):
    if len(triggerables)>0:
        x=triggerables[0].owner.rect.x+triggerables[0].owner.image.get_width()/2-15
        y=triggerables[0].owner.rect.y
        triggerables[0].rect = get_rect(x, y, triggerables[0].board_image.get_width(), triggerables[0].board_image.get_height())
        triggerables[0].location =triggerables[0].rect.x,triggerables[0].rect.y
        
        offset=1
        for k in range(len(triggerables)-1):
            triggerable_x=x-(-1)**k*45*(1+0.7*math.log(offset))
            triggerable_y=y+30*offset*(1+offset/10)
            triggerables[k+1].rect=get_rect(triggerable_x, triggerable_y, triggerables[k+1].board_image.get_width(), triggerables[k+1].board_image.get_height())
            triggerables[k+1].location=triggerables[k+1].rect.x,triggerables[k+1].rect.y
            if k%2==1:
                offset+=1
        
               
def show_card(card):

    if (not card.owner.board.DEBUG_MODE and card.side==-1 and card.board_area!="Board" and not card.always_show_face) or card.show_back:
        #Card image
        screen.blit(card.owner.mini_card_back_image, (card.rect.x,card.rect.y))
    else:
        #Show taunt on background
        if card.isMinion() and card.has_taunt and card.image==card.board_image:
            center_of_minion=get_center(card,card.taunt_image)
            screen.blit(card.taunt_image, (center_of_minion[0],center_of_minion[1]+20))
            
        #Card image
        if card.zoomed and card.board_area=="Hand" and card.side==1:
            screen.blit(card.image, (card.rect.x,card.rect.y-card.image.get_height()))
        else:
            screen.blit(card.image, (card.rect.x,card.rect.y))
                
        
        #Show deathrattle lists when zoomed   
        if card.isMinion() and card.zoomed and card.board_area=="Board" and card.has_deathrattle and card.image==card.raw_image:
            offset=0
            size=25
            for deathrattle in card.deathrattles:
                x=card.location[0]
                y=card.location[1]+card.image.get_height()+30+offset
                pygame.draw.rect(screen, BLACK, (x,y,card.image.get_width(),size), 0)
                show_text(deathrattle[1], size=size-4, location=(x,y), color=WHITE, flip=False)
                offset+=(size)
        
        #Show deathrattle, poison, windfury, divine shield, stealth, elusive icons      
        if card.isMinion() and card.has_deathrattle and card.image==card.board_image:
            center_of_minion=get_center(card,card.deathrattle_image)
            screen.blit(card.deathrattle_image, (center_of_minion[0],center_of_minion[1]+60))
        
        if card.isMinion() and card.has_trigger and card.image==card.board_image:
            center_of_minion=get_center(card,card.trigger_image)
            screen.blit(card.trigger_image, (center_of_minion[0],center_of_minion[1]+60))
        
        if card.isMinion() and card.has_inspire and card.image==card.board_image:
            center_of_minion=get_center(card,card.trigger_image)
            screen.blit(card.inspire_image, (center_of_minion[0],center_of_minion[1]+60))
            
        if card.isMinion() and card.has_keyword("lifesteal") and card.image==card.board_image:
            center_of_minion=get_center(card,card.lifesteal_image)
            screen.blit(card.lifesteal_image, (center_of_minion[0],center_of_minion[1]+60))
                   
        if card.isMinion() and card.has_poisonous and card.image==card.board_image:
            center_of_minion=get_center(card,card.poisonous_image)
            screen.blit(card.poisonous_image, (center_of_minion[0],center_of_minion[1]+60))
        
        if card.isMinion() and (card.current_spell_damage_boost or card.current_opponent_spell_damage_boost) and card.image==card.board_image:
            center_of_minion=get_center(card,card.spell_damage_boost_image)
            blit_alpha(screen, card.spell_damage_boost_image, (center_of_minion[0],center_of_minion[1]), 180)
    
        if card.isMinion() and card.enrage and card.damaged() and card.image==card.board_image:
            center_of_minion=get_center(card,card.enrage_image)
            blit_alpha(screen, card.enrage_image, (center_of_minion[0],center_of_minion[1]), 120)
    
        if card.isMinion() and (card.has_keyword("stealth")) and card.image==card.board_image:
            center_of_minion=get_center(card,card.stealth_image)
            blit_alpha(screen, card.stealth_image, (center_of_minion[0],center_of_minion[1]), 4000)
           
        if card.isMinion() and (card.has_keyword("elusive")) and card.image==card.board_image:
            center_of_minion=get_center(card,card.elusive_image)
            blit_alpha(screen, card.elusive_image, (center_of_minion[0],center_of_minion[1]), 100)
            
        if card.isMinion() and card.has_divine_shield and card.image==card.board_image:
            center_of_minion=get_center(card,card.divine_shield_image)
            screen.blit(card.divine_shield_image, (center_of_minion[0],center_of_minion[1]+20))
    
        if card.isMinion() and card.windfury_active() and card.image==card.board_image:
            center_of_minion=get_center(card,card.windfury_image)
            blit_alpha(screen, card.windfury_image, (center_of_minion[0],center_of_minion[1]), 100)
            
        if card.isMinion() and (card.frozen and not card.owner.board.get_buff(card)['defrozen']) and card.image==card.board_image:
            center_of_minion=get_center(card,card.freeze_image)
            screen.blit(card.freeze_image, (center_of_minion[0],center_of_minion[1]+20))
        
        if card.isMinion() and card.has_reborn and card.image==card.board_image:
            center_of_minion=get_center(card,card.reborn_image)
            blit_alpha(screen,card.reborn_image, (center_of_minion[0],center_of_minion[1]),140)
        
        if card.isMinion() and "Corruption" in card.attachments and card.attachments["Corruption"] and card.image==card.board_image:
            center_of_minion=get_center(card,card.reborn_image)
            blit_alpha(screen,card.corrupted_image, (center_of_minion[0],center_of_minion[1]),100)
 
        if card.isMinion() and (card.has_immune or card.temporary_effects["immune"] or card.owner.board.get_buff(card)['immune']) and card.image==card.board_image:
            center_of_minion=get_center(card,card.immune_image)
            blit_alpha(screen,card.immune_image, (center_of_minion[0],center_of_minion[1]),50)
        
        if card.isMinion() and card.owner.board.get_buff(card)['shout'] and card.image==card.board_image:
            center_of_minion=get_center(card,card.immune_image)
            blit_alpha(screen,card.immune_image, (center_of_minion[0],center_of_minion[1]),35)
             
        if card.isMinion() and card.silenced and card.image==card.board_image:
            center_of_minion=get_center(card,card.silence_image)
            blit_alpha(screen,card.silence_image, (center_of_minion[0],center_of_minion[1]),90)
         
        if card.isMinion() and card.has_dormant and card.image==card.board_image:
            center_of_minion=get_center(card,card.silence_image)
            blit_alpha(screen, card.stealth_image, (center_of_minion[0],center_of_minion[1]), 4000)
            blit_alpha(screen,card.dormant_image, (center_of_minion[0]+25,center_of_minion[1]+20),200)
           
        if (card.ephemeral or card.copy_target is not None) and card.board_area=="Hand" and not card.zoomed:
            center_of_minion=get_center(card,ephemeral_image)
            blit_alpha(screen, ephemeral_image, (center_of_minion[0],center_of_minion[1]), 330)
    
           
        # Show HP and ATK
        if card.isMinion() and not card.has_dormant:
            if card.image==card.raw_image:
                atk_b=atk_background_zoom
                hp_b=hp_background_zoom
            else:
                atk_b=atk_background
                hp_b=hp_background
                
            #Performance Enhancement
            atk_buff=card.owner.board.get_buff(card)['atk']
            hp_buff=card.owner.board.get_buff(card)['hp']
    
            
            atk_color={-1:RED,0:WHITE,1:GREEN}[sign(card.current_atk+atk_buff-card.atk)]
            #hp_color={-1:RED2,0:WHITE,1:GREEN}[sign(card.current_hp+hp_buff-card.temp_hp)]\
            hp_color={-1:RED2,0:WHITE,1:GREEN}[sign(card.current_hp-card.temp_hp)]
            if card.temp_hp>card.hp and card.current_hp==card.temp_hp:
                hp_color=GREEN
            screen.blit(pygame.transform.scale(atk_b,(int(card.image.get_width()*0.25),int(card.image.get_width()*0.25))), (card.rect.x+card.image.get_width()*0.01,card.rect.y+card.image.get_height()*0.8))
            show_number(max(0,card.current_atk+atk_buff), size=int(card.image.get_width()*0.3), location=(card.rect.x+card.image.get_width()*0.08,card.rect.y+card.image.get_height()*0.83), color=atk_color, flip=False)
            screen.blit(pygame.transform.scale(hp_b,(int(card.image.get_width()*0.25),int(card.image.get_width()*0.25))), (card.rect.x+card.image.get_width()*0.70,card.rect.y+card.image.get_height()*0.77))
            show_number(card.current_hp+hp_buff, size=int(card.image.get_width()*0.3), location=(card.rect.x+card.image.get_width()*0.77,card.rect.y+card.image.get_height()*0.83), color=hp_color, flip=False)
    
        # Show durability and ATK
        if card.isWeapon() and card.board_area=="Hand":
            if card.image==card.raw_image:
                atk_b=atk_background_zoom
                hp_b=hp_background_zoom
            else:
                atk_b=atk_background
                hp_b=hp_background
                

            atk_color={-1:RED,0:WHITE,1:GREEN}[sign(card.current_atk-card.atk)]
            hp_color={-1:RED2,0:WHITE,1:GREEN}[sign(card.current_durability-card.durability)]
            screen.blit(pygame.transform.scale(atk_b,(int(card.image.get_width()*0.25),int(card.image.get_width()*0.25))), (card.rect.x+card.image.get_width()*0.01,card.rect.y+card.image.get_height()*0.8))
            show_number(max(0,card.current_atk), size=int(card.image.get_width()*0.3), location=(card.rect.x+card.image.get_width()*0.08,card.rect.y+card.image.get_height()*0.83), color=atk_color, flip=False)
            screen.blit(pygame.transform.scale(hp_b,(int(card.image.get_width()*0.25),int(card.image.get_width()*0.25))), (card.rect.x+card.image.get_width()*0.70,card.rect.y+card.image.get_height()*0.77))
            show_number(card.current_durability, size=int(card.image.get_width()*0.3), location=(card.rect.x+card.image.get_width()*0.77,card.rect.y+card.image.get_height()*0.83), color=hp_color, flip=False)
    
    
        #Show Cost
        if (card.board_area=="Hand" or card.board_area=="Deck") and card.image!=card.arrow_image and card.name!="Fatigue":
            if card.zoomed:
                cost_b=cost_background_zoom
            elif card.owner.board.get_buff(card)['cost health']:
                cost_b=cost_background_red
            else:
                cost_b=cost_background
                
            cost=card.get_current_cost()
            cost_color={-1:RED,0:WHITE,1:GREEN}[-sign(cost-card.cost)] 
            screen.blit(pygame.transform.scale(cost_b,(int(card.image.get_width()*0.25),int(card.image.get_width()*0.25))), (card.rect.x+card.image.get_width()*0.01,card.rect.y+card.image.get_height()*0.05))
            show_number(cost, size=int(card.image.get_width()*0.3), location=(card.rect.x+card.image.get_width()*0.08,card.rect.y+card.image.get_height()*0.08), color=cost_color, flip=False)
        
def show_selection(options):
    
    space=15
    if len(options)>0:
        card_width=options[0].big_image.get_width()
        left_x=SCREEN_WIDTH/2-len(options)/2*(card_width+space)+space/2-card_width*15/24
        offset=0
        y=SCREEN_HEIGHT/2-285
        for card in options:
            y_offset=0
            if card.selected:
                y_offset=50
                show_text("return", size=40, location=(left_x+offset+card.image.get_width()/3,y+card.image.get_height()+50), color=ORANGE, outline=RED, flip=False)
            card.rect=get_rect(left_x+offset, y+y_offset,card.big_image.get_width(),card.big_image.get_height())
            card.location=card.rect.x,card.rect.y
            offset+=(card_width+space)
            if card.side==-1:
                screen.blit(card.owner.big_card_back_image,card.location)
            else:
                screen.blit(card.big_image,card.location)

def show_hero_selection(options):
    
    screen.blit(pick_hero_background,(0,0))

    space=-20
    hero_rects={}
    
    if len(options)>0:
        left_x=SCREEN_WIDTH*0.06
        offset=0
        y=SCREEN_HEIGHT/2-250
        for hero_name in options:
            hero_image=get_image("images/hero_images/"+hero_name+".png",(510,708))
            hero_rect=get_rect(left_x+offset,y,hero_image.get_width(),hero_image.get_height())
            screen.blit(hero_image,(hero_rect.x,hero_rect.y))
            hero_rects[hero_name]=hero_rect
            offset+=(hero_image.get_width()+space)
    pygame.display.flip()        
    
    return hero_rects
        
def show_draft_screen(selected_cards,options,player,flip=True):
    screen.blit(draft_background,(0,0))
    show_draft(selected_cards)
    show_selection(options)
    show_hero(player)
    show_text("Choose a Card:",location=(450,130))
    if flip:
        pygame.display.flip()
        clock.tick(FPS)
                    
def show_draft(cards):
    
    zoomed_card=None
    hist={0:0,1:0,2:0,3:0,4:0,5:0,6:0,7:0,}
    

            
    #Draw drafted card icons
    if len(cards)>0:
        space=32
        x=SCREEN_WIDTH-cards[0].mini_image.get_width()-350
        offset=0
        y=SCREEN_HEIGHT*0.1
        for card in cards:
            # Count card cost histogram
            if card.cost<=7:
                hist[card.cost]+=1
            else:
                hist[7]+=1
            card.rect=get_rect(x, y+offset,card.mini_image.get_width(),space)
            
            #Place card on right panel
            card.location=card.rect.x,card.rect.y
            offset+=space-5
            
            #Place the zoomed card on top layer
            if card.selected:
                zoomed_card=card
            screen.blit(card.mini_image.subsurface((0, 0, card.mini_image.get_width(), space)),card.location)  
        
        if zoomed_card is not None:
            screen.blit(zoomed_card.big_image,(zoomed_card.location))
    
    #Draw card cost distribution
    left_x = SCREEN_WIDTH*0.325
    bottom=SCREEN_HEIGHT*0.9
    width=23.8
    space=9.7
    offset=0
    for count in hist.values():
        pygame.draw.rect(screen, WHITE, (left_x+offset,bottom-count*15,width,count*15), 1)
        pygame.draw.rect(screen, ORANGE, (left_x+offset+2,bottom-count*15+2,width-4,count*15-2), 0)
        offset+=width+space
    show_text("0   1   2   3   4   5   6   7+",location=(left_x,bottom+10),size=36)  

def show_hero(player):
    screen.blit(player.big_image,(SCREEN_WIDTH*9/72,SCREEN_HEIGHT*16/24))  

            
def show_player(player):
    '''Hero image'''
    screen.blit(player.image, (player.rect.x,player.rect.y))
    if player.is_under_shadow_mode():
        blit_alpha(screen, player.shadow_image, (player.rect.x,player.rect.y), opacity=120)

    if player.frozen:
        screen.blit(player.freeze_image, (player.rect.x,player.rect.y))
        
    if player.has_stealth or player.temporary_effects['stealth'] or player.board.get_buff(player)['stealth']:
        blit_alpha(screen,player.stealth_image, (player.rect.x-30,player.rect.y-40),660)
        
    if player.has_immune or player.temporary_effects['immune'] or player.board.get_buff(player)['immune']:
        blit_alpha(screen,player.immune_image, (player.rect.x-30,player.rect.y-40),60)
    
    if player.has_elusive or player.temporary_effects['elusive'] or player.board.get_buff(player)['elusive']:
        blit_alpha(screen,player.elusive_image, (player.rect.x-10,player.rect.y-10),60)
        
    '''Hero stats'''
    #atk_color={-1:RED,0:WHITE,1:GREEN}[sign(player.current_atk-player.atk)]
    hp_color={-1:RED2,0:WHITE,1:GREEN}[sign(player.current_hp-player.hp)]
    if(player.get_current_atk()>0): 
        screen.blit(atk_background_zoom, (player.rect.x-1/40*player.image.get_width(),player.rect.y+18/32*player.image.get_height()))
        show_number(player.get_current_atk(),40,(player.rect.x+1/20*player.image.get_width(),player.rect.y+19/32*player.image.get_height()),WHITE)
    
    ''''HP'''
    screen.blit(hp_background_zoom, (player.rect.x+23/32*player.image.get_width(),player.rect.y+33/65*player.image.get_height()))
    show_number(player.current_hp,40,(player.rect.x+3/4*player.image.get_width(),player.rect.y+19/32*player.image.get_height()),hp_color)
    
    ''''Shield'''
    if(player.shield>0):
        shield_x,shiekld_y = player.rect.x+10/16*player.image.get_width(),player.rect.y+7/16*player.image.get_height()
        screen.blit(player.shield_image, (shield_x,shiekld_y))
        show_number(player.shield,32,(shield_x+16,shiekld_y+8),WHITE)
     
    '''Hero Power'''
    if player.hero_power.zoomed and player.side==1:
            screen.blit(player.hero_power.image, (player.rect.x+player.image.get_width(),player.rect.y))
    else:
        screen.blit(player.hero_power.image, (player.rect.x+player.image.get_width(),player.rect.y+player.image.get_height()*2/7))
    cost_color={-1:RED2,0:WHITE,1:GREEN}[-sign(player.hero_power.get_current_cost()-player.hero_power.cost)]
    if not player.hero_power.passive:
        show_number(player.hero_power.get_current_cost(), 32, (player.hero_power.rect.x+27/60*player.hero_power.image.get_width(),player.hero_power.rect.y),cost_color)

    show_weapon(player)
    
def show_weapon(player):
    
    #weapon rect move with player
    if player.has_weapon():
        atk_color={-1:RED2,0:WHITE,1:GREEN}[sign(player.weapon.get_current_atk()-player.weapon.atk)]
        durability_color={-1:RED2,0:WHITE,1:GREEN}[sign(player.weapon.current_durability-player.weapon.durability)]
        
        player.weapon.rect.x=player.rect.x-150
        player.weapon.rect.y=player.rect.y+50    
                          
        screen.blit(player.weapon.board_image, (player.weapon.rect.x,player.weapon.rect.y))
        
        show_number(player.weapon.get_current_atk(),40,(player.weapon.rect.x-5,player.weapon.rect.y+95),atk_color)
        show_number(player.weapon.current_durability,40,(player.weapon.rect.x+90,player.weapon.rect.y+95),durability_color)
        
        if player.weapon.has_windfury:
            windfury=player.weapon.windfury_image
            weapon_center=get_center(player.weapon, windfury)
            screen.blit(windfury, (weapon_center))
            
        if player.weapon.has_deathrattle:
            skull=player.weapon.deathrattle_image
            weapon_center=get_center(player.weapon, skull)
            screen.blit(skull, (weapon_center[0],weapon_center[1]+60))
        
        if player.weapon.has_keyword("lifesteal"):
            lifesteal=player.weapon.lifesteal_image
            weapon_center=get_center(player.weapon, lifesteal)
            screen.blit(lifesteal, (weapon_center[0],weapon_center[1]+60))
            
        if player.weapon.has_poisonous:
            poison=player.weapon.poisonous_image
            weapon_center=get_center(player.weapon, poison)
            screen.blit(poison, (weapon_center[0],weapon_center[1]+60))
         
        if player.weapon.has_trigger:
            trigger=player.weapon.trigger_image
            weapon_center=get_center(player.weapon, trigger)
            screen.blit(trigger, (weapon_center[0],weapon_center[1]+60))
                     
def show_mana(player):
    x={-1:310,1:360}[player.side]
    y={-1:50,1:882}[player.side]

    for i in range(player.mana):
        blit_alpha(screen, player.crystal, (SCREEN_WIDTH/2+x+22*i,y), 100)
    for i in range(max(player.current_mana,0)):
        screen.blit(player.crystal, (SCREEN_WIDTH/2+x+22*i,y))
    for i in range(player.locked_mana):
        blit_alpha(screen, player.lock, (SCREEN_WIDTH/2+x+22*(player.mana-1-i),y), 100)
    for i in range(player.overloaded_mana):
        blit_alpha(screen, player.lock, (SCREEN_WIDTH/2+x+22*i,y+26), 100)
            
    show_text(str(player.current_mana)+"/"+str(player.mana), size=30, location=(SCREEN_WIDTH/2+x-70,y), color=WHITE, outline=BLACK, flip=False)

def show_turn(player):
    show_text(message=str(player.player_name)+"'s Turn !",size=120,location=(SCREEN_WIDTH/2-200, SCREEN_HEIGHT/2-75),color=ORANGE,outline=WHITE,flip=True,pause=1.3)

def show_victory(player):
    show_text(message=str(player.player_name)+" won the game !!",size=120,location=(SCREEN_WIDTH/2-500, SCREEN_HEIGHT/2-75),color=PINK,outline=WHITE,flip=True,pause=3)
    
def show_obj(obj):
    screen.blit(obj.image,obj.rect)
    
def show_board(board,exclude=[],flip=True):
    pygame.event.pump()
    
    #if exclude is not None:
    #    board.exclude=exclude
    
    '''Draw backgrounds'''
    screen.blit(board.background,(board.rect.x,board.rect.y))
    for obj in board.bottom_objects:
        screen.blit(obj.image,(obj.rect.x,obj.rect.y))
    
    '''Draw heroes and mana crystrals'''
    for player in board.players.values():
        show_player(player)
        show_mana(player)
        #show_weapon(player)
    

    '''Draw cards'''
    selected_card=0   
    for k in [1,-1]:
        for triggerable in board.secrets[k]+board.quests[k]:
            if triggerable not in board.exclude+exclude:
                show_card(triggerable)
                if triggerable.image==triggerable.raw_image:   #Being selected
                    selected_card=triggerable
          
        for card in board.minions[k]+board.hands[k]+board.objs:
            if card not in board.exclude+exclude:
                show_card(card)
                if card.dragging or card.zoomed:
                    selected_card=card
                          
    '''Highlight the dragged card on top'''
    if selected_card and selected_card not in board.exclude+exclude:
        show_card(selected_card)
    
    for obj in board.upper_objects:
        screen.blit(obj.image,(obj.rect.x,obj.rect.y))
           
    #Draw count down timer
    countdown(board.players[board.control])
    
    #show player names
    show_text(board.players[1].name, size=30, location=(40,780), color=WHITE, outline=BLACK, flip=False)
    show_text(board.players[-1].name, size=30, location=(40,50), color=WHITE, outline=BLACK, flip=False)
    
    #Draw Emote buttons
    show_text("End turn with buttons below:", size=30, location=(1420,650), color=WHITE, outline=BLACK, flip=False)
    
    screen.blit(button,(1450,650))
    show_text("End Turn Normally", size=30, location=(1500,700), color=BLACK, outline=WHITE, flip=False)

    screen.blit(button,(1450,750))
    show_text("Curse Opponent", size=30, location=(1500,800), color=BLACK, outline=WHITE, flip=False)
    
    screen.blit(button,(1450,850))
    show_text("Feeling Good", size=30, location=(1500,900), color=BLACK, outline=WHITE, flip=False)

    #Draw music button
    screen.blit(button,(1450,30))
    show_text("Music "+{True:"Off",False:"On"}[board.music_on], size=30, location=(1500,80), color=BLACK, outline=WHITE, flip=False)
   
    '''Show arrow if any'''
    player=board.players[board.control]
    if player.dragging or player.hero_power.dragging or (player.current_card is not None and player.current_card.image==player.current_card.arrow_image):
        show_arrow(player)
        
    if(flip):
        pygame.display.flip()
 
def countdown(player):
    #inputbox.display_multiline_box(screen,str(player.player_name)+"'s turn", 0,SCREEN_WIDTH-300,100,48,font_color=WHITE,box_color=BLACK,border_color=BLACK)
    #inputbox.display_multiline_box(screen,"Remaining Time: "+str(player.remaining_time), 0,SCREEN_WIDTH-400,150,48,font_color=WHITE,box_color=BLACK,border_color=BLACK)
    
    t=player.board.get_buff(player)['time_limit']
    num_of_nozs=t//15
    if t>0:
        x=int((15-t)/15*rope.get_width())
        screen.blit(rope.subsurface(x,0,rope.get_width()-x,rope.get_height()),(x+230,SCREEN_HEIGHT/2-130))
        screen.blit(ropefire,(x+200,SCREEN_HEIGHT/2-70))
    else: 
        if player.remaining_time<=15:
            x=int((15-player.remaining_time)/15*rope.get_width())
            screen.blit(rope.subsurface(x,0,rope.get_width()-x,rope.get_height()),(x+230,SCREEN_HEIGHT/2-130))
            screen.blit(ropefire,(x+200,SCREEN_HEIGHT/2-70))
          
def explode_rope(player):
    fade_in_out_animation(explode, player, (player.board.end_turn_button.x,player.board.end_turn_button.y), duration=10, stay=0.05)
    white_out_animation(player)

def flare_animation(spell_card):
    effect1=pygame.transform.scale(pygame.image.load('images/flare1.png').convert_alpha(), (60,60))
    effect2=pygame.transform.scale(pygame.image.load('images/flare2.png').convert_alpha(), (120,120))
    center=get_center(spell_card.owner,effect1)
    projectile=BoardObject(effect1,rect=center,owner=spell_card.owner)
    
    move_animation(projectile, dest=(center[0],center[1]-spell_card.owner.side*400), speed=8, zoom=True)
    zoom_up_animation(effect2, spell_card, get_center(projectile,effect2), speed=5, max_size=240)        
        
def trigger_secret_animation(secret_card):
    image=pygame.transform.scale(pygame.image.load('images/hero_images/'+secret_card.card_class+'_secret_trigger.png').convert_alpha(), (540,360))
    fade_in_animation(image, secret_card, (SCREEN_WIDTH/2-270,SCREEN_HEIGHT/2-120), 20)
    show_text("Secret!", size=120, location=(SCREEN_WIDTH/2-130,SCREEN_HEIGHT/2+100), color=ORANGE, outline=BLACK, flip=True, pause=1.5)
    move_animation(secret_card, dest=(200,SCREEN_HEIGHT/2), speed=15, zoom=True)
    time.sleep(1)

def destroy_secret_animation(secret_card):
    move_animation(secret_card, dest=(secret_card.rect.x,secret_card.rect.y-5), speed=15, zoom=True)
    time.sleep(0.6)
    move_animation(secret_card, dest=(secret_card.location[0],secret_card.location[1]-50), speed=12)
    secret_card.owner.secrets.remove(secret_card)
    fade_out_animation(secret_card.image, secret_card, secret_card.location, duration=100)
    secret_card.owner.secrets.append(secret_card)

def destroy_multiple_secret_animation(secret_cards):
    images=[]
    dests=[]
    for secret in secret_cards:
        secret.image=secret.mini_image
        images.append(secret.image)
        dests.append((secret.location[0],secret.location[1]-50))
    move_multiple_animation(secret_cards, dests, speed=12)
    
    for secret in secret_cards:
        secret.owner.secrets.remove(secret)
    fade_out_multiple_animation(images, secret_cards[0], dests, duration=100)
    for secret in secret_cards:
        secret.owner.secrets.append(secret)
        
def complete_quest_animation(quest_card):
    quest_card.location=quest_card.rect.x,quest_card.rect.y
    move_animation(quest_card, dest=(760,360), speed=15, zoom=True)
    effect=pygame.transform.scale(pygame.image.load('images/quest_complete.png').convert_alpha(), (540,360))
    fade_in_animation(quest_card.big_image, quest_card, (760,340), 20)
    zoom_in_animation(effect,quest_card,location=(820,460),max_size=3,min_size=1,speed=70,pause=1)
    #screen.blit(effect,(SCREEN_WIDTH/2-120,SCREEN_HEIGHT/2-120))
    #show_board(quest_card.owner.board,exclude)
    show_text("Quest Complete!", size=120, location=(SCREEN_WIDTH/2-230,SCREEN_HEIGHT/2+100), color=ORANGE, outline=BLACK, flip=True, pause=1.5)

def zoom_in_animation(image,entity,location,max_size=3,min_size=1,speed=50,pause=0):
    board=get_player(entity).board
    scale=int(1000/speed)
    
    board.MOVING_ANIMATION=True
    for k in range(scale+1):
        multiplier=min_size+(max_size-min_size)/scale*(scale-k)
        effect=pygame.transform.scale(image,(int(image.get_width()*multiplier),int(image.get_height()*multiplier)))
        x,y=location[0]-effect.get_width()/2,location[1]-effect.get_height()/2
        show_board(board,exclude=[entity],flip=False)
        screen.blit(effect,(x,y))
        pygame.display.flip()
    board.MOVING_ANIMATION=False
        
    time.sleep(pause)
    
def incur_damage_animation(target,damage):
    show_board(get_player(target).board)
    image=pygame.transform.scale(pygame.image.load('images/exp.png').convert_alpha(), (120,120))  
    center=get_center(target,image)
    screen.blit(image,center)
    show_text("-"+str(damage), size=30, location=(center[0]+45,center[1]+50), color=WHITE, outline=BLACK, flip=True, pause=0.6)

def incur_aoe_damage_animation(targets,amounts):
    if len(targets)>0:
        show_board(get_player(targets[0]).board)
        image=pygame.transform.scale(pygame.image.load('images/exp.png').convert_alpha(), (120,120))  
        
        i=0
        for target in targets:
            damage=amounts[i]
            if target.isMinion() and target.has_divine_shield:
                damage=0
            center=get_center(target,image)
            screen.blit(image,center)
            show_text("-"+str(damage), size=30, location=(center[0]+45,center[1]+50), color=WHITE, outline=BLACK, flip=False)
            i+=1
        pygame.display.flip()
        time.sleep(1)
    
def taunt_animation(minion):
    effect=pygame.transform.scale(pygame.image.load('images/taunt3.png').convert_alpha(),(130,177))
    fade_in_animation(effect, minion.owner, get_center(minion,effect), 20)

def divine_shield_animation(minion):
    effect=pygame.transform.scale(pygame.image.load('images/divine_shield.png').convert_alpha(),(130,177))
    fade_in_animation(effect, minion.owner, get_center(minion,effect), 20)

def windfury_animation(minion):
    effect=pygame.transform.scale(pygame.image.load('images/windfury.png').convert_alpha(),(130,177))
    fade_in_animation(effect, minion.owner, get_center(minion,effect), 10)

def elusive_animation(minion):
    effect=pygame.transform.scale(pygame.image.load('images/elusive.png').convert_alpha(),(130,177))
    fade_in_animation(effect, minion.owner, get_center(minion,effect), 10)
    
def stealth_animation(minion):
    effect=pygame.transform.scale(pygame.image.load('images/stealth.png').convert_alpha(),(130,177))
    fade_in_animation(effect, minion.owner, get_center(minion,effect), 10)

def poisonous_animation(minion):
    effect=pygame.transform.scale(pygame.image.load('images/poisonous.png').convert_alpha(),(35,35))
    minion_center=get_center(minion,effect)
    fade_in_animation(effect, minion.owner, (minion_center[0],minion_center[1]+60), 20)   

def trigger_effect_animation(card,triggering_card):
    center_of_minion=get_center(card,card.trigger_image)
    fade_in_out_animation(card.trigger2_image, triggering_card, (center_of_minion[0],center_of_minion[1]+60), duration=10, stay=0.5)

def inspire_animation(card):
    center_of_minion=get_center(card,card.trigger_image)
    fade_in_out_animation(card.inspire2_image, card, (center_of_minion[0],center_of_minion[1]+60), duration=10, stay=0.5)

def overkill_animation(card):
    center_of_minion=get_center(card,card.overkill_image)
    fade_in_out_animation(card.overkill_image, card, (center_of_minion[0],center_of_minion[1]+60), duration=30, stay=0.5)


def trigger_poisonous_animation(card):
    center_of_minion=get_center(card,card.trigger_image)
    zoom_up_animation(card.poisonous_image,card,(center_of_minion[0]-5,center_of_minion[1]+60),speed=10,max_size=50)
  
def trigger_lifesteal_animation(card):
    if card.isMinion():
        center_of_minion=get_center(card,card.lifesteal_image)
        zoom_up_animation(card.lifesteal_image,card,(center_of_minion[0],center_of_minion[1]+60),speed=10,max_size=50)
        
def zoom_up_animation(image,entity,target_center,speed=10,max_size=50):
    board=get_player(entity).board
    board.MOVING_ANIMATION=True
    for i in range(int(max_size/speed)):
        size=int(speed*i)
        z_image=pygame.transform.scale(image,(int(size),int(size)))
        x=target_center[0]+image.get_width()/2-z_image.get_width()/2
        y=target_center[1]+image.get_height()/2-z_image.get_height()/2
        show_board(board,flip=False)
        screen.blit(z_image,(x,y))
        pygame.display.flip()  
    board.MOVING_ANIMATION=False
                
def zoom_down_animation(image,entity,target_center,speed=10,max_size=50):
    board=get_player(entity).board
    board.MOVING_ANIMATION=True
    for i in range(int(max_size/speed)):
        size=int(max_size-speed*(i+1))
        z_image=pygame.transform.scale(image,(int(size),int(size)))
        x=target_center[0]+image.get_width()/2-z_image.get_width()/2
        y=target_center[1]+image.get_height()/2-z_image.get_height()/2
        show_board(board,flip=False)
        screen.blit(z_image,(x,y))
        pygame.display.flip()
    board.MOVING_ANIMATION=False

def zoom_up_multiple_animation(images,entity,target_centers,speed=1,max_size=2,min_size=1):
    board=get_player(entity).board
    board.MOVING_ANIMATION=True
    for i in range(int(100/speed)):
        size=min_size+(max_size-min_size)/100*speed*(i+1)
             
        show_board(board,flip=False)
        for k in range(len(images)):
            z_image=pygame.transform.scale(images[k],(int(images[k].get_width()*size),int(images[k].get_height()*size)))
            x=target_centers[k][0]+images[k].get_width()/2-z_image.get_width()/2
            y=target_centers[k][1]+images[k].get_height()/2-z_image.get_height()/2
            
            screen.blit(z_image,(x,y))
        pygame.display.flip()
    board.MOVING_ANIMATION=False

def zoom_down_multiple_animation(images,entity,target_centers,speed=1,max_size=2,min_size=1):
    board=get_player(entity).board
    board.MOVING_ANIMATION=True
    for i in range(int(100/speed)):
        size=max_size-(max_size-min_size)/100*speed*(i+1)
             
        show_board(board,flip=False)
        for k in range(len(images)):
            z_image=pygame.transform.scale(images[k],(int(images[k].get_width()*size),int(images[k].get_height()*size)))
            x=target_centers[k][0]+images[k].get_width()/2-z_image.get_width()/2
            y=target_centers[k][1]+images[k].get_height()/2-z_image.get_height()/2
            
            screen.blit(z_image,(x,y))
        pygame.display.flip()
    board.MOVING_ANIMATION=False

                           
def transform_animation(original,new):
    effect=pygame.transform.scale(pygame.image.load('images/smoke.png').convert_alpha(),(200,200))
    fade_in_animation(effect, new, get_center(original,effect), 20)
    fade_out_animation(effect, original, get_center(original,effect), 20)

def shake_board(entity,intensity=0.05,duration=10):
    board=get_player(entity).board
    board.MOVING_ANIMATION=True
    for i in range(duration):
        board.rect.x=-intensity*200
        show_board(board)
        pygame.display.flip()
        board.rect.x=intensity*200
        show_board(board)
        pygame.display.flip()
    board.MOVING_ANIMATION=False
    board.rect.x=0
    show_board(board)
    pygame.display.flip()
  
def shake_animation(target,cause=None,direction="horizontal",intensity=0.05,duration=30):
    if cause.isCard():
        board=cause.owner.board
        show_cause=show_card
    elif cause.isHero():
        board=cause.board
        show_cause=show_player
    else:
        board=cause.owner.board
        show_cause=show_obj
    
    if target.isCard():
        show_target=show_card
    elif target.isHero():
        show_target=show_player
    else:
        show_target=show_obj
        
    t=int(duration)
    board.MOVING_ANIMATION=True
    for k in range(t):
        if direction=="horizontal":
            target.rect.x,target.rect.y=target.location[0]+(-1)**(k+1)*target.image.get_width()*intensity,target.location[1]
        elif direction=="vertical":
            target.rect.x,target.rect.y=target.location[0],target.location[1]+(-1)**k*target.image.get_height()*intensity
       
        show_board(board,flip=False)
        show_target(target)
        if not(cause.isCard() and cause.card_type=="Spell"):
            show_cause(cause)
        target.rect.x,target.rect.y=target.location
        pygame.display.flip()
    board.MOVING_ANIMATION=False
    
def move_multiple_animation(entities,dests,speed=100,zoom=False):
    if len(entities)>0:
        board=get_player(entities[0]).board
    
        t=int(500//speed)
        board.MOVING_ANIMATION=True
        for k in range(t):
            show_board(board,flip=False)
            for i in range(len(entities)):
                entity=entities[i]
                dest=dests[i]
                entity.rect.x,entity.rect.y=entity.location[0]+(k+1)/t*(dest[0]-entity.location[0]),entity.location[1]+(k+1)/t*(dest[1]-entity.location[1])
                if entity.isCard():
                    if zoom:
                        entity.image = pygame.transform.scale(entity.raw_image, (int(entity.raw_image.get_width()*(k+t)/2/t),int(entity.raw_image.get_height()*(k+t)/2/t)))
                    show_card(entity)
                elif entity.isHero():
                    show_player(entity)
                else:
                    screen.blit(entity.image,(entity.rect.x,entity.rect.y))
            pygame.display.flip()
            clock.tick(FPS)
        board.MOVING_ANIMATION=False
        for entity in entities:
            entity.location=entity.rect.x,entity.rect.y
        
            
def move_animation(entity,dest=(0,0),speed=100,trace=False,zoom=False):
    board=get_player(entity).board
    x,y=dest[0]-entity.location[0],dest[1]-entity.location[1]
    t=int(500//speed)
    board.MOVING_ANIMATION=True
    for k in range(t):
        entity.rect.x,entity.rect.y=entity.location[0]+(k+1)/t*x,entity.location[1]+(k+1)/t*y
        if entity.isCard():
            if zoom:
                entity.image = pygame.transform.scale(entity.raw_image, (int(entity.raw_image.get_width()*(k+t)/2/t),int(entity.raw_image.get_height()*(k+t)/2/t)))
            show_board(board,flip=False)
            show_card(entity)
        elif entity.isHero():
            show_board(board,flip=False)
            show_player(entity)
        else:
            if not trace:
                show_board(board,flip=False)
            screen.blit(entity.image,(entity.rect.x,entity.rect.y))
        pygame.display.flip()
        clock.tick(FPS)
    board.MOVING_ANIMATION=False
    entity.location=entity.rect.x,entity.rect.y

def move_multiple_curve_animation(entities,dests,Y=150,speed=20,zoom=False):
    if len(entities)>0:
        board=get_player(entities[0]).board
    
        t=int(500//speed)
        board.MOVING_ANIMATION=True
        for k in range(t):
            show_board(board,flip=False)
            for i in range(len(entities)):
                entity,dest=entities[i],dests[i]
                x0,y0=entity.rect.x,entity.rect.y
                xd,yd=dest[0],dest[1]
                if x0==xd:
                    x0+=0.1
                X=(x0*x0+y0*y0-xd*xd-yd*yd-2*Y*(y0-yd))/(2*(x0-xd))
                R=sqrt((X-xd)**2+(Y-yd)**2)
                
                entity.rect.y=entity.location[1]-(1+k)/t*(y0-yd)
                entity.rect.x=X-entity.owner.side*sqrt(R**2-(entity.rect.y-Y)**2)
                if entity.isCard():
                    if zoom:
                        entity.image = pygame.transform.scale(entity.raw_image, (int(entity.raw_image.get_width()*(k+t)/2/t),int(entity.raw_image.get_height()*(k+t)/2/t)))
                    show_card(entity)
                elif entity.isHero():
                    show_player(entity)
                else:
                    screen.blit(entity.image,(entity.rect.x,entity.rect.y))
            pygame.display.flip()
            clock.tick(FPS)
        board.MOVING_ANIMATION=False
        
        for entity in entities:    
            entity.location=entity.rect.x,entity.rect.y

def move_curve_animation(entity,dest=(0,0),Y=150,speed=500,zoom=False):
    board=get_player(entity).board
    x0,y0=entity.rect.x,entity.rect.y
    xd,yd=dest[0],dest[1]
    X=(x0*x0+y0*y0-xd*xd-yd*yd-2*Y*(y0-yd))/(2*(x0-xd))
    R=sqrt((X-xd)**2+(Y-yd)**2)

    t=int(500//speed)
    board.MOVING_ANIMATION=True
    for k in range(t):
        entity.rect.y=entity.location[1]-(1+k)/t*(y0-yd)
        entity.rect.x=X-entity.owner.side*sqrt(R**2-(entity.rect.y-Y)**2)
        if entity.isCard():
            if zoom:
                entity.image = pygame.transform.scale(entity.raw_image, (int(entity.raw_image.get_width()*(k+t)/2/t),int(entity.raw_image.get_height()*(k+t)/2/t)))
            show_board(board,flip=False)
            show_card(entity)
        elif entity.isHero():
            show_board(board,flip=False)
            show_player(entity)
        else:
            show_board(board,flip=False)
            screen.blit(entity.image,(entity.rect.x,entity.rect.y))
        pygame.display.flip()
        clock.tick(FPS)
    entity.location=entity.rect.x,entity.rect.y
    board.MOVING_ANIMATION=False

def scroll_of_wonder_animation(card,spell):
        spell.initialize_location((spell.owner.deck.location[0]-50,spell.owner.deck.location[1]))
        spell.image=spell.big_image
        show_card(spell)
        pygame.display.flip()
        time.sleep(1)
        
def reveal_animation(card):
    #Initialzie cards on deck positions
    if card is not None: 
        card.rect.x,card.rect.y=card.owner.deck.rect.x,card.owner.deck.rect.y
        card.location=card.rect.x,card.rect.y

    if card is not None:
        move_multiple_animation([card], dests=[(1250,SCREEN_HEIGHT/2-150+card.owner.side*150)], speed=30, zoom=False)
        time.sleep(1.2)
            
def joust_animation(card1,card2):
    
    #Initialzie cards on deck positions
    if card1 is not None: 
        card1.rect.x,card1.rect.y=card1.owner.deck.rect.x,card1.owner.deck.rect.y
        card1.location=card1.rect.x,card1.rect.y
    if card2 is not None: 
        card2.rect.x,card2.rect.y=card2.owner.deck.rect.x,card2.owner.deck.rect.y
        card2.location=card2.rect.x,card2.rect.y

    if card1 is not None and card2 is not None:
        #Move left
        move_multiple_animation([card1,card2], dests=[(1250,SCREEN_HEIGHT/2-150+card1.owner.side*150),(1250,SCREEN_HEIGHT/2-150+card2.owner.side*150)], speed=30, zoom=False)
        time.sleep(1.2)
    
    elif card1 is not None and card2 is None:
        move_animation(card1, dest=(1250,SCREEN_HEIGHT/2-150+card1.owner.side*150), speed=30, zoom=False)
        time.sleep(1.2)
    elif card2 is not None and card1 is None:
        move_animation(card2, dest=(1250,SCREEN_HEIGHT/2-150+card2.owner.side*150), speed=30, zoom=False)
        time.sleep(1.2)

def winner_animation(winner,loser):
    
    winner.image=winner.big_image
    show_board(winner.owner.board, flip=False)
    if loser is not None:
        show_card(loser)
    show_card(winner)
    pygame.display.flip()
    time.sleep(1.2)
    winner.image=winner.raw_image
    show_board(winner.owner.board, flip=False)
    if loser is not None:
        show_card(loser)
    show_card(winner)
    pygame.display.flip()
    winner.image=winner.mini_image
     
def deck_in_animation(card,deck,skip_zoom=False):  
    if card is not None:   
        if not skip_zoom:  
            #Moving up a bit
            move_animation(card,dest=(card.rect.x,card.rect.y-50),speed=30)
            time.sleep(0.5)
    
        #Move to target deck
        move_animation(card,dest=(deck.rect.x,deck.rect.y),speed=80)
        
        #Card into deck
        show_board(card.owner.board)
    
def draw_animation(player,card):  
    hand_x=SCREEN_WIDTH/2
    if(player.side==1):
        hand_y=740
        offset=0
    else:
        hand_y=10
        offset=-card.image.get_height()*2
        
    #Initialize card on deck position
    card.rect=pygame.rect.Rect(SCREEN_WIDTH-card.image.get_width()*2, SCREEN_HEIGHT/2+offset, card.image.get_width(), card.image.get_height())
    card.location=card.rect.x,card.rect.y
    
    #Moving up a bit
    move_animation(card,dest=(card.rect.x,card.rect.y-50),speed=25)
    time.sleep(0.1)
    
    #Moving from deck to hand
    move_animation(card,dest=(hand_x,hand_y),speed=60)
    
    sort_hand_animation(player)
    
def discard_animation(card):
    move_animation(card, dest=(card.rect.x,card.rect.y-(card.owner.side)*200), speed=10, zoom=True)

def discard_multiple_animation(cards):
    dests=[]
    for card in cards:
        dests.append((card.rect.x,card.rect.y-(card.owner.side)*200))
    move_multiple_animation(cards, dests, speed=10, zoom=False)
    
    dests=[]
    for card in cards:
        card.owner.board.exclude.append(card)
        dests.append((card.rect.x,card.rect.y-(card.owner.side)*1500))
    move_multiple_animation(cards, dests, speed=80, zoom=False)
    
    for card in cards:
        card.owner.board.exclude.remove(card)


def recruit_animation(minion):
       
    #Moving forward
    move_animation(minion,dest=(minion.rect.x,minion.rect.y),speed=30)  
    minion.image=minion.board_image
    
def echoing_ooze_animation(minion):
    effect1=pygame.transform.scale(pygame.image.load('images/slime.png').convert_alpha(),(184,120))
    effect2=pygame.transform.scale(pygame.image.load('images/slime.png').convert_alpha(),(184,120))
    
    fade_in_out_animation(effect1,minion,get_center(minion,effect1),duration=50,stay=0.4,max_opacity=100)
    
    projectile=BoardObject(effect2,rect=get_center(minion,effect2),owner=minion.owner)
    target_center=get_center(minion,effect2)
    move_animation(projectile, dest=(target_center[0]+minion.image.get_width(),target_center[1]), speed=10, zoom=False)
                   
def summon_animation(minion,speed=30,skip_zoom=False):
           
    #Moving forward
    move_animation(minion,dest=(minion.rect.x,minion.rect.y),speed=speed)

    if not skip_zoom:
        #Moving up a bit and zoom
        move_animation(minion,dest=(minion.rect.x,minion.rect.y-50),speed=30,zoom=True)
        time.sleep(0.4)
        
        #Moving back
        minion.image=minion.board_image
        move_animation(minion,dest=(minion.rect.x,minion.rect.y+50),speed=80)
        
    minion.image=minion.board_image
    minion.owner.board.sort_minions(minion.owner.side)

def choose_mulligan_cards(cards):

    mulligan_button=get_rect(1400,410,130,80)
    player=cards[0].owner
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for target in cards:            
                        if target.rect.collidepoint(event.pos):
                            target.selected= not target.selected
                            
                    if mulligan_button.collidepoint(event.pos):
                        selected_cards=[]
                        remaining_cards=[]
                        for card in cards:
                            if card.selected:
                                card.selected=False
                                selected_cards.append(card)
                            else:
                                remaining_cards.append(card)
                                
                        return selected_cards,remaining_cards
   
        show_board(player.board,flip=False)
        show_text("Choose cards to return to deck", location=(100,100),color=WHITE, outline=BLACK, flip=False)
        show_selection(cards)
        screen.blit(button,(1300,370))
        #pygame.draw.rect(screen, ORANGE, (1400,410,130,80), 0)
        show_text("Done with selection", size=30, location=(1330,410), color=BLACK, outline=WHITE, flip=False)
        pygame.display.flip()
  
  
        '''player.remaining_time=player.board.turn_time_limit-int(time.perf_counter()-player.board.start_time)
        if player.remaining_time<=0:
            database.insert_event(player,entity=player,target=0,event_pos=(0,0),event_type="choose")     
            return cards[0]'''
        
def choose_one(cards):
    if len(cards)==0:
        return None
    player=cards[0].owner
    if player.name=='AI':
        return random.choice(cards)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and (player.side==1 or player.board.DEBUG_MODE):
                if event.button == 1:
                    for target in cards:            
                        if target.rect.collidepoint(event.pos):
                            target.selected = True
                                        
            elif event.type == pygame.MOUSEBUTTONUP and (player.side==1 or player.board.DEBUG_MODE):
                if event.button == 1:
                    for target in cards:            
                        if target.rect.collidepoint(event.pos) and target.selected:
                            database.insert_event(player,entity=player,target=cards.index(target),event_pos=event.pos,event_type="choose")
                            target.selected=False
                            return target  
                    for target in cards:
                        target.selected=False
                        
        if player.board.control==-1 and not player.board.DEBUG_MODE:
            opponent_events = database.get_events(player.board.players[-1],event_type="choose")
            for event in opponent_events:
                event_id,event_str=event
                target=player.board.resolve_choose(event_str,cards)
                database.resolve_event(event_id)
                return target
              
        show_board(player.board,flip=False)
        show_selection(cards)
        pygame.display.flip()
  
        player.remaining_time=player.board.turn_time_limit[player.side]-int(time.perf_counter()-player.board.start_time)
        if player.remaining_time<=0:
            database.insert_event(player,entity=player,target=0,event_pos=(0,0),event_type="choose")     
            return cards[0]
        
def choose_target(chooser,target="character",target_type=None,message=""):
    player=get_player(chooser)
    
    targets=[]
    if target=="minion":
        for minion in player.all_minions():
            if not (minion.side==-chooser.side and minion.is_stealthed()):
                if target_type is not None:
                    if minion.has_race(target_type) or (len(target_type.split())==2 and getattr(minion,target_type.split()[0])) or (len(target_type.split())==3 and getattr(getattr(minion,target_type.split()[0])(),target_type.split()[1])(int(target_type.split()[2]))):
                        targets.append(minion)
                else:
                    targets.append(minion)
    elif target=="enemy minion":
        for minion in player.enemy_minions():
            if not (minion.side==-chooser.side and minion.is_stealthed()):
                if target_type is not None:
                    if minion.has_race(target_type) or (len(target_type.split())==2 and getattr(minion,target_type.split()[0])) or (len(target_type.split())==3 and getattr(getattr(minion,target_type.split()[0])(),target_type.split()[1])(int(target_type.split()[2]))):
                        targets.append(minion)
                else:
                    targets.append(minion)
    elif target=="friendly minion":
        for minion in player.friendly_minions():
            if not (minion.side==-chooser.side and minion.is_stealthed()):
                if target_type is not None:
                    if minion.has_race(target_type) or (len(target_type.split())==2 and getattr(minion,target_type.split()[0])) or (len(target_type.split())==3 and getattr(getattr(minion,target_type.split()[0])(),target_type.split()[1])(int(target_type.split()[2]))):
                        targets.append(minion)
                else:
                    targets.append(minion)
    elif target=="enemy character":
        for target in player.enemy_characters():
            if not (target.side==-chooser.side and target.is_stealthed()):
                targets.append(target)
    elif target=="friendly character":
        targets=player.friendly_characters()
    elif target=="hero":
        targets=[chooser.owner]
        if not chooser.owner.opponent.is_stealthed():
            targets.append(chooser.owner.opponent)
    elif target=="character":
        for target in player.all_characters():
            if not (target.side==-chooser.side and target.is_stealthed()):
                targets.append(target)
    elif target=="enemy card":
        targets=player.board.hands[player.opponent.side]
    elif target=="friendly card":
        targets=player.board.hands[player.side]
    elif target=="card":
        targets=player.board.hands[1]+player.board.hands[-1]
    elif target=="any":
        targets=player.all_characters()+player.board.hands[1]+player.board.hands[-1]
    
    if chooser in targets:
        targets.remove(chooser)
        
    if len(targets)==0:
        return "Empty"
    elif player.name=="AI":
        return random.choice(targets)
    
    SELECTED=False
    mouse_x,mouse_y=chooser.rect.x,chooser.rect.y
    while not SELECTED:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pass
                
            elif event.type == pygame.MOUSEBUTTONDOWN and (player.side==1 or player.board.DEBUG_MODE):
                if event.button == 1:
                    for target in targets:            
                        if target.rect.collidepoint(event.pos):
                            target.selected = True
            
            elif event.type == pygame.MOUSEMOTION and (player.side==1 or player.board.DEBUG_MODE):           
                mouse_x,mouse_y=event.pos
                                    
            elif event.type == pygame.MOUSEBUTTONUP and (player.side==1 or player.board.DEBUG_MODE):
                if event.button == 1:
                    for target in targets:            
                        if target.rect.collidepoint(event.pos) and target.selected:
                            target.selected=False
                            database.insert_event(player,entity=None,target=target,event_pos=event.pos,event_type="choose")  
                            return target
                     
                    database.insert_event(player,entity=None,target=None,event_pos=event.pos,event_type="choose")   
                    for target in targets:
                        target.selected=False
                    
                    if chooser.isMinion():
                        chooser.return_hand(reset=False)
                    return None
        
        if player.board.control==-1 and not player.board.DEBUG_MODE:
            opponent_events = database.get_events(player.board.players[-1],event_type="choose")
            for event in opponent_events:
                event_id,event_str=event
                target=player.board.resolve_choose(event_str,targets,chooser)
                database.resolve_event(event_id)
                return target
              
        player.remaining_time=player.board.turn_time_limit[player.side]-int(time.perf_counter()-player.board.start_time)
        show_board(player.board,flip=False)
        pygame.draw.line(screen, RED, (chooser.location[0]+chooser.image.get_width()/2,chooser.location[1]+chooser.image.get_height()/2), (mouse_x,mouse_y), 5)
        msg="Choose a target to "+message
        bigfont = pygame.font.Font(None, 70)
        text_img=fontlib.textOutline(bigfont, msg, RED, WHITE)
        screen.blit(text_img,(400, 300))
        pygame.display.flip()
  
        if player.remaining_time<=0:
            database.insert_event(player,entity=None,target=None,event_pos=(0,0),event_type="choose")  
            if chooser.isMinion():
                chooser.return_hand(reset=False)
            return None

def return_hand_animation(minion):
    
    #Move up a bit
    move_animation(minion, dest=(minion.location[0],minion.location[1]-50), speed=20)
    
    
    #Move back to hand
    hand_x=SCREEN_WIDTH/2
    if(minion.owner.side==1):
        hand_y=740
    else:
        hand_y=10
    move_animation(minion, dest=(hand_x,hand_y), speed=30)    

def equip_weapon_animation(player,weapon):
    weapon.initialize_location((player.rect.x-150,player.rect.y))
    move_animation(weapon, dest=(player.rect.x-150,player.rect.y+player.side*50), speed=30)
    weapon.image=weapon.board_image
    
            
def attack_animation(attacker,target):
    board=get_player(attacker).board
    
    original_x,original_y=attacker.location
    
    #Move back a little
    move_animation(attacker,dest=(8/7*attacker.location[0]-1/7*target.location[0],8/7*attacker.location[1]-1/7*target.location[1]),speed=30)

    #Moving forward
    move_animation(attacker,dest=(target.rect.x,target.rect.y+50),speed=80)

    #Shake the target horizontally
    shake_animation(target,cause=attacker,direction="horizontal",intensity=0.1,duration=10)

    #return to original location    
    attacker.location = original_x,original_y
    attacker.rect.x,attacker.rect.y = attacker.location 
    target.rect.x,target.rect.y=target.location
    show_board(board)
    clock.tick(FPS)

def burn_animation(card):
    
    board=card.owner.board

    #Initialize card on deck position
    #card.rect=pygame.rect.Rect(card.owner.deck.rect.x, card.owner.deck.rect.y, card.image.get_width(), card.image.get_height())
    card.location=card.rect.x,card.rect.y
    show_board(board,flip=False)
    show_card(card)
    pygame.display.flip()
        
    #Moving to left a bit
    move_animation(card,dest=(card.location[0]-150,card.location[1]-50),speed=30)
    time.sleep(0.2)
    
    #Moving up a bit and zoom
    move_animation(card,dest=(card.location[0],card.location[1]-50),speed=30,zoom=True)
    time.sleep(0.8)

    #Shake the target vertically
    shake_animation(card,cause=card.owner,direction="vertical",intensity=0.1)
    
    #show burning effect
    burn=pygame.image.load('images/burn.png').convert_alpha()
    burn=pygame.transform.scale(burn, (140,140))
    show_board(board,flip=False)
    screen.blit(burn,card.location)
    pygame.display.flip()
    time.sleep(1)

def on_drawn_animation(card):
    board=card.owner.board

    #Initialize card on deck position
    card.rect=pygame.rect.Rect(card.owner.deck.rect.x-50, card.owner.deck.rect.y, card.image.get_width(), card.image.get_height())
    card.location=card.rect.x,card.rect.y
    show_board(board,flip=False)
    show_card(card)
    pygame.display.flip()
        
    #Moving up a bit and zoom
    move_animation(card,dest=(card.location[0],card.location[1]-50),speed=30,zoom=True)
    time.sleep(0.8)
    
def explode_animation(card):
    
    board=card.owner.board

    #Initialize card on deck position
    card.rect=pygame.rect.Rect(card.owner.deck.rect.x, card.owner.deck.rect.y, card.image.get_width(), card.image.get_height())
    card.location=card.rect.x,card.rect.y
    show_board(board,flip=False)
    show_card(card)
    pygame.display.flip()
        
    #Moving to player
    move_animation(card, dest=(card.owner.rect.x,card.owner.rect.y), speed=17)
    time.sleep(0.5)
    
    #Moving up a bit and zoom
    move_animation(card,dest=(card.location[0],card.location[1]-50),speed=30,zoom=True)
    time.sleep(0.8)

    #Shake the target vertically
    shake_animation(card,cause=card.owner.opponent,direction="vertical",intensity=0.15)
    
    #show burning effect
    burn=pygame.image.load('images/explode.png').convert_alpha()
    burn=pygame.transform.scale(burn, (140,140))
    show_board(board,flip=False)
    screen.blit(burn,card.location)
    pygame.display.flip()
    time.sleep(1)

def fatigue_animation(card):
    
    board=card.owner.board

    #Initialize card on deck position
    card.rect=pygame.rect.Rect(card.owner.deck.rect.x, card.owner.deck.rect.y, card.image.get_width(), card.image.get_height())
    card.location=card.rect.x,card.rect.y
    show_board(board,flip=False)
    show_card(card)
    pygame.display.flip()
        
    #Moving to player
    move_animation(card, dest=(card.owner.rect.x,card.owner.rect.y), speed=17,zoom=True)
    time.sleep(0.5)

    #show fatigue effect


            
def destroy_animation(minion):
    
    board=minion.owner.board
    
    time.sleep(0.5)
    
    #Shake the target vertically
    shake_animation(minion,cause=minion,direction="vertical",intensity=0.1,duration=10)
    
    #show explode effect
    minion.image=pygame.image.load('images/exp.png').convert_alpha()
    minion.image=pygame.transform.scale(minion.image, (85,118))
    show_board(board)
    time.sleep(0.2)

def destroy_multiple_animation(minions):
    if len(minions)>0:
        board=minions[0].owner.board
        
        time.sleep(0.2)
    
        #show explode effect
        for minion in minions:
            minion.image=pygame.transform.scale(pygame.image.load('images/exp.png').convert_alpha(), (85,118))
        show_board(board)
        time.sleep(0.5)

            
def destroy_hero_animation(player):
    board=player.board
    
    time.sleep(0.5)
    
    #Shake the target vertically
    shake_animation(player,cause=player,direction="vertical",intensity=0.15)

    #Shattering the hero
    player.rect.x,player.rect.y=player.location
    show_board(board)
    shatter_source=pygame.image.load('images/shatter.png').convert()
    shatter=pygame.transform.scale(shatter_source, (160,160))
    for k in range(50):
        shatter.set_alpha(k*1.5)
        show_board(board,flip=False)
        screen.blit(shatter,player.location)
        pygame.display.flip()
        clock.tick(FPS)
        
    #show skull 
    player.image=pygame.image.load('images/skull.png').convert_alpha()
    player.image=pygame.transform.scale(player.image, (160,160))
    show_board(board)
    time.sleep(1)
    clock.tick(FPS*2)

def shield_animation(player):
    
    shield_x,shield_y = player.rect.x+10/16*player.image.get_width(),player.rect.y+7/16*player.image.get_height()
    shield=BoardObject(player.shield_image,rect=(shield_x,shield_y),owner=player)
    screen.blit(player.shield_image, (shield_x,shield_y))
    shake_animation(shield, player.hero_power, direction="horizontal", intensity=0.05, duration=10)

def replace_hero_animation(hero_card):
    new_hero_image=get_image("images/hero_images/"+hero_card.name+".png",(204,283))
    hero_card.image=new_hero_image
    hero_card.location=(760,400)
    fade_in_animation(new_hero_image, hero_card, target_location=hero_card.location, duration=150)
    time.sleep(0.6)
    move_animation(hero_card, dest=hero_card.owner.location, speed=30, zoom=False)
    
def enable_hero_power_animation(hero_power):
    move_animation(hero_power, dest=(hero_power.rect.x,hero_power.rect.y-10), speed=30, zoom=False)
    hero_power.image = hero_power.board_image
    move_animation(hero_power, dest=(hero_power.rect.x,hero_power.rect.y+10), speed=30, zoom=False)
    
def disable_hero_power_animation(hero_power):
    hero_power.image = hero_power.disabled_image

def slide_animation(image,entity,location,direction="right",speed=10):
    board=get_player(entity).board
    slices=int(500/speed)
    board.MOVING_ANIMATION=True
    if direction=="right":
        for i in range(slices):
            effect=image.subsurface(0,0,image.get_width()*(i+1)/slices,image.get_height())
            show_board(board, flip=False)
            screen.blit(effect,location)
            pygame.display.flip()
    elif direction=="left":
        for i in range(slices):
            effect=image.subsurface(image.get_width()-image.get_width()*(i+1)/slices,0,image.get_width()*(i+1)/slices,image.get_height())
            show_board(board, flip=False)
            screen.blit(effect,(location[0]+image.get_width()-image.get_width()*(i+1)/slices,location[1]))
            pygame.display.flip()
    elif direction=="down":
        for i in range(slices):
            effect=image.subsurface(0,0,image.get_width(),image.get_height()*(i+1)/slices)
            show_board(board, flip=False)
            screen.blit(effect,location)
            pygame.display.flip()
    elif direction=="up":
        for i in range(slices):
            effect=image.subsurface(0,image.get_height()-image.get_height()*(i+1)/slices,image.get_width(),image.get_height()*(i+1)/slices)
            show_board(board, flip=False)
            screen.blit(effect,location)
            pygame.display.flip()
    board.MOVING_ANIMATION=False

def slide_multiple_animation(images,entity,locations,direction="right",speed=10):
    board=get_player(entity).board
    slices=int(500/speed)
    board.MOVING_ANIMATION=True
    if direction=="right":
        for i in range(slices):
            j=0
            show_board(board, flip=False)
            for image in images:
                effect=image.subsurface(0,0,image.get_width()*(i+1)/slices,image.get_height())
                screen.blit(effect,locations[j])
                j+=1
            pygame.display.flip()
    elif direction=="left":
        for i in range(slices):
            j=0
            show_board(board, flip=False)
            for image in images:
                effect=image.subsurface(image.get_width()-image.get_width()*(i+1)/slices,0,image.get_width()*(i+1)/slices,image.get_height())
                screen.blit(effect,(locations[j][0]+image.get_width()-image.get_width()*(i+1)/slices,locations[j][1]))
                j+=1
            pygame.display.flip()
    elif direction=="down":
        for i in range(slices):
            j=0
            show_board(board, flip=False)
            for image in images:
                effect=image.subsurface(0,0,image.get_width(),image.get_height()*(i+1)/slices)
                screen.blit(effect,locations[j])
                j+=1
            pygame.display.flip()
    elif direction=="up":
        for i in range(slices):
            j=0
            show_board(board, flip=False)
            for image in images:
                effect=image.subsurface(0,image.get_height()-image.get_height()*(i+1)/slices,image.get_width(),image.get_height()*(i+1)/slices)
                screen.blit(effect,locations[j])
                j+=1
            pygame.display.flip()
    board.MOVING_ANIMATION=False
            
def rotate_animation(image,entity, location,speed=30):
    board=get_player(entity).board
    board.MOVING_ANIMATION=True
    for i in range(50):
        effect=pygame.transform.rotate(image,speed*i)
        show_board(board, flip=False)
        screen.blit(effect,location)
        pygame.display.flip()
    board.MOVING_ANIMATION=False
    
def charge_card_animation(spell_card,target):    
    effect = pygame.transform.scale(pygame.image.load('images/red_eye.png').convert_alpha(),(100,70))
    fade_in_out_animation(effect, spell_card, get_center(target,effect), duration=50,stay=0.2,max_opacity=150)

def white_out_animation(entity):
    board=get_player(entity).board
    effect = pygame.transform.scale(pygame.image.load('images/whiteout.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(effect,(0,0))
    pygame.display.flip()
    time.sleep(0.07)
    show_board(board)

def black_out_animation(entity):
    board=get_player(entity).board
    effect = pygame.transform.scale(pygame.image.load('images/blackout.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(effect,(0,0))
    pygame.display.flip()
    time.sleep(0.07) 
    
def execute_animation(spell_card,target):    
    effect = pygame.transform.scale(pygame.image.load('images/headaxe.png').convert_alpha(),(160,170))
    fade_in_out_animation(effect, spell_card, get_center(spell_card.owner,effect), duration=50,stay=0.5)
    effect = pygame.transform.scale(pygame.image.load('images/slash.png').convert_alpha(),(80,80))
    projectile = BoardObject(effect,rect=spell_card.owner.location,owner=spell_card.owner)
    move_animation(projectile,dest=target.rect,speed=120,zoom=False)
    shake_animation(target, cause=spell_card, direction="horizontal", intensity=0.15, duration=10)
    white_out_animation(target)

def crush_animation(spell_card,target):    
    shake_board(spell_card)
    white_out_animation(spell_card)
    effect = pygame.transform.scale(pygame.image.load('images/crush.png').convert_alpha(),(219,201))
    fade_in_out_animation(effect, spell_card, get_center(target,effect), duration=10,stay=1)
    
def shield_block_animation(spell_card):    
    effect = pygame.transform.scale(pygame.image.load('images/red_circle.png').convert_alpha(),(160,170))
    center = get_center(spell_card.owner,effect)
    zoom_down_animation(effect, spell_card, center, speed=20, max_size=300)
    shake_animation(spell_card.owner, cause=spell_card, direction="horizontal", intensity=0.05, duration=10)
    white_out_animation(spell_card)    
     
def warpath_animation(spell_card):
    effect = pygame.transform.scale(pygame.image.load('images/warpath.png').convert_alpha(),(900,900))
    center=get_center(spell_card.owner,effect)
    rotate_animation(effect,spell_card,location=(center[0],center[1]-spell_card.owner.side*300),speed=100,)

def whirlwind_animation(spell_card):
    effect = pygame.transform.scale(pygame.image.load('images/red_circle.png').convert_alpha(),(900,900))
    center=get_center(spell_card.owner,effect)
    rotate_animation(effect,spell_card,location=(center[0],center[1]-spell_card.owner.side*300),speed=100,)

def blade_flurry_animation(spell_card):
    effect = pygame.transform.scale(pygame.image.load('images/steel_circle.png').convert_alpha(),(1400,1400))
    center=get_center(spell_card.owner,effect)
    rotate_animation(effect,spell_card,location=(center[0]-100,center[1]-spell_card.owner.side*300),speed=100,)

def inner_demon_animation(spell_card):
    effect1 = pygame.transform.scale(pygame.image.load('images/demon_eye.png').convert_alpha(),(300,200))
    effect2 = pygame.transform.scale(pygame.image.load('images/inner_demon.png').convert_alpha(),(200,200))
    center=get_center(spell_card.owner,effect1)   
    fade_in_out_animation(effect1, spell_card, center, duration=80)
    zoom_in_animation(effect2, spell_card, spell_card.owner.rect.center, max_size=3, min_size=1, speed=60)

def muklas_champion_animation(minion,targets):
    effect = pygame.transform.scale(pygame.image.load('images/banana.png').convert_alpha(),(80,80))
    dests=[]
    projectiles=[]
    for target in targets:
        projectiles.append(BoardObject(effect,rect=minion.rect,owner=minion.owner))
        dests.append(get_center(target,effect)) 
    move_multiple_animation(projectiles,dests,speed=20, zoom=False)
        
def missile_launcher_animation(minion):
    missile_image = pygame.transform.scale(pygame.image.load('images/missile.png').convert_alpha(),(40,40))
    dests=[]
    missiles=[]
    for k in range(minion.current_atk):
        missiles.append(BoardObject(missile_image,rect=minion.rect,owner=minion.owner))
        dests.append((random.randint(100,SCREEN_WIDTH-100),random.randint(100,SCREEN_HEIGHT-100))) 
    move_multiple_animation(missiles,dests,speed=20, zoom=False)
    
def reborn_animation(minion):
    board=minion.owner.board
    effect=minion.reborn_image
    fade_in_out_animation(effect, minion, get_center(minion,effect), duration=30, stay=0.5)

def lightning_jolt_animation(hero,target):
    effect1=pygame.transform.scale(pygame.image.load('images/arcane_explosion.png').convert_alpha(),(120,120))
    fade_in_animation(effect1, target, get_center(hero.hero_power,effect1), duration=50, max_opacity=150)
    zoom_down_animation(effect1, target, get_center(hero.hero_power,effect1), speed=5, max_size=320)
    
    fireball_image = pygame.transform.scale(pygame.image.load('images/arcane_explosion.png').convert_alpha(), (95,95))
    fireball = BoardObject(fireball_image,rect=hero.hero_power.rect,owner=hero)
    move_animation(fireball,dest=target.rect,speed=30,zoom=False)
              
def fire_blast_animation(hero,target):
    fireball_image = pygame.transform.scale(pygame.image.load('images/fireball.png').convert_alpha(), (60,60))
    fireball = BoardObject(fireball_image,rect=hero.hero_power.rect,owner=hero)
    move_animation(fireball,dest=target.rect,speed=30,zoom=False)
    
    #show burning effect
    burn=pygame.image.load('images/exp.png').convert_alpha()
    burn=pygame.transform.scale(burn, (140,140))
    screen.blit(burn,fireball.location)

def nightblade_animation(card,target):
    effect = pygame.transform.scale(pygame.image.load('images/nightblade.png').convert_alpha(), (60,60))
    angle_offset=math.atan2((target.rect.x-card.rect.x),(target.rect.y-card.rect.y),)*180/math.pi
    effect=pygame.transform.rotate(effect, 225+angle_offset)
    blade = BoardObject(effect,rect=card.rect,owner=card.owner)
    move_animation(blade,dest=target.rect,speed=70,zoom=False)
    
def steady_shot_animation(hero,target):
    bolt_image = pygame.transform.scale(pygame.image.load('images/bolt.png').convert_alpha(), (60,60))
    angle_offset=math.atan2((target.rect.x-hero.rect.x),(target.rect.y-hero.rect.y),)*180/math.pi
    bolt_image=pygame.transform.rotate(bolt_image, 120+angle_offset)
    bolt = BoardObject(bolt_image,rect=hero.hero_power.rect,owner=hero)
    move_animation(bolt,dest=target.rect,speed=50,zoom=False)
    
    #Shake the target horizontally
    shake_animation(target,cause=hero,direction="horizontal",intensity=0.15)
    target.rect.x,target.rect.y=target.location
    show_board(hero.board)
    
    #show hit effect
    burn=pygame.image.load('images/exp.png').convert_alpha()
    burn=pygame.transform.scale(burn, (140,140))
    screen.blit(burn,bolt.location)

def zodiac_animation(player,zodiac=""):
    #Show a pentagon on player
    effect = pygame.image.load('images/hero_images/'+zodiac+'_zodiac.png').convert_alpha()
    effect = pygame.transform.scale(effect, (2*player.image.get_width(),int(2*player.image.get_width()*effect.get_height()/effect.get_width())))
    
    fade_in_out_animation(effect, player, get_center(player,effect), duration=20, stay=0.5,max_opacity=180)

def ice_block_animation(spell_card):
    #Show ice
    fade_in_out_animation(hero_freeze_image, spell_card, get_center(spell_card.owner,hero_freeze_image), 20, 0.8)

def mage_minion_animation(minion):
    effect=pygame.transform.scale(silence_image,(240,240))
    fade_in_out_animation(effect, minion, target_location=get_center(minion,effect), stay=0.4)
 
def arcane_blast_animation(minion):
    effect=pygame.transform.scale(pygame.image.load('images/Neutral_zodiac.png').convert_alpha(),(300,300))
    zoom_down_animation(effect, minion, get_center(minion,effect), speed=25, max_size=600)
        
def arcane_shot_animation(spell_card,target):
    #Show a pentagon on player
    effect = pygame.transform.scale(pygame.image.load('images/magic pentagram.png').convert_alpha(), (260,180))
    fade_in_out_animation(effect, spell_card, get_center(spell_card.owner,effect), 20, 0.5)
    
    #shoot a magic arrow on target
    bolt_image = pygame.transform.scale(pygame.image.load('images/arcane shot.png').convert_alpha(), (60,60))
    x,y=get_center(target,bolt_image)
    bolt = BoardObject(bolt_image,rect=(x,y-150),owner=spell_card.owner)
    move_animation(bolt,dest=get_center(target,bolt_image),speed=50,zoom=False)
    time.sleep(0.5)
    
    #Shake the target horizontally
    shake_animation(target,cause=spell_card,direction="horizontal",intensity=0.10)
    target.rect.x,target.rect.y=target.location
    show_board(spell_card.owner.board)
    
    #show hit effect
    burn=pygame.image.load('images/exp.png').convert_alpha()
    burn=pygame.transform.scale(burn, (140,140))
    screen.blit(burn,bolt.location)

def on_the_hunt_animation(spell_card,target):
    #shoot a magic arrow on target
    bolt_image = pygame.transform.scale(pygame.image.load('images/arcane shot.png').convert_alpha(), (60,60))
    x,y=get_center(target,bolt_image)
    bolt = BoardObject(bolt_image,rect=(x,y-150),owner=spell_card.owner)
    move_animation(bolt,dest=get_center(target,bolt_image),speed=50,zoom=False)
    time.sleep(0.5)
    
    #show hit effect
    burn=pygame.image.load('images/exp.png').convert_alpha()
    burn=pygame.transform.scale(burn, (140,140))
    screen.blit(burn,bolt.location)
    
def fist_of_jaraxxus_animation(spell_card,target):
    #shoot a magic arrow on target
    effect = pygame.transform.scale(pygame.image.load('images/fist.png').convert_alpha(), (224,320))
    effect=  pygame.transform.rotate(effect,180)
    
    x,y=get_center(target,effect)
    projectile = BoardObject(effect,rect=(x,y-500),owner=spell_card.owner)
    move_animation(projectile,dest=get_center(target,effect),speed=50,zoom=False)
    time.sleep(0.1)
    
def hunters_mark_animation(spell_card,target):
    board=spell_card.owner.board
    
    effect = pygame.transform.scale(pygame.image.load('images/snipe.png').convert_alpha(), (90,90))

    screen.blit(effect,get_center(target,effect))
    pygame.display.flip()
    time.sleep(0.5)
    show_board(board)
    time.sleep(0.1)
    screen.blit(effect,get_center(target,effect))
    pygame.display.flip()
    time.sleep(0.2)
    show_board(board)
    time.sleep(0.1)
    screen.blit(effect,get_center(target,effect))
    pygame.display.flip()
    time.sleep(0.2)
    show_board(board)
    time.sleep(0.1)
        
def leader_of_the_pack_animation(spell_card):
    show_board(spell_card.owner.board) 
    effect=pygame.transform.scale(pygame.image.load('images/fang.png').convert_alpha(),(1000,220))
    target_location = (360,SCREEN_HEIGHT/2-110+spell_card.owner.side*150)
    fade_in_out_animation(effect,spell_card,target_location)

def echo_of_medivh_animation(spell_card,targets):
    effect=pygame.transform.scale(pygame.image.load('images/purple_mirror.png').convert_alpha(),(1440,320))
    n=len(targets)
    if n%2==0:
        target_location=(get_center(spell_card.owner.board,effect)[0],get_center(targets[0],effect)[1])
    else:
        target_location = get_center(targets[int((n-1)/2)],effect)
    fade_in_out_animation(effect,spell_card,target_location)

def loatheb_animation(minion):
    effect=pygame.transform.scale(pygame.image.load('images/mind_spike.png').convert_alpha(),(700,700))
    target_location=get_center(minion.owner.board,effect)
    fade_in_out_animation(effect,minion,target_location,max_opacity=100)
    
def scarlet_purifier_animation(minion,targets):
    paladin_buff_animation(minion, minion)
    effect=pygame.transform.scale(pygame.image.load('images/magic_bolt.png').convert_alpha(),(140,140))
    dests=[]
    projectiles=[]
    for k in range(len(targets)):
        projectiles.append(BoardObject(effect,rect=minion.rect,owner=minion.owner))
        dests.append(get_center(targets[k],effect))
    move_multiple_animation(projectiles, dests, speed=50)    

def quartermaster_animation(minion,targets):
    effect=pygame.transform.scale(pygame.image.load('images/glowing_sword.png').convert_alpha(),(140,140))
    dests=[]
    projectiles=[]
    for k in range(len(targets)):
        projectiles.append(BoardObject(effect,rect=minion.rect,owner=minion.owner))
        dests.append(get_center(targets[k],effect))
    move_multiple_animation(projectiles, dests, speed=30)    
    

def explosive_trap_animation(spell_card):
    effect=pygame.transform.scale(pygame.image.load('images/explosive_trap.png').convert_alpha(),(1440,240))
    target_location = (180,SCREEN_HEIGHT/2-spell_card.owner.side*200)
    fade_in_out_animation(effect,spell_card,target_location)

def poison_seeds_animation(spell_card):
    effect=pygame.transform.scale(pygame.image.load('images/poison_seeds.png').convert_alpha(),(1295,975))
    target_location = (180,SCREEN_HEIGHT/2-spell_card.owner.side*200)
    fade_in_out_animation(effect,spell_card,get_center(spell_card.owner.board,effect),max_opacity=200)


def cone_of_cold_animation(spell_card,target):
    effect=pygame.transform.scale(pygame.image.load('images/snowflake.png').convert_alpha(),(90,90))
    cone_animation(effect, spell_card, get_center(spell_card.owner,effect), get_center(target,effect), width=300, K=20,speed=80)

def flamecannon_animation(spell_card,target):
    effect=pygame.transform.scale(pygame.image.load('images/fire_breath.png').convert_alpha(),(90,90))
    cone_animation(effect, spell_card, get_center(spell_card.owner,effect), get_center(target,effect), width=150, K=15,speed=80)

def flamestrike_animation(spell_card):
    board=spell_card.owner.board
    effect1=pygame.transform.scale(pygame.image.load('images/explosive_trap.png').convert_alpha(),(1440,240))
    effect2=pygame.transform.scale(pygame.image.load('images/flamestrike.png').convert_alpha(),(1440,240))
    effect3=pygame.transform.scale(pygame.image.load('images/flamestrike2.png').convert_alpha(),(1440,240))
    effect4=pygame.transform.scale(pygame.image.load('images/flamestrike3.png').convert_alpha(),(1440,240))
    
    target_location = (180,SCREEN_HEIGHT/2-120-spell_card.owner.side*100)
    effects=[effect1,effect2,effect3,effect4]
    
    for k in range(40):
        show_board(board,flip=False) 
        blit_alpha(screen,effects[k%4],target_location,(k+1)*10)
        pygame.display.flip()
    for k in range(40):
        show_board(board,flip=False) 
        blit_alpha(screen,effects[k%4],target_location,(50-k)*10)
        pygame.display.flip()

def vanish_animation(spell_card,targets):
    images=[]
    target_centers=[]
    for target in targets:
        images.append(target.image)
        target_centers.append(target.location)
    
    zoom_up_multiple_animation(images, spell_card, target_centers, speed=1, max_size=1.6,min_size=1)
    
    dests=[]
    for target in targets:
        dests.append((target.rect.x,target.owner.rect.y))
    move_multiple_animation(targets, dests, speed=50)
    
    show_board(spell_card.owner.board)
    time.sleep(0.3)

def psychic_scream_animation(spell_card,targets):
    images=[]
    target_centers=[]
    for target in targets:
        images.append(target.image)
        target_centers.append(target.location)
    
    zoom_up_multiple_animation(images, spell_card, target_centers, speed=1, max_size=1.6,min_size=1)
    
    dests=[]
    for target in targets:
        dests.append((spell_card.owner.opponent.deck.location[0],spell_card.owner.opponent.deck.location[1]))
    move_multiple_animation(targets, dests, speed=50)
    
    show_board(spell_card.owner.board)
    time.sleep(0.3)
    
           
def consecration_animation(spell_card,targets):
    spell_card.owner.board.background = pygame.transform.scale(pygame.image.load('images/background_dark.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
    
    images=[]
    target_centers=[]
    for target in targets:
        images.append(target.image)
        target_centers.append(target.location)
    
    zoom_up_multiple_animation(images, spell_card, target_centers, speed=1, max_size=1.6,min_size=1)

    show_board(spell_card.owner.board)
    time.sleep(0.3)
    spell_card.owner.board.background = pygame.transform.scale(pygame.image.load('images/background.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

def enter_the_coliseum_animation(spell_card,winners,losers):
    if len(winners)>0:
        spell_card.owner.board.background = pygame.transform.scale(pygame.image.load('images/background_dark.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
        
        images=[]
        target_centers=[]
        for target in winners:
            spell_card.owner.board.upper_objects.append(target)
            images.append(target.image)
            target_centers.append((SCREEN_WIDTH/2-target.image.get_width()/2,target.rect.y))
        
        #zoom_up_multiple_animation(images, spell_card, target_centers, speed=1, max_size=1.6,min_size=1)
        move_multiple_animation(winners, target_centers, speed=30,zoom=True)
        
        show_board(spell_card.owner.board)
        time.sleep(0.5)
        for target in winners:
            target.image=target.board_image
            spell_card.owner.board.upper_objects.remove(target)
        shake_board(spell_card)
        destroy_multiple_animation(losers)
    
    
        spell_card.owner.board.background = pygame.transform.scale(pygame.image.load('images/background.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))


def hammer_of_wrath_animation(spell_card,target):
    effect = pygame.transform.scale(pygame.image.load('images/hammer.png').convert_alpha(), (80,160))
    angle_offset=math.atan2((target.rect.x-spell_card.owner.rect.x),(target.rect.y-spell_card.owner.rect.y),)*180/math.pi
    effect=pygame.transform.rotate(effect, 180+angle_offset)
    
    hammer = BoardObject(effect,rect=spell_card.owner.location,owner=spell_card.owner)
    spell_card.owner.board.background = pygame.transform.scale(pygame.image.load('images/background_dark.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
    show_board(spell_card.owner.board)
    time.sleep(0.5)
    move_animation(hammer, dest=get_center(target,effect), speed=25, zoom=False)
    show_board(spell_card.owner.board)
    time.sleep(0.3)
    spell_card.owner.board.background = pygame.transform.scale(pygame.image.load('images/background.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

def holy_smite_animation(spell_card,target):
    effect1 = pygame.transform.scale(pygame.image.load('images/smite.png').convert_alpha(), (120,120))
    effect2 = pygame.transform.scale(pygame.image.load('images/arcane_explosion.png').convert_alpha(), (240,240))

    smite = BoardObject(effect1,rect=spell_card.owner.location,owner=spell_card.owner)
    fade_in_out_animation(effect2, spell_card, get_center(spell_card.owner,effect2), duration=15, stay=0.9,max_opacity=150)
    move_animation(smite, dest=get_center(target,effect1), speed=25, zoom=False)

def shadowboxer_animation(minion,target):
    effect1 = pygame.transform.scale(pygame.image.load('images/smite.png').convert_alpha(), (60,60))
    effect2 = pygame.transform.scale(pygame.image.load('images/arcane_explosion.png').convert_alpha(), (240,240))

    smite = BoardObject(effect1,rect=minion.owner.location,owner=minion.owner)
    fade_in_out_animation(effect2, minion, get_center(minion,effect2), duration=15, stay=0.9,max_opacity=150)
    move_animation(smite, dest=get_center(target,effect1), speed=25, zoom=False)
    
def snipe_animation(spell_card,target):
    effect = pygame.transform.scale(pygame.image.load('images/bolt.png').convert_alpha(), (120,120))
    angle_offset=math.atan2((target.rect.x-spell_card.owner.rect.x),(target.rect.y-spell_card.owner.rect.y),)*180/math.pi
    effect=pygame.transform.rotate(effect,angle_offset+140)
    projectile = BoardObject(effect,rect=spell_card.owner.location,owner=spell_card.owner)
    move_animation(projectile, dest=get_center(target,effect), speed=55, zoom=False)
    shake_animation(target, spell_card, direction="horizontal", intensity=0.1)

def deathstalker_rexxar_animation(card,targets):
    effect = pygame.transform.scale(pygame.image.load('images/bolt.png').convert_alpha(), (120,120))
    images=[]
    dests=[]
    for target in targets:
        angle_offset=math.atan2((target.rect.x-card.owner.rect.x),(target.rect.y-card.owner.rect.y),)*180/math.pi
        image=pygame.transform.rotate(effect,angle_offset+140)
        projectile = BoardObject(image,rect=card.owner.location,owner=card.owner)
        images.append(projectile)
        dests.append(get_center(target,image))
    move_multiple_animation(images,dests, speed=55, zoom=False)
    
def vaporize_animation(spell_card,target):
    effect = pygame.transform.scale(pygame.image.load('images/fireball2.png').convert_alpha(), (120,80))
    angle_offset=math.atan2((target.rect.x-spell_card.owner.rect.x),(target.rect.y-spell_card.owner.rect.y),)*180/math.pi
    effect=pygame.transform.rotate(effect,angle_offset+140)
    projectile = BoardObject(effect,rect=spell_card.owner.location,owner=spell_card.owner)
    move_animation(projectile, dest=get_center(target,effect), speed=25, zoom=False)
    
    
    effect = pygame.transform.scale(pygame.image.load('images/vaporize.png').convert_alpha(), (246,162))
    fade_in_out_animation(effect, spell_card, get_center(target,effect), duration=15, stay=0.7,max_opacity=120)
    

def explosive_shot_animation(spell_card,target):
    effect = pygame.transform.scale(pygame.image.load('images/fire_arrow.png').convert_alpha(), (120,120))
    angle_offset=math.atan2((target.rect.x-spell_card.owner.rect.x),(target.rect.y-spell_card.owner.rect.y),)*180/math.pi
    effect=pygame.transform.rotate(effect,angle_offset+50)
    projectile = BoardObject(effect,rect=spell_card.owner.location,owner=spell_card.owner)
    move_animation(projectile, dest=get_center(target,effect), speed=55, zoom=False)
    
    time.sleep(0.4)   
    
    effect = pygame.transform.scale(pygame.image.load('images/explode.png').convert_alpha(), (180,180))
    center=get_center(target,effect)
    target_centers=[(center[0]-120,center[1]),center,(center[0]+120,center[1])]
    zoom_up_multiple_animation([effect]*3, spell_card, target_centers, speed=3, max_size=1,min_size=0.1)
    time.sleep(0.4) 

def powershot_animation(spell_card,target):
    effect = pygame.transform.scale(pygame.image.load('images/bolt.png').convert_alpha(), (160,160))
    angle_offset=math.atan2((target.rect.x-spell_card.owner.rect.x),(target.rect.y-spell_card.owner.rect.y),)*180/math.pi
    effect=pygame.transform.rotate(effect,angle_offset+140)
    projectile = BoardObject(effect,rect=spell_card.owner.location,owner=spell_card.owner)
    move_animation(projectile, dest=get_center(target,effect), speed=55, zoom=False)
    
    time.sleep(0.4)   
    shake_board(spell_card)
    
    effect = pygame.transform.scale(pygame.image.load('images/stun.png').convert_alpha(), (180,180))
    center=get_center(target,effect)
    target_centers=[(center[0]-120,center[1]),center,(center[0]+120,center[1])]
    zoom_up_multiple_animation([effect]*3, spell_card, target_centers, speed=3, max_size=1,min_size=0.1)
    time.sleep(0.4) 
    
def shadow_word_ruin_animation(spell_card):
    effect1 = pygame.transform.scale(pygame.image.load('images/purple_whirl.png').convert_alpha(), (1220,1220))
    effect2 = pygame.transform.scale(pygame.image.load('images/purple_fog.png').convert_alpha(), (1220,1220))

    target_location = get_center(spell_card.owner.board,effect1)
    for k in range(3):
        show_board(spell_card.owner.board,exclude=[spell_card]) 
        screen.blit(effect1,target_location)
        pygame.display.flip()
        time.sleep(0.05)
        show_board(spell_card.owner.board,exclude=[spell_card]) 
        screen.blit(effect2,target_location)
        pygame.display.flip()
        time.sleep(0.05)
    fade_out_animation(effect2,spell_card,target_location)
    
def shadow_word_animation(spell_card,target):
    effect1 = pygame.transform.scale(pygame.image.load('images/shadow_word.png').convert_alpha(), (160,160))
    effect2 = pygame.transform.scale(pygame.image.load('images/purple_fog.png').convert_alpha(), (240,240))

    smite = BoardObject(effect1,rect=spell_card.owner.location,owner=spell_card.owner)
    fade_in_out_animation(effect2, spell_card, get_center(spell_card.owner,effect2), duration=15, stay=0.9,max_opacity=170)
    move_animation(smite, dest=get_center(target,effect1), speed=25, zoom=False)
    fade_out_animation(effect1, spell_card, get_center(target,effect1), duration=50, max_opacity=200)

def voodoo_doll_animation(minion,target):
    effect1 = pygame.transform.scale(pygame.image.load('images/shadow_word.png').convert_alpha(), (160,160))
    smite = BoardObject(effect1,rect=minion.location,owner=minion.owner)
    move_animation(smite, dest=get_center(target,effect1), speed=25, zoom=False)
    fade_out_animation(effect1, minion, get_center(target,effect1), duration=50, max_opacity=200)


def mind_blast_animation(spell_card):
    effect = pygame.transform.scale(pygame.image.load('images/shadow_word.png').convert_alpha(), (160,160))
    smite = BoardObject(effect,rect=spell_card.owner.location,owner=spell_card.owner)
    move_animation(smite, dest=get_center(spell_card.owner.opponent,effect), speed=55, zoom=False)

def holy_fire_animation(spell_card,target):
    effect1 = pygame.transform.scale(pygame.image.load('images/magic_bolt.png').convert_alpha(), (330,330))
    effect2 = pygame.transform.scale(pygame.image.load('images/holy_cross.png').convert_alpha(), (330,330))

    smite = BoardObject(effect1,rect=spell_card.owner.location,owner=spell_card.owner)
    fade_in_out_animation(effect2, spell_card, get_center(spell_card.owner,effect2), duration=15, stay=0.9,max_opacity=170)
    move_animation(smite, dest=get_center(target,effect1), speed=25, zoom=False)
    fade_out_animation(effect1, spell_card, get_center(target,effect1), duration=50, max_opacity=200)

def steller_drift_animation(spell_card):
    effect = pygame.transform.scale(pygame.image.load('images/blue_moon.png').convert_alpha(), (90,90))
    target_center=SCREEN_WIDTH/2,SCREEN_HEIGHT*5/8-50-spell_card.owner.side*SCREEN_HEIGHT*1/8
    rain_animation(effect,spell_card,target_center,width=1200,duration=8,speed=20)

def blizzard_animation(spell_card):
    effect = pygame.transform.scale(pygame.image.load('images/ice_bolt.png').convert_alpha(), (90,90))
    target_center=SCREEN_WIDTH/2,SCREEN_HEIGHT*5/8-50-spell_card.owner.side*SCREEN_HEIGHT*1/8
    rain_animation(effect,spell_card,target_center,width=1200,duration=8,speed=30)

    
def rain_animation(image,entity,target_center,width=500,duration=10,speed=15):
    player=get_player(entity)
    K=30
    
    for i in range(duration):
        images=[]
        dests=[]
        for k in range(K):
            scale=random.uniform(0.9,1.1)
            effect=pygame.transform.scale(image,(int(image.get_width()*scale),int(image.get_height()*scale)))
            location=random.uniform(target_center[0]-width/4,target_center[0]+width/2),target_center[1]-400
            projectile=BoardObject(effect,rect=location,owner=player)
            images.append(projectile)
            dests.append((target_center[0]-width/2+k*width/(K-1),target_center[1]))
        move_multiple_animation(images, dests=dests, speed=speed)

def bolf_ramshield_animation(minion):
    effect=pygame.transform.scale(pygame.image.load('images/shield_grey.png').convert_alpha(),(300,300))
    fade_out_animation(effect, minion, get_center(minion.owner,effect), duration=80, max_opacity=120)
  
def nexus_champion_saraad_animation(minion):
    effect=pygame.transform.scale(pygame.image.load('images/shadow_bolt.png').convert_alpha(),(200,200))
    zoom_up_animation(effect, minion, get_center(minion,effect), speed=2, max_size=250)
    fade_out_animation(effect, minion, get_center(minion,effect), duration=80, max_opacity=150)
  
def ysera_animation(minion):
    effect=pygame.transform.scale(pygame.image.load('images/monet.png').convert_alpha(),(320,180))
    zoom_up_animation(effect, minion, get_center(minion,effect), speed=2, max_size=250)
    fade_out_animation(effect, minion, get_center(minion,effect), duration=80, max_opacity=150)
    
def ysera_awakens_animation(spell_card):
    effect=pygame.transform.scale(pygame.image.load('images/ysera_awakens.png').convert_alpha(),(50,50))
    zoom_up_animation(effect, spell_card, get_center(spell_card,effect), speed=200, max_size=3600)

def excavated_evil_animation(spell_card):    
    show_board(spell_card.owner.board,exclude=[spell_card]) 
    effect1=pygame.transform.scale(pygame.image.load('images/purple_flame1.png').convert_alpha(),(1440,440))
    effect2=pygame.transform.scale(pygame.image.load('images/purple_flame2.png').convert_alpha(),(1440,440))
    target_location = (180,SCREEN_HEIGHT/2-220)
    fade_in_animation(effect1,spell_card,target_location)
    for k in range(8):
        show_board(spell_card.owner.board,exclude=[spell_card]) 
        screen.blit(effect1,target_location)
        pygame.display.flip()
        time.sleep(0.05)
        show_board(spell_card.owner.board,exclude=[spell_card]) 
        screen.blit(effect2,target_location)
        pygame.display.flip()
        time.sleep(0.05)
    fade_out_animation(effect2,spell_card,target_location)
                       
def chaos_nova_animation(spell_card):
    zodiac_animation(spell_card.owner, spell_card.card_class)
    show_board(spell_card.owner.board,exclude=[spell_card]) 
    effect1=pygame.transform.scale(pygame.image.load('images/green_fire1.png').convert_alpha(),(1440,440))
    effect2=pygame.transform.scale(pygame.image.load('images/green_fire2.png').convert_alpha(),(1440,440))
    target_location = (180,SCREEN_HEIGHT/2-220)
    fade_in_animation(effect1,spell_card,target_location)
    for k in range(15):
        show_board(spell_card.owner.board,exclude=[spell_card]) 
        screen.blit(effect1,target_location)
        pygame.display.flip()
        time.sleep(0.05)
        show_board(spell_card.owner.board,exclude=[spell_card]) 
        screen.blit(effect2,target_location)
        pygame.display.flip()
        time.sleep(0.05)
    fade_out_animation(effect2,spell_card,target_location)

def hellfire_animation(spell_card):
    effect1=pygame.transform.scale(pygame.image.load('images/explosive_trap.png').convert_alpha(),(1440,640))
    effect2=pygame.transform.scale(pygame.image.load('images/flamestrike2.png').convert_alpha(),(1440,640))
    target_location = (180,SCREEN_HEIGHT/2-350)
    fade_in_animation(effect1,spell_card,target_location)
    for k in range(15):
        show_board(spell_card.owner.board,exclude=[spell_card]) 
        screen.blit(effect1,target_location)
        pygame.display.flip()
        time.sleep(0.05)
        show_board(spell_card.owner.board,exclude=[spell_card]) 
        screen.blit(effect2,target_location)
        pygame.display.flip()
        time.sleep(0.05)
    fade_out_animation(effect2,spell_card,target_location)
        
def lightning_storm_animation(spell_card):
    time.sleep(0.3)
    show_board(spell_card.owner.board,exclude=[spell_card]) 
    effect1=pygame.transform.scale(pygame.image.load('images/lightning_storm.png').convert_alpha(),(1440,240))
    effect2=pygame.transform.scale(pygame.image.load('images/lightning_storm2.png').convert_alpha(),(1440,240))
    target_location = (180,SCREEN_HEIGHT/2-120-spell_card.owner.side*120)
    fade_in_animation(effect1,spell_card,target_location)
    for k in range(15):
        show_board(spell_card.owner.board,exclude=[spell_card]) 
        screen.blit(effect1,target_location)
        pygame.display.flip()
        time.sleep(0.05)
        show_board(spell_card.owner.board,exclude=[spell_card]) 
        screen.blit(effect2,target_location)
        pygame.display.flip()
        time.sleep(0.05)
    fade_out_animation(effect2,spell_card,target_location)

        
def elemental_destruction_animation(spell_card):
    time.sleep(0.3)
    show_board(spell_card.owner.board,exclude=[spell_card]) 
    effect1=pygame.transform.scale(pygame.image.load('images/lightning_storm.png').convert_alpha(),(1440,640))
    effect2=pygame.transform.scale(pygame.image.load('images/flamestrike2.png').convert_alpha(),(1440,640))
    effect3=pygame.transform.scale(pygame.image.load('images/green_fire1.png').convert_alpha(),(1440,640))
    effect4=pygame.transform.scale(pygame.image.load('images/water_effect.png').convert_alpha(),(1440,640))
    
    fade_in_animation(effect1,spell_card,get_center(spell_card.owner.board,effect1))
    for k in range(15):
        show_board(spell_card.owner.board,exclude=[spell_card]) 
        screen.blit(effect1,get_center(spell_card.owner.board,effect1))
        pygame.display.flip()
        time.sleep(0.05)
        show_board(spell_card.owner.board,exclude=[spell_card]) 
        screen.blit(effect2,get_center(spell_card.owner.board,effect2))
        pygame.display.flip()
        time.sleep(0.05)
        show_board(spell_card.owner.board,exclude=[spell_card]) 
        screen.blit(effect3,get_center(spell_card.owner.board,effect3))
        pygame.display.flip()
        time.sleep(0.05)
        show_board(spell_card.owner.board,exclude=[spell_card]) 
        screen.blit(effect4,get_center(spell_card.owner.board,effect4))
        pygame.display.flip()
        time.sleep(0.05)
    fade_out_animation(effect4,spell_card,get_center(spell_card.owner.board,effect4))
    
def confessor_paletress_animation(minion):
    effect1=pygame.transform.scale(pygame.image.load('images/lightning_storm.png').convert_alpha(),(300,240))
    effect2=pygame.transform.scale(pygame.image.load('images/lightning_storm2.png').convert_alpha(),(300,240))
    target_location = get_center(minion,effect1)[0]+minion.image.get_width(),get_center(minion,effect1)[1]
    fade_in_animation(effect1,minion,target_location)
    for k in range(5):
        show_board(minion.owner.board) 
        screen.blit(effect1,target_location)
        pygame.display.flip()
        time.sleep(0.05)
        show_board(minion.owner.board) 
        screen.blit(effect2,target_location)
        pygame.display.flip()
        time.sleep(0.05)
        
    effect3=pygame.transform.scale(pygame.image.load('images/white_light.png').convert_alpha(),(280,280))
    target_location = get_center(minion,effect3)[0]+minion.image.get_width(),get_center(minion,effect3)[1]
    fade_in_out_animation(effect3,minion,target_location,stay=0.2,max_opacity=300)

def mass_dispel_animation(spell_card):
    effect=pygame.transform.scale(pygame.image.load('images/silence.png').convert_alpha(),(91,91))
    hero_center=get_center(spell_card.owner,effect)
    zoom_up_animation(effect, spell_card, (hero_center[0],hero_center[1]-spell_card.owner.side*150), speed=320, max_size=3600)


def circle_of_healing_animation(spell_card):
    zodiac_animation(spell_card.owner, spell_card.card_class)
    effect=pygame.transform.scale(pygame.image.load('images/holy_nova.png').convert_alpha(),(50,50))
    hero_center=get_center(spell_card.owner,effect)
    zoom_up_animation(effect, spell_card, (hero_center[0],hero_center[1]-spell_card.owner.side*150), speed=40, max_size=3600)

def equality_animation(spell_card):
    zodiac_animation(spell_card.owner, spell_card.card_class)
    effect=pygame.transform.scale(pygame.image.load('images/holy_nova.png').convert_alpha(),(50,50))
    hero_center=get_center(spell_card.owner,effect)
    zoom_up_animation(effect, spell_card, (hero_center[0],hero_center[1]-spell_card.owner.side*150), speed=50, max_size=3600)

def lightbomb_animation(spell_card,minions):
    effect=pygame.transform.scale(pygame.image.load('images/holy_nova.png').convert_alpha(),(50,50))
    if len(minions)==0:
        hero_center=get_center(spell_card.owner,effect)
        zoom_up_animation(effect, spell_card, (hero_center[0],hero_center[1]-spell_card.owner.side*150), speed=500, max_size=3600)
    else:
        dests=[]
        for minion in minions:
            dests.append(get_center(minion,effect))
        zoom_up_multiple_animation([effect]*len(minions), spell_card,dests, speed=12, max_size=50,min_size=1)

    
def holy_nova_animation(spell_card):
    effect=pygame.transform.scale(pygame.image.load('images/holy_nova.png').convert_alpha(),(50,50))
    hero_center=get_center(spell_card.owner,effect)
    zoom_up_animation(effect, spell_card, (hero_center[0],hero_center[1]-spell_card.owner.side*150), speed=500, max_size=3600)

def shadowflame_animation(spell_card,minion):
    effect=pygame.transform.scale(pygame.image.load('images/fire_circle_green.png').convert_alpha(),(50,50))
    zoom_up_animation(effect, minion, get_center(minion,effect), speed=500, max_size=3600)


def dread_infernal_animation(minion):
    effect=pygame.transform.scale(pygame.image.load('images/fire_circle_green.png').convert_alpha(),(50,50))
    zoom_up_animation(effect, minion, get_center(minion,effect), speed=500, max_size=3600)

def abomination_animation(minion):
    effect=pygame.transform.scale(pygame.image.load('images/purple_explode.png').convert_alpha(),(50,50))
    zoom_up_animation(effect, minion, get_center(minion,effect), speed=500, max_size=3600)

def unstable_ghoul_animation(minion):
    effect=pygame.transform.scale(pygame.image.load('images/fire_circle.png').convert_alpha(),(50,50))
    zoom_up_animation(effect, minion, get_center(minion,effect), speed=500, max_size=3600)

def anomalus_animation(minion):
    effect=pygame.transform.scale(pygame.image.load('images/chillmaw_circle.png').convert_alpha(),(84,87))
    zoom_down_multiple_animation([effect], minion, [get_center(minion,effect)], speed=3, max_size=40, min_size=0.1)
    
    time.sleep(0.4)
    effect=pygame.transform.scale(pygame.image.load('images/arcane_explosion.png').convert_alpha(),(50,50))
    for i in range(3):
        zoom_up_animation(effect, minion, get_center(minion,effect), speed=500, max_size=3600)
    
def doomsayer_animation(minion):
    effect=pygame.transform.scale(pygame.image.load('images/fire_circle.png').convert_alpha(),(50,50))
    zoom_up_animation(effect, minion, get_center(minion,effect), speed=400, max_size=3600)

def baron_geddon_animation(minion):
    effect=pygame.transform.scale(pygame.image.load('images/fire_circle.png').convert_alpha(),(50,50))
    for k in range(4):
        zoom_up_animation(effect, minion, get_center(minion,effect), speed=800, max_size=3600)

def dreadscale_animation(minion):
    effect=pygame.transform.scale(pygame.image.load('images/fire_circle_green.png').convert_alpha(),(50,50))
    for k in range(2):
        zoom_up_animation(effect, minion, get_center(minion,effect), speed=200, max_size=3600)

def chillmaw_animation(minion):
    effect=pygame.transform.scale(pygame.image.load('images/chillmaw_circle.png').convert_alpha(),(50,50))
    for k in range(4):
        zoom_up_animation(effect, minion, get_center(minion,effect), speed=800, max_size=3600)

def flame_leviathan_animation(minion):
    effect=pygame.transform.scale(pygame.image.load('images/fire_circle.png').convert_alpha(),(50,50))
    for k in range(2):
        zoom_up_animation(effect, minion, get_center(minion,effect), speed=800, max_size=3600)

def wild_pyromancer_animation(minion):
    board=minion.owner.board
    effect1=pygame.transform.scale(pygame.image.load('images/explosive_trap.png').convert_alpha(),(1440,440))
    effect2=pygame.transform.scale(pygame.image.load('images/flamestrike3.png').convert_alpha(),(1440,440))
    effect3=pygame.transform.scale(pygame.image.load('images/flamestrike2.png').convert_alpha(),(1440,440))
    effect4=pygame.transform.scale(pygame.image.load('images/flamestrike.png').convert_alpha(),(1440,440))
    
    target_location = (180,SCREEN_HEIGHT/2-220)
    effects=[effect1,effect2,effect3,effect4]
    
    time.sleep(0.5)
    
    for k in range(20):
        show_board(board,flip=False) 
        blit_alpha(screen,effects[k%4],target_location,(k+1)*10)
        pygame.display.flip()
    for k in range(20):
        show_board(board,flip=False) 
        blit_alpha(screen,effects[k%4],target_location,(50-k)*10)
        pygame.display.flip()
 
def arcane_explosion_animation(spell_card):
    effect=pygame.transform.scale(pygame.image.load('images/arcane_explosion.png').convert_alpha(),(50,50))
    hero_center=get_center(spell_card.owner,effect)
    zoom_up_animation(effect, spell_card, (hero_center[0],hero_center[1]-spell_card.owner.side*150), speed=500, max_size=3600)

def frost_nova_animation(spell_card):
    #effect=pygame.transform.scale(pygame.image.load('images/snowflake.png').convert_alpha(),(650,650))
    #fade_in_out_animation(effect, spell_card, (500,100), duration=60, stay=0.5)
    effect=pygame.transform.scale(pygame.image.load('images/ice_circle.png').convert_alpha(),(50,50))
    hero_center=get_center(spell_card.owner,effect)
    zoom_up_animation(effect, spell_card, (hero_center[0],hero_center[1]-spell_card.owner.side*150), speed=500, max_size=3600)

def lightning_spell_animation(spell_card,target):
    effect1=pygame.transform.scale(pygame.image.load('images/arcane_explosion.png').convert_alpha(),(120,120))
    fade_in_animation(effect1, spell_card, get_center(spell_card.owner,effect1), duration=50, max_opacity=150)
    zoom_down_animation(effect1, spell_card, get_center(spell_card.owner,effect1), speed=5, max_size=320)
    
    effect2=pygame.transform.scale(pygame.image.load('images/lightning.png').convert_alpha(),(136,114))
    projectile=BoardObject(effect2,rect=spell_card.owner.location,owner=spell_card.owner)
    
    move_animation(projectile, dest=get_center(target,effect2), speed=45)  

def fire_spell_animation(spell_card,target):
    effect1=pygame.transform.scale(pygame.image.load('images/fire_circle.png').convert_alpha(),(102,102))
    fade_in_animation(effect1, spell_card, get_center(spell_card.owner,effect1), duration=50, max_opacity=150)
    zoom_down_animation(effect1, spell_card, get_center(spell_card.owner,effect1), speed=5, max_size=320)
    
    effect2=pygame.transform.scale(pygame.image.load('images/fireball2.png').convert_alpha(),(270,172))
    projectile=BoardObject(effect2,rect=spell_card.owner.location,owner=spell_card.owner)
    
    move_animation(projectile, dest=get_center(target,effect2), speed=45)  

def glacial_shard_animation(minion,target):
    effect=pygame.transform.scale(pygame.image.load('images/frostbolt.png').convert_alpha(),(80,80))
    frostbolt=BoardObject(effect,rect=minion.owner.location,owner=minion.owner)
    
    move_animation(frostbolt, dest=get_center(target,effect), speed=25)  


def frostbolt_animation(spell_card,target):
    effect1=pygame.transform.scale(pygame.image.load('images/snowflake.png').convert_alpha(),(200,200))
    effect2=pygame.transform.scale(pygame.image.load('images/frostbolt.png').convert_alpha(),(80,80))
    frostbolt=BoardObject(effect2,rect=spell_card.owner.location,owner=spell_card.owner)
    
    fade_in_out_animation(effect1, spell_card, get_center(spell_card.owner,effect1), duration=50, stay=0.4)
    move_animation(frostbolt, dest=get_center(target,effect2), speed=25)  

def demented_frostcaller_animation(minion,target):
    effect=pygame.transform.scale(pygame.image.load('images/frostbolt.png').convert_alpha(),(80,80))
    frostbolt=BoardObject(effect,rect=minion.location,owner=minion.owner)
    move_animation(frostbolt, dest=get_center(target,effect), speed=25)  

def ragnaros_lightlord_animation(minion,target):
    effect=pygame.transform.scale(pygame.image.load('images/ball_of_light.png').convert_alpha(),(200,200))
    frostbolt=BoardObject(effect,rect=minion.location,owner=minion.owner)
    move_animation(frostbolt, dest=get_center(target,effect), speed=25)  
    
def mini_fireball_animation(spell_card,target):
    effect=pygame.transform.scale(pygame.image.load('images/fireball.png').convert_alpha(),(60,60))
    fireball=BoardObject(effect,rect=spell_card.owner.location,owner=spell_card.owner)
    
    move_animation(fireball, dest=get_center(target,effect), speed=45) 

def fireball_animation(spell_card,target):
    effect=pygame.transform.scale(pygame.image.load('images/fireball.png').convert_alpha(),(120,120))
    fireball=BoardObject(effect,rect=spell_card.owner.location,owner=spell_card.owner)
    
    fade_in_out_animation(effect, spell_card, get_center(spell_card.owner,effect), duration=50, stay=0.2)
    move_animation(fireball, dest=get_center(target,effect), speed=35) 

def pyroblast_animation(spell_card,target):
    effect=pygame.transform.scale(pygame.image.load('images/fireball2.png').convert_alpha(),(273,178))
    fireball=BoardObject(effect,rect=spell_card.owner.location,owner=spell_card.owner)
    
    for i in range(2):
        fade_in_out_animation(effect, spell_card, get_center(spell_card.owner,effect), duration=120, stay=0.01,max_opacity=140)
    move_animation(fireball, dest=get_center(target,effect), speed=20) 
 
def ragnaros_the_firelord_animation(minion,target):
    effect=pygame.transform.scale(pygame.image.load('images/fireball2.png').convert_alpha(),(273,178))
    fireball=BoardObject(effect,rect=get_center(minion,effect),owner=minion.owner)
    fade_in_animation(effect, minion, get_center(minion,effect), duration=200,max_opacity=180)
    move_animation(fireball, dest=get_center(target,effect), speed=20) 
  
              
def misdirection_animation(spell_card,target):
    show_board(spell_card.owner.board) 
    effect=pygame.transform.scale(pygame.image.load('images/snipe.png').convert_alpha(),(120,120))
    effect=BoardObject(effect,rect=spell_card.location,owner=spell_card.owner)
    target_location = get_center(target,effect.image)
    fade_in_animation(effect.image,spell_card,spell_card.location)
    move_animation(effect, spell_card.owner.location, 20)
    move_animation(effect, (1360,360), 20)
    move_animation(effect, (100,540), 20)
    move_animation(effect, spell_card.owner.opponent.location, 20)
    move_animation(effect, target_location, 20)
    time.sleep(1)

def mind_vision_animation(spell_card):
    effect = pygame.transform.scale(pygame.image.load('images/whirl.png').convert_alpha(), (180,180))
    fade_in_out_animation(effect, spell_card, get_center(spell_card.owner,effect), stay=0.5,max_opacity=100)
 
def wild_growth_animation(spell_card):
    effect = pygame.transform.scale(pygame.image.load('images/wild_growth.png').convert_alpha(), (260,180))
    zoom_up_animation(effect, spell_card, get_center(spell_card.owner,effect), speed=5, max_size=spell_card.owner.image.get_width()*2)

def claw_animation(spell_card):
    effect = pygame.transform.scale(pygame.image.load('images/claw.png').convert_alpha(), (230,180))
    fade_in_out_animation(effect, spell_card, get_center(spell_card.owner,effect), stay=0.2)

def bite_animation(spell_card):
    effect = pygame.transform.scale(pygame.image.load('images/bite.png').convert_alpha(), (230,180))
    fade_in_out_animation(effect, spell_card, get_center(spell_card.owner,effect), stay=0.2)

def swipe_animation(spell_card):
    zodiac_animation(spell_card.owner,spell_card.card_class)
    time.sleep(0.3)
    
    effect = pygame.transform.scale(pygame.image.load('images/swipe.png').convert_alpha(), (530,530))
    slide_animation(effect, spell_card, location=(580,330), direction="left", speed=40)
    
    effect = pygame.transform.scale(pygame.image.load('images/overkill.png').convert_alpha(), (1030,230))
    slide_animation(effect, spell_card, location=(460,400), direction="right", speed=25)
    
    time.sleep(0.5)

def swipe_multiple_animation(minion,targets):
    images=[]
    locations=[]
    effect = pygame.transform.scale(pygame.image.load('images/swipe.png').convert_alpha(), (159,159))
    for target in targets:  
        images.append(effect)
        locations.append(get_center(target,effect))
    slide_multiple_animation(images, minion, locations, direction="left", speed=40)
    time.sleep(0.5)
    
def king_mosh_animation(minion,targets):
    swipe_multiple_animation(minion,targets)
    destroy_multiple_animation(targets)

def skulking_geist_animation(minion,targets):
    images=[]
    locations=[]
    effect = pygame.transform.scale(pygame.image.load('images/swipe.png').convert_alpha(), (159,159))
    for target in targets:  
        images.append(effect)
        locations.append(get_center(target,effect))
    slide_multiple_animation(images, minion, locations, direction="left", speed=40)
    time.sleep(0.5)
            
def attack_adjacent_animation(minion,target):
    effect = pygame.transform.scale(pygame.image.load('images/swipe.png').convert_alpha(), (450,200))
    slide_animation(effect, minion, location=get_center(target,effect), direction="left", speed=40)

    time.sleep(0.5)
        
def elite_tauren_chieftain_animation(minion):
    minion.owner.board.background = pygame.transform.scale(pygame.image.load('images/rock_concert.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
    for i in range(3):
        white_out_animation(minion)
        time.sleep(0.5)
    minion.owner.board.background = pygame.transform.scale(pygame.image.load('images/background.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
    
    
def moonfire_animation(spell_card,target):
    effect = pygame.transform.scale(pygame.image.load('images/blue_moon.png').convert_alpha(), (60,60))
    moon = BoardObject(effect,rect=(target.rect.x+500,target.rect.y-500),owner=spell_card.owner)
    spell_card.owner.board.background = pygame.transform.scale(pygame.image.load('images/background_dark.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
    move_animation(moon, dest=get_center(target,effect), speed=15, zoom=False)
    show_board(spell_card.owner.board)
    time.sleep(0.3)
    spell_card.owner.board.background = pygame.transform.scale(pygame.image.load('images/background.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

def meteor_animation(spell_card,target):
    effect = pygame.transform.scale(pygame.image.load('images/explode.png').convert_alpha(), (300,300))
    moon = BoardObject(effect,rect=(target.rect.x+500,target.rect.y-500),owner=spell_card.owner)
    spell_card.owner.board.background = pygame.transform.scale(pygame.image.load('images/background_dark.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
    move_animation(moon, dest=get_center(target,effect), speed=7, zoom=False)
    
    effect = pygame.transform.scale(pygame.image.load('images/explode.png').convert_alpha(), (180,180))
    center=get_center(target,effect)
    target_centers=[(center[0]-120,center[1]),center,(center[0]+120,center[1])]
    zoom_up_multiple_animation([effect]*3, spell_card, target_centers, speed=3, max_size=1,min_size=0.1)
    
    show_board(spell_card.owner.board)
    shake_board(spell_card, intensity=0.25, duration=20)
    spell_card.owner.board.background = pygame.transform.scale(pygame.image.load('images/background.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))


def starfire_animation(spell_card,target):
    effect = pygame.transform.scale(pygame.image.load('images/blue_moon.png').convert_alpha(), (180,180))
    moon = BoardObject(effect,rect=(target.rect.x+800,target.rect.y-800),owner=spell_card.owner)
    spell_card.owner.board.background = pygame.transform.scale(pygame.image.load('images/background_dark.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
    move_animation(moon, dest=get_center(target,effect), speed=15, zoom=False)
    show_board(spell_card.owner.board)
    time.sleep(0.3)
    spell_card.owner.board.background = pygame.transform.scale(pygame.image.load('images/background.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

def kill_command_animation(spell_card,target):
    effect = pygame.transform.scale(pygame.image.load('images/red_fang.png').convert_alpha(), (120,120))
    zodiac_animation(spell_card.owner, spell_card.card_class)
    zoom_up_animation(effect, spell_card, get_center(target,effect), speed=10, max_size=200)
     
def healing_touch_animation(spell_card,target):
    effect = pygame.transform.scale(pygame.image.load('images/wild_growth.png').convert_alpha(), (260,230))
    fade_in_out_animation(effect, spell_card, get_center(spell_card.owner,effect), stay=0.2)
    pygame.display.flip()
    time.sleep(0.4)

def enhance_o_mechano_animation(minion,targets):
    effect = pygame.transform.scale(pygame.image.load('images/gear.png').convert_alpha(), (92,98))
    target_centers=[]
    for target in targets:
        target_centers.append(get_center(target,effect))
    zoom_up_multiple_animation([effect]*len(targets), minion, target_centers, speed=5, max_size=1.7,min_size=0.1)


def battle_rage_animation(spell_card,targets):
    if len(targets)>0:
        effect = pygame.transform.scale(pygame.image.load('images/rage.png').convert_alpha(), (119,154))
        target_centers=[]
        for target in targets:
            target_centers.append(get_center(target,effect))
        fade_in_out_multiple_animation([effect]*len(targets), spell_card, target_centers, duration=50,stay=0.3,max_opacity=80)
      
def savage_roar_animation(spell_card,targets):
    effect1 = pygame.transform.scale(pygame.image.load('images/red_eye.png').convert_alpha(), (200,180))
    effect2 = pygame.transform.scale(pygame.image.load('images/red_fang.png').convert_alpha(), (260,230))
    
    fade_in_out_animation(effect1, spell_card, get_center(spell_card.owner,effect1), duration=20,stay=0.6)
    
    target_centers=[]
    for target in targets:
        target_centers.append(get_center(target,effect2))
    zoom_up_multiple_animation([effect2]*len(targets), spell_card, target_centers, speed=3, max_size=1,min_size=0.1)

def gift_of_the_wild_animation(spell_card,targets):
    effect = pygame.transform.scale(pygame.image.load('images/paw.png').convert_alpha(), (82,65))
    target_centers=[]
    for target in targets:
        target_centers.append(get_center(target,effect))
    zoom_up_multiple_animation([effect]*len(targets), spell_card, target_centers, speed=3, max_size=1.7,min_size=0.1)

def buff_multiple_animation(spell_card,targets):
    effect = pygame.transform.scale(pygame.image.load('images/red_fang.png').convert_alpha(), (80,80))
    target_centers=[]
    for target in targets:
        target_centers.append(get_center(target,effect))
    zoom_up_multiple_animation([effect]*len(targets), spell_card, target_centers, speed=3, max_size=1.7,min_size=0.1)

def debuff_multiple_animation(spell_card,targets):
    effect = pygame.transform.scale(pygame.image.load('images/warpath.png').convert_alpha(), (80,80))
    target_centers=[]
    for target in targets:
        target_centers.append(get_center(target,effect))
    zoom_down_multiple_animation([effect]*len(targets), spell_card, target_centers, speed=2, max_size=1.7,min_size=0.1)

def weapon_buff_animation(minion):
    effect = pygame.transform.scale(pygame.image.load('images/warpath.png').convert_alpha(), (80,80))
    zoom_down_animation(effect, minion, get_center(minion.owner.weapon,effect), speed=2, max_size=200)
    
def light_buff_multiple_animation(spell_card,targets):
    effect=pygame.transform.scale(pygame.image.load('images/white_light.png').convert_alpha(),(240,240))
    target_centers=[]
    for target in targets:
        target_centers.append(get_center(target,effect))
    zoom_up_multiple_animation([effect]*len(targets), spell_card, target_centers, speed=3, max_size=1.7,min_size=0.1)


def glitter_moth_animation(minion,targets):
    effect = pygame.transform.scale(pygame.image.load('images/light.png').convert_alpha(), (82,82))
    target_centers=[]
    for target in targets:
        target_centers.append(get_center(target,effect))
    zoom_up_multiple_animation([effect]*len(targets), minion, target_centers, speed=3, max_size=1.7,min_size=0.1)

def righteousness_animation(spell_card,targets):
    effect = pygame.transform.scale(pygame.image.load('images/light.png').convert_alpha(), (82,82))
    target_centers=[]
    for target in targets:
        target_centers.append(get_center(target,effect))
    zoom_up_multiple_animation([effect]*len(targets), spell_card, target_centers, speed=3, max_size=1.7,min_size=0.1)

def gnomish_experimenter_animation(card,chicken):
    original_location=card.location
    time.sleep(0.5)
    move_animation(card, dest=(780,400), speed=10, zoom=True)
    time.sleep(0.7)
    card.owner.hand.remove(card)
    card.owner.hand.append(chicken)
    chicken.image=chicken.raw_image
    chicken.initialize_location(card.location)
    transform_animation(card, chicken)
    time.sleep(1)
    chicken.image=chicken.mini_image
    move_animation(chicken, dest=original_location, speed=10)
    card.owner.hand.append(card)
    card.owner.hand.remove(chicken)
    sort_hand_animation(card.owner)
    
def charge_animation(entity,duration=20):
    effect = pygame.transform.scale(pygame.image.load('images/stun.png').convert_alpha(), (200,180))
    for i in range(duration):
        zoom_down_animation(effect, entity, get_center(entity,effect), speed=70, max_size=220)

def gain_charge_animation(minion):
    effect = pygame.transform.scale(pygame.image.load('images/stun.png').convert_alpha(), (200,180))
    for i in range(10):
        zoom_down_animation(effect, minion, get_center(minion,effect), speed=70, max_size=220)
    shake_animation(minion, minion, direction="vertical", intensity=0.10, duration=15)
       
def charge_shot_animation(entity,target):
    charger=entity
    if entity.isSpell:
        charger=entity.owner
    charge_animation(charger)
    

    effect = pygame.transform.scale(pygame.image.load('images/stun.png').convert_alpha(), (200,180))
    projectile = BoardObject(effect,rect=charger.location,owner=get_player(entity))
    move_animation(projectile, dest=get_center(target,effect), speed=80)
    shake_board(entity)
    
def savagery_animation(spell_card,target):
    charge_animation(spell_card.owner)

    effect = pygame.transform.scale(pygame.image.load('images/stun.png').convert_alpha(), (200,180))
    projectile = BoardObject(effect,rect=spell_card.owner.location,owner=spell_card.owner)
    move_animation(projectile, dest=target.location, speed=80)
    shake_board(spell_card)
    
def eye_for_an_eye_animation(spell_card):
    effect = pygame.transform.scale(pygame.image.load('images/light.png').convert_alpha(), (200,200))
    fade_in_animation(effect, spell_card, get_center(spell_card.owner,effect), duration=40, max_opacity=100)
    
    effect = pygame.transform.scale(pygame.image.load('images/magic_bolt.png').convert_alpha(), (160,160))
    projectile = BoardObject(effect,rect=spell_card.owner.location,owner=spell_card.owner)
    move_animation(projectile, dest=spell_card.owner.opponent.location, speed=120)

def mossy_horror_animation(minion,targets):
        charge_animation(minion) 
        shake_board(minion)
        destroy_multiple_animation(targets)  
        
def holy_wrath_animation(spell_card,target,cost):
    size=200+cost*10
    effect = pygame.transform.scale(pygame.image.load('images/light.png').convert_alpha(), (size,size))
    fade_in_animation(effect, spell_card, get_center(spell_card.owner,effect), duration=80, max_opacity=130)
    
    charge_animation(spell_card.owner,duration=cost*10)
    
    effect = pygame.transform.scale(pygame.image.load('images/magic_bolt.png').convert_alpha(), (size-40,size-40))
    projectile = BoardObject(effect,rect=spell_card.owner.location,owner=spell_card.owner)
    move_animation(projectile, dest=get_center(target,effect), speed=min(20,120-size//4))

    
def heroic_strike_animation(spell_card):
    effect = pygame.transform.scale(pygame.image.load('images/red_fang.png').convert_alpha(), (200,180))
    zoom_up_animation(effect, spell_card, get_center(spell_card.owner,effect), speed=10, max_size=250)

def bloodlust_animation(spell_card,targets):
    effect1 = pygame.transform.scale(pygame.image.load('images/hp_background.png').convert_alpha(), (160,192))
    effect2 = pygame.transform.scale(pygame.image.load('images/red_circle.png').convert_alpha(), (260,260))
    
    fade_in_out_animation(effect1, spell_card, get_center(spell_card.owner,effect1), duration=20,stay=0.6,max_opacity=140)
    
    target_centers=[]
    for target in targets:
        target_centers.append(get_center(target,effect2))
    zoom_up_multiple_animation([effect2]*len(targets), spell_card, target_centers, speed=3, max_size=1,min_size=0.1)

def sacrificial_pact_animation(spell_card,target):
    effect = pygame.transform.scale(pygame.image.load('images/shadow_word.png').convert_alpha(), (180,180))
    fade_in_out_animation(effect, spell_card, get_center(target,effect), stay=0.7,max_opacity=120)

    
def totemic_call_animation(player):
    #Show a totem on player
    effect = pygame.transform.scale(pygame.image.load('images/totem.png').convert_alpha(), (260,180))
    fade_in_out_animation(effect, player, get_center(player,effect), 20, 0.5)

def crushing_wall_animation(spell_card,minions):
    effect=pygame.transform.scale(pygame.image.load('images/spiked_wall.png').convert_alpha(), (162,600))
    projectile1 = BoardObject(effect,rect=(0,SCREEN_HEIGHT/2-effect.get_height()/2),owner=spell_card.owner)
    projectile2 = BoardObject(effect,rect=(SCREEN_WIDTH-effect.get_width(),SCREEN_HEIGHT/2-effect.get_height()/2),owner=spell_card.owner)
    dest1=get_center(minions[0],effect)
    dest2=get_center(minions[-1],effect)
    
    move_multiple_animation([projectile1,projectile2], [dest1,dest2], speed=60)
    shake_board(spell_card)
    time.sleep(0.2)
    destroy_multiple_animation(minions)

def shadowbomber_animation(minion):
    effect=pygame.transform.scale(pygame.image.load('images/mind_spike.png').convert_alpha(), (100,100))
    projectile = BoardObject(effect,rect=minion.location,owner=minion.owner)
    move_multiple_animation([projectile]*2, [get_center(minion.owner.opponent,effect),get_center(minion.owner,effect)], speed=60)

def unwilling_sacrifice_animation(spell_card,friendly_minion,opponent_minion):
    effect=pygame.transform.scale(pygame.image.load('images/mind_spike.png').convert_alpha(), (100,100))
    projectile = BoardObject(effect,rect=spell_card.location,owner=spell_card.owner)
    move_multiple_animation([projectile]*2, [get_center(friendly_minion,effect),get_center(opponent_minion,effect)], speed=30)

def emerald_reaver_animation(minion):
    effect=pygame.transform.scale(pygame.image.load('images/slash.png').convert_alpha(), (84,85))
    projectile = BoardObject(effect,rect=minion.location,owner=minion.owner)
    move_multiple_animation([projectile]*2, [get_center(minion.owner.opponent,effect),get_center(minion.owner,effect)], speed=60)

def void_crusher_animation(minion,targets):
    effect=pygame.transform.scale(pygame.image.load('images/mind_spike.png').convert_alpha(), (100,100))
    projectile = BoardObject(effect,rect=minion.location,owner=minion.owner)
    dests=[]
    for target in targets:
        dests.append(get_center(target,effect))
    
    fade_in_animation(effect, minion, get_center(minion,effect), max_opacity=150)
    time.sleep(0.2)
    move_multiple_animation([projectile]*len(targets), dests, speed=60)
    destroy_multiple_animation(targets)
       
def refreshment_vendor_animation(minion):
    effect=pygame.transform.scale(pygame.image.load('images/soda.png').convert_alpha(), (92,68))
    projectile = BoardObject(effect,rect=minion.location,owner=minion.owner)
    move_multiple_animation([projectile]*2, [get_center(minion.owner.opponent,effect),get_center(minion.owner,effect)], speed=25)
    
def priest_of_the_feast_animation(minion):
    effect=pygame.transform.scale(pygame.image.load('images/soda.png').convert_alpha(), (92,68))
    projectile = BoardObject(effect,rect=minion.location,owner=minion.owner)
    move_multiple_animation([projectile], [get_center(minion.owner,effect)], speed=15)
    
            
def mind_spike_animation(hero_power,target):
    #show healing effect
    aura=pygame.image.load('images/mind_spike.png').convert_alpha()
    size=int(70+hero_power.damage*50)
    aura=pygame.transform.scale(aura, (size,size))
    screen.blit(aura,(target.rect.x+target.image.get_width()/2-aura.get_width()/2,target.rect.y+target.image.get_height()/2-aura.get_height()/2))
    #show_text("+"+str(hero.hero_power.strength), 63, (target.location[0],target.location[1]+200), GREEN, BLACK,flip=True,pause=0.5)
    pygame.display.flip()
    time.sleep(0.6)
                      
def lesser_heal_animation(hero,target):
    #show healing effect
    aura=pygame.image.load('images/aura.png').convert_alpha()
    aura=pygame.transform.scale(aura, (140,140))
    screen.blit(aura,(target.rect.x+target.image.get_width()/2-aura.get_width()/2,target.rect.y+target.image.get_height()/2-aura.get_height()/2))
    #show_text("+"+str(hero.hero_power.strength), 63, (target.location[0],target.location[1]+200), GREEN, BLACK,flip=True,pause=0.5)
    pygame.display.flip()
    time.sleep(0.6)
    
def heal_aoe_animation(targets,amounts):
    if len(targets)>0:
        show_board(get_player(targets[0]).board)
        image=pygame.transform.scale(pygame.image.load('images/aura.png').convert_alpha(), (150,150))  
        for i in range(len(targets)):
            target=targets[i]
            healed_amount=amounts[i]
            #Healing amoutn logic
            if target.current_hp+amounts[i]>target.temp_hp:
                healed_amount=target.temp_hp-target.current_hp
    
            center=get_center(target,image)
            screen.blit(image,center)
            show_text("+"+str(healed_amount), size=30, location=(center[0]+45,center[1]+50), color=GREEN, outline=WHITE, flip=False)
        pygame.display.flip()
        time.sleep(0.6)
        
        show_board(get_player(targets[0]).board)
        pygame.display.flip()

def silence_animation(silencer):
    effect=pygame.transform.scale(silence_image,(240,240))
    fade_in_out_animation(effect, entity=silencer, target_location=get_center(silencer,effect), stay=0.8)
            
def heal_animation(target,amount):
    #show healing effect
    if amount>0:
        effect=pygame.image.load('images/heal.png').convert_alpha()
        effect=pygame.transform.scale(effect, (350,350))
        blit_alpha(screen, effect, get_center(target,effect), 80)
        #screen.blit(aura,get_center(target,effect))
        show_text("+"+str(amount), 63, (target.location[0]+target.image.get_width()/2-30,target.location[1]+target.image.get_height()/2-30), GREEN, BLACK,flip=True,pause=0.8)

def lifesteal_animation(player):
    aura=pygame.image.load('images/lifesteal_aura.png').convert_alpha()
    aura=pygame.transform.scale(aura, (200,200))
    fade_in_out_animation(aura, player, get_center(player,aura), duration=30, stay=0.9)

def leper_gnome_animation(minion):
    effect = pygame.transform.scale(pygame.image.load('images/purple_fog.png').convert_alpha(), (200,180))
    fade_out_animation(effect, minion, get_center(minion,effect), duration=100, max_opacity=200)

def high_inquisitor_whitemane_animation1(minion):
    effect=pygame.transform.scale(pygame.image.load('images/cross.png').convert_alpha(),(200,200))
    fade_in_out_animation(effect,minion,get_center(minion,effect),max_opacity=130)

def high_inquisitor_whitemane_animation2(minion,summoned_minions):
    effect=pygame.transform.scale(pygame.image.load('images/angel_wing.png').convert_alpha(),(172,110))
    target_centers=[]
    for target in summoned_minions:
        target_centers.append(get_center(target,effect))
    zoom_up_multiple_animation([effect]*len(summoned_minions), minion, target_centers, speed=8, max_size=2, min_size=0.5)

def kelthuzad_animation(minion,summoned_minions):
    effect=pygame.transform.scale(pygame.image.load('images/tomb.png').convert_alpha(),(100,130))
    target_centers=[]
    for target in summoned_minions:
        target_centers.append(get_center(target,effect))
    zoom_up_multiple_animation([effect]*len(summoned_minions), minion, target_centers, speed=8, max_size=2, min_size=0.5)

def nat_pagle_animation(minion):
    effect=pygame.transform.scale(pygame.image.load('images/water_effect.png').convert_alpha(),(106,111))
    fade_in_out_animation(effect,minion,(minion.owner.deck.location[0]+60,minion.owner.deck.location[1]))

def patches_the_pirate_animation(minion):
    effect=pygame.transform.scale(pygame.image.load('images/water_effect.png').convert_alpha(),(106,111))
    fade_in_out_animation(effect,minion,(minion.owner.deck.location[0]+60,minion.owner.deck.location[1]),duration=20)

def nat_the_darkfisher_animation(minion):
    effect=pygame.transform.scale(pygame.image.load('images/water_effect.png').convert_alpha(),(106,111))
    fade_in_out_animation(effect,minion,(minion.owner.opponent.deck.location[0]+60,minion.owner.opponent.deck.location[1]))


def brightwing_animation(minion):
    effect=pygame.transform.scale(pygame.image.load('images/bright_wing.png').convert_alpha(),(257,200))
    fade_in_out_animation(effect,minion,get_center(minion,effect))

def king_mukla_animation(minion):
    effect=pygame.transform.scale(pygame.image.load('images/bananas.png').convert_alpha(),(268,188))
    fade_in_out_animation(effect,minion,get_center(minion,effect),max_opacity=150)

def xavius_animation(minion):
    effect=pygame.transform.scale(pygame.image.load('images/blackhole.png').convert_alpha(),(164,230))
    zoom_down_animation(effect, minion, get_center(minion,effect), speed=20, max_size=200)
 

def cobalt_scalebane_animation(minion,target):
    effect=pygame.transform.scale(pygame.image.load('images/twinblade.png').convert_alpha(),(140,90))
    projectile=BoardObject(effect,rect=get_center(minion,effect),owner=minion.owner)
    move_animation(projectile, get_center(target,effect), speed=20)
    
def captain_greenskin_animation(minion):
    effect=pygame.transform.scale(pygame.image.load('images/twinblade.png').convert_alpha(),(281,180))
    fade_in_out_animation(effect,minion,get_center(minion,effect),max_opacity=150)
    effect=pygame.transform.scale(pygame.image.load('images/twinblade.png').convert_alpha(),(140,90))
    projectile=BoardObject(effect,rect=get_center(minion,effect),owner=minion.owner)
    move_animation(projectile, minion.owner.weapon.location, speed=20)

def the_black_knight_animation(minion,target):
    minion.owner.board.background = pygame.transform.scale(pygame.image.load('images/background_dark.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
    minion.has_stealth=True
    
    effect=pygame.transform.scale(pygame.image.load('images/red_eyes.png').convert_alpha(),(103,77))
    fade_in_out_animation(effect,minion,get_center(minion,effect),max_opacity=100)
    time.sleep(0.5)
    
    effect=pygame.transform.scale(pygame.image.load('images/red_slash.png').convert_alpha(),(240,240))
    slide_animation(effect, minion, get_center(target,effect), direction="right", speed=80)
    time.sleep(0.4)
 
    minion.owner.board.background = pygame.transform.scale(pygame.image.load('images/background.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
    minion.has_stealth=False

def brawl_animation(spell_card,minions,survivor):
    board=spell_card.owner.board
    original_location=survivor.location
    
    board.background = pygame.transform.scale(pygame.image.load('images/battle_arena.png').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

    effect=pygame.transform.scale(pygame.image.load('images/brawl.png').convert_alpha(),(1104,508))
    dust = BoardObject(effect,rect=get_center(board,effect),owner=spell_card.owner)
    board.upper_objects.append(dust)
    
    while len(board.minions[1]+board.minions[-1])>0:
        minion=random.choice(board.minions[1]+board.minions[-1])
        minion.owner.minions.remove(minion)
        x=random.randint(600,800)
        y=random.randint(300,500)
        move_animation(minion, dest=(x,y), speed=35,zoom=True)
    show_board(board)
    time.sleep(1.5)
    
    losers=[]
    for minion in minions:
        if minion is not survivor:
            x=random.choice([100,200,1100,1200])
            y=random.randint(100,700)
            move_animation(minion, dest=(x,y), speed=45) 
            minion.owner.minions.append(minion)
            minion.image=minion.board_image
            losers.append(minion)

    survivor.image=survivor.board_image
    survivor.owner.minions.append(survivor) 
     
    board.upper_objects.remove(dust)
    fade_out_animation(effect,spell_card,get_center(board,effect),duration=50,max_opacity=150)

    survivor.rect.x,survivor.rect.y=original_location
    survivor.location=original_location
    destroy_multiple_animation(losers)

    board.background = pygame.transform.scale(pygame.image.load('images/background.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

def tree_of_life_animation(spell_card,targets):
    board=spell_card.owner.board
    
    board.background = pygame.transform.scale(pygame.image.load('images/forest.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
    black_out_animation(spell_card)
    

    effect=pygame.transform.scale(pygame.image.load('images/heal.png').convert_alpha(),(850,850))
    healing_ball = BoardObject(effect,rect=get_center(board,effect),owner=spell_card.owner)
    board.upper_objects.append(healing_ball)
    
    for i in range(3):
        for target in targets:
            effect2=pygame.transform.scale(pygame.image.load('images/heal.png').convert_alpha(),(150,150))
            small_healing_ball = BoardObject(effect2,rect=get_center(board,effect2),owner=spell_card.owner)
            move_animation(small_healing_ball, get_center(target,effect2), speed=55)
            
    board.upper_objects.remove(healing_ball)
    fade_out_animation(effect,spell_card,get_center(board,effect),duration=50,max_opacity=150)

    board.background = pygame.transform.scale(pygame.image.load('images/background.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))


def twisting_nether_animation(spell_card,minions):
    board=spell_card.owner.board
    
    board.background = pygame.transform.scale(pygame.image.load('images/universe.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
    black_out_animation(spell_card)
    
    effect=pygame.transform.scale(pygame.image.load('images/blackhole.png').convert_alpha(),(550,800))
    blackhole = BoardObject(effect,rect=get_center(board,effect),owner=spell_card.owner)
    board.bottom_objects.append(blackhole)
    
    fade_in_animation(effect,spell_card,get_center(board,effect),duration=50,max_opacity=150)
    for i in range(100):
        blackhole.rect.x+=(-1)**i*5
        show_board(board)
        time.sleep(0.02)
    
    #Move minions into blackhole
    for minion in minions:
        dest=get_center(blackhole,minion.image)
        move_animation(minion,dest=(dest[0]-50+random.randint(-50,50),dest[1]-80+random.randint(-50,50)),speed=40,zoom=True)
        time.sleep(0.2)
    
    board.bottom_objects.remove(blackhole)
    fade_out_animation(effect,spell_card,get_center(board,effect),duration=50,max_opacity=150)

    board.background = pygame.transform.scale(pygame.image.load('images/background.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

def DOOM_animation(spell_card,minions):
    board=spell_card.owner.board
    black_out_animation(spell_card)
    
    effect=pygame.transform.scale(pygame.image.load('images/blackhole.png').convert_alpha(),(550,800))
    blackhole = BoardObject(effect,rect=get_center(board,effect),owner=spell_card.owner)
    board.bottom_objects.append(blackhole)
    
    fade_in_animation(effect,spell_card,get_center(board,effect),duration=50,max_opacity=150)
    for i in range(25):
        blackhole.rect.x+=(-1)**i*5
        show_board(board)
        time.sleep(0.02)
    board.bottom_objects.remove(blackhole)
    fade_out_animation(effect,spell_card,get_center(board,effect),duration=50,max_opacity=150)

def amara_warden_of_hope_animation(minion):
    board=minion.owner.board
    
    board.background = pygame.transform.scale(pygame.image.load('images/forest.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

    effect=pygame.transform.scale(pygame.image.load('images/heal.png').convert_alpha(),(850,850))
    healing_ball = BoardObject(effect,rect=get_center(board,effect),owner=minion.owner)
    board.upper_objects.append(healing_ball)
    
    for i in range(3):
        effect2=pygame.transform.scale(pygame.image.load('images/heal.png').convert_alpha(),(150,150))
        small_healing_ball = BoardObject(effect2,rect=get_center(board,effect2),owner=minion.owner)
        move_animation(small_healing_ball, get_center(minion.owner,effect2), speed=15)
            
    board.upper_objects.remove(healing_ball)
    fade_out_animation(effect,minion,get_center(board,effect),duration=50,max_opacity=150)

    board.background = pygame.transform.scale(pygame.image.load('images/background.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))


def nefarian_animation(minion):
    board=minion.owner.board
    board.exclude.append(minion)
    effect=pygame.transform.scale(pygame.image.load('images/dragon_shadow.png').convert_alpha(),(900,1035))
    center=get_center(board,effect)
    shadow = BoardObject(effect,rect=(center[0],center[1]+1500),owner=minion.owner)
    move_animation(shadow, dest=(center[0],center[1]-1500), speed=10)
    board.exclude=[]
    
def anubarak_animation(minion):
    board=minion.owner.board
    board.exclude.append(minion)
    effect=pygame.transform.scale(pygame.image.load('images/spider_shadow.png').convert_alpha(),(1020,600))
    center=get_center(board,effect)
    shadow = BoardObject(effect,rect=(center[0]-1000,center[1]-1000),owner=minion.owner)
    move_animation(shadow, dest=(center[0]+500,center[1]+500), speed=8)
    
    spider_image = pygame.transform.scale(pygame.image.load('images/spider_shadow.png').convert_alpha(),(34,20))
    dests=[]
    missiles=[]
    for k in range(100):
        missiles.append(BoardObject(spider_image,rect=(random.randint(100,SCREEN_WIDTH-100),random.randint(100,SCREEN_HEIGHT-100)),owner=minion.owner))
        dests.append((random.randint(100,SCREEN_WIDTH-100),random.randint(100,SCREEN_HEIGHT-100))) 
    white_out_animation(minion)
    move_multiple_animation(missiles,dests,speed=10, zoom=False)
    

    board.exclude=[]

def prince_keleseth_animation(minion):
    effect=pygame.transform.scale(pygame.image.load('images/chillmaw_circle.png').convert_alpha(),(200,200))
    if len(minion.owner.deck.cards)<=0:
        minion.owner.deck.cards.append(minion)
    zoom_down_multiple_animation([effect], minion, [get_center(minion.owner.deck.cards[0],effect)], speed=2, max_size=2,min_size=0.1)
    if minion in minion.owner.deck.cards:
        minion.owner.deck.cards.remove(minion)
           
def the_mistcaller_animation(minion):
    board=minion.owner.board
    effect=pygame.transform.scale(pygame.image.load('images/mist.png').convert_alpha(),(1536,2187))
    target_location=get_center(board,effect)[0],get_center(board,effect)[1]+300
    fog = BoardObject(effect,target_location,owner=minion.owner)
    fade_in_animation(effect, minion, target_location, duration=50, max_opacity=500)
    board.upper_objects.append(fog)
    
    effect=pygame.transform.scale(pygame.image.load('images/chillmaw_circle.png').convert_alpha(),(200,200))
    target_centers=[]
    n=0
    
    if len(minion.owner.deck.cards)<=0:
        minion.owner.deck.cards.append(minion)
    for target in minion.owner.hand+[minion.owner.deck.cards[0]]:
        target_centers.append(get_center(target,effect))
        n+=1
    zoom_down_multiple_animation([effect]*n, minion, target_centers, speed=2, max_size=2,min_size=0.1)
    board.upper_objects.remove(fog)
    
    if minion in minion.owner.deck.cards:
        minion.owner.deck.cards.remove(minion)

def swap_deck_animation(player):
    effect=pygame.transform.scale(pygame.image.load('images/chillmaw_circle.png').convert_alpha(),(200,200))
    target_centers=[]
    for target in [player.deck,player.opponent.deck]:
        target_centers.append(get_center(target,effect))
    zoom_down_multiple_animation([effect]*2, player, target_centers, speed=2, max_size=2,min_size=0.1)

def corrupting_mist_animation(minion):
    board=minion.owner.board
    effect=pygame.transform.scale(pygame.image.load('images/mist.png').convert_alpha(),(1536,2187))
    target_location=get_center(board,effect)[0],get_center(board,effect)[1]+300
    fog = BoardObject(effect,target_location,owner=minion.owner)
    fade_in_animation(effect, minion, target_location, duration=50, max_opacity=500)

def clutchmother_zavas_animation(minion):
    board=minion.owner.board
    board.bottom_objects.append(minion)
    
    effect=pygame.transform.scale(pygame.image.load('images/smoke.png').convert_alpha(),(200,200))
    fade_in_animation(effect, minion, get_center(minion,effect), 20)
    fade_out_animation(effect, minion, get_center(minion,effect), 20)
    board.bottom_objects.remove(minion)
    minion.image=minion.mini_image
    
def replace_hand_animation(entity):
    board=entity.owner.board
    effect=pygame.transform.scale(pygame.image.load('images/chillmaw_circle.png').convert_alpha(),(200,200))
    target_centers=[]
    n=0
    
    for target in entity.owner.hand:
        target_centers.append(get_center(target,effect))
        n+=1
    zoom_down_multiple_animation([effect]*n, entity, target_centers, speed=2, max_size=2,min_size=0.1)
                            
def golden_monkey_animation(minion):
    board=minion.owner.board
    effect=pygame.transform.scale(pygame.image.load('images/golden_statue.png').convert_alpha(),(1400,700))
    fade_in_out_animation(effect, minion, get_center(board,effect), stay=0.4, max_opacity=160)
  
    effect=pygame.transform.scale(pygame.image.load('images/fire_breath.png').convert_alpha(),(90,90))
    for card in minion.owner.hand:
        cone_animation(effect,minion,get_center(minion,effect),get_center(card,effect),width=200,K=5)
      
    effect=pygame.transform.scale(pygame.image.load('images/chillmaw_circle.png').convert_alpha(),(200,200))
    target_centers=[]
    n=0
    
    if len(minion.owner.deck.cards)<=0:
        minion.owner.deck.cards.append(minion)
    for target in minion.owner.hand+[minion.owner.deck.cards[0]]:
        target_centers.append(get_center(target,effect))
        n+=1
    zoom_down_multiple_animation([effect]*n, minion, target_centers, speed=2, max_size=2,min_size=0.1)

    if minion in minion.owner.deck.cards:
        minion.owner.deck.cards.remove(minion)

def explore_ungoro_animation(spell):
    board=spell.owner.board
    effect=pygame.transform.scale(pygame.image.load('images/primal_terrain.jpg').convert_alpha(),(1920,1080))
    fade_in_out_animation(effect, spell, get_center(board,effect), stay=0.01, max_opacity=160)
  
    effect=pygame.transform.scale(pygame.image.load('images/chillmaw_circle.png').convert_alpha(),(200,200))
    target_centers=[]
    n=0
    
    if len(spell.owner.deck.cards)<=0:
        spell.owner.deck.cards.append(spell)
    for target in [spell.owner.deck.cards[0]]:
        target_centers.append(get_center(target,effect))
        n+=1
    zoom_down_multiple_animation([effect]*n, spell, target_centers, speed=2, max_size=2,min_size=0.1)

    if spell in spell.owner.deck.cards:
        spell.owner.deck.cards.remove(spell)
                   
def unstable_portal_animation(spell_card,minion):
    board=spell_card.owner.board
    
    effect=pygame.transform.scale(pygame.image.load('images/blackhole.png').convert_alpha(),(55,80))

    
    zoom_up_multiple_animation([effect], spell_card, [get_center(board,effect)], speed=30, max_size=5, min_size=0.1)
    effect=pygame.transform.scale(pygame.image.load('images/blackhole.png').convert_alpha(),(275,400))
    blackhole = BoardObject(effect,rect=get_center(board,effect),owner=spell_card.owner)
    board.upper_objects.append(blackhole)
    for i in range(30):
        blackhole.rect.x+=(-1)**i*5
        show_board(board)
        time.sleep(0.02)
        
    zoom_down_multiple_animation([effect], spell_card, [get_center(board,effect)], speed=30, max_size=1, min_size=0.1)
    board.upper_objects.remove(blackhole)
    minion.location=get_center(board,minion.mini_image)

def nether_portal_animation(minion):
    board=minion.owner.board
    effect=pygame.transform.scale(pygame.image.load('images/blackhole.png').convert_alpha(),(55,80))

    zoom_up_multiple_animation([effect], minion, [get_center(board,effect)], speed=30, max_size=5, min_size=0.1)
    effect=pygame.transform.scale(pygame.image.load('images/blackhole.png').convert_alpha(),(275,400))
    blackhole = BoardObject(effect,rect=get_center(minion,effect),owner=minion.owner)
    board.upper_objects.append(blackhole)
    for i in range(30):
        blackhole.rect.x+=(-1)**i*5
        show_board(board)
        time.sleep(0.02) 
    zoom_down_multiple_animation([effect], minion, [get_center(board,effect)], speed=30, max_size=1, min_size=0.1)
    board.upper_objects.remove(blackhole)
    
def mimirons_head_animation(mimiron,minions,robot):
    board=robot.owner.board
    board.background = pygame.transform.scale(pygame.image.load('images/background_dark.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

    triangle_positions=[(450,150),(1050,150),(750,150+300*sqrt(3))]
    dests=[]
    i=0
    for minion in minions:
        dests.append(triangle_positions[i%3])
        i+=1
    move_multiple_animation(minions, dests, speed=10, zoom=True)
        
    robot.rect.x=(triangle_positions[0][0]+triangle_positions[1][0]+triangle_positions[2][0])/3
    robot.rect.y=(triangle_positions[0][1]+triangle_positions[1][1]+triangle_positions[2][1])/3
    effect = pygame.transform.scale(pygame.image.load('images/electric_triangle.png').convert_alpha(), (350,245))
    center=get_center(robot,effect)
    
    for i in range(4):
        zoom_up_multiple_animation([effect], robot, [(center[0]+40,center[1]+70)], speed=7, max_size=1.8, min_size=0.1)
    white_out_animation(robot)
    robot.image=robot.raw_image
    mimiron.rect.x,mimiron.rect.y=robot.rect.x,robot.rect.y
    mimiron.location=robot.rect.x,robot.rect.y
    
    show_board(board,exclude=minions,flip=False)
    show_card(robot)
    pygame.display.flip()
    time.sleep(2)

    board.background = pygame.transform.scale(pygame.image.load('images/background.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

def cthun_animation(minion):
    minion.owner.board.background = pygame.transform.scale(pygame.image.load('images/deep_sea.png').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
    white_out_animation(minion)
    zoom_down_animation(minion.image, minion, minion.location, speed=20, max_size=500)
    black_out_animation(minion)

    effect=pygame.transform.scale(pygame.image.load('images/kraken.png').convert_alpha(),(820, 823))
    fade_in_out_animation(effect, minion, get_center(minion.owner.board,effect), duration=30, stay=1, max_opacity=120)
 
    minion.owner.board.background = pygame.transform.scale(pygame.image.load('images/background.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

def yshaarj_rage_unbound_animation(minion):
    minion.owner.board.background = pygame.transform.scale(pygame.image.load('images/apocalyptic_sky.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
    white_out_animation(minion)
    zoom_down_animation(minion.image, minion, minion.location, speed=20, max_size=500)
    black_out_animation(minion)

    effect=pygame.transform.scale(pygame.image.load('images/kraken.png').convert_alpha(),(820, 823))
    fade_in_out_animation(effect, minion, get_center(minion.owner.board,effect), duration=30, stay=1, max_opacity=120)
 
    minion.owner.board.background = pygame.transform.scale(pygame.image.load('images/background.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

def nzoth_the_corruptor_animation(minion):
    minion.owner.board.background = pygame.transform.scale(pygame.image.load('images/ship_graveyard.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
    white_out_animation(minion)
    zoom_down_animation(minion.image, minion, minion.location, speed=20, max_size=500)
    black_out_animation(minion)

    effect=pygame.transform.scale(pygame.image.load('images/kraken.png').convert_alpha(),(820, 823))
    fade_in_out_animation(effect, minion, get_center(minion.owner.board,effect), duration=30, stay=1, max_opacity=120)
 
    minion.owner.board.background = pygame.transform.scale(pygame.image.load('images/background.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

def krul_the_unshackled_animation(minion):
    minion.owner.board.background = pygame.transform.scale(pygame.image.load('images/Hell_prison.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
    white_out_animation(minion)
    zoom_down_animation(minion.image, minion, minion.location, speed=20, max_size=500)
    black_out_animation(minion)

    effect=pygame.transform.scale(pygame.image.load('images/shadow_bolt.png').convert_alpha(),(800, 800))
    fade_in_out_animation(effect, minion, get_center(minion.owner.board,effect), duration=30, stay=1, max_opacity=120)
 
    minion.owner.board.background = pygame.transform.scale(pygame.image.load('images/background.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))


def thaddius_animation(minion):
    effect = pygame.transform.scale(pygame.image.load('images/lightning_storm.png').convert_alpha(), (480,480))
    minion.owner.board.background = pygame.transform.scale(pygame.image.load('images/background_dark.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
    
    white_out_animation(minion)
    time.sleep(0.2)
    white_out_animation(minion)
    time.sleep(0.1)
    white_out_animation(minion)
    time.sleep(0.5)
    
    fade_in_out_animation(effect, minion, get_center(minion,effect), duration=20, stay=0.6)
    white_out_animation(minion)
    minion.owner.board.background = pygame.transform.scale(pygame.image.load('images/background.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

def ragnaros_the_firelord_summon_animation(minion):
    minion.owner.board.background = pygame.transform.scale(pygame.image.load('images/magma.png').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
    white_out_animation(minion)
    zoom_down_animation(minion.image, minion, minion.location, speed=20, max_size=500)
    black_out_animation(minion)
    
    effect=pygame.transform.scale(pygame.image.load('images/581.png').convert_alpha(),(1162, 458))
    fade_in_out_animation(effect, minion, get_center(minion.owner.board,effect), duration=30, stay=1, max_opacity=70)
 
    minion.owner.board.background = pygame.transform.scale(pygame.image.load('images/background.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

def deathwing_animation(minion):
    minion.owner.board.background = pygame.transform.scale(pygame.image.load('images/inferno.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
    white_out_animation(minion)
    zoom_down_animation(minion.image, minion, minion.location, speed=20, max_size=500)
    black_out_animation(minion)
    
    effect=pygame.transform.scale(pygame.image.load('images/red_eyes.png').convert_alpha(),(103,77))
    fade_in_out_animation(effect,minion,get_center(minion,effect),duration=50,max_opacity=100)
    time.sleep(0.5)
    white_out_animation(minion)
    
    effect=pygame.transform.scale(pygame.image.load('images/581.png').convert_alpha(),(1162, 458))
    fade_in_out_animation(effect, minion, get_center(minion.owner.board,effect), duration=30, stay=1, max_opacity=120)
 
    minion.owner.board.background = pygame.transform.scale(pygame.image.load('images/background.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

def cenarius_animation(minion):
    minion.owner.board.background = pygame.transform.scale(pygame.image.load('images/forest.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
    black_out_animation(minion)
    
    zoom_down_animation(minion.image, minion, minion.location, speed=20, max_size=500)
    
    effect=pygame.transform.scale(pygame.image.load('images/forest_light.png').convert_alpha(),(SCREEN_WIDTH, SCREEN_HEIGHT))
    fade_in_out_animation(effect, minion, (0,0), duration=30, stay=1, max_opacity=120)
 
    minion.owner.board.background = pygame.transform.scale(pygame.image.load('images/background.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

def kun_the_forgotten_king_animation(minion):
    minion.owner.board.background = pygame.transform.scale(pygame.image.load('images/kun_site.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
    black_out_animation(minion)
    
    zoom_down_animation(minion.image, minion, minion.location, speed=20, max_size=500)
    
    effect=pygame.transform.scale(pygame.image.load('images/forest_light.png').convert_alpha(),(SCREEN_WIDTH, SCREEN_HEIGHT))
    fade_in_out_animation(effect, minion, (0,0), duration=30, stay=1, max_opacity=120)
 
    minion.owner.board.background = pygame.transform.scale(pygame.image.load('images/background.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))


def prophet_velen_animation(minion):
    effect=pygame.transform.scale(pygame.image.load('images/velen_triangle.png').convert_alpha(),(271,186))
    zoom_up_animation(effect, minion, get_center(minion,effect), speed=500, max_size=3600)

def rhonin_animation(minion):
    effect=pygame.transform.scale(pygame.image.load('images/Neutral_zodiac.png').convert_alpha(),(300,300))
    zoom_down_animation(effect, minion, get_center(minion,effect), speed=100, max_size=3600)
    fade_in_out_animation(effect, minion, get_center(minion,effect), duration=30, stay=1, max_opacity=170)
 
def azari_animation(minion):
    effect=pygame.transform.scale(pygame.image.load('images/Warlock_zodiac.png').convert_alpha(),(300,324))
    zoom_down_animation(effect, minion, get_center(minion,effect), speed=100, max_size=3600)
    fade_in_out_animation(effect, minion, get_center(minion,effect), duration=30, stay=1, max_opacity=170)
 
def malygos_animation(minion):
    minion.owner.board.background = pygame.transform.scale(pygame.image.load('images/storm_night.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
    white_out_animation(minion)
    
    zoom_down_animation(minion.image, minion, minion.location, speed=20, max_size=500)
    
    effect=pygame.transform.scale(pygame.image.load('images/storm.png').convert_alpha(),(SCREEN_WIDTH, SCREEN_HEIGHT))
    fade_in_out_animation(effect, minion, (0,0), duration=30, stay=1, max_opacity=120)
 
    minion.owner.board.background = pygame.transform.scale(pygame.image.load('images/background.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

def king_crush_animation(minion):

    show_board(minion.owner.board, exclude=[minion], flip=True)
    time.sleep(2)
    minion.location=minion.rect.x,minion.rect.y-1000
    move_animation(minion, (minion.rect.x,minion.rect.y), speed=200, zoom=True)
    zoom_down_animation(minion.image, minion, minion.location, speed=20, max_size=500)
    
    
    minion.owner.board.background = pygame.transform.scale(pygame.image.load('images/primal_jungle.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
    white_out_animation(minion)
    show_board(minion.owner.board)
    time.sleep(1)
    #effect=pygame.transform.scale(pygame.image.load('images/storm.png').convert_alpha(),(SCREEN_WIDTH, SCREEN_HEIGHT))
    #fade_in_out_animation(effect, minion, (0,0), duration=30, stay=1, max_opacity=120)
 
    minion.owner.board.background = pygame.transform.scale(pygame.image.load('images/background.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

def icehowl_animation(minion):
    minion.owner.board.background = pygame.transform.scale(pygame.image.load('images/snow_mountain.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
    black_out_animation(minion)
    
    zoom_down_animation(minion.image, minion, minion.location, speed=20, max_size=500)
    
    effect=pygame.transform.scale(pygame.image.load('images/snow_effect.png').convert_alpha(),(1200, 1024))
    fade_in_out_animation(effect, minion, get_center(minion.owner.board,effect), duration=30, stay=1, max_opacity=120)
 
    minion.owner.board.background = pygame.transform.scale(pygame.image.load('images/background.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
   
def aviana_animation(minion):
    minion.owner.board.background = pygame.transform.scale(pygame.image.load('images/heaven_garden.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
    white_out_animation(minion)
    
    zoom_down_animation(minion.image, minion, minion.location, speed=20, max_size=500)
    
    effect=pygame.transform.scale(pygame.image.load('images/feather_flower.png').convert_alpha(),(728, 571))
    fade_in_out_animation(effect, minion, get_center(minion.owner.board,effect), duration=30, stay=1, max_opacity=120)
 
    minion.owner.board.background = pygame.transform.scale(pygame.image.load('images/background.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

def time_warp_animation(entity):
    effect=pygame.transform.scale(pygame.image.load('images/clockgear.png').convert_alpha(),(600, 600))
    fade_in_out_animation(effect, entity, get_center(entity.owner.board,effect), duration=30, stay=1, max_opacity=120)
 
def hobart_grapplehammer_animation(minion):
    effect=pygame.transform.scale(pygame.image.load('images/clockgear.png').convert_alpha(),(600, 600))
    fade_in_out_animation(effect, minion, get_center(minion.owner.board,effect), duration=30, stay=1, max_opacity=120)
 
def nozdormu_animation(minion):
    minion.owner.board.background = pygame.transform.scale(pygame.image.load('images/sandstorm.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
    black_out_animation(minion)
    
    zoom_down_animation(minion.image, minion, minion.location, speed=20, max_size=500)
    
    effect=pygame.transform.scale(pygame.image.load('images/clockgear.png').convert_alpha(),(600, 600))
    fade_in_out_animation(effect, minion, get_center(minion.owner.board,effect), duration=30, stay=1, max_opacity=120)
 
    minion.owner.board.background = pygame.transform.scale(pygame.image.load('images/background.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

def the_ancient_one_animation(minion):
    minion.owner.board.background = pygame.transform.scale(pygame.image.load('images/ancient_black_hole.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
    black_out_animation(minion)
    
    zoom_down_animation(minion.image, minion, minion.location, speed=20, max_size=500)
    
    effect=pygame.transform.scale(pygame.image.load('images/ancient_rocks.png').convert_alpha(),(860, 473))
    fade_in_out_animation(effect, minion, get_center(minion.owner.board,effect), duration=30, stay=1, max_opacity=120)
 
    minion.owner.board.background = pygame.transform.scale(pygame.image.load('images/background.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))


def malganis_animation(minion):
    minion.owner.board.background = pygame.transform.scale(pygame.image.load('images/pandemonium.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
    black_out_animation(minion)
    
    zoom_down_animation(minion.image, minion, minion.location, speed=20, max_size=500)
    
    effect=pygame.transform.scale(pygame.image.load('images/devil_wings.png').convert_alpha(),(1200, 415))
    fade_in_out_animation(effect, minion, get_center(minion.owner.board,effect), duration=60, stay=1, max_opacity=180)
 
    minion.owner.board.background = pygame.transform.scale(pygame.image.load('images/background.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
   
      
def reno_jackson_animation(minion):
    effect=pygame.transform.scale(pygame.image.load('images/treasure.png').convert_alpha(),(200,200))
    zoom_down_animation(effect, minion, get_center(minion,effect), speed=7, max_size=700)
    effect=pygame.transform.scale(pygame.image.load('images/light.png').convert_alpha(),(180,110))
    zoom_up_animation(effect, minion, get_center(minion.owner,effect), speed=40, max_size=1500)
    zoom_down_animation(effect, minion, get_center(minion.owner,effect), speed=40, max_size=1500)
                  
def harrison_jones_animation(minion):
    effect=pygame.transform.scale(pygame.image.load('images/museum.png').convert_alpha(),(180,110))
    zoom_down_animation(effect, minion, get_center(minion.owner.opponent.weapon,effect), speed=5, max_size=700)

def recycle_animation(spell_card,target):
    zodiac_animation(spell_card.owner, spell_card.card_class)
    effect=pygame.transform.scale(pygame.image.load('images/wild_growth.png').convert_alpha(),(180,160))
    zoom_down_animation(effect, spell_card, get_center(target,effect), speed=15, max_size=300)

def rage_buff_animation(minion):
    aura=pygame.transform.scale(pygame.image.load('images/rage.png').convert_alpha(),(119,154))
    fade_in_out_animation(aura,minion,get_center(minion,aura),stay=0.5,max_opacity=80)

def light_buff_animation(minion):
    aura=pygame.transform.scale(pygame.image.load('images/white_light.png').convert_alpha(),(240,240))
    fade_in_out_animation(aura,minion,get_center(minion,aura),stay=0.2,max_opacity=150)

def lantern_of_power_animation(spell_card,target):
    effect=pygame.transform.scale(pygame.image.load('images/blackhole.png').convert_alpha(),(82,116))
    zoom_down_multiple_animation([effect], spell_card, [get_center(target,effect)], speed=3,max_size=5, min_size=0.2)
    shake_board(spell_card, intensity=0.15)

def dinosize_animation(minion):
    rage_buff_animation(minion)
    for i in range(2):
        buff_animation(minion,speed=20)
    shake_board(minion)
        
def pyros_animation(minion):
    aura=pygame.transform.scale(pygame.image.load('images/phoenix.png').convert_alpha(),(315,261))
    fade_in_out_animation(aura,minion,get_center(minion,aura),stay=0.1,max_opacity=150)

def resurrect_animation(minion):
    aura=pygame.transform.scale(pygame.image.load('images/holy_cross.png').convert_alpha(),(240,240))
    fade_out_animation(aura,minion,get_center(minion,aura),max_opacity=150)

def curious_glimmerroot_animation(minion,correct_card,selection):
    for card in selection:
        if isinstance(card,correct_card.__class__):
            correct_selection=[card]
    show_board(minion.owner.board)
    show_selection(correct_selection)
    pygame.display.flip()
    time.sleep(1)
    
def blessing_of_kings_animation(spell_card,target):
    show_board(spell_card.owner.board,exclude=[spell_card],flip=True) 
    aura=pygame.transform.scale(pygame.image.load('images/Blessing_of_Kings.png').convert_alpha(),(180,180))
    target_location = (target.rect.x+target.image.get_width()/2-aura.get_width()/2,target.rect.y+target.image.get_height()/2-aura.get_height()/2-80)
    fade_in_out_animation(aura,spell_card,target_location)
    buff_animation(target,speed=5)

def rogue_buff_animation(spell_card,target):
    if spell_card.isSpell:
        show_board(spell_card.owner.board,exclude=[spell_card],flip=True) 
    aura=pygame.transform.scale(pygame.image.load('images/shadow.png').convert_alpha(),(220,220))
    fade_in_out_animation(aura,spell_card,get_center(target,aura),duration=100,stay=0.6,max_opacity=150)

def priest_heal_animation(spell_card,target):
    show_board(spell_card.owner.board,flip=True) 
    aura=pygame.transform.scale(pygame.image.load('images/light.png').convert_alpha(),(380,380))
    fade_in_out_animation(aura,spell_card,get_center(target,aura))
    
def paladin_buff_animation(spell_card,target):
    show_board(spell_card.owner.board,exclude=[spell_card],flip=True) 
    aura=pygame.transform.scale(pygame.image.load('images/light.png').convert_alpha(),(220,220))
    fade_in_out_animation(aura,spell_card,get_center(target,aura))

def priest_buff_animation(spell_card,target):
    show_board(spell_card.owner.board,exclude=[spell_card],flip=True) 
    aura=pygame.transform.scale(pygame.image.load('images/cross.png').convert_alpha(),(160,220))
    fade_in_out_animation(aura,spell_card,get_center(target,aura))

def shaman_buff_animation(spell_card,target):
    show_board(spell_card.owner.board,exclude=[spell_card],flip=True) 
    aura=pygame.transform.scale(pygame.image.load('images/totem.png').convert_alpha(),(94,102))
    fade_in_out_animation(aura,spell_card,get_center(target,aura))
        
def paladin_debuff_animation(spell_card,target):
    show_board(spell_card.owner.board,exclude=[spell_card],flip=True) 
    aura=pygame.transform.scale(pygame.image.load('images/debuff.png').convert_alpha(),(129,61))
    fade_in_out_animation(aura,spell_card,get_center(target,aura),duration=50,stay=0.4)
        
def druid_buff_animation(spell_card,target):
    zodiac_animation(spell_card.owner, spell_card.card_class)
    aura=pygame.transform.scale(pygame.image.load('images/paw.png').convert_alpha(),(180,180))
    fade_in_out_animation(aura,spell_card,get_center(target,aura),stay=0.5)
    buff_animation(target,speed=10)

def warrior_buff_animation(spell_card,target):
    zodiac_animation(spell_card.owner, spell_card.card_class)
    aura=pygame.transform.scale(pygame.image.load('images/rage.png').convert_alpha(),(119,154))
    fade_in_out_animation(aura,spell_card,get_center(target,aura),stay=0.5,max_opacity=80)
    buff_animation(target,speed=10)
    
def hunter_buff_animation(spell_card,target):
    zodiac_animation(spell_card.owner, spell_card.card_class)
    aura=pygame.transform.scale(pygame.image.load('images/red_fang.png').convert_alpha(),(180,180))
    zoom_up_animation(aura, spell_card, get_center(target,aura), speed=5, max_size=200)
 
def lightforged_blessing_animation(spell_card,target):
    show_board(spell_card.owner.board,exclude=[spell_card],flip=True) 
    aura=pygame.transform.scale(pygame.image.load('images/light.png').convert_alpha(),(220,220))
    fade_in_out_animation(aura,spell_card,get_center(target,aura))

def ancestral_spirit_animation(spell_card,target):
    aura=pygame.transform.scale(pygame.image.load('images/totem.png').convert_alpha(),(141,159))
    fade_in_out_animation(aura,spell_card,get_center(target,aura),stay=0.5)
        
def gadgetzan_auctioneer_animation(minion):
    effect=pygame.transform.scale(pygame.image.load('images/coins.png').convert_alpha(),(90,90))
    target_location = (minion.rect.x+minion.image.get_width()*0.10,minion.rect.y-50)
    fade_in_out_animation(effect,minion,target_location,duration=25,stay=0.1)

def youthful_brewmaster_animation(minion,target):
    effect=pygame.transform.scale(pygame.image.load('images/barrel.png').convert_alpha(),(90,90))
    angle_offset=math.atan2((target.rect.x-minion.rect.x),(target.rect.y-minion.rect.y),)*180/math.pi
    effect=pygame.transform.rotate(effect, 135+angle_offset)
    projectile=BoardObject(effect,rect=get_center(minion,effect),owner=minion.owner)
    target_center=get_center(target,effect)
    move_animation(projectile, dest=target_center, speed=15, zoom=False)

def mad_hatter_animation(minion,target):
    effect=pygame.transform.scale(pygame.image.load('images/hat.png').convert_alpha(),(82,57))
    angle_offset=math.atan2((target.rect.x-minion.rect.x),(target.rect.y-minion.rect.y),)*180/math.pi
    effect=pygame.transform.rotate(effect, 135+angle_offset)
    projectile=BoardObject(effect,rect=get_center(minion,effect),owner=minion.owner)
    target_center=get_center(target,effect)
    move_animation(projectile, dest=target_center, speed=15, zoom=False)
    
def demolisher_animation(minion,target):
    effect=pygame.transform.scale(pygame.image.load('images/mortar.png').convert_alpha(),(115,115))
    angle_offset=math.atan2((target.rect.x-minion.rect.x),(target.rect.y-minion.rect.y),)*180/math.pi
    effect=pygame.transform.rotate(effect, 135+angle_offset)
    projectile=BoardObject(effect,rect=get_center(minion,effect),owner=minion.owner)
    target_center=get_center(target,effect)
    move_animation(projectile, dest=target_center, speed=10, zoom=False)

def fel_cannon_animation(minion,target):
    effect=pygame.transform.scale(pygame.image.load('images/fel_cannon.png').convert_alpha(),(155,155))
    angle_offset=math.atan2((target.rect.x-minion.rect.x),(target.rect.y-minion.rect.y),)*180/math.pi
    effect=pygame.transform.rotate(effect, 135+angle_offset)
    projectile=BoardObject(effect,rect=get_center(minion,effect),owner=minion.owner)
    target_center=get_center(target,effect)
    
    fade_in_out_animation(effect, minion, get_center(minion,effect),stay=0.1, max_opacity=150)
    move_animation(projectile, dest=target_center, speed=15, zoom=False)

def hobgoblin_animation(minion,target):
    effect=pygame.transform.scale(pygame.image.load('images/mead.png').convert_alpha(),(72,90))
    angle_offset=math.atan2((target.rect.x-minion.rect.x),(target.rect.y-minion.rect.y),)*180/math.pi
    effect=pygame.transform.rotate(effect, 135+angle_offset)
    projectile=BoardObject(effect,rect=get_center(minion,effect),owner=minion.owner)
    target_center=get_center(target,effect)
    move_animation(projectile, dest=target_center, speed=15, zoom=False)
    buff_animation(target)
        
def crazed_alchemist_animation(minion,target):
    effect=pygame.transform.scale(pygame.image.load('images/chemical.png').convert_alpha(),(90,90))
    angle_offset=math.atan2((target.rect.x-minion.rect.x),(target.rect.y-minion.rect.y),)*180/math.pi
    effect=pygame.transform.rotate(effect, 135+angle_offset)
    projectile=BoardObject(effect,rect=get_center(minion,effect),owner=minion.owner)
    target_center=get_center(target,effect)
    move_animation(projectile, dest=target_center, speed=15, zoom=False)

def big_game_hunter_animation(minion,target):
    effect=pygame.transform.scale(pygame.image.load('images/metal_ball.png').convert_alpha(),(90,90))
    projectile=BoardObject(effect,rect=get_center(minion,effect),owner=minion.owner)
    target_center=get_center(target,effect)
    move_animation(projectile, dest=target_center, speed=85, zoom=False)
    white_out_animation(minion)

def azari_the_devourer_animation(minion,target):
    effect=pygame.transform.scale(pygame.image.load('images/shadow_bolt.png').convert_alpha(),(190,190))
    projectile=BoardObject(effect,rect=get_center(minion,effect),owner=minion.owner)
    target_center=get_center(target,effect)
    move_animation(projectile, dest=target_center, speed=15, zoom=False)
    white_out_animation(minion)
    
def natalie_seline_animation(minion,target)  :
    effect=pygame.transform.scale(pygame.image.load('images/purple_whirl.png').convert_alpha(),(250,250))
    fade_in_out_animation(effect, minion, get_center(minion,effect), duration=80, stay=0.4, max_opacity=200)
    fade_in_animation(effect, minion, get_center(target,effect), duration=150, max_opacity=200)
    projectile=BoardObject(effect,rect=get_center(target,effect),owner=minion.owner)
    move_animation(projectile, get_center(minion,effect), speed=25, zoom=False)
    fade_out_animation(effect, minion, get_center(minion,effect), duration=80, max_opacity=200)

def bloodsail_corsair_animation(minion):
    target=minion.owner.opponent.weapon
    effect=pygame.transform.scale(pygame.image.load('images/knife.png').convert_alpha(),(30,30))
    knife=BoardObject(effect,rect=get_center(minion,effect),owner=minion.owner)
    target_center=get_center(target,effect)
    move_animation(knife, dest=target_center, speed=120, zoom=False)
     
def knife_juggler_animation(minion,target):
    effect=pygame.transform.scale(pygame.image.load('images/knife.png').convert_alpha(),(30,30))
    knife=BoardObject(effect,rect=get_center(minion,effect),owner=minion.owner)
    target_center=get_center(target,effect)
    move_animation(knife, dest=target_center, speed=120, zoom=False)

def cheaty_anklebiter_animation(minion,target):
    effect=pygame.transform.scale(pygame.image.load('images/knife.png').convert_alpha(),(30,30))
    knife=BoardObject(effect,rect=get_center(minion,effect),owner=minion.owner)
    target_center=get_center(target,effect)
    move_animation(knife, dest=target_center, speed=120, zoom=False)

def weapon_enchantment_animation(spell_card,weapon):
    effect=pygame.transform.scale(pygame.image.load('images/chemical.png').convert_alpha(),(22,30))
    angle_offset=math.atan2((weapon.rect.x-spell_card.rect.x),(weapon.rect.y-weapon.rect.y),)*180/math.pi
    effect=pygame.transform.rotate(effect, 45+angle_offset)
    projectile=BoardObject(effect,rect=get_center(spell_card,effect),owner=spell_card.owner)
    target_center=get_center(weapon,effect)
    move_animation(projectile, dest=target_center, speed=20, zoom=False)

def saboteur_animation(minion):
    effect=pygame.transform.scale(pygame.image.load('images/chemical.png').convert_alpha(),(22,30))
    projectile=BoardObject(effect,rect=get_center(minion,effect),owner=minion.owner)
    target_center=get_center(minion.owner.opponent.hero_power,effect)
    move_animation(projectile, dest=target_center, speed=30, zoom=False)

def sideshow_spelleater_animation(minion):
    effect=pygame.transform.scale(pygame.image.load('images/purple_whirl.png').convert_alpha(),(250,250))
    fade_in_out_animation(effect, minion, get_center(minion,effect), duration=80, stay=0.4, max_opacity=200)
    effect=pygame.transform.scale(pygame.image.load('images/purple_mirror.png').convert_alpha(),(90,52))
    projectile=BoardObject(effect,rect=get_center(minion.owner.opponent.hero_power,effect),owner=minion.owner)
    target_center=get_center(minion.owner.hero_power,effect)
    move_animation(projectile, dest=target_center, speed=30, zoom=False)
    enable_hero_power_animation(minion.owner.hero_power)

def yogg_saron_spell_animation(spell):
    spell.initialize_location((200,400))
    spell.image=spell.big_image
    spell.board_area="Hand"
    show_board(spell.owner.board)
    show_card(spell)
    pygame.display.flip()
    time.sleep(1) 
        
def bouncing_blade_animation(spell_card,target):
    effect=pygame.transform.scale(pygame.image.load('images/steel_circle.png').convert_alpha(),(70,70))
    initial_location=random.randint(-100,1820),random.choice([-100,860])
    projectile=BoardObject(effect,rect=initial_location,owner=spell_card.owner)
    target_center=get_center(target,effect)
    move_animation(projectile, dest=target_center, speed=60, zoom=False)
    move_animation(projectile, dest=(initial_location[0],target_center[1]*2-initial_location[1]), speed=60, zoom=False)
    
def elven_archer_animation(minion,target):
    effect=pygame.transform.scale(pygame.image.load('images/bolt.png').convert_alpha(),(30,30))
    angle_offset=math.atan2((target.rect.x-minion.rect.x),(target.rect.y-minion.rect.y),)*180/math.pi
    effect=pygame.transform.rotate(effect, 135+angle_offset)
    projectile=BoardObject(effect,rect=get_center(minion,effect),owner=minion.owner)
    target_center=get_center(target,effect)
    move_animation(projectile, dest=target_center, speed=50, zoom=False)

def eydis_darkbane_animation(minion,target):
    light_buff_animation(minion)
    effect=pygame.transform.scale(pygame.image.load('images/electric_triangle.png').convert_alpha(),(140,98))
    angle_offset=math.atan2((target.rect.x-minion.rect.x),(target.rect.y-minion.rect.y),)*180/math.pi
    effect=pygame.transform.rotate(effect, 225+angle_offset)
    projectile=BoardObject(effect,rect=get_center(minion,effect),owner=minion.owner)
    move_animation(projectile, dest=get_center(target,effect), speed=50, zoom=False)

def fjola_lightbane_animation(minion):
    light_buff_animation(minion)
    effect=pygame.transform.scale(pygame.image.load('images/angel_wing.png').convert_alpha(),(192,126))
    fade_in_out_animation(effect, minion, get_center(minion,effect), duration=80, stay=0.4, max_opacity=130)
    
   
def axe_flinger_animation(minion):
    target=minion.owner.opponent
    effect=pygame.transform.scale(pygame.image.load('images/headaxe.png').convert_alpha(),(58,62))
    angle_offset=math.atan2((target.rect.x-minion.rect.x),(target.rect.y-minion.rect.y),)*180/math.pi
    effect=pygame.transform.rotate(effect, 225+angle_offset)
    projectile=BoardObject(effect,rect=get_center(minion,effect),owner=minion.owner)
    move_animation(projectile, dest=get_center(target,effect), speed=50, zoom=False)

def flame_juggler_animation(minion,target):
    effect=pygame.transform.scale(pygame.image.load('images/fire_arrow.png').convert_alpha(),(100,100))
    angle_offset=math.atan2((target.rect.x-minion.rect.x),(target.rect.y-minion.rect.y),)*180/math.pi
    effect=pygame.transform.rotate(effect, 225+angle_offset)
    projectile=BoardObject(effect,rect=get_center(minion,effect),owner=minion.owner)
    move_animation(projectile, dest=get_center(target,effect), speed=50, zoom=False)
  
     
def zombie_chow_animation(minion):
    effect=pygame.transform.scale(pygame.image.load('images/heal.png').convert_alpha(),(141,141))
    projectile=BoardObject(effect,rect=get_center(minion,effect),owner=minion.owner)
    target_center=get_center(minion.owner.opponent,effect)
    move_animation(projectile, dest=target_center, speed=20, zoom=False)

def bolvar_fordragon_animation(bolvar,died_minion):
    if bolvar.side==1:
        effect=pygame.transform.scale(pygame.image.load('images/heal.png').convert_alpha(),(141,141))
        projectile=BoardObject(effect,rect=get_center(died_minion,effect),owner=died_minion.owner)
        move_animation(projectile, dest=get_center(bolvar,effect), speed=60)
        move_animation(bolvar, dest=(bolvar.location[0],bolvar.location[1]-10), speed=80, zoom=True)
        bolvar.image=bolvar.mini_image
        sort_hand_animation(bolvar.owner)
    
def buff_hand_animation(player,cards):
    if player.side==1:
        dests=[]
        for card in cards:
            dests.append((card.location[0],card.location[1]-15))
            
        move_multiple_animation(cards, dests, speed=35)
        for card in cards:
            card.image=card.mini_image
        time.sleep(0.1)

    
        
        
def murkspark_eel_animation(minion,target):
    effect=pygame.transform.scale(pygame.image.load('images/trigger2.png').convert_alpha(),(111,111))
    projectile=BoardObject(effect,rect=get_center(minion,effect),owner=minion.owner)
    target_center=get_center(target,effect)
    move_animation(projectile, dest=target_center, speed=50, zoom=False)
        
def ironforge_rifleman_animation(minion,target):
    effect=pygame.transform.scale(pygame.image.load('images/bullet.png').convert_alpha(),(30,30))
    angle_offset=math.atan2((target.rect.x-minion.rect.x),(target.rect.y-minion.rect.y),)*180/math.pi
    effect=pygame.transform.rotate(effect, 270+angle_offset)
    bullet=BoardObject(effect,rect=get_center(minion,effect),owner=minion.owner)
    target_center=get_center(target,effect)
    move_animation(bullet, dest=target_center, speed=50, zoom=False)

def gormok_the_gmpaler_animation(minion,target):
    effect=pygame.transform.scale(pygame.image.load('images/ivory.png').convert_alpha(),(164,134))
    angle_offset=math.atan2((target.rect.x-minion.rect.x),(target.rect.y-minion.rect.y),)*180/math.pi
    effect=pygame.transform.rotate(effect, 160+angle_offset)
    bullet=BoardObject(effect,rect=get_center(minion,effect),owner=minion.owner)
    target_center=get_center(target,effect)
    move_animation(bullet, dest=target_center, speed=70, zoom=False)
    shake_board(minion)

def stormpike_commando_animation(minion,target):
    effect=pygame.transform.scale(pygame.image.load('images/metal_ball.png').convert_alpha(),(30,30))
    angle_offset=math.atan2((target.rect.x-minion.rect.x),(target.rect.y-minion.rect.y),)*180/math.pi
    effect=pygame.transform.rotate(effect, 270+angle_offset)
    bullet=BoardObject(effect,rect=get_center(minion,effect),owner=minion.owner)
    target_center=get_center(target,effect)
    move_animation(bullet, dest=target_center, speed=50, zoom=False)

def bomb_lobber_animation(minion,target):
    effect=pygame.transform.scale(pygame.image.load('images/bomb.png').convert_alpha(),(96,115))
    projectile=BoardObject(effect,rect=get_center(minion,effect),owner=minion.owner)
    target_center=get_center(target,effect)
    move_animation(projectile, dest=target_center, speed=10, zoom=False)

def boom_bot_animation(minion,target):
    effect=pygame.transform.scale(pygame.image.load('images/bomb.png').convert_alpha(),(96,115))
    projectile=BoardObject(effect,rect=get_center(minion,effect),owner=minion.owner)
    target_center=get_center(target,effect)
    move_animation(projectile, dest=target_center, speed=15, zoom=False)
        
def sylvanas_windrunner_animation(minion,target):
    effect=pygame.transform.scale(pygame.image.load('images/purple_whirl.png').convert_alpha(),(130,130))
    projectile=BoardObject(effect,rect=get_center(minion,effect),owner=minion.owner)
    target_center=get_center(target,effect)
    move_animation(projectile, dest=target_center, speed=20, zoom=False)


def perditions_blade_animation(minion,target):
    effect=pygame.transform.scale(pygame.image.load('images/metal_ball.png').convert_alpha(),(30,30))
    angle_offset=math.atan2((target.rect.x-minion.rect.x),(target.rect.y-minion.rect.y),)*180/math.pi
    effect=pygame.transform.rotate(effect, 270+angle_offset)
    bullet=BoardObject(effect,rect=get_center(minion,effect),owner=minion.owner)
    target_center=get_center(target,effect)
    move_animation(bullet, dest=target_center, speed=50, zoom=False)
    
def fire_bolt_animation(minion,target):
    effect=pygame.transform.scale(pygame.image.load('images/fireball.png').convert_alpha(),(90,95))
    bullet=BoardObject(effect,rect=get_center(minion,effect),owner=minion.owner)
    target_center=get_center(target,effect)
    move_animation(bullet, dest=target_center, speed=40, zoom=False)
    
def glaivebound_adept_animation(minion,target):
    effect=pygame.transform.scale(pygame.image.load('images/soul_cleave.png').convert_alpha(),(80,80))
    cleave=BoardObject(effect,rect=get_center(minion,effect),owner=minion.owner)
    target_center=get_center(target,effect)
    move_animation(cleave, dest=target_center, speed=40, zoom=False)
         
def acidic_swamp_ooze_animation(minion,target):
    effect=pygame.transform.scale(pygame.image.load('images/acid.png').convert_alpha(),(30,30))
    acid=BoardObject(effect,rect=get_center(minion,effect),owner=minion.owner)
    move_animation(acid, get_center(target,effect), speed=35, zoom=False)

def acidmaw_animation(minion,target):
    effect=pygame.transform.scale(pygame.image.load('images/acid.png').convert_alpha(),(30,30))
    acid=BoardObject(effect,rect=get_center(minion,effect),owner=minion.owner)
    target_center=get_center(target,effect)
    move_animation(acid, dest=target_center, speed=25, zoom=False)
    
    effect=pygame.transform.scale(pygame.image.load('images/acid_melt.png').convert_alpha(),(164,156))
    fade_in_animation(effect, target, get_center(target,effect), duration=50, max_opacity=150)
    
def cleave_animation(spell_card,targets):
    zodiac_animation(spell_card.owner, spell_card.card_class)
    
    effect1=pygame.transform.scale(pygame.image.load('images/slash.png').convert_alpha(),(80,80))
    effect2=pygame.transform.flip(effect1,True,False)
    
    cleave1=BoardObject(effect1,rect=get_center(spell_card.owner,effect1),owner=spell_card.owner)
    cleave2=BoardObject(effect2,rect=get_center(spell_card.owner,effect2),owner=spell_card.owner)
    target_center1,target_center2=(700,400-80*spell_card.owner.side),(780,400-80*spell_card.owner.side)
    if len(targets)>0:
        target_center1=get_center(targets[0],effect1)
        target_center2=get_center(targets[0],effect2)
    if len(targets)>1:
        target_center2=get_center(targets[1],effect2)
        
    move_multiple_animation([cleave1,cleave2], dests=[target_center1,target_center2], speed=80)

    
def forked_lightning_animation(spell_card,targets):
    effect=pygame.transform.scale(pygame.image.load('images/arcane_explosion.png').convert_alpha(),(120,120))
    fade_in_animation(effect, spell_card, get_center(spell_card.owner,effect), duration=50, max_opacity=150)
    zoom_down_animation(effect, spell_card, get_center(spell_card.owner,effect), speed=5, max_size=320)
   
    
    effect1=pygame.transform.scale(pygame.image.load('images/lightning.png').convert_alpha(),(136,114))
    effect2=pygame.transform.flip(effect1,True,False)
    
    projectile1=BoardObject(effect1,rect=get_center(spell_card.owner,effect1),owner=spell_card.owner)
    projectile2=BoardObject(effect2,rect=get_center(spell_card.owner,effect2),owner=spell_card.owner)
    target_center1,target_center2=(700,400-80*spell_card.owner.side),(780,400-80*spell_card.owner.side)
    if len(targets)>0:
        target_center1=get_center(targets[0],effect1)
        target_center2=get_center(targets[0],effect2)
    if len(targets)>1:
        target_center2=get_center(targets[1],effect2)
        
    move_multiple_animation([projectile1,projectile2], dests=[target_center1,target_center2], speed=50)
    
def soul_cleave_animation(spell_card,targets):
    effect1=pygame.transform.scale(pygame.image.load('images/soul_cleave.png').convert_alpha(),(80,80))
    effect2=pygame.transform.flip(effect1,True,False)
    
    cleave1=BoardObject(effect1,rect=get_center(spell_card.owner,effect1),owner=spell_card.owner)
    cleave2=BoardObject(effect2,rect=get_center(spell_card.owner,effect2),owner=spell_card.owner)
    target_center1,target_center2=(700,400-80*spell_card.owner.side),(780,400-80*spell_card.owner.side)
    if len(targets)>0:
        images=[]
        dests=[]
        for target in targets:
            effect=pygame.transform.flip(effect2,True,False)
            projectile=BoardObject(effect,rect=get_center(spell_card.owner,effect),owner=spell_card.owner)
            images.append(projectile)
            dests.append(get_center(target,effect))

    move_multiple_animation(images, dests, speed=30)

def multi_shot_animation(spell_card,targets):
    zodiac_animation(spell_card.owner, spell_card.card_class)
    
    effect1=pygame.transform.scale(pygame.image.load('images/bolt.png').convert_alpha(),(120,120))
    effect2=pygame.transform.scale(pygame.image.load('images/bolt.png').convert_alpha(),(120,120))
    
    target_center1,target_center2=(700,400-80*spell_card.owner.side),(780,400-80*spell_card.owner.side)
    effect1=pygame.transform.rotate(effect1,135+90*(spell_card.owner.side+1))
    effect2=pygame.transform.rotate(effect2,135+90*(spell_card.owner.side+1))
    
    if len(targets)>0:
        target_center1=get_center(targets[0],effect1)
        target_center2=get_center(targets[0],effect2)
        angle_offset=math.atan2((targets[0].rect.x-spell_card.owner.rect.x),(targets[0].rect.y-spell_card.owner.rect.y),)*180/math.pi
        effect1=pygame.transform.rotate(effect1,angle_offset+90*(spell_card.owner.side+1))
        effect2=pygame.transform.rotate(effect2,angle_offset+90*(spell_card.owner.side+1))
    if len(targets)>1:
        target_center2=get_center(targets[1],effect2)
        angle_offset=math.atan2((targets[1].rect.x-spell_card.owner.rect.x),(targets[1].rect.y-spell_card.owner.rect.y),)*180/math.pi
        effect2=pygame.transform.rotate(effect2,angle_offset+90*(spell_card.owner.side+1))
        
    bolt1=BoardObject(effect1,rect=get_center(spell_card.owner,effect1),owner=spell_card.owner)
    bolt2=BoardObject(effect2,rect=get_center(spell_card.owner,effect2),owner=spell_card.owner)
   
    move_multiple_animation([bolt1,bolt2], dests=[target_center1,target_center2], speed=50)
    time.sleep(0.3)
    if len(targets)>0:
        for target in targets:
            shake_animation(target, cause=spell_card, direction="horizontal", intensity=0.1, duration=40)

def fan_of_knives_animation(spell_card):
    images=[]
    dests=[]
    effect0=pygame.transform.scale(pygame.image.load('images/knife.png').convert_alpha(),(60,60))
    for k in range(14):
        target_x=k*140
        target_y=SCREEN_HEIGHT/2-120-100*spell_card.side
        angle_offset=math.atan2((target_x-spell_card.owner.rect.x),(target_y-spell_card.owner.rect.y),)*180/math.pi
        effect=pygame.transform.rotate(effect0,angle_offset-50+90*(spell_card.owner.side+1))
        knife=BoardObject(effect,rect=get_center(spell_card.owner,effect),owner=spell_card.owner)
        images.append(knife)
        dests.append((target_x,target_y))
    for k in range(6):
        move_multiple_animation(images, dests, speed=50)
        for image in images:
            image.location=spell_card.owner.location

def north_sea_kraken_animation(minion,target):
    effect=pygame.transform.scale(pygame.image.load('images/water_shot.png').convert_alpha(),(78,52))
    cone_animation(effect,minion,get_center(minion,effect),get_center(target,effect),width=60,K=10)

def water_spell_animation(entity,target):
    if entity.isSpell:
        source=entity.owner
    else:
        source=entity
    effect=pygame.transform.scale(pygame.image.load('images/water_shot.png').convert_alpha(),(78,52))
    cone_animation(effect,entity,get_center(source,effect),get_center(target,effect),width=40,K=10)
 
  
def alexstrasza_animation(minion,target):
    effect=pygame.transform.scale(pygame.image.load('images/fire_breath.png').convert_alpha(),(90,90))
    cone_animation(effect,minion,get_center(minion,effect),get_center(target,effect),width=200,K=15)
    
def cone_animation(image,entity,source_center,target_center,width=100,K=30,speed=120):
    images=[]
    dests=[]

    for k in range(K):
        xt,yt=target_center[0],target_center[1]
        xs,ys=source_center[0],source_center[1]
        
        L=width*(abs(yt-ys))/math.sqrt((xt-xs)**2+(yt-ys)**2)
        x=xt-L/2+k*(L/(K-1))
        y=(xt-xs)/(ys-yt)*x+yt+xt*((xs-xt)/(ys-yt))

        angle_offset=math.atan2((x-xs),(y-ys),)*180/math.pi
        effect=pygame.transform.rotate(image,angle_offset+50+90*(-entity.side+1))
        projectile=BoardObject(effect,rect=source_center,owner=get_player(entity))
        images.append(projectile)
        dests.append((x,y))
    for k in range(10):
        move_multiple_animation(images, dests, speed=speed)
        for image in images:
            image.location=source_center
            
def split_damage_animation(entity,target,image=None,speed=30,curve=False):
    effect=image
    if entity.isMinion():
        source=entity
    else:
        source=get_player(entity)
    if entity.isMinion():
        source=entity
    
    if image is None:
        effect=pygame.transform.scale(pygame.image.load('images/arcane_missile.png').convert_alpha(),(80,80))
    missile=BoardObject(effect,rect=get_center(source,effect),owner=entity.owner)
    if curve:
        move_curve_animation(missile, dest=(entity.owner.rect.x-entity.owner.side*200,entity.owner.rect.y-entity.owner.side*200), Y=410-10*entity.owner.side,speed=30, zoom=False)
    move_animation(missile, dest=get_center(target,effect), speed=speed, zoom=False)

def wrath_animation(spell_card,target):
    effect = pygame.transform.scale(pygame.image.load('images/wild_growth.png').convert_alpha(), (260,230))
    fade_in_out_animation(effect, spell_card, get_center(spell_card.owner,effect), stay=0.2)
    
    effect=pygame.transform.scale(pygame.image.load('images/inner_demon.png').convert_alpha(),(94,84))
    projectile=BoardObject(effect,rect=get_center(spell_card.owner,effect),owner=spell_card.owner)
    move_curve_animation(projectile, dest=(spell_card.owner.rect.x-spell_card.owner.side*200,spell_card.owner.rect.y-spell_card.owner.side*200), Y=410-10*spell_card.owner.side,speed=30, zoom=False)
    move_animation(projectile, dest=get_center(target,effect), speed=80, zoom=False)
 
def buff_cthun_animation(card):
    show_board(card.owner.board, flip=False)
    
    fade_in_animation(card.raw_image, card, card.owner.deck.location, max_opacity=300)
    screen.blit(card.raw_image,card.owner.deck.location)
    atk_b=atk_background_zoom
    hp_b=hp_background_zoom

    atk_color={-1:RED,0:WHITE,1:GREEN}[sign(card.temp_atk-card.atk)]
    hp_color={-1:RED2,0:WHITE,1:GREEN}[sign(card.temp_hp-card.hp)]
    screen.blit(pygame.transform.scale(atk_b,(int(card.raw_image.get_width()*0.25),int(card.raw_image.get_width()*0.25))), (card.rect.x+card.raw_image.get_width()*0.01,card.rect.y+card.raw_image.get_height()*0.8))
    screen.blit(pygame.transform.scale(hp_b,(int(card.raw_image.get_width()*0.25),int(card.raw_image.get_width()*0.25))), (card.rect.x+card.raw_image.get_width()*0.70,card.rect.y+card.raw_image.get_height()*0.77))
    if card.owner.board.control==card.side:
        show_number(card.temp_atk, size=int(card.raw_image.get_width()*0.3), location=(card.rect.x+card.raw_image.get_width()*0.08,card.rect.y+card.raw_image.get_height()*0.83), color=atk_color, flip=False)
        show_number(card.temp_hp, size=int(card.raw_image.get_width()*0.3), location=(card.rect.x+card.raw_image.get_width()*0.77,card.rect.y+card.raw_image.get_height()*0.83), color=hp_color, flip=False)
    
    pygame.display.flip()
    time.sleep(1.3)

            
def si7_agent_animation(minion,target):
    effect=pygame.transform.scale(pygame.image.load('images/knife.png').convert_alpha(),(50,50))
    knife=BoardObject(effect,rect=get_center(minion,effect),owner=minion.owner)
    target_center=get_center(target,effect)
    move_curve_animation(knife, dest=(minion.rect.x-minion.side*200,minion.rect.y-minion.side*200), Y=410-10*minion.side,speed=30, zoom=False)
    move_animation(knife, dest=target_center, speed=80, zoom=False)

def dark_iron_skulker_animation(minion,targets):
    for target in targets:
        effect=pygame.transform.scale(pygame.image.load('images/knife.png').convert_alpha(),(50,50))
        knife=BoardObject(effect,rect=get_center(minion.owner,effect),owner=minion.owner)
        target_center=get_center(target,effect)
        time.sleep(0.1)
        
        move_curve_animation(knife, dest=(target.rect.x-target.side*100,target.rect.y-target.side*100), Y=210-10*target.side,speed=57, zoom=False)
        move_animation(knife, dest=target_center, speed=60)
        
        effect=pygame.transform.scale(pygame.image.load('images/slash.png').convert_alpha(),(120,120))
        slide_animation(effect, minion, get_center(target,effect), direction="right", speed=60)
        time.sleep(0.1)
    
def backstab_animation(spell_card,target):
    
    spell_card.owner.has_stealth=True
    #effect0=pygame.transform.scale(pygame.image.load('images/smog.png').convert_alpha(),(260,260))
    effect=pygame.transform.scale(pygame.image.load('images/knife.png').convert_alpha(),(50,50))
    knife=BoardObject(effect,rect=get_center(spell_card.owner,effect),owner=spell_card.owner)
    target_center=get_center(target,effect)
    
    #fade_in_animation(effect0,spell_card,get_center(spell_card.owner,effect0),duration=25,max_opacity=200)
    time.sleep(0.5)
    
    move_curve_animation(knife, dest=(target.rect.x-target.side*100,target.rect.y-target.side*100), Y=210-10*target.side,speed=17, zoom=False)
    move_animation(knife, dest=target_center, speed=30)
    
    effect=pygame.transform.scale(pygame.image.load('images/slash.png').convert_alpha(),(120,120))
    slide_animation(effect, spell_card, get_center(target,effect), direction="right", speed=60)
    time.sleep(0.5)
    spell_card.owner.has_stealth=False

def assassinate_animation(spell_card,target):

    spell_card.owner.board.background = pygame.transform.scale(pygame.image.load('images/background_dark.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
    spell_card.owner.has_stealth=True
    #effect0=pygame.transform.scale(pygame.image.load('images/smog.png').convert_alpha(),(260,260))
    effect=pygame.transform.scale(pygame.image.load('images/knife.png').convert_alpha(),(50,50))
    knife=BoardObject(effect,rect=get_center(spell_card.owner,effect),owner=spell_card.owner)
    target_center=get_center(target,effect)
    
    #fade_in_animation(effect0,spell_card,get_center(spell_card.owner,effect0),duration=25,max_opacity=200)
    time.sleep(0.5)
    
    move_animation(knife, dest=target_center, speed=80)
    effect=pygame.transform.scale(pygame.image.load('images/red_slash.png').convert_alpha(),(240,240))
    slide_animation(effect, spell_card, get_center(target,effect), direction="right", speed=60)
    time.sleep(0.8)
 
    spell_card.owner.board.background = pygame.transform.scale(pygame.image.load('images/background.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

    spell_card.owner.has_stealth=False
    
        
def sinister_strike_animation(spell_card,target):
    effect=pygame.transform.scale(pygame.image.load('images/knife.png').convert_alpha(),(50,50))
    knife=BoardObject(effect,rect=get_center(spell_card.owner,effect),owner=spell_card.owner)
    target_center=get_center(target,effect)
    time.sleep(0.2)
    move_curve_animation(knife, dest=(target.rect.x-target.side*200,target.rect.y-target.side*200), Y=410-10*target.side,speed=10, zoom=False)
    move_animation(knife, dest=target_center, speed=30)
    
    effect=pygame.transform.scale(pygame.image.load('images/slash.png').convert_alpha(),(120,120))
    slide_animation(effect, spell_card, get_center(target,effect), direction="right", speed=60)
    time.sleep(0.5)
     
     
def headcrack_animation(spell_card):
    '''Smash'''
    effect=pygame.transform.scale(pygame.image.load('images/metal_ball.png').convert_alpha(),(90,90))
    blow=BoardObject(effect,rect=get_center(spell_card.owner,effect),owner=spell_card.owner)
    target_location = get_center(spell_card.owner.opponent, effect)
    move_animation(blow, dest=target_location, speed=45, zoom=False)

    shake_board(spell_card)

def shiv_animation(spell_card,target):
    effect=pygame.transform.scale(pygame.image.load('images/shiv.png').convert_alpha(),(50,50))
    projectile=BoardObject(effect,rect=get_center(spell_card.owner,effect),owner=spell_card.owner)
    target_center=get_center(target,effect)
    time.sleep(0.2)
    move_animation(projectile, dest=target_center, speed=30)

def eviscerate_animation(spell_card,target):
    rogue_buff_animation(spell_card, spell_card.owner)
    effect=pygame.transform.scale(pygame.image.load('images/shiv.png').convert_alpha(),(80,80))
    projectile=BoardObject(effect,rect=get_center(spell_card.owner,effect),owner=spell_card.owner)
    target_center=get_center(target,effect)
    move_animation(projectile, dest=target_center, speed=40)

    effect=pygame.transform.scale(pygame.image.load('images/slash.png').convert_alpha(),(150,150))
    slide_animation(effect, spell_card, get_center(target,effect), direction="right", speed=60)
    time.sleep(0.3)

def razorpetal_animation(spell_card,target):
    effect=pygame.transform.scale(pygame.image.load('images/knife.png').convert_alpha(),(30,30))
    projectile=BoardObject(effect,rect=get_center(spell_card.owner,effect),owner=spell_card.owner)
    target_center=get_center(target,effect)
    move_animation(projectile, dest=target_center, speed=40)
    
def betrayal_animation(spell_card,target):
    effect=pygame.transform.scale(pygame.image.load('images/smog.png').convert_alpha(),(192,108))
    fade_in_out_animation(effect,spell_card,get_center(target,effect),duration=80,stay=0.5)
    
    effect=pygame.transform.scale(pygame.image.load('images/stun.png').convert_alpha(),(200,180))
    target_center=get_center(target,effect)
    fade_in_out_animation(effect,spell_card,(target_center[0]-150,target_center[1]),duration=10,stay=0.05)
    shake_board(spell_card)
    fade_in_out_animation(effect,spell_card,(target_center[0]+150,target_center[1]),duration=10,stay=0.05)
    shake_board(spell_card)
    
def mortal_coil_animation(spell_card,target):
    effect=pygame.transform.scale(pygame.image.load('images/purple_fog.png').convert_alpha(),(150,160))
    fade_in_out_animation(effect,spell_card,get_center(spell_card.owner,effect),duration=40,stay=0.5)
    effect=pygame.transform.scale(pygame.image.load('images/mortal_coil.png').convert_alpha(),(50,50))
    projectile=BoardObject(effect,rect=get_center(spell_card.owner,effect),owner=spell_card.owner)
    target_center=get_center(target,effect)
    time.sleep(0.2)
    move_animation(projectile, dest=target_center, speed=15)     

def demonheart_animation(spell_card,target):
    effect=pygame.transform.scale(pygame.image.load('images/demon_eye.png').convert_alpha(),(164,112))
    fade_in_out_animation(effect,spell_card,get_center(spell_card.owner,effect),duration=40,stay=0.5)
    effect=pygame.transform.scale(pygame.image.load('images/demonheart.png').convert_alpha(),(164,174))
    projectile=BoardObject(effect,rect=get_center(spell_card.owner,effect),owner=spell_card.owner)
    target_center=get_center(target,effect)
    time.sleep(0.2)
    move_animation(projectile, dest=target_center, speed=15)  

def eye_beam_animation(spell_card,target):
    effect=pygame.transform.scale(pygame.image.load('images/demon_eye.png').convert_alpha(),(82,56))
    fade_in_out_animation(effect,spell_card,get_center(spell_card.owner,effect),duration=40,stay=0.5)
    projectile=BoardObject(effect,rect=get_center(spell_card.owner,effect),owner=spell_card.owner)
    target_center=get_center(target,effect)
    move_animation(projectile, dest=target_center, speed=40)  
        
def drain_life_animation(spell_card,target):
    effect1=pygame.transform.scale(pygame.image.load('images/purple_fog.png').convert_alpha(),(150,160))
    effect2=pygame.transform.scale(pygame.image.load('images/mortal_coil.png').convert_alpha(),(140,100))
    fade_in_out_animation(effect1,spell_card,get_center(spell_card.owner,effect1),duration=40,stay=0.5)
    fade_in_out_animation(effect2,spell_card,get_center(target,effect2),duration=40,stay=0.8)
     
def flame_lance_animation(spell_card,target):
    effect=pygame.transform.scale(pygame.image.load('images/fire_circle.png').convert_alpha(),(102,102))
    fade_in_animation(effect, spell_card, get_center(spell_card.owner,effect), duration=50, max_opacity=150)
    zoom_down_animation(effect, spell_card, get_center(spell_card.owner,effect), speed=5, max_size=320)
    
    effect=pygame.transform.scale(pygame.image.load('images/flame_lance.png').convert_alpha(),(90,321))
    angle_offset=math.atan2((target.rect.x-spell_card.owner.rect.x),(target.rect.y-spell_card.owner.rect.y),)*180/math.pi
    effect=pygame.transform.rotate(effect, angle_offset)
    projectile=BoardObject(effect,rect=get_center(spell_card.owner,effect),owner=spell_card.owner)
    target_center=get_center(target,effect)
    move_animation(projectile, dest=target_center, speed=20)  
    
def shadow_bolt_animation(spell_card,target):
    effect=pygame.transform.scale(pygame.image.load('images/purple_fog.png').convert_alpha(),(150,160))
    fade_in_out_animation(effect,spell_card,get_center(spell_card.owner,effect),duration=40,stay=0.5)
    effect=pygame.transform.scale(pygame.image.load('images/shadow_bolt.png').convert_alpha(),(80,80))
    projectile=BoardObject(effect,rect=get_center(spell_card.owner,effect),owner=spell_card.owner)
    target_center=get_center(target,effect)
    move_animation(projectile, dest=target_center, speed=20)  
        
def soulfire_animation(spell_card,target):
    effect=pygame.transform.scale(pygame.image.load('images/purple_fog.png').convert_alpha(),(150,160))
    fade_in_out_animation(effect,spell_card,get_center(spell_card.owner,effect),duration=40,stay=0.5)
    effect=pygame.transform.scale(pygame.image.load('images/soulfire.png').convert_alpha(),(90,90))
    projectile=BoardObject(effect,rect=get_center(spell_card.owner,effect),owner=spell_card.owner)
    target_center=get_center(target,effect)
    time.sleep(0.2)
    move_animation(projectile, dest=target_center, speed=15)  

def lifedrinker_animation(minion):
    effect1=pygame.transform.scale(pygame.image.load('images/shadow_bolt.png').convert_alpha(),(80,80))
    projectile1=BoardObject(effect1,rect=get_center(minion.owner.opponent,effect1),owner=minion.owner)
    target_center1=get_center(minion,effect1)
    
    effect2=pygame.transform.scale(pygame.image.load('images/heal.png').convert_alpha(),(140,140))
    projectile2=BoardObject(effect2,rect=get_center(minion,effect2),owner=minion.owner)
    target_center2=get_center(minion.owner,effect2)
    
    move_multiple_animation([projectile1, projectile2], [target_center1,target_center2], speed=20)
                 
def prince_malchezaar_animation(prince,cards):
    time.sleep(0.5)
    old_location=prince.location
    prince.initialize_location()
    prince.owner.board.objs.append(prince)
    prince.image=prince.raw_image
    fade_in_animation(prince.image, prince, prince.location, duration=50)
    
    for card in cards:
        card.location=(800,400)
        card.show_back=True
        move_animation(card, dest=(prince.owner.deck.location[0]+100,prince.owner.deck.location[1]), speed=50)
        card.show_back=False
     
    fade_out_animation(prince.image, prince, prince.location, duration=50)   
    prince.owner.board.objs.remove(prince)
    prince.rect.x,prince.rect.y=old_location
    prince.location=prince.rect.x,prince.rect.y
    prince.image=prince.mini_image
    time.sleep(0.5)

def ungoro_pack_animation(cards):
    i=0
    R = 220
    for card in cards:
        x = R*math.cos(math.radians(90+i*72))+SCREEN_WIDTH*0.45
        y = R*math.sin(math.radians(90+i*72))+SCREEN_HEIGHT*0.3
        card.image=card.raw_image
        card.initialize_location((x,y))
        #card.initialize_location((SCREEN_WIDTH*0.2+card.raw_image.get_width()*i*1.3,SCREEN_HEIGHT/2-card.raw_image.get_height()/2))
        show_card(card)
        i+=1
    pygame.display.flip()
    shake_board(cards[0])
    time.sleep(1)
    dests=[]
    for card in cards:
        card.image=card.mini_image
        if len(card.owner.hand)-len(cards)<=1:
            x,y=SCREEN_WIDTH/2-388,{-1:5,1:820}[card.owner.side]
        else:
            x,y=card.owner.hand[-2-len(cards)].location[0]+card.mini_image.get_width()+100,card.owner.hand[-2-len(cards)].location[1]
        dests.append((x,y))
    move_multiple_animation(cards, dests, speed=20)

        
    
        
def upgrade_hero_power_animation(minion):
    time.sleep(0.3)
    old_location=minion.location
    minion.initialize_location()
    minion.owner.board.objs.append(minion)
    minion.image=minion.raw_image
    fade_in_animation(minion.image, minion, minion.location,duration=150)
    time.sleep(0.5)
    
    effect=pygame.transform.scale(pygame.image.load('images/ice_bolt.png').convert_alpha(),(180,180))
    projectile=BoardObject(effect,rect=get_center(minion,effect),owner=minion.owner)
    move_animation(projectile, get_center(minion.owner.hero_power,effect), speed=10,zoom=True)
    
    fade_out_animation(minion.image, minion, minion.location, duration=50)   
    minion.owner.board.objs.remove(minion)
    minion.rect.x,minion.rect.y=old_location
    minion.location=minion.rect.x,minion.rect.y
    minion.image=minion.mini_image
    
    disable_hero_power_animation(minion.owner.hero_power)
    

                    
def buff_animation(target,speed=5):
    buff_circle=pygame.image.load('images/buff_circle.png').convert_alpha()
    for k in range(int(150/speed)):
        size=k*speed
        effect=pygame.transform.scale(buff_circle,(size,size))
        target_center=get_center(target,effect)
        show_board(target.owner.board,flip=False)
        screen.blit(effect,target_center)
        pygame.display.flip()
'''
def zoom_up_animation(image,entity=None,target_location=(0,0),speed=5) :
    board=get_player(entity).board
    for k in range(int(150/speed)):
        size=k*speed
        effect=pygame.transform.scale(buff_circle,(size,size))
        target_center=get_center(target,effect)
        show_board(target.owner.board,flip=False)
        screen.blit(effect,target_center)
        pygame.display.flip()'''

def mech_buff_animation(target,speed=5):
    effect=pygame.transform.scale(pygame.image.load('images/gear.png').convert_alpha(),(92,98))
    target_center=get_center(target,effect)
    rotate_animation(effect, target, (target_center[0],target_center[1]-100), speed)
            
def fade_in_animation(image,entity=None,target_location=(0,0),duration=50,max_opacity=500):
    board=get_player(entity).board
    board.MOVING_ANIMATION=True
    for k in range(duration):
        show_board(board,flip=False) 
        blit_alpha(screen,image,target_location,(k+1)*max_opacity/duration)
        pygame.display.flip()
    board.MOVING_ANIMATION=False 
      
def fade_out_animation(image,entity=None,target_location=(0,0),duration=50,max_opacity=500):  
    board=get_player(entity).board   
    board.MOVING_ANIMATION=True
    for k in range(duration):
        show_board(board,flip=False) 
        blit_alpha(screen,image,target_location,(duration-k)*max_opacity/duration)
        pygame.display.flip()
    board.MOVING_ANIMATION=False
                        
def fade_in_out_animation(image,entity=None,target_location=(0,0),duration=50,stay=0,max_opacity=500):
    fade_in_animation(image,entity,target_location,duration,max_opacity=max_opacity)
    time.sleep(stay)
    fade_out_animation(image,entity,target_location,duration,max_opacity=max_opacity)
    
def fade_in_out_multiple_animation(images,entity,target_locations,duration=50,stay=0,max_opacity=500):
    fade_in_multiple_animation(images,entity,target_locations,duration,max_opacity=max_opacity)
    time.sleep(stay)
    fade_out_multiple_animation(images,entity,target_locations,duration,max_opacity=max_opacity)
            
def fade_in_multiple_animation(images,entity,target_locations,duration=50,max_opacity=500):
    board=get_player(entity).board
    board.MOVING_ANIMATION=True
    for k in range(duration):
        show_board(board,flip=False)
        for i in range(len(images)):
            blit_alpha(screen,images[i],target_locations[i],(k+1)*max_opacity/duration)
        pygame.display.flip()
    board.MOVING_ANIMATION=False
        
def fade_out_multiple_animation(images,entity,target_locations,duration=50,max_opacity=500):
    board=get_player(entity).board
    board.MOVING_ANIMATION=True
    for k in range(duration):
        show_board(board,flip=False)
        for i in range(len(images)):
            blit_alpha(screen,images[i],target_locations[i],(duration-k)*max_opacity/duration)
        pygame.display.flip()
    board.MOVING_ANIMATION=False