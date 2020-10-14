import importlib,time,pygame,math,random,sys
from board import Board
from player import Druid,Warrior,Mage,Priest,Paladin,Shaman,Warlock,Hunter,Rogue,Demon_Hunter
from GUIHandler import show_board,countdown,explode_rope,show_text,clock,FPS

card_collection = importlib.import_module("card")

#Enable this if to craft deck
#player1 = login(side=1)
#player2 = login(side=-1)

#For debugging purpose, create adhoc players and decks
player1 = Rogue(side=1)
player2 = Warlock(side=-1,player_name="Opponent")

player1.mana=8
player2.mana=8


# - parameters -


#Initialize board
board=Board()
board.control=1
board.DEBUG_MODE=True
board.add_players(player1,player2)

#For debugging

for i in range(3):  # Add 30 cards to each player's deck
    #card1  = getattr(card_collection, "Malorne")()
    #card2  = getattr(card_collection, "Iron_Juggernaut")()
    #card3  = getattr(card_collection, "Novice_Engineer")()
    #card4  = getattr(card_collection, "Shattered_Sun_Cleric")()
    #card5  = getattr(card_collection, "Murloc_Tidehunter")()
    #card6  = getattr(card_collection, "Gruul")()
    #card7  = getattr(card_collection, "Blessing_of_Kings")()
    #card8  = getattr(card_collection, "Arcane_Shot")()
    #card9  = getattr(card_collection, "Mirror_Entity")()
    #card10 = getattr(card_collection, "Explosive_Trap")()
    #card11 = getattr(card_collection, "Freezing_Trap")()
    #card12 = getattr(card_collection, "Misdirection")()
    #card13 = getattr(card_collection, "Noble_Sacrifice")()
    #card14 = getattr(card_collection, "Power_of_the_Wild")()
    #card15 = getattr(card_collection, "Druid_of_the_Claw")()
    #card16 = getattr(card_collection, "Argent_Squire")()
    #card17 = getattr(card_collection, "Patient_Assassin")()
    #card18 = getattr(card_collection, "Volcanosaur")()
    #card19 = getattr(card_collection, "Envenom_Weapon")()
    #card20 = getattr(card_collection, "Stormwind_Champion")()
    #card21 = getattr(card_collection, "Dire_Wolf_Alpha")()
    #card22 = getattr(card_collection, "Arcane_Amplifier")()
    #card23 = getattr(card_collection, "Dwarven_Sharpshooter")()
    #card24 = getattr(card_collection, "Pint_Sized_Summoner")()
    #card25 = getattr(card_collection, "Southsea_Deckhand")()
    #card26 = getattr(card_collection, "Gyrocopter")()
    #card27 = getattr(card_collection, "Lightning_Storm")()
    #card28 = getattr(card_collection, "Felstalker")()
    #card29 = getattr(card_collection, "Malchezaars_Imp")()
    #card30 = getattr(card_collection, "Unbound_Elemental")()
    #card31 = getattr(card_collection, "Spiteful_Smith")()
    #card32 = getattr(card_collection, "Gadgetzan_Auctioneer")()
    #card33 = getattr(card_collection, "Knife_Juggler")()
    #card34 = getattr(card_collection, "Water_Elemental")()
    #card35 = getattr(card_collection, "Living_Dragonbreath")()
    #card36 = getattr(card_collection, "Cheaty_Anklebiter")()
    #card37 = getattr(card_collection, "Aldrachi_Warblades")()
    #card38 = getattr(card_collection, "Ethereal_Conjurer")() 
    #card39 = getattr(card_collection, "Sir_Finley_Mrrgglton")() 
    #card40 = getattr(card_collection, "Murloc_Knight")() 
    #card41 = getattr(card_collection, "SI7_Agent")()
    #card42 = getattr(card_collection, "Headcrack")()
    #card43 = getattr(card_collection, "Warpath")()
    #card44 = getattr(card_collection, "Ghost_Light_Angler")()
    #card45 = getattr(card_collection, "Glinda_Crowskin")()
    #card46 = getattr(card_collection, "Kings_Elekk")()
    #card47 = getattr(card_collection, "Armored_Warhorse")()
    #card48 = getattr(card_collection, "Deathspeaker")()
    #card49 = getattr(card_collection, "Gladiators_Longbow")()
    #card50 = getattr(card_collection, "Violet_Illusionist")()
    #card51 = getattr(card_collection, "Ice_Block")()
    #card52 = getattr(card_collection, "Generous_Mummy")()
    #card53 = getattr(card_collection, "Woecleaver")()
    #card54 = getattr(card_collection, "Micro_Mummy")()
    #card55 = getattr(card_collection, "Annoy_o_Module")()
    #card56 = getattr(card_collection, "Missile_Launcher")()
    #card57 = getattr(card_collection, "Voidcaller")()
    #card58 = getattr(card_collection, "Sulthraze")()
    #card59 = getattr(card_collection, "Sightless_Ranger")()
    #card60 = getattr(card_collection, "Mind_Control")()
    #card61 = getattr(card_collection, "Shadow_Madness")()
    #card62 = getattr(card_collection, "Activate_the_Obelisk")()
    #card63 = getattr(card_collection, "Jungle_Giants")()
    #card64 = getattr(card_collection, "Prince_Malchezaar")()
    #card65 = getattr(card_collection, "Ironbeak_Owl")()
    #card66 = getattr(card_collection, "Lightforged_Blessing")()
    #card67 = getattr(card_collection, "Valeera_the_Hollow")()
    #card68 = getattr(card_collection, "Acidic_Swamp_Ooze")()
    #card69 = getattr(card_collection, "Elven_Archer")()
    #card70 = getattr(card_collection, "Grimscale_Oracle")()
    #card71 = getattr(card_collection, "Voodoo_Doctor")()
    #card72 = getattr(card_collection, "Gurubashi_Berserker")()
    #card73 = getattr(card_collection, "Nightblade")()
    #card74 = getattr(card_collection, "Razorfen_Hunter")()
    #card75 = getattr(card_collection, "Shadowhoof_Slayer")()
    #card76 = getattr(card_collection, "Sightless_Watcher")()
    #card77 = getattr(card_collection, "Coordinated_Strike")()
    #card78 = getattr(card_collection, "CThun")()
    card79 = getattr(card_collection, "Faceless_Manipulator")()
    card80 = getattr(card_collection, "Deathwing")()
    card81 = getattr(card_collection, "Blackwater_Pirate")()
    card82 = getattr(card_collection, "Primordial_Glyph")()
    card83 = getattr(card_collection, "Ethereal_Conjurer")()
    card84 = getattr(card_collection, "Toki_Time_Tinker")()
    card85 = getattr(card_collection, "Fiery_War_Axe")()
    card86 = getattr(card_collection, "Worgen_Abomination")()


    player1.deck.add_card(card82)
    player1.deck.add_card(card83)
    player1.deck.add_card(card85)
    player1.deck.add_card(card81)
    #player1.deck.add_card(card78)
    #player1.deck.add_card(card77)
    #player1.deck.add_card(card78)
    #player1.deck.add_card(card26)
    #player1.deck.add_card(card25)
    #player1.deck.add_card(card24)
    #player2.deck.add_card(card20)
    player2.deck.add_card(card84)
    player2.deck.add_card(card80)
    player2.deck.add_card(card79)
    player2.deck.add_card(card86)
    #player2.deck.add_card(card18)
    #player2.deck.add_card(card17)
    #player2.deck.add_card(card19)
    #player2.deck.add_card(card35)
    #player2.deck.add_card(card17)


