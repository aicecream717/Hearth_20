import importlib,time,pygame,database,random,math,sys
from board import Board
from GUIHandler import show_board,countdown,explode_rope,show_text,clock,FPS
from login_module import login,create_player


card_collection = importlib.import_module("card")


player1 = login(side=1)
opponent_name, seed,sessionID = database.search_opponent(player1)
player2 = create_player(opponent_name)

#Initialize board
board=Board(sessionID=sessionID)
board.control=({True:1,False:-1}[player1.player_name>=player2.player_name])*((-1)**seed)
board.add_players(player1,player2)
#Play BGM
try:
    pygame.mixer.init()
    pygame.mixer.music.load("audio/bgm/"+str(random.randint(1,8))+".mp3")
    pygame.mixer.music.play(loops=-1, start=0.0)
    pygame.mixer.music.pause()
except:
    print("Audio Device Error! No BGM will be played")


#Start game
board.mulligan(player1)
random.seed(seed) #Synchronizing pseudo random seed
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
                  
                database.insert_event(player,entity=None,target=None,event_pos=event.pos,event_type="click",instant_resolve=True) #Record any mouse clicking activities.
                CARD_SELECTED=False     
                for card in board.get_cards(player)+board.get_cards(player.opponent):       
                    '''When a card is selected'''     
                    if card.rect.collidepoint(event.pos):
                        #Card Zooming
                        card.image=card.raw_image
                        card.zoomed=True
                        
                        # control parameters
                        player.current_card=card
                        
                        
                        #if card.board_area=="Hand" or (card.board_area=="Board" and card.card_type=="Minion" and card.current_atk+card.owner.board.get_buff(card)['atk']>0 and not card.attacked and (not card.summoning_sickness or card.has_rush or card.has_charge or board.get_buff(card)['charge'] )):
                        if player.side==1 and (card.board_area=="Hand" or (card.board_area=="Board" and card.isMinion())) and (card.owner is player or card.temporary_effects['owned'] is player) and not card.has_dormant:
                            
                            card.selected = True
                            #prepare moving parameters
                            mouse_x, mouse_y = event.pos
                            offset_x = card.rect.x - mouse_x
                            offset_y = card.rect.y - mouse_y
                            
                        CARD_SELECTED=True
                        break
                        
                if not CARD_SELECTED and player.side==1:        
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
                    
                    #When turn ends 
                    elif board.negative_emote_button.collidepoint(event.pos):
                        database.insert_event(player,entity="Curse",target=None,event_pos=event.pos,event_type="play")
                        player.negative_emote()
                        board.end_turn=True
                    elif board.positive_emote_button.collidepoint(event.pos):
                        database.insert_event(player,entity="Well Played",target=None,event_pos=event.pos,event_type="play")
                        player.positive_emote()
                        board.end_turn=True      
                    elif board.end_turn_button.collidepoint(event.pos):
                        database.insert_event(player,entity=None,target=None,event_pos=event.pos,event_type="play")
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
                    card.selected = False
                    
                    if card.board_area=="Hand":
                        card.image = card.mini_image
                    elif card.board_area=="Board":
                        card.image = card.board_image
                    
                    #play card only when the current card is being dragged
                    if card.dragging:
                        card.dragging = False
                        
                        if player.current_mana>=card.get_current_cost() or board.get_buff(player.current_card)['cost health'] or card.board_area=="Board":
                            card_target=None
                            for target in player.all_characters():
                                if target is not card and target.rect.collidepoint(event.pos):
                                    card_target=target
                            database.insert_event(player,card,card_target,event.pos)
                            player.play(card,card_target,mouse_pos=event.pos)
                            
                        else:
                            show_text("I don't have enough mana!",flip=True, pause=0.6)
                            card.rect.x,card.rect.y=card.location
                    player.current_card = None
                
                elif player.dragging:
                    player.dragging=False
                    for target in player.enemy_characters():
                        if target.rect.collidepoint(event.pos):
                            if target.is_attackable_by(player):
                                database.insert_event(player,player,target,event.pos)
                                player.attack(target)
                                break
                    player.rect.x,player.rect.y=player.location
                        
                #Invoke Hero Power   
                elif player.hero_power.dragging and player.hero_power.targeted:
                    for target in player.all_characters():
                        if target.rect.collidepoint(event.pos) and target.is_targetable():
                            #Mana management
                            if player.current_mana>=player.hero_power.get_current_cost():
                                database.insert_event(player,player.hero_power,target,event.pos)
                                player.hero_power.invoke(target)
                            else:
                                show_text("I don't have enough mana!",flip=True, pause=0.6)
                                
                elif player.hero_power.selected and not player.hero_power.targeted and not player.hero_power.passive:
                    player.hero_power.image = player.hero_power.board_image
                    player.hero_power.zoomed=False
                    if player.hero_power.rect.collidepoint(event.pos) and not player.hero_power.disabled():
                        #Mana management
                        if player.current_mana>=player.hero_power.get_current_cost():
                            database.insert_event(player,player.hero_power,target=None,event_pos=event.pos)
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
                        elif card.attacked and not not card.windfury_active():
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

    if board.control==-1:
        opponent_events = database.get_events(board.players[-1])
        for event in opponent_events:
            event_id,event_str=event
            board.resolve(event_str)
            database.resolve_event(event_id)
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
            board.turn_time_limit[player.side]=15
            
        #Refresh Turn only effects
        board.end_turn_phase(player)
        show_board(board)
        
        player=player.opponent
        board.control*=-1

        board.start_turn_phase(player)

        
    # - constant game speed / FPS -

    clock.tick(FPS)

# - end -

pygame.quit()
sys.exit()