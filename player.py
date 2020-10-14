'''
Created on Apr 2, 2020

@author: shan.jiang
'''
import random,importlib,time,database
from card import Enchantment,Demon_Claws,Shapeshift,Fireblast,Lesser_Heal,Life_Tap,Dagger_Mastery,Armor_Up,Reinforce,Totemic_Call,Steady_Shot,\
                Embrace_the_Shadow_Effect
from GUIHandler import SCREEN_HEIGHT,SCREEN_WIDTH,get_image,get_rect,show_text,draw_animation,incur_damage_animation,sort_hand_animation,\
    summon_animation,destroy_hero_animation,show_victory,attack_animation,shield_animation,heal_animation,equip_weapon_animation,get_player,\
    trigger_lifesteal_animation,lifesteal_animation,move_animation, trigger_effect_animation,attack_adjacent_animation,discard_multiple_animation,\
    buff_hand_animation,swap_deck_animation
from GUIHandler import mana_crystal_image,shield_image,lock_image,hero_freeze_image,hero_immune_image,hero_elusive_image,hero_stealth_image,sort_triggerables_animation
card_collection = importlib.import_module("card")

class Deck:
    def __init__(self,owner="",cards=list()):
        self.owner=owner
        self.cards=cards
        self.initialize_position()
        self.image=get_image("images/secret.png",(170,50))
    
    def initialize_position(self):
        offset={1:0,-1:-235}[self.owner.side]
        #Initialize card on deck position
        self.rect=get_rect(SCREEN_WIDTH-210, SCREEN_HEIGHT/2+offset, 170, 50)
        self.location=self.rect.x,self.rect.y
    
    def top(self):
        if len(self.cards)>0:
            return self.cards.pop(0)
        else:
            card=getattr(card_collection,"Fatigue")(owner=self.owner)
            return card
    
    def add_card(self,card,owner=None,randomize=True):
        if owner is None:
            card.owner=self.owner
            card.side=card.owner.side
        if randomize:
            k=random.randint(0,len(self.cards))
            self.cards.insert(k,card)
        else:
            self.cards.append(card)

        card.board_area="Deck"
        card.rect=get_rect(card.owner.deck.location[0], card.owner.deck.location[1], card.image.get_width(), card.image.get_height())
        card.location=card.owner.deck.location
      
    def shuffle(self):
        random.shuffle(self.cards)
        
    def has_odd_cards_only(self):
        flag=True
        for card in self.cards:
            if card.current_cost%2==0:
                flag=False
                
        return flag
    
    def has_even_cards_only(self):
        flag=True
        for card in self.cards:
            if card.current_cost%2==1:
                flag=False
                
        return flag
     
    def has_no_duplicates(self):
        return len(set([card.name for card in self.cards]))==len(self.cards)
    
    def has_no_minions(self):
        for card in self.cards:
            if card.isMinion():
                return False
        return True
        
    def has_no_cost(self,cost):
        for card in self.cards:
            if card.cost==cost:
                return False
        return True

            
                     
