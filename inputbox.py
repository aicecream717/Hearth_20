# by Timothy Downs, inputbox written for my map editor

# This program needs a little cleaning up
# It ignores the shift key
# And, for reasons of my own, this program converts "-" to "_"

# A program to get user input, allowing backspace etc
# shown in a box in the middle of the screen
# Called by:
# import inputbox
# answer = inputbox.ask(screen, "Your name")
#
# Only near the center of the screen is blitted to

import pygame, pygame.font, pygame.event, pygame.draw, string
from pygame.locals import *

white=(255,255,255)
black=(0,0,0)

def get_key():
    while 1:
        event = pygame.event.poll()
        if event.type == KEYDOWN:
            return event.key
        else:
            pass

def display_box(screen, message):
    "Print a message in a box in the middle of the screen"
    fontobject = pygame.font.Font(None,18)
    pygame.draw.rect(screen, (0,0,0), ((screen.get_width() / 2) - 100,(screen.get_height() / 2) - 10, 200,20), 0)
    pygame.draw.rect(screen, (255,255,255), ((screen.get_width() / 2) - 102, (screen.get_height() / 2) - 12,204,24), 1)
    if len(message) != 0:
        screen.blit(fontobject.render(message, 1, (255,255,255)),((screen.get_width() / 2) - 100, (screen.get_height() / 2) - 10))
    pygame.display.flip()

def display_hp_bar(screen,pokemon,x,y):
    green=(124,252,0)
    yellow=(255,255,0)
    red=(255,255,0)
    if(pokemon.current_hp/pokemon.hp>0.5):
        color=green
    elif(0.5>=pokemon.current_hp/pokemon.hp>0.25):
        color=yellow
    else:
        color=red
    
    pygame.draw.rect(screen,white,(x,y,170,34),0)
    pygame.draw.rect(screen,black,(x+2,y+2,166,30),0)
    pygame.draw.rect(screen,color,(x+2,y+2,int(166*pokemon.current_hp/pokemon.hp),30),0)

def display_gauge_bar(screen,pokemon,x,y):
    blue=(0,128,255)
    border_color=(153,204,255)
    gauge_length=50
    for i in range(pokemon.gauge):
        pygame.draw.rect(screen,border_color,(x+i*(gauge_length+8)+15,y,gauge_length,30),0)
        pygame.draw.rect(screen,blue,(x+i*(gauge_length+8)+17,y+2,gauge_length-4,26),0)

    
    
def display_multiline_box(screen, message, width,x, y,font_size,font_color,box_color,border_color):
    fontobject = pygame.font.Font(None,font_size)
    lines = message.splitlines()
    if(width==0):
        num_of_char_longest_line=0
        for line in lines:
            if (len(line)>num_of_char_longest_line):
                num_of_char_longest_line=len(line)
        width=int(num_of_char_longest_line*font_size*12/30)

    pygame.draw.rect(screen,border_color,(x-10,y-5,width,font_size*len(lines)+10),0)
    pygame.draw.rect(screen,box_color,(x-8,y-3,width-4,font_size*len(lines)+6),0)
    for i, line in enumerate(lines):
        screen.blit(fontobject.render(line, 0, font_color), (x, y + font_size*i))

    
def display_menu(screen, menu, width):
    color=""
    if(menu.box_color==black):
        color="black"
    if(menu.box_color==white):
        color="white"
    message=menu.text_content
    display_multiline_box(screen,message,width,menu.x,menu.y,menu.font_size,menu.font_color,menu.box_color,menu.border_color)
    arrow_icon = pygame.image.load('images/selection_arrow_'+color+'.png').convert()
    screen.blit(arrow_icon, menu.arrow.position)

def display_menu_with_egg_icon(screen, menu):
    additional_width=40
    display_menu(screen, menu, menu.width+additional_width)
    for i,option in menu.option.items():
        if(i!=len(menu.option)):
            egg_color=option.text[0:option.text.find("(")].lstrip(str(i)+": ").strip()[0]
            egg_status=option.text[0:option.text.find("(")].lstrip(str(i)+": ").strip()[1]
            egg_image = pygame.image.load("images/items/egg_"+egg_color+'.png').convert()
            incubator_image = pygame.image.load("images/items/incubator.png").convert()
            egg_icon=pygame.transform.scale(egg_image,(menu.font_size-5,menu.font_size-5))
            incubator_icon=pygame.transform.scale(incubator_image,(menu.font_size-5,menu.font_size-5))
            screen.blit(egg_icon, (menu.x+24,menu.option[i].y))
            if(egg_status=='1'):
                screen.blit(incubator_icon, (menu.x+64,menu.option[i].y))
    egg_color=menu.option[menu.arrow.current_index].text[0:menu.option[menu.arrow.current_index].text.find("(")].lstrip(str(menu.arrow.current_index)+": ").strip()[0]
    egg_status=menu.option[menu.arrow.current_index].text[0:menu.option[menu.arrow.current_index].text.find("(")].lstrip(str(menu.arrow.current_index)+": ").strip()[1]
    if(menu.arrow.current_index!=len(menu.option)):
        egg_image=pygame.image.load("images/items/egg_"+egg_color+'.png').convert()
        screen.blit(egg_image, (150,screen.get_height()/2-200))

