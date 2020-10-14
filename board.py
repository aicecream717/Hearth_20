'''
Created on Apr 9, 2020

@author: shan.jiang
'''

import random,time,database
from GUIHandler import SCREEN_WIDTH,SCREEN_HEIGHT,background,sort_minions_animation, show_text,get_rect,\
    move_multiple_animation,choose_mulligan_cards, sort_hand_animation,show_turn
from card import Secret,Enchantment

class Board:
    def __init__(self,sessionID="00000"):
        self.sessionID=sessionID
        self.background=background
        self.upper_objects=[]
        self.bottom_objects=[]
        self.players={1:[],-1:[]}
        self.minions={1:[],-1:[]}
        self.hands={1:[],-1:[]}
        self.weapons={1:[],-1:[]}
        self.decks={1:[],-1:[]}
        self.secrets={1:[],-1:[]}
        self.quests={1:[],-1:[]}
        self.enchantments={1:[],-1:[]}
        self.graves={1:[],-1:[]}
        self.spell_graves={1:[],-1:[]}
        self.weapon_graves={1:[],-1:[]}
        self.discards={1:[],-1:[]}
        self.burnouts={1:[],-1:[]}
        self.temps={1:[],-1:[]}
        self.queue=[] #Record the order in which minions come into play
        self.objs=[]
        self.exclude=[] #Objects not displayed
        self.turn_time_limit={1:60,-1:60}
        self.capacity = 7  #max num of minions
        self.control=1
        self.random_select=False
        self.end_turn_button=get_rect(1500,670,200,50)
        self.negative_emote_button=get_rect(1500,770,200,50)
        self.positive_emote_button=get_rect(1500,870,200,50)
        self.music_button=get_rect(1500,50,200,50)
        self.running=True
        self.end_turn=False
        self.music_on=True
        self.buff_factory={}
        self.MOVING_ANIMATION=False #Control performance during moving animation
        self.DEBUG_MODE=False
        
        self.rect=get_rect(0,0,SCREEN_WIDTH,SCREEN_HEIGHT)
        self.image=background

        
    def add_players(self,player1,player2):
        self.players[player1.side]=player1
        self.players[player2.side]=player2
        for player in self.players.values():
            player.board=self                    
            player.opponent=self.players[-player.side]
            self.decks[player.side]=player.deck
            self.hands[player.side]=player.hand
            self.minions[player.side]=player.minions   
            self.secrets[player.side]=player.secrets
            self.quests[player.side]=player.quests
            self.enchantments[player.side]=player.enchantments
            self.graves[player.side]=player.grave
            self.spell_graves[player.side]=player.spell_grave
            self.weapon_graves[player.side]=player.weapon_grave
            self.discards[player.side]=player.discards
            
    def add_hands(self,cards):
        for card in cards:
            self.hands[card.owner.side].append(card)

    def add_hand(self,card):
        self.hands[card.owner.side].append(card)
            
    def add_minion(self,summoned_minion):
        index=0
        for minion in self.minions[summoned_minion.owner.side]:
            if minion.rect.x >= summoned_minion.rect.x:
                break
            index+=1
        self.minions[summoned_minion.owner.side].insert(index,summoned_minion)
        
        '''Remember the previous location for summon animation'''
        x,y=summoned_minion.location
        self.sort_minions(summoned_minion.owner.side)
        summoned_minion.location=x,y
        
    def sort_minions(self,side):
        minions=self.minions[side]
        sort_minions_animation(minions)
    
    def add_deck(self,deck):
        self.decks[deck.owner.side].extend(deck.cards)
     
    def add_secrets(self,secrets):
        self.secrets[secrets.owner.side]=secrets
     
    def get_side(self,player_name):
        if self.players[1].name==player_name:
            return 1
        else:
            return -1
                 
    def get_cards(self,player):
        cards=[]
        if player.board.control==player.side:
            cards = self.minions[player.side]+self.hands[player.side]+self.secrets[player.side]+self.quests[player.side]
        else:
            cards=self.minions[player.side]+self.quests[player.side]
        
        '''Cards being played always show on top layer'''
        for card in cards:
            if card.dragging:
                cards.remove(card)
                cards.append(card)
            
        return cards

    def start_turn_phase(self,player):
        #Turn initialization
        show_turn(player)
        self.start_time=time.perf_counter()
        player.turn+=1
        player.played_cards[player.turn]=[]
        player.minions_died[player.turn]=[]
        
        #Player setup
        player.refresh_status()
        if player.mana<10:
            player.mana+=1
        player.current_mana=player.mana-player.locked_mana
        
        #Minion setup
        for minion in self.minions[player.side]:
            minion.refresh_status()
            
        for card in self.temps[player.side]:
            card.hand_in()
        self.temps[player.side]=[]
        
        #Passive hero power effect if any
        #if player.hero_power.passive and not player.hero_power.disabled() and player.hero_power.trigger_event_type=="start of turn":
        #    player.hero_power.invoke()
         
        self.activate_triggered_effects("start of turn",player)
        
        player.draw()
        self.end_turn=False
        
    def end_turn_phase(self,player):
        self.activate_triggered_effects("end of turn",player)
        if self.get_buff(player)['double end turn']:
            self.activate_triggered_effects("end of turn",player)
        
        #Player setup
        player.restore_status()
        
        #Minion setup
        for minion in player.minions+player.opponent.minions:
            if not minion.has_dormant:
                minion.restore_status()
        
        #Hand setup        
        corrupted_cards=[]
        ephemeral_cards=[]    
        for card in player.hand:
            if card.corrupted:
                corrupted_cards.append(card)
                
            if card.ephemeral:
                ephemeral_cards.append(card)
                
        for card in corrupted_cards:
            card.discard()
            
        for card in ephemeral_cards:
            player.hand.remove(card)

        player.minions_died[player.turn].append("@")
     
    def isFull(self,player):
        num_of_minions = len(self.minions[player.side])
        if num_of_minions>=self.capacity:
            print("The board is full!")
            return True
        else:
            return False
      
    def get_ongoing_effect_pool(self):
        summoning_portals=[]
        pool = []
        for entity in self.queue:
            if entity.name=="Summoning Portal":
                summoning_portals.append(entity)
            else:
                pool.append(entity)
                
        for entity in self.hands[1]+self.hands[-1]:
            if "In-hand effect" in entity.tags:
                pool.append(entity)
        
        for entity in self.enchantments[1]+self.enchantments[-1]:
            pool.append(entity)
                   
        pool.extend([self.players[self.control].hero_power,self.players[-self.control].hero_power])
                
        summoning_portals.extend(pool)
        
        return summoning_portals

    def get_buff(self,target):
        ongoing_effects={'atk':0,'hp':0,'cost':0,'hero power damage':0,'target minion':False,\
                         'can attack':False,'charge':False,'rush':False,'defrozen':False,\
                         'echo':False,'immune':False,'elusive':False,'not replace':False,'stealth':False,\
                         'elusive':False,'windfury':0,'lifesteal':False,'heal reverse':False,\
                         'choose both':False,'shout':False,'disable hero power':False,\
                         'battlecry twice':False,'deathrattle twice':False,'double effect':0,\
                         'double end turn':False,'double damage':False,'cost health':False,\
                         'freeze target':False,'durability immune':False,'Fizzlebang':False,\
                         'time_limit':0,"Crystal Core":False}
        if not self.MOVING_ANIMATION:
            target_pool=self.get_ongoing_effect_pool()
            for entity in target_pool:
                if (entity.board_area=="Board" and not entity.silenced and not entity.has_dormant) or (entity.board_area=="Hand" and "In-hand effect" in entity.tags) or isinstance(entity,Enchantment):
                    if entity.name=="Summoning Portal":
                        entity_buff = entity.ongoing_effect(target,target_pool)
                    else:
                        entity_buff = entity.ongoing_effect(target)
                    for k,v in entity_buff.items():
                        if k not in ongoing_effects:
                            ongoing_effects[k]=v
                        else:
                            if k=="time_limit" and ongoing_effects[k]>0:# Do not stack Nozdormu effects
                                pass
                            else:
                                ongoing_effects[k]+=v
            self.buff_factory[target]=ongoing_effects
        
        if target not in self.buff_factory:
            self.buff_factory[target]=ongoing_effects
            
        return self.buff_factory[target]

    def get_overriding_buff(self,target):
        ongoing_effects={'cost':-1,'usage cap':-1}
        target_pool=self.get_ongoing_effect_pool()
        for entity in target_pool:
            if (entity.board_area=="Board" and not entity.silenced and not entity.has_dormant) or (entity.board_area=="Hand" and "In-hand effect" in entity.tags) or isinstance(entity,Enchantment):
                entity_buff = entity.overriding_ongoing_effect(target)
                for k,v in entity_buff.items():
                    if k=="usage cap" and v>=ongoing_effects["usage cap"]:
                        ongoing_effects[k]=v
                    elif k=="cost":
                        ongoing_effects[k]=v
        return ongoing_effects
        
    '''def activate_triggered_effects(self,trigger_event="",triggering_entity=None,triggering_target=None):
        target_pool=self.queue+self.hands[triggering_entity.side]+self.hands[-triggering_entity.side]+self.weapons[triggering_entity.side]+self.weapons[-triggering_entity.side]
        for target in target_pool:
            if (target.board_area=="Board" or target.board_area=="Hand") and not target.has_dormant: #Still alive
                for trigger in target.trigger_events:
                    if trigger[0]==trigger_event:
                        if triggering_target is None:
                            trigger[1](triggering_entity)
                        else:
                            trigger[1](triggering_entity,triggering_target)'''

    def activate_triggered_effects(self,trigger_event="",triggering_entity=None):
        for target in [self.players[1].hero_power,self.players[-1].hero_power]:
            if not target.disabled() or target.activate_while_disabled:
                for trigger in target.trigger_events:
                    if trigger[0]==trigger_event:
                        trigger[1](triggering_entity)
        
        for target in self.queue+self.enchantments[1]+self.enchantments[-1]:
            if target.board_area=="Board" and not (isinstance(target, Secret) and target.side==self.control and not target.trigger_on_owner_turn): #Still alive
                for trigger in target.trigger_events:
                    if trigger[0]==trigger_event:
                        trigger[1](triggering_entity)

        for target in self.hands[1]+self.hands[-1]:
            if target.board_area=="Hand" and ("In-hand effect" in target.tags or "Upgradable" in target.abilities or "Unidentified" in target.abilities or target.transform_in_hand): 
                if len(target.trigger_events)>0:#Shapeshifting ability takes priority
                    for trigger in target.trigger_events:
                        if trigger[0]==trigger_event:
                            trigger[1](triggering_entity)
                else:
                    if target.trigger_event_type==trigger_event:
                        target.trigger_effect(triggering_entity)
         
        for target in self.decks[1].cards+self.decks[-1].cards:
            if target.board_area=="Deck" and "In-deck effect" in target.tags:
                if len(target.trigger_events)>0:
                    for trigger in target.trigger_events:
                        if trigger[0]==trigger_event:
                            trigger[1](triggering_entity)
                else:
                    if target.trigger_event_type==trigger_event:
                        target.trigger_effect(triggering_entity)
        
        if trigger_event not in ["minion dies","minion damage","add to hand"]:       
            self.resolve_destroy_queue()
                                                      
    def activate_start_of_game_effects(self,trigger_event="",triggering_entity=None):
        target_pool=self.hands[1]+self.hands[-1]+self.decks[1].cards+self.decks[-1].cards
        for target in target_pool:
            target.start_of_game()
                   
                             
    def resolve(self,event):
        player=self.players[self.control]
        source_str,target_str,mouse_pos=event.split(";")
        s_owner,s_area,s_index=source_str.split(":")
        t_owner,t_area,t_index=target_str.split(":")
        mouse_pos=float(mouse_pos.split(":")[0]),SCREEN_HEIGHT-float(mouse_pos.split(":")[1])
        if s_area=="hand" or s_area=="minion":
            if t_owner=="":
                player.play(getattr(self,s_area+"s")[self.get_side(s_owner)][int(s_index)],mouse_pos=mouse_pos)
            else:
                if t_area=="player":
                    player.play(getattr(self,s_area+"s")[self.get_side(s_owner)][int(s_index)],self.players[self.get_side(t_owner)],mouse_pos=mouse_pos)
        
                else:
                    player.play(getattr(self,s_area+"s")[self.get_side(s_owner)][int(s_index)],getattr(self,t_area+"s")[self.get_side(t_owner)][int(t_index)],mouse_pos=mouse_pos)
        elif s_area=="hero_power":
            if t_owner=="":
                player.hero_power.invoke()
            else:
                if t_area=="player":
                    player.hero_power.invoke(self.players[self.get_side(t_owner)])
                else:
                    player.hero_power.invoke(getattr(self,t_area+"s")[self.get_side(t_owner)][int(t_index)])
        elif s_area=="player":
            if t_area=="player":
                player.attack(player.opponent)
            else:
                player.attack(getattr(self,t_area+"s")[self.get_side(t_owner)][int(t_index)])
        elif s_area.isdigit():# When turn end event is triggered
            if len(s_index)>0:
                msg=player.emotes[s_index]
                show_text(msg, location=player.location,flip=True, pause=0.5)
            self.end_turn=True

            
    def resolve_choose(self,event,targets,chooser=None):
        player=self.players[self.control]
        source_str,target_str,mouse_pos=event.split(";")
        s_owner,s_area,s_index=source_str.split(":")
        t_owner,t_area,t_index=target_str.split(":")
        
        for target in targets:
                target.selected=False
                
        if t_area=="":
            if t_index=="": # No target chosen
                if chooser.isMinion():
                    chooser.return_hand(reset=False)
                return None
            else:           # Choose a card
                return targets[int(t_index)]
        else: # Choose from board
            target = getattr(self,t_area+"s")[self.get_side(t_owner)][int(t_index)]
            return target

     
    def mulligan(self,player):
        num_cards={True:4,False:3}[self.control==-1]
     
        #Deal initial options
        initial_cards = random.sample(player.deck.cards,k=num_cards)
        for card in initial_cards:
            player.deck.cards.remove(card)
            card.image=card.big_image
            
        #Ask player to choose mulligan cards
        mulligan_cards,remaining_cards=choose_mulligan_cards(initial_cards)
        for card in remaining_cards:
            player.add_hand(card)
        
        #Redraw mulliganned cards
        player.deck.cards.extend(mulligan_cards)
        redrawn_cards = random.sample(player.deck.cards,k=len(mulligan_cards))
        for card in redrawn_cards:
            player.deck.cards.remove(card)
            card.image=card.big_image

        #Animations
        if len(mulligan_cards)>0:
            '''prepare the positions for redrawn cards'''
            original_locations=[]
            for card in mulligan_cards:
                original_locations.append((card.rect.x,card.rect.y-50))
                
            move_multiple_animation(mulligan_cards,dests=[player.deck.location]*len(mulligan_cards),speed=20) 
            move_multiple_animation(redrawn_cards,dests=original_locations,speed=20)
            for card in mulligan_cards:
                card.image=card.mini_image
        
        for card in redrawn_cards :
            player.add_hand(card)
        
        if not self.DEBUG_MODE:
            database.update_player_starting_cards(player)
            database.synchronize_opponent_starting_cards(player.opponent)
        sort_hand_animation(player.opponent)
        
            
        for card in player.hand:
            card.image=card.mini_image
        move_multiple_animation(player.hand, dests=[(720,820)]*len(player.hand), speed=50, zoom=False)
      
        if self.control==-1:
            player.get_coin()
        else:
            player.opponent.get_coin()
            
    def start_game(self):
        self.start_time=time.perf_counter()
        player=self.players[self.control]
        self.activate_start_of_game_effects()
        self.start_turn_phase(player)
        
    '''def resolve_destroy_queue(self):
        ANY_DESTROYED=False
        for minion in self.minions[1]+self.minions[-1]:
            if minion.get_current_hp()<=0:
                minion.trigger_destroy()
                ANY_DESTROYED=True
        if ANY_DESTROYED: # Repeat until no minions are destroyed
            self.resolve_destroy_queue()'''
            
    def resolve_destroy_queue(self):
        for minion in self.minions[1]+self.minions[-1]:
            if minion.get_current_hp()<=0:
                minion.trigger_destroy()