class Hero:
    def __init__(self,player_name="Player",hero_name="",class_name="",side=1,hp=30):
        self.player_name       = player_name
        self.hero_name         = hero_name
        self.name              = player_name
        self.class_name        = class_name
        self.side              = side
        self.image             = get_image("images/hero_images/"+self.hero_name+".png",(170,236))
        self.big_image         = get_image("images/hero_images/"+self.hero_name+".png",(265,367))
        self.shadow_image    = get_image("images/hero_images/shadow_image.png",(170,236))
        self.big_card_back_image= get_image("images/hero_images/Card_back-Classic.png",(265,367))
        self.raw_card_back_image= get_image("images/hero_images/Card_back-Classic.png",(170,236))
        self.mini_card_back_image= get_image("images/hero_images/Card_back-Classic.png",(103,141))
        self.board             = None
        self.mana              = 0
        self.current_mana      = 0
        self.overloaded_mana   = 0
        self.total_overloaded_mana   = 0
        self.locked_mana       = 0
        self.crystal           = mana_crystal_image
        self.lock              = lock_image
        self.shield_image      = shield_image
        self.freeze_image      = hero_freeze_image
        self.stealth_image     = hero_stealth_image
        self.immune_image      = hero_immune_image
        self.elusive_image     = hero_elusive_image
        self.atk               = 0
        self.current_atk       = self.atk
        self.hp                = hp
        self.temp_hp           = hp
        self.current_hp        = self.hp
        self.shield            = 0
        self.weapon            = None
        self.current_card      = None
        self.frozen_timer      = 0
        self.hero_power_count  = 0
        self.turn              = 0
        self.played_cards      = {0:[]}
        self.minions_died      = {0:[]}
        self.play_logs         = {}
        self.summoned_minions  = {}
        self.hand              = []
        self.minions           = []
        self.secrets           = []
        self.quests            = []
        self.enchantments      = []
        self.grave             = []
        self.spell_grave       = []
        self.weapon_grave      = []
        self.discards          = []
        self.on_hit_effects    = []
        self.temporary_effects = {"immune":False,"stealth":False,"elusive":False}
        self.remaining_time    = 60
        self.hand_limit        = 10
        self.board_area        = "Board"
        self.overdraw          = 0
        self.dragging          = False
        self.mouse_pos         = (0,0)
        self.mouse_move_length = 0
        self.selected          = False
        self.isSpell           = False
        self.attacked          = False
        self.remaining_attack  = 1
        self.healed            = False
        self.has_taunt         = False
        self.has_elusive       = False
        self.has_stealth       = False
        self.has_poisonous     = False
        self.frozen            = False
        self.has_immune        = False
        self.modified_damage   = -1
        self.destroyed_by      = None
        self.take_extra_turn   = 0
        self.total_discards    = 0
        self.jade_counter      = 1
        self.deck              = Deck(owner=self,cards=[])
        self.initial_deck      = []
        self.vsAI              = False
        self.emotes            = {"Curse":"Fxxk You!","Well Played":"Well Played"}
        self.initialize_position()
        self.initialize_play_logs()
      
    def initialize_position(self):
        y={-1:100,1:650}[self.side]
        self.rect=get_rect(SCREEN_WIDTH/2-self.image.get_width()/2,y, self.image.get_width(), self.image.get_height())
        self.deck.rect=get_rect(SCREEN_WIDTH-200,SCREEN_HEIGHT/2+self.side*120-60,180,120)
        self.location=self.rect.x,self.rect.y
 
    def initialize_play_logs(self):
        self.play_logs["Health Restored"]=[]
        self.play_logs["Spells Cast"]=[]
        self.play_logs["Spells Cast on Minions"]=[]
        self.play_logs["Cards Drawn"]=[]
        self.play_logs["Minions Summoned"]=[]
        self.play_logs["Cards Discarded"]=[]
        self.play_logs["Turns Ended with Unspent Mana"]=[]
        self.play_logs["Other Class Cards Added"]=[]
        self.play_logs["Battlecry Cards Played"]=[]
        self.play_logs["Reborn Minions Played"]=[]
        self.play_logs["Taunt Minions Played"]=[]
        self.play_logs["Deathrattle Minions Summoned"]=[]
        self.play_logs["Murlocs Summoned"]=[]
        self.play_logs["1-Cost Minions Summoned"]=[]
        self.play_logs["2-Cost Minions Summoned"]=[]
        self.play_logs["3-Cost Minions Summoned"]=[]
        self.play_logs["4-Cost Minions Summoned"]=[]
        self.play_logs["5-Cost Minions Summoned"]=[]
        self.play_logs["6-Cost Minions Summoned"]=[]
        self.play_logs["7-Cost Minions Summoned"]=[]
        self.play_logs["8-Cost Minions Summoned"]=[]
        self.play_logs["9-Cost Minions Summoned"]=[]
        self.play_logs["10+Cost Minions Summoned"]=[]
        self.play_logs["Attacked with Hero"]=[]
        
    def restore_status(self):
        self.current_atk = self.atk
        #self.current_hp  = self.temp_hp
        
        for attribute in self.temporary_effects:
            self.temporary_effects[attribute]=False
        if self.has_weapon():
            self.weapon.temporary_effects[attribute]=False
            
        print("Total mouse movement this turn: "+str(self.mouse_move_length))
        self.mouse_move_length=0
        
    def refresh_status(self):
        if self.has_weapon():
            self.weapon.current_atk=self.weapon.temp_atk
        if self.hero_power.disabled():
            self.hero_power.refresh()
        self.attacked=False
        self.remaining_attack=1
        self.healed=False
        
        
        self.locked_mana=self.overloaded_mana
        self.overloaded_mana=0
        
        if self.frozen_timer>0:
            self.frozen_timer-=1
            if self.frozen_timer==0:
                self.frozen=False
        
    def get_coin(self):
        coin = getattr(card_collection,"The_Coin")(owner=self)
        coin.appear_in_hand()
       
    def draw(self,num=1,target=None):
        for i in range(num):
            if target and target in self.deck.cards:
                card=target
                self.deck.cards.remove(target)
            else:
                card=self.deck.top()
                
            if not card.isFatigue():
                if card.casts_when_drawn:
                    card.on_drawn()
                elif len(self.hand)<self.hand_limit:
                    self.add_hand(card)
                    self.board.activate_triggered_effects("draw a card",card)

                    if card.board_area=="Hand":
                        card.image=card.mini_image
                        draw_animation(self,card)
                        sort_hand_animation(self)
                        
                        #Trigger on add to hand effect if any
                        #self.board.activate_triggered_effects('add to hand',card)

     
                else:
                    card.burn()
            else:
                card.perish()
                
            # Terminate game if a player is destroyed
            if not self.board.running:
                break
        
        
        return card
    
    def add_hand(self,card):
        self.hand.append(card)
        card.board_area="Hand"
            
    def play(self,card,target=None,mouse_pos=None):
        if len(self.played_cards[self.turn])==0:#Refresh timer for past idled turn
            self.board.turn_time_limit[self.side]=60
        INVALID_PLAY=False
        
        if mouse_pos is not None:
            card.rect.x,card.rect.y=mouse_pos
        if card.outcasted():
            card.trigger_outcast=True
                
        if card.board_area=="Hand":
            #mana_management
            mana_table=card.recrue_cost()
            
            #summon a minion
            if card.card_type=="Minion" and card.landed_board_area()=="Board":
                #if card.copy_target is not None:
                    #self.hand.remove(card) 
                    #card=card.copy_target
                result=self.summon(card)
                if result!="Success":
                    INVALID_PLAY=True

            elif card.card_type=="Spell":
                if card.is_valid_on(target) and not ("Targeted" in card.tags and target is not None and not target.is_targetable()):
                        card.target=target 
                            
                        #Trigger secret (Counterspell, Spellbender) if any
                        self.board.exclude.append(card)
                        self.board.activate_triggered_effects("cast a spell",card)
                        self.board.exclude.remove(card)
                            
                        if card.board_area=="Hand": # Spell still not invoked due to secrets
                            if self.board.get_buff(card)['cost health']:
                                self.incur_damage(max(card.get_current_cost(),0))
                            if "Choose One" in card.abilities and self.board.get_buff(card)["choose both"]:
                                card.trigger_choose_both()
                            else:
                                card.invoke(target)
                            
                        if card.board_area=="Hand": # Spell not invoked due to failed choose one
                            INVALID_PLAY=True
                else:
                    INVALID_PLAY=True
                    
            elif card.card_type=="Weapon":
                if card.is_valid_on(target):
                    card.trigger_battlecry(target)
                    self.equip_weapon(card,target)
                    
                else:
                    INVALID_PLAY=True
            elif card.card_type=="Hero card" and card.landed_board_area()=="Board":
                card.replace_hero()
            else:
                INVALID_PLAY=True
               
            self.board.resolve_destroy_queue()
             
            if INVALID_PLAY:
                card.rect.x,card.rect.y=card.location
                card.trigger_outcast=False
                self.reverse_mana(mana_table)
            else:
                #Trigger outcast if any
                if card.trigger_outcast:
                    card.outcast() 
                
                #Trigger play card effect if any
                self.board.activate_triggered_effects('play a card',card)
                
                #Trigger quest if any
                self.trigger_quests('play a card',card)
                                      
                if card.Echo or card.owner.board.get_buff(card)['echo']:
                    card.echo()
                    
                elif card.Twinspell:
                    card.twinspell()

                self.played_cards[self.turn].append(card)
        
            sort_hand_animation(self)
                
        elif card.board_area=="Board":
            
            '''Attacking Opponent minion'''
            if target is not None and target.side==self.opponent.side:
                if target.is_attackable_by(card):
                    if not card.summoning_sickness:
                        card.attack(target)
                    elif card.has_charge or card.owner.board.get_buff(card)['charge']:
                        if target.isHero() and card.temporary_effects["cannot attack hero"]:
                            show_text("The minion cannot attack hero!", flip=True, pause=0.6)
                        else:
                            card.attack(target)
                    elif card.has_rush or card.owner.board.get_buff(card)['rush']:
                        if not target.isHero():
                            card.attack(target)
                        else:
                            show_text("Rush minion cannot attack hero!", flip=True, pause=0.6)
                    else:
                        show_text("Give minion a turn to get ready!", flip=True, pause=0.6)
            self.board.sort_minions(self.side)    
         
        return INVALID_PLAY
           
    def discard(self,num=1):
        if len(self.hand)>0:
            cards=random.sample(self.hand,k=min(num,len(self.hand)))
            for card in cards:
                card.discard() 
                
    def discard_hand(self):
        discard_multiple_animation(self.hand)
        for i in range(len(self.hand)):
            self.hand[0].discard(skip_animation=True)
                        
    def user_hero_power(self):
        pass         
    
    def damaged(self):
        return self.current_hp<self.hp
    
    def summon(self,minion):
        if not self.board.isFull(self):

            #Prepare the destination of summoned minion
            minion.owner.board.add_minion(minion)
            minion.board_area="Board"
            if minion in minion.owner.hand:
                minion.owner.hand.remove(minion) 

            #Summoning animation
            summon_animation(minion)
            if minion.has_special_summon_effect:
                minion.special_summoning_effect()
            
            index=self.board.minions[self.side].index(minion)
            if hasattr(minion, "trigger_choose_one"):
                if self.board.get_buff(minion)['choose both']:
                    minion.trigger_choose_both()
                else:
                    minion.trigger_choose_one()

            if len(self.played_cards[self.turn])>0:
                minion.combo()
            
            if "Targeted" in minion.tags and not "Choose One" in minion.abilities and not "Combo" in minion.abilities:
                target=minion.get_target()
                if target is not None:
                    minion.come_on_board()
                    if target!="Empty": #No available targets
                        minion.trigger_battlecry(target)
            else:
                minion.come_on_board()         
                minion.trigger_battlecry()
                
            if minion.transformed:#Some minions transform during battlecry or choose one
                minion=self.board.minions[self.side][index]
                       
            if minion.board_area=="Board" : # If the minion summon is not cancelled due to battlecry
                #Trigger magnetic effects if any
                if minion.magnetic and minion.magnetizable():
                    minion.magnetize()
                
                if minion.board_area=="Board": # If the minion summoned is still alive and on battlefield
                    minion.summoning_sickness=True
                    #Trigger on summon effect if any
                    self.board.activate_triggered_effects('summon from hand',minion)
                    if minion.transformed:
                        minion=self.minions[index] # original minion may transform due to potion of polymorph

                    self.board.activate_triggered_effects('summon a minion',minion)
                    
                    #Trigger quest if any
                    self.trigger_quests('summon a minion',minion)


                return "Success"  
        else:
            minion.rect.x,minion.rect.y=minion.location
            show_text("The board is full!",flip=True,pause=1) 
            
    def recruit(self,minion,speed=30):# minion in deck or generated from spell or hero power
        if not self.board.isFull(self):
            
            #Prepare the destination of summoned minion
            minion.owner.board.add_minion(minion)
            minion.board_area="Board"
            if minion in minion.owner.hand:
                minion.owner.hand.remove(minion)
            if minion in minion.owner.deck.cards:
                minion.owner.deck.cards.remove(minion)
            summon_animation(minion,skip_zoom=True,speed=speed)
            minion.come_on_board()
            
            #Trigger on summon effect if any
            self.board.activate_triggered_effects('summon a minion',minion)
            
            #Trigger quest if any
            self.trigger_quests('summon a minion',minion)
        else:
            minion.rect.x,minion.rect.y=minion.location
     
    def put_into_battlefield(self,minion,location="board"):
        if not self.board.isFull(self) and minion in self.hand:
            old_location=minion.location
            minion.initialize_location(location)
            minion.location=old_location
            
            #Prepare the destination of summoned minion
            self.board.add_minion(minion)
            minion.board_area="Board"
            if minion in minion.owner.hand:
                minion.owner.hand.remove(minion)   
            summon_animation(minion,skip_zoom=True)

            minion.come_on_board()
            
            #Trigger on summon effect if any
            self.board.activate_triggered_effects('summon a minion',minion)
            
            #Trigger quest if any
            self.trigger_quests('summon a minion',minion)
     
    def all_minions(self,race=None):
        targets=[]
        for target in self.board.queue:
            if target.isMinion() and (race is None or target.has_race(race)):
                targets.append(target)
        return targets
    
    def all_characters(self,race=None):
        targets=[]
        for target in self.board.queue:
            if target.isMinion() and (race is None or target.has_race(race)):
                targets.append(target)
        return targets+[self,self.opponent]
    
    def enemy_minions(self,race=None):
        targets=[]
        for target in self.board.queue:
            if target.side==-self.side and target.isMinion() and (race is None or target.has_race(race)): 
                targets.append(target)
        return targets
    
    def enemy_characters(self,race=None):
        targets=[]
        for target in self.board.queue:
            if target.side==-self.side and target.isMinion() and (race is None or target.has_race(race)):
                targets.append(target)
        return targets+[self.opponent]  
    
    def friendly_characters(self,race=None):
        targets=[]
        for target in self.board.queue:
            if target.side==self.side and target.isMinion() and (race is None or target.has_race(race)):
                targets.append(target)
        return targets+[self]    
    
    def friendly_minions(self,race=None):
        targets=[]
        for target in self.board.queue:
            if target.side==self.side and target.isMinion() and (race is None or target.has_race(race)):
                targets.append(target)
        return targets  

    def all_minions_except(self,race):
        targets=[]
        for target in self.board.queue:
            if target.isMinion() and not target.has_race(race):
                targets.append(target)
        return targets
    
    def friendly_minions_except(self,race):
        targets=[]
        for target in self.board.queue:
            if target.side==self.side and target.isMinion() and not target.has_race(race):
                targets.append(target)
        return targets    
    
    def enemy_minions_except(self,race):
        targets=[]
        for target in self.board.queue:
            if target.side==-self.side and target.isMinion() and not target.has_race(race):
                targets.append(target)
        return targets
         
    def can_attack(self):
        return self.current_hp>0 and self.get_current_atk()>0 and self.has_remaining_attack() and not (self.frozen and not self.board.get_buff(self)['defrozen'])
    
    def has_remaining_attack(self):
        lb=0
        if self.has_weapon() and self.weapon.has_windfury:
            lb=-1
            
        return self.remaining_attack>lb
                          
    def attack(self,target):
        self.target=target         
        #Trigger attack effect if any
        self.board.activate_triggered_effects("attack",self)
        
        if self.can_attack() and self.target.board_area=="Board":
            #Disable stealth
            self.has_stealth=False

            attack_animation(self,self.target)
            self.attacked=True
            self.remaining_attack-=1
            
            target_current_atk    = self.target.get_current_atk() # Record the value in case target dies
            target_on_hit_effects = self.target.on_hit_effects
            
            if self.has_weapon():
                damage_source=self.weapon
                on_hits=self.weapon.on_hit_effects
            else:
                damage_source=self
                on_hits=self.on_hit_effects
                

            
            self.target.incur_damage(self.get_current_atk(),on_hits,damage_source=damage_source)
            #Trigger after attack effect if any
            self.board.activate_triggered_effects("during attack",self)
            
            if target_current_atk>0 and not self.target.isHero():
                self.target.deal_damage([self],[target_current_atk],on_hit_effects=target_on_hit_effects)
                #self.incur_damage(target_current_atk,target_on_hit_effects,damage_source=self.target)
            
            #Trigger after attack effect if any
            self.board.activate_triggered_effects("after attack",self)
            
            if self.has_weapon():    
                self.weapon.trigger_after_effect(self.target)
    
    def attack_adjacent_minions(self,target):
        minions=target.adjacent_minions()
        attack_adjacent_animation(self,target)
        self.weapon.deal_damage(minions, [self.get_current_atk()]*len(minions))
        
    def attack_wrong_enemy(self,chance=0.5):
        original_target=self.target
        target_pool=self.enemy_characters()
        if original_target in target_pool:
            target_pool.remove(original_target)
        if random.uniform(0,1)<chance and len(target_pool)>0:
            if self.has_weapon():
                trigger_effect_animation(self.weapon,self)
            new_target=random.choice(target_pool)
            self.target=new_target            
             
    def get_current_atk(self):
        atk_value=self.current_atk+self.board.get_buff(self)['atk']
        if self.has_weapon():
            atk_value+=self.weapon.get_current_atk()
            
        return atk_value
    
    def get_current_hp(self):
        return self.current_hp
            
    def incur_damage(self,amount,on_hit_effects=[],damage_source=None,skip_animation=False):
        if self.is_immunized() or self.current_hp<-128:
            pass
        else:
            if self.board.get_buff(self)['double damage']:
                amount*=2
                
            if not skip_animation:
                incur_damage_animation(self,amount)
            
            self.board.activate_triggered_effects("modify damage",(damage_source,amount,self))
            
  
            if self.modified_damage!=0: # Ice Block not activated,Ramshield not activated
                if self.modified_damage>0:
                    amount=self.modified_damage
                if (damage_source is not None and damage_source.isCard()) and damage_source.has_keyword("lifesteal"):
                    trigger_lifesteal_animation(damage_source)
                    lifesteal_animation(damage_source.owner)
                    damage_source.heal([damage_source.owner],[amount])
                    
                resulting_hp=self.current_hp+self.shield-amount
                if resulting_hp<=self.current_hp:
                    self.shield=0
                    self.current_hp=resulting_hp
                else:
                    self.shield-=amount
                
                if amount>0:
                    self.board.activate_triggered_effects("hero damage",(damage_source,amount))
                    
                #Destroy Logic
                resulting_hp=self.current_hp
                if resulting_hp<=0:
                    if damage_source.isCard() and resulting_hp<0:
                        damage_source.overkill(self)
                    self.destroyed_by=damage_source
                    self.destroy()

                    
                for on_hit in on_hit_effects:
                    if self.current_hp>0:
                        on_hit(self)
            
            else:
                self.modified_damage=-1
                
    def restore_health(self,amount,heal_source=None,skip_animation=False):  
        previous_hp     = self.current_hp
        self.current_hp+= amount

        if self.current_hp>self.hp:
            self.current_hp=self.hp
            
        if not skip_animation:
            heal_animation(self,self.current_hp-previous_hp)
        
        #Trigger restore health effect if any
        healing_amount=self.current_hp-previous_hp
        if healing_amount>0:
            self.board.activate_triggered_effects("character healed",(self,healing_amount,heal_source))
            self.healed=True
                
        get_player(heal_source).trigger_quests("restore health",self.current_hp-previous_hp)
        #self.play_logs["Health Restored"].append(self.current_hp-previous_hp)
    
    def increase_shield(self,amount):
        self.shield+=amount
        shield_animation(self)
        
        self.board.activate_triggered_effects('gain armor',(self,amount))
    
    def gain_mana(self,quantity=1,empty=False):
        self.mana+=quantity
        if self.mana>10:
            self.mana=10
        elif self.mana<0:
            self.mana=0
            
        if not empty:
            self.current_mana+=quantity
            if self.current_mana>self.mana:
                self.current_mana=self.mana

    def reverse_mana(self,mana_table):
        self.current_mana+=mana_table['mana_spent']
        self.overloaded_mana-=mana_table['mana_overloaded']
     
    def gain_hero_power(self,hero_power):
        self.hero_power=hero_power
        self.hero_power.trigger_events=[[self.hero_power.trigger_event_type,self.hero_power.trigger_effect]]
        self.hero_power.refresh()
        
    def take_control(self,target):
        if target.side==-self.side:
            if self.board.isFull(self):
                target.destroy()
            else:
                old_location=target.location
                target.owner.minions.remove(target)
                self.minions.append(target)
                target.owner=self
                target.side=self.side
                target.summoning_sickness=True
                self.board.sort_minions(self.side)
                self.board.sort_minions(self.opponent.side)
                
                target.location=old_location
                move_animation(target,dest=(target.rect.x,target.rect.y),speed=20,zoom=False)
    
    def take_control_secret(self,secret):
        if secret in self.opponent.secrets:
            self.opponent.secrets.remove(secret)
            secret.owner=self
            secret.side=self.side
            self.secrets.append(secret)
            sort_triggerables_animation(self.secrets+self.quests)
            sort_triggerables_animation(self.opponent.secrets+self.opponent.quests)
            
            
    def control(self,minion_type):
        for minion in self.friendly_minions():
            if minion.has_race(minion_type):
                return True
        return False
    
    def control_all(self,minions):
        for minion in minions:
            if minion not in [minion.__class__ for minion in self.friendly_minions()]:
                return False
        return True
         
    def holding(self,minion_type):
        for card in self.hand:
            if card.has_race(minion_type):
                return True
        return False
    
    def played_before(self,minion_type,turn=-1):
        if self.turn<=1:
            return False
        else:
            for card in self.played_cards[self.turn+turn]:
                if card.has_race(minion_type):
                    return True
            return False
     
    def has_spell_damage(self):
        spell_damage=False
        minions=self.friendly_minions()
        for minion in minions:
            if minion.spell_damage_boost>0:
                spell_damage=True
                
        return spell_damage
                 
    def empty_handed(self):
        count=0
        for card in self.hand:
            if not isinstance(card, Enchantment):
                count+=1
        
        return count==0
    
    def buff_hand(self,card_type="Minion",atk=1,hp=1,multiple=False):
        targets=[]
        if multiple:
            for card in self.hand:
                if (card_type=="Minion" and card.isMinion()) or card.has_race(card_type):
                    card.buff_stats(atk,hp)
                    targets.append(card)
            buff_hand_animation(self, targets)
        else:                
            minion=self.search_card(self.hand,card_type=card_type)
            if minion is not None:
                minion.buff_stats(atk,hp)
                buff_hand_animation(self, [minion])
                                     
    def has_weapon(self):
        return self.weapon is not None
    
    def equip_weapon(self,weapon,target=None):
        #Animation
        equip_weapon_animation(self,weapon)
        
        '''Replace Existing Weapon'''
        if self.has_weapon():
            self.weapon.destroy()

        self.weapon=weapon
        
        'Weapon Registry'
        self.board.weapons[self.side].append(weapon)
        self.board.queue.append(weapon)
        weapon.board_area="Board"
        if weapon in self.hand:
            self.hand.remove(weapon)
            
        '''Register Weapon effects'''    
        if "Deathrattle" in self.weapon.abilities:
            self.weapon.deathrattles.append([self.weapon.deathrattle,self.weapon.deathrattle_msg])
            self.weapon.has_deathrattle=True
        
        if "Triggered effect" in self.weapon.tags or len(self.weapon.trigger_event_type)>0:
            self.weapon.trigger_events.append([self.weapon.trigger_event_type,self.weapon.trigger_effect])
            self.weapon.has_trigger=True
        
        weapon.on_hit_effects.append(weapon.on_hit_effect)    
        self.on_hit_effects.append(weapon.on_hit_effect)
                
        if weapon.lifesteal:
            weapon.has_lifesteal=True
            
        if weapon.poisonous:
            weapon.gain_poisonous()
            
        if weapon.windfury:
            weapon.gain_windfury()
     
        weapon.transform_in_hand="Transform in hand" in self.weapon.abilities
        
        #Trigger equip weapon effect if any
        self.board.activate_triggered_effects("equip weapon",weapon)
    
    def has_keyword(self,keyword):
        try:
            result=getattr(self,"has_"+keyword)
        except:
            result=False
        
        return result or self.board.get_buff(self)[keyword] or self.temporary_effects[keyword]
    
           
    def is_attackable_by(self,attacker): 
        if attacker.isHero():
            if attacker.has_weapon() and attacker.weapon.cannot_attack_hero:
                return False
            else:
                return True
        else:
            return not self.is_taunted() and not self.is_stealthed() and not attacker.cannot_attack_hero
    
    def is_targetable(self):
        return not self.has_keyword("elusive") and not self.has_keyword("stealth")
    
    def is_stealthed(self):
        return self.has_keyword("stealth")
    
    def is_taunted(self):
        if self.has_taunt:
            return False
        
        minions=self.friendly_minions()
        for minion in minions:
            if minion.has_taunt and not minion.has_stealth:
                print("A Taunt Minion is in the way!")
                #show_text("A Taunt Minion is in the way!", flip=True,pause=1)
                return True
        return False
    
    def is_immunized(self):
        return self.has_immune or self.temporary_effects["immune"] or self.board.get_buff(self)['immune'] 
    
    def is_under_shadow_mode(self):
        result=False
        if self.hero_power.name in ["Mind Spike","Mind Shatter"]:
            result=True
        for enchantment in self.enchantments:
            if isinstance(enchantment, Embrace_the_Shadow_Effect):
                result=True
                
        return result
    
    def has_minion_in_hand(self):
        for card in self.hand:
            if card.isMinion():
                return True
        return False
            
    def get_frozen(self,timer=2):
        self.frozen=True
        self.frozen_timer=timer
        if self.board.control==self.side and self.attacked==False:
            self.frozen_timer-=1
              
    def destroy(self):
        destroy_hero_animation(self)
        self.board_area="Grave"
        show_victory(self.opponent)
        if self.side==-1 and self.board.sessionID!="00000" and not self.opponent.vsAI:
            database.update_winner(self.opponent)
        self.board.running=False  
    
    def trigger_secrets(self,condition,trigger_source=None):
        secret_copies=[secret for secret in self.secrets]
            
        for secret in secret_copies:
            if self.board.control==self.opponent.side and secret.secret_type==condition:
                secret.trigger(trigger_source)
    
    def trigger_quests(self,condition,trigger_source=None):
        quest_copies=[]
        for quest in self.quests:
            quest_copies.append(quest)
            
        for quest in quest_copies:
            if quest.quest_type==condition:
                quest.trigger(trigger_source)
                
        if condition=="summon a minion":
            if trigger_source.race not in self.summoned_minions:
                self.summoned_minions[trigger_source.race]=[trigger_source]
            else:
                self.summoned_minions[trigger_source.race].append(trigger_source)
                
    def search_card(self,cards,card_type="Minion",k=1):
        pool=[]
        
        for card in cards:
            if card.card_type==card_type or card.has_race(card_type) or card.card_class.find(card_type)!=-1:
                pool.append(card)
        if len(pool)>0:
            if k==1:
                return random.choice(pool)
            else:
                return random.sample(pool,k=min(k,len(pool)))
        else:
            return None
    
    def search_card_based_cost(self,cards,card_type="Minion",cost=0,compare="__eq__",k=1):
        pool=[]
        
        for card in cards:
            if card.card_type==card_type and getattr(card.cost,compare,cost):
                pool.append(card)
        if len(pool)>0:
            if k==1:
                return random.choice(pool)
            else:
                return random.sample(pool,k=min(k,len(pool)))
        else:
            return None
    
    def search_card_based_keyword(self,cards,card_type=None,keyword="taunt",k=1):
        pool=[]
        
        for card in cards:
            try:
                if (card_type is None or card.card_type==card_type) and getattr(card,keyword):
                    pool.append(card)
            except:
                pass      
        if len(pool)>0:
            if k==1:
                return random.choice(pool)
            else:
                return random.sample(pool,k=min(k,len(pool)))
        else:
            return None   
         
    def get_num_minions_died(self,turn=None):
        if turn is None:
            turn=self.turn
        
        self_deaths=self.minions_died[self.turn]
        opponent_deaths = self.opponent.minions_died[self.opponent.turn]
        n1=len(self_deaths)
        n2=len(opponent_deaths)
        if "@" in self_deaths:
            n1=len(self_deaths[self_deaths.index("@")+1:])
        if "@" in opponent_deaths:
            n2=len(opponent_deaths[opponent_deaths.index("@")+1:]) 
            
        return n1+n2
        
    def swap_deck(self):
        swap_deck_animation(self)
        new_deck_1=[]
        new_deck_2=[]
        for card in self.deck.cards:
            card.owner=self.opponent
            new_deck_1.append(card)
            
        for card in self.opponent.deck.cards:
            card.owner=self
            new_deck_2.append(card)
                
        self.deck.cards,self.opponent.deck.cards=new_deck_2,new_deck_1
        
                  
    def get_area(self):
        return "player"
    
    def get_index(self):
        return 0
      
    def isCard(self):
        return False
    
    def isHero(self):
        return True
        
    def isMinion(self):
        return False

    def isWeapon(self):
        return False
    
    def isHero_Power(self):
        return False
    
    def negative_emote(self):
        msg=self.emotes["Curse"]
        show_text(msg, location=self.location,flip=True, pause=0.5)
        
    def positive_emote(self):
        msg=self.emotes["Well Played"]
        show_text(msg, location=self.location,flip=True, pause=0.5)
      
    def AIlogic(self):
        for card in self.hand:
            if card.get_current_cost()<=self.current_mana:
                AI_position=(500,400)
                card.rect.x,card.rect.y=AI_position
                card_target=None
                if card.isSpell and "Targeted" in card.tags:
                    target_pool=[]
                    for target in self.all_characters():
                        if target is not card and card.is_valid_on(target):
                            target_pool.append(target)
                    if len(target_pool)>0:
                        card_target=random.choice(target_pool)
                INVALID_PLAY=self.play(card, card_target, AI_position)
                if INVALID_PLAY:
                    card.rect.x,card.rect.y=card.location
        self.board.end_turn=True
                                           