def display_menu_with_item_icon(screen, menu):
    additional_width=40
    display_menu(screen, menu, menu.width+additional_width)
    for i,option in menu.option.items():
        if(i!=len(menu.option)):
            item_name=option.text[0:option.text.find("(")].lstrip(str(i)+": ").strip()
            item_icon = pygame.image.load("images/items/"+item_name+'.png').convert()
            item_icon=pygame.transform.scale(item_icon,(menu.font_size-5,menu.font_size-5))
            screen.blit(item_icon, (menu.option[i].x+menu.width-40,menu.option[i].y))
    current_item_name=menu.option[menu.arrow.current_index].text[0:menu.option[menu.arrow.current_index].text.find("(")].lstrip(str(menu.arrow.current_index)+": ").strip()
    if(menu.arrow.current_index!=len(menu.option)):
        item_image=pygame.image.load("images/items/"+current_item_name+'.png').convert()
        screen.blit(item_image, (150,screen.get_height()/2-200))

def display_menu_with_pokemon_icon(screen, menu,player):
    additional_width=40
    display_menu(screen, menu, menu.width+additional_width)
    for i,option in menu.option.items():
        if(i!=len(menu.option)):
            pokemon_name=option.text[0:option.text.find("CP")].lstrip(str(i)+": ").strip()
            pokemon_image = pygame.image.load("images/pokemons/"+pokemon_name+'.png').convert()
            pokemon_image=pygame.transform.scale(pokemon_image,(250,250))
            pokemon_image.set_colorkey(white)
            pokemon_icon=pygame.transform.scale(pokemon_image,(menu.font_size-5,menu.font_size-5))
            screen.blit(pokemon_icon, (menu.option[i].x+menu.width-40,menu.option[i].y))
    current_pokemon_name=menu.option[menu.arrow.current_index].text[0:menu.option[menu.arrow.current_index].text.find("CP")].lstrip(str(menu.arrow.current_index)+": ").strip()
    if(menu.arrow.current_index!=len(menu.option)):
        pokemon_image=pygame.image.load("images/pokemons/"+current_pokemon_name+'.png').convert()
        pokemon_image=pygame.transform.scale(pokemon_image,(250,250))
        pokemon_image.set_colorkey(white)
        screen.blit(pokemon_image, (800,screen.get_height()/2-150))
        display_multiline_box(screen, str(player.pokemons_in_hand[menu.arrow.current_index-1]), 500, 700, screen.get_height()/2+120,font_size=32,font_color=black,box_color=white,border_color=black)

def display_menu_with_candy_icon(screen, menu,player,pokemon):
    additional_width=-240
    display_multiline_box(screen, "                              "+str(player.candy_bag['stardust'])+"                             "+str(player.candy_bag[pokemon.candy_type])+"\n                       STARDUST   "+pokemon.candy_type.upper(), 630, menu.x, menu.y-2*menu.font_size-18, font_size=menu.font_size, font_color=menu.font_color, box_color=menu.box_color, border_color=menu.border_color)
    display_menu(screen, menu, 630)
    stardust_icon=pygame.image.load('images/items/stardust_icon.png').convert()
    candy_icon=pygame.image.load('images/items/candy_icon.png').convert()

    #Player owning:
    screen.blit(stardust_icon, (menu.x+140,menu.y-menu.font_size*2-20))   
    screen.blit(candy_icon, (menu.x+370,menu.y-menu.font_size*2-20)) 
    
    #POWER UP required
    screen.blit(stardust_icon, (menu.x+140,menu.y))
    screen.blit(candy_icon, (menu.x+370,menu.y))
    
    #Evolve required
    screen.blit(candy_icon, (menu.x+370,menu.y+menu.font_size))
    
    
    
   


         
    
def ask(screen, question,font_size,font_color,box_color,border_color):
    "ask(screen, question) -> answer"
    fontobject = pygame.font.Font(None,font_size)
    current_string = []
    display_multiline_box(screen, question+"\n\n\n\n", screen.get_width()/2-250,screen.get_height()/2-1,font_size,font_color,box_color,border_color)
    pygame.draw.rect(screen,border_color,(screen.get_width()/2-220,screen.get_height()/2-1+font_size*2,10*font_size*22/30,font_size),0)
    pygame.draw.rect(screen,box_color,(screen.get_width()/2-218,screen.get_height()/2+1+font_size*2,10*font_size*22/30-4,font_size-4),0)
    screen.blit(fontobject.render(join(current_string,""), 1, font_color), (screen.get_width()/2-220, screen.get_height()/2+1+font_size*2))
    pygame.display.flip()
    #display_multiline_box(screen, join(current_string,""), screen.get_width()/2-220,screen.get_height()/2-1+font_size*2,font_size,font_color,box_color,box_color)
    #display_box(screen, question + ": " + join(current_string,""))
    while 1:
        inkey = get_key()
        if inkey == K_BACKSPACE:
            current_string = current_string[0:-1]
        elif inkey == K_RETURN:
            break
        elif inkey == K_MINUS:
            current_string.append("_")
        elif inkey <= 127:
            current_string.append(chr(inkey))
        display_multiline_box(screen, question+"\n\n\n\n", screen.get_width()/2-250,screen.get_height()/2-1,font_size,font_color,box_color,border_color)
        pygame.draw.rect(screen,border_color,(screen.get_width()/2-220,screen.get_height()/2-1+font_size*2,10*font_size*22/30,font_size),0)
        pygame.draw.rect(screen,box_color,(screen.get_width()/2-218,screen.get_height()/2+1+font_size*2,10*font_size*22/30-4,font_size-4),0)
        screen.blit(fontobject.render(join(current_string,""), 1, font_color), (screen.get_width()/2-220, screen.get_height()/2+1+font_size*2))
        pygame.display.flip()
    return join(current_string,"")

def join(list,symbol):
    result=""
    for char in list:
        result+=char+symbol
    return result
'''
def main_old():
    screen = pygame.display.set_mode((320,240))
    print (ask(screen, "Name") + " was entered")

if __name__ == '__main__':
    main_old()
'''