#Play BGM
try:
    pygame.mixer.init()
    pygame.mixer.music.load("audio/bgm/"+str(random.randint(1,8))+".mp3")
    pygame.mixer.music.play(loops=-1, start=0.0)
    pygame.mixer.music.pause()
except:
    print("Audio Device Error! No BGM will be played")

#Remembering Initial Deck Cards
for player in [player1, player2]:
    for card in player.deck.cards:
        player.initial_deck.append(card)
        card.started_in_deck=True

player2.draw(4)
board.mulligan(player1)

#Start game
board.start_game()
player=board.players[board.control]




# - mainloop -
while board.running:

    # - events -
    pygame.event.pump()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            board.running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                  
                CARD_SELECTED=False     
                for card in board.get_cards(player)+board.get_cards(player.opponent):    
                    '''When a card is selected'''     
                    if card.rect.collidepoint(event.pos) and (card.owner is player or card.temporary_effects['owned'] is player) :
                        #Card Zooming
                        card.image=card.raw_image
                        card.zoomed=True
                        player.current_card=card
                        
                        #if card.board_area=="Hand" or (card.board_area=="Board" and card.card_type=="Minion" and card.current_atk+card.owner.board.get_buff(card)['atk']>0 and not card.attacked and (not card.summoning_sickness or card.has_rush or card.has_charge or board.get_buff(card)['charge'] )):
                        if (card.board_area=="Hand" or (card.board_area=="Board" and card.isMinion())) and (card.owner is player or card.temporary_effects['owned'] is player) and not card.has_dormant:
                            # control parameters
                            card.selected = True
                            
                            #prepare moving parameters
                            mouse_x, mouse_y = event.pos
                            offset_x = card.rect.x - mouse_x
                            offset_y = card.rect.y - mouse_y
                            
                        CARD_SELECTED=True
                        break
                        
                if not CARD_SELECTED:        
                    #When hero power is selected
                    if player.hero_power.rect.collidepoint(event.pos):
                        player.hero_power.image=player.hero_power.raw_image
                        player.hero_power.zoomed=True
                        player.hero_power.selected = True
                        if not player.hero_power.disabled():
                            if player.hero_power.is_targeted():
                                player.hero_power.dragging=True
  
                    #When hero is selected
                    elif player.rect.collidepoint(event.pos) and player.can_attack():
                        # control parameters
                        player.dragging = True
                    
                    #When player emotes
                    elif board.negative_emote_button.collidepoint(event.pos):
                        player.negative_emote()
                        board.end_turn=True
                    elif board.positive_emote_button.collidepoint(event.pos):
                        player.positive_emote()
                        board.end_turn=True
                    elif board.end_turn_button.collidepoint(event.pos):
                        board.end_turn=True

                    #Sound on/off
                    elif board.music_button.collidepoint(event.pos):
                        try:
                            if board.music_on:                        
                                pygame.mixer.music.pause()
                            else:
                                pygame.mixer.music.unpause()
                            board.music_on = not board.music_on
                        except:
                            print("No Audio device! Music control failed")
                            
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:

                if player.current_card != None:
                                  
                    #Card Zooming
                    card=player.current_card
                    card.zoomed=False
                    card.selected=False
                    
                    if card.board_area=="Hand":
                        card.image = card.mini_image
                    elif card.board_area=="Board":
                        card.image = card.board_image
                    
                    #play card only when the current card is being dragged
                    if player.current_card.dragging:
                        player.current_card.dragging = False
                        player.current_card.selected = False
                    
                        if player.current_mana>=player.current_card.get_current_cost() or board.get_buff(player.current_card)['cost health'] or player.current_card.board_area=="Board":
                            card_target=None
                            for target in player.all_characters():
                                if target is not player.current_card and target.rect.collidepoint(event.pos):
                                    card_target=target
                            player.play(player.current_card,card_target)
                        else:
                            show_text("I don't have enough mana!",flip=True, pause=0.6)
                            player.current_card.rect.x,player.current_card.rect.y=player.current_card.location
                    player.current_card = None
                
                elif player.dragging:
                    player.dragging=False
                    for target in player.enemy_characters():
                        if target.rect.collidepoint(event.pos):
                            if target.is_attackable_by(player):
                                player.attack(target)
                                break
                    player.rect.x,player.rect.y=player.location
                        
                #Invoke Hero Power   
                elif player.hero_power.dragging and player.hero_power.targeted:
                    for target in player.all_characters():
                        if target.rect.collidepoint(event.pos) and target.is_targetable():
                            #Mana management
                            if player.current_mana>=player.hero_power.get_current_cost():
                                player.hero_power.invoke(target)
                            else:
                                show_text("I don't have enough mana!",flip=True, pause=0.6)
                                
                elif player.hero_power.selected and not player.hero_power.targeted and not player.hero_power.passive:
                    player.hero_power.zoomed=False
                    player.hero_power.image = player.hero_power.board_image
                    if player.hero_power.rect.collidepoint(event.pos) and not player.hero_power.disabled():
                        #Mana management
                        if player.current_mana>=player.hero_power.get_current_cost():
                            player.hero_power.invoke()
                        else:
                            show_text("I don't have enough mana!",flip=True, pause=0.6)
            player.hero_power.dragging=False
            player.hero_power.image = player.hero_power.board_image
            if player.hero_power.disabled():
                player.hero_power.image = player.hero_power.disabled_image
            player.hero_power.zoomed=False
            player.hero_power.selected = False
            
            board.resolve_destroy_queue()
                            
        elif event.type == pygame.MOUSEMOTION:
            player.mouse_move_length+=math.sqrt((player.mouse_pos[0]-event.pos[0])**2+(player.mouse_pos[1]-event.pos[1])**2)
            player.mouse_pos=event.pos
            for card in board.get_cards(player):  
                if card.selected:
                    card.zoomed=False
                    
                    card.dragging=True
                    if card.board_area=="Board" and card.isMinion():
                        if card.unable_to_attack():
                            show_text("The minion cannot attack!", flip=True, pause=0.6)
                            card.dragging=False
                            card.selected=False
                        elif card.attacked and not card.windfury_active():
                            show_text("The minion has already attacked!", flip=True, pause=0.6)
                            card.dragging=False
                            card.selected=False
                        elif card.summoning_sickness and not (card.has_rush or card.has_charge or board.get_buff(card)['charge'] or board.get_buff(card)['rush']):
                            show_text("Give minion a turn to get ready!", flip=True, pause=0.6)
                            card.dragging=False
                            card.selected=False
                        elif card.frozen and not card.owner.board.get_buff(card)['defrozen']:
                            show_text("The minion is frozen!", flip=True, pause=0.6)
                            card.dragging=False
                            card.selected=False
                            
                    if card.dragging:                      
                        mouse_x, mouse_y = event.pos
                        card.rect.x = mouse_x + offset_x
                        card.rect.y = mouse_y + offset_y
                        if ("Targeted" in card.tags and not "Choose One" in card.abilities) and (card.card_type=="Spell" or card.card_type=="Weapon") and card.landed_board_area()!="Hand":
                            card.image=card.arrow_image
                        elif card.isMinion() and card.board_area=="Board" and card.landed_board_area()=="Opponent":
                            card.image=card.arrow_image
                        elif card.board_area=="Board":
                            card.image=card.board_image
                        else:
                            card.image=card.mini_image
            
            if player.hero_power.selected:
                player.hero_power.image=player.hero_power.board_image
                player.hero_power.zoomed=False          


    # - draws (without updates) -
    
    if board.running==False:
        break
    
    player.remaining_time=board.turn_time_limit[player.side]-(time.perf_counter()-board.start_time)
    show_board(board)
    #if player.dragging or (player.current_card is not None and player.current_card.image==player.current_card.arrow_image):
    #    show_arrow(player,event.pos)
    pygame.display.flip()
 

    if player.remaining_time<=0 or board.get_buff(player)['time_limit']<0 or board.end_turn:
        if player.remaining_time<=0 or board.get_buff(player)['time_limit']<0:
            explode_rope(player)
            
        #Refresh Turn only effects
        board.end_turn_phase(player)
        show_board(board)
        
        if not player.take_extra_turn:
            player=player.opponent
            board.control*=-1
        else:
            player.take_extra_turn-=1
            
        board.start_turn_phase(player)

        
    # - constant game speed / FPS -

    clock.tick(FPS)

# - end -

pygame.quit()
sys.exit()