class Druid(Hero):
    def __init__(self,player_name="Player",hero_name="Malfurion",side=1,hp=30):
        super(self.__class__,self).__init__(player_name,hero_name,"Druid",side,hp)
        self.hero_power=Shapeshift(owner=self)
        self.emotes={"Curse":"The nature will raise against you!","Well Played":"Well Played"}
        
class Warrior(Hero):
    def __init__(self,player_name="Player",hero_name="Garrosh",side=1,hp=30):
        super(self.__class__,self).__init__(player_name,hero_name,"Warrior",side,hp)
        self.hero_power=Armor_Up(owner=self)
        self.emotes={"Curse":"I will crush you!","Well Played":"Well Played"}
                
class Mage(Hero):
    def __init__(self,player_name="Player",hero_name="Jaina",side=1,hp=30):
        super(self.__class__,self).__init__(player_name,hero_name,"Mage",side,hp)
        self.hero_power=Fireblast(owner=self)
        self.emotes={"Curse":"My magic will tear you apart!","Well Played":"Well Played"}
                
class Priest(Hero):
    def __init__(self,player_name="Player",hero_name="Anduin",side=1,hp=30):
        super(self.__class__,self).__init__(player_name,hero_name,"Priest",side,hp)
        self.hero_power=Lesser_Heal(owner=self)
        self.emotes={"Curse":"The light shall burn you!","Well Played":"Well Played"}
            
