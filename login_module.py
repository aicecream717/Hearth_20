'''
Created on Apr 18, 2020

@author: shan.jiang
'''

import re,database
import pygame,importlib,random
from GUIHandler import show_hero_selection,show_draft_screen,white_out,flash_out


hero_collection = importlib.import_module("player")

class_of={"Jaina":"Mage",
          "Garrosh":"Warrior",
          "Uther":"Paladin",
          "Gul'dan":"Warlock",
          "Illidan":"Demon_Hunter",
          "Malfurion":"Druid",
          "Anduin":"Priest",
          "Valera":"Rogue",
          "Thrall":"Shaman",
          "Rexxar":"Hunter",
    }

def login(side=1):
    username=input("enter your name:\n")
    current_hero=None
    deck_str=None
    
    username_in_use=True
    while username_in_use:
        user_exist,username_in_use=database.check_username_in_database(username)
        if user_exist :
            username, password, current_hero, deck_str = database.get_user_info(username)
            decrypted_password=database.decrypt(password)
            #while(input("Please enter your password:\n")!=decrypted_password):
            #    print("Wrong password! Please Try again!")
            print("\nWelcome back! Login completed.\n")     
        elif not username_in_use:
            password=input("Welcome new player! Please create your password(less than 20 letters):")
            database.create_new_player(username,password)
        else:
            username=input("The username is already used! enter another name:\n")
            

    #Prompt to select hero if None
    if current_hero is None:
        hero_names=random.sample(["Malfurion","Uther","Garrosh","Rexxar","Jaina","Thrall","Anduin","Valera","Gul'dan","Illidan"],k=3)
        heroes = show_hero_selection(hero_names)
    
        selecting=True
        while selecting:
           
        # - events -
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    selecting = False
        
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        #Pick a card  
                        for hero in heroes:       
                            if heroes[hero].collidepoint(event.pos):
                                current_hero=hero
                                selecting=False
                                
    player          = getattr(hero_collection,class_of[current_hero])(player_name=username,hero_name=current_hero,side=side)
    database.update_current_hero(player)
    finalize_deck(player,deck_str) 
    
    return player

def finalize_deck(player,deck_str):    
    deck_limit=30
    
    card_collection = importlib.import_module("card")
 
    #Initializing cards selected by player already
    if deck_str is None:
        selected_card_names=[]
    else:
        selected_card_names = deck_str.split(";")
    selected_cards=[]
    for card_name in selected_card_names:
        card=getattr(card_collection,database.cleaned(card_name))(owner=player)
        selected_cards.append(card)
    num_of_cards=len(selected_cards)
    
    cards=database.get_random_cards(filter_str="[class]='Neutral' or [class] LIKE '%"+class_of[player.hero_name]+"%'",owner=player,k=3)
    '''card1  = getattr(card_collection, random.choice(["Malorne","Iron_Juggernaut","Novice_Engineer","Shattered_Sun_Cleric","Murloc_Tidehunter","Gruul"]))(owner=player)
    card2  = getattr(card_collection, random.choice(["Malorne","Iron_Juggernaut","Novice_Engineer","Shattered_Sun_Cleric","Murloc_Tidehunter","Gruul"]))(owner=player)
    card3  = getattr(card_collection, random.choice(["Malorne","Iron_Juggernaut","Novice_Engineer","Shattered_Sun_Cleric","Murloc_Tidehunter","Gruul"]))(owner=player)
    cards=[card1,card2,card3]'''

    show_draft_screen(selected_cards,cards,player)
    flash_out(cards)
                            
    running=True
    while running and num_of_cards<=deck_limit:

        show_draft_screen(selected_cards,cards,player)
    # - events -
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
    
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    #Pick a card  
                    for card in cards:       
                        if card.rect.collidepoint(event.pos):
                            white_out(card)
                            selected_cards.append(card)
                            num_of_cards+=1
                            database.add_card_to_draft(player,card)
                            
                            #Get new selection
                            cards=database.get_random_cards(filter_str="[format]='standard' and ([class]='Neutral' or [class] LIKE '%"+class_of[player.hero_name]+"%')",owner=player,k=3)
                            '''card1  = getattr(card_collection, random.choice(["Malorne","Iron_Juggernaut","Novice_Engineer"]))(owner=player)
                            card2  = getattr(card_collection, random.choice(["Malorne","Iron_Juggernaut","Novice_Engineer"]))(owner=player)
                            card3  = getattr(card_collection, random.choice(["Malorne","Iron_Juggernaut","Novice_Engineer"]))(owner=player)
                            cards=[card1,card2,card3]'''
                            
                            show_draft_screen(selected_cards,cards,player,flip=False)
                            flash_out(cards)
                           
            elif event.type == pygame.MOUSEMOTION:
                for card in selected_cards:
                    if card.rect.collidepoint(event.pos):
                        card.selected=True
                    else:
                        card.selected=False
     
    for card in selected_cards:
        player.deck.add_card(card)
        player.initial_deck.append(card)
        card.started_in_deck=True
    player.deck.shuffle()
    
def create_player(player_name):
    username, password, current_hero, deck_str = database.get_user_info(player_name)
    player = getattr(hero_collection,class_of[current_hero])(player_name=username,hero_name=current_hero,side=-1)
    finalize_deck(player,deck_str)
    return player
    
        
if __name__ == '__main__':
    f=open("card.py","r",encoding="utf-8")
    pattern=re.compile(r"def __init__\(self,name=\"(.*?)\".*?:(#Uncollectible)?")
    for line in f:
        results=pattern.findall(line)
        if len(results)>0:
            #print(results)
            card_name=results[0][0]
            uncollectible=results[0][1]=='#Uncollectible'
            try:
                database.set_standard(card_name,uncollectible)
            except:
                pass
    

                 
    player1 = login(side=1)
    player2 = login(side=-1)