class Paladin(Hero):
    def __init__(self,player_name="Player",hero_name="Uther",side=1,hp=30):
        super(self.__class__,self).__init__(player_name,hero_name,"Paladin",side,hp)
        self.hero_power=Reinforce(owner=self)
        self.emotes={"Curse":"justice demands retribution!","Well Played":"Well Played"}
                
class Shaman(Hero):
    def __init__(self,player_name="Player",hero_name="Thrall",side=1,hp=30):
        super(self.__class__,self).__init__(player_name,hero_name,"Shaman",side,hp)
        self.hero_power=Totemic_Call(owner=self)
        self.emotes={"Curse":"The element will destroy you!","Well Played":"Well Played"}
                
class Warlock(Hero):
    def __init__(self,player_name="Player",hero_name="Gul'dan",side=1,hp=30):
        super(self.__class__,self).__init__(player_name,hero_name,"Warlock",side,hp)
        self.hero_power=Life_Tap(owner=self)
        self.emotes={"Curse":"Your soul shall suffer!","Well Played":"Well Played"}
                
class Hunter(Hero):
    def __init__(self,player_name="Player",hero_name="Rexxar",side=1,hp=30):
        super(self.__class__,self).__init__(player_name,hero_name,"Hunter",side,hp)
        self.hero_power=Steady_Shot(owner=self)
        self.emotes={"Curse":"I will hunt you down!","Well Played":"Well Played"}
                
class Rogue(Hero):
    def __init__(self,player_name="Player",hero_name="Valera",side=1,hp=30):
        super(self.__class__,self).__init__(player_name,hero_name,"Rogue",side,hp)
        self.hero_power=Dagger_Mastery(owner=self)
        self.emotes={"Curse":"I will be your death!","Well Played":"Well Played"}
                
class Demon_Hunter(Hero):
    def __init__(self,player_name="Player",hero_name="Illidan",side=1,hp=30):
        super(self.__class__,self).__init__(player_name,hero_name,"Demon Hunter",side,hp)
        self.hero_power=Demon_Claws(owner=self)
        self.emotes={"Curse":"You are not prepared!","Well Played":"Well Played"}
        