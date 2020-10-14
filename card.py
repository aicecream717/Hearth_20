
'''
Created on Apr 2, 2020

@author: shan.jiang
'''
import database,importlib,random

#from GUIHandler import SCREEN_HEIGHT,SCREEN_WIDTH,get_image,get_rect,get_landed_board_area,choose_target,summon_animation,\
#attack_animation,add_card_to_deck_animation,burn_animation,destroy_animation,fatigue_animation,\
#    explode_animation,return_hand_animation, sort_hand_animation,heal_animation,blessing_of_kings_animation,arcane_shot_animation

from types import MethodType
from GUIHandler import *
card_collection = importlib.import_module("card")

def on_hit_poison(self,target):
    if not target.isHero():
        trigger_poisonous_animation(self)
        target.destroy()
            
            
class Card:
    def __init__(self,name="",owner=None,source=None):
        self.name = name
        self.big_image  = get_image("images/card_images/"+name.replace(":","").replace('"',"").replace("%2B","")+".png",(265,367)) 
        self.raw_image  = get_image("images/card_images/"+name.replace(":","").replace('"',"").replace("%2B","")+".png",(265,367)) 
        self.mini_image = get_image("images/card_images/"+name.replace(":","").replace('"',"").replace("%2B","")+".png",(103,141))
        self.arrow_image=arrow_image
        self.image = self.mini_image
        self.initialize_card_metadata()
        self.owner=owner
        if owner is not None:
            self.side=owner.side
        self.dragging=False
        self.overlay=False
        self.board_area="Deck"
        self.selected=False
        self.zoomed=False
        self.Deathrattle="Deathrattle" in self.abilities
        self.Echo="Echo" in self.abilities
        self.Twinspell="Twinspell" in self.abilities
        self.transform_in_hand="Transform in hand" in self.abilities
        self.corrupted=False
        self.ephemeral=False
        self.overload=0
        self.has_dormant=False
        self.trigger_outcast=False
        self.lifesteal=False
        self.has_lifesteal=False
        self.silenced=False
        self.trigger_event_type=""
        self.trigger_events=[]
        self.attachments={}
        self.isSpell=False
        self.always_show_face=False
        self.casts_when_drawn=False
        self.show_back=False
        self.started_in_deck=False
        self.is_legendary=(self.rarity=="Legendary")
        self.temporary_effects=self.get_initial_temporary_effects()
        self.copy_target=None
        if self.owner is not None:
            self.initialize_location(source)
            
    def get_initial_temporary_effects(self):
        return {"immune":False,"stealth":False,"elusive":False,"windfury":0,"lifesteal":False,"can attack":False,"owned":False,"cannot attack hero":False}
            
    def initialize_card_metadata(self):
        name,card_type,card_class,race,cardset,rarity,cost,attack,health,durability,craft_cost,disenchant_cost,\
        artist,card_text,back_text,lore,abilities,tags = database.get_card_metadata(self.name)
        
        self.card_type          = card_type
        self.card_class         = card_class
        self.race               = race
        self.cardset            = cardset
        self.rarity             = rarity
        self.cost               = int(cost)
        self.current_cost       = self.cost 
        self.atk                = int(attack)
        self.hp                 = int(health)
        self.durability         = int(durability)
        self.craft_cost         = int(craft_cost)
        self.disenchant_cost    = int(disenchant_cost)
        self.artist             = artist
        self.card_text          = card_text
        self.back_text          = back_text
        self.lore               = lore
        self.abilities          = abilities
        self.tags               = tags
        
    def initialize_location(self,source=None):
        if source is None:
            self.rect=get_rect(self.owner.deck.rect.x,self.owner.deck.rect.y,self.image.get_width(),self.image.get_height())
            self.location=self.rect.x,self.rect.y
        elif source=="board":
            board_minions = self.owner.board.minions[self.owner.side]
            if len(board_minions)==0:
                x=SCREEN_WIDTH/2-1/2*(self.image.get_width())
                y={-1:SCREEN_HEIGHT/4+45,1:SCREEN_HEIGHT/2}[self.owner.side]
            else:
                x,y=board_minions[-1].rect.x+self.image.get_width(),board_minions[-1].rect.y
            self.rect=get_rect(x,y,self.image.get_width(),self.image.get_height())
            self.location=self.rect.x-self.image.get_width()/2,self.rect.y
        else:
            self.rect=get_rect(source[0],source[1],self.image.get_width(),self.image.get_height())
            self.location=source[0],source[1]
               
    def play(self):
        self.board_area="Board"
    
    def __str__(self):
        return self.name+":\n"+self.card_text
    
    def __repr__(self):
        return self.name+":"+self.card_text
    
    def isFatigue(self):
        return isinstance(self, Fatigue)
    
    def isMinion(self):
        return isinstance(self, Minion)
    
    def isWeapon(self):
        return isinstance(self, Weapon)

    def isHero_power(self):
        return isinstance(self, Hero_Power)
    
    def isCard(self):
        return True
    
    def isHero(self):
        return False
    
    def has_race(self,race):
        return self.race.find(race)!=-1 or self.race=="All"
    
    def burn(self,skip_animation=False):
        if not skip_animation:
            burn_animation(self)
            
        if self in self.owner.hand:
            self.owner.hand.remove(self)
        if self in self.owner.deck.cards:
            self.owner.deck.cards.remove(self)
            
        self.owner.board.burnouts[self.owner.side].append(self)
        self.board_area="Burned"
               
    def at_hand(self):
        if self.owner.side==1: #main player
            return 0<=self.rect.x<=SCREEN_WIDTH-self.mini_image.get_width() and SCREEN_HEIGHT*3/4<=self.rect.y<=SCREEN_HEIGHT-self.mini_image.get_height()
        else: # opponent player
            return 0<=self.rect.x<=SCREEN_WIDTH-self.mini_image.get_width() and 0<=self.rect.y<=SCREEN_HEIGHT*1/4-self.mini_image.get_height()
    
    def on_board(self):
        if self.owner.side==1: #main player
            return 0<=self.rect.x<=SCREEN_WIDTH-self.mini_image.get_width() and SCREEN_HEIGHT/2-45<=self.rect.y<=SCREEN_HEIGHT*3/4-self.mini_image.get_height()
        else: # opponent player
            return 0<=self.rect.x<=SCREEN_WIDTH-self.mini_image.get_width() and SCREEN_HEIGHT*1/4<=self.rect.y<=SCREEN_HEIGHT/2-45-self.mini_image.get_height()

    def landed_board_area(self):
        return get_landed_board_area(self)
    
    def get_area(self):
        area=self.board_area
        if area=="Board":
            area="minion"
        elif area=="Hand":
            area="hand"
        return area
    
    def get_index(self):
        if self.board_area=="Hand" and self in self.owner.hand:
            return self.owner.hand.index(self)
        elif self.board_area=="Board" and self in self.owner.minions:
            return self.owner.minions.index(self)
        else:
            return -1
    
    def get_copy(self,owner=None):
        if owner is None:
            owner=self.owner
        card_copy=getattr(card_collection,database.cleaned(self.name))(owner=owner)
        return card_copy
        
    def get_current_cost(self):
        cost = self.current_cost+self.owner.board.get_buff(self)['cost']
        overriding_cost = self.owner.board.get_overriding_buff(self)['cost']
        if overriding_cost>=0:
            cost=overriding_cost
            
        return max(0,cost)
    
    def get_current_atk(self):
        return self.current_atk+self.owner.board.get_buff(self)['atk']
    
    def get_current_hp(self):
        return self.current_hp+self.owner.board.get_buff(self)['hp']
    
    def has_keyword(self,keyword):
        try:
            result=getattr(self,"has_"+keyword) or ((self.isSpell or isinstance(self,Hero_Power)) and getattr(self,keyword))
        except:
            result=False
        
        return result or self.owner.board.get_buff(self)[keyword] or self.temporary_effects[keyword]
    
    def first_played(self):
        return len(self.owner.played_cards[self.owner.turn])==0
    
    def collide(self,target):
        return target.rect.collidepoint(self.rect.x+self.image.get_width()/2,self.rect.y+self.image.get_height()/2)
    
    def all_minions(self,race=None,exclude_self=True):
        targets=[]
        for target in self.owner.board.queue:
            if target.isMinion() and (race is None or target.has_race(race)):
                targets.append(target)
                
        if exclude_self and self in targets:
            targets.remove(self)
            
        return targets
    
    def all_characters(self,race=None,exclude_self=True):
        targets=[]
        for target in self.owner.board.queue:
            if target.isMinion() and (race is None or target.has_race(race)):
                targets.append(target)
        
        if exclude_self and self in targets:
            targets.remove(self)
            
        return targets+[self.owner,self.owner.opponent]
    
    def enemy_secrets(self):
        targets=[]
        for target in self.owner.opponent.secrets:
            targets.append(target)
        return targets
    
    def enemy_minions(self,race=None):
        targets=[]
        for target in self.owner.board.queue:
            if target.side==-self.side and target.isMinion() and (race is None or target.has_race(race)):
                targets.append(target)
        return targets
    
    def enemy_characters(self,race=None):
        targets=[]
        for target in self.owner.board.queue:
            if target.side==-self.side and target.isMinion() and (race is None or target.has_race(race)):
                targets.append(target)
        return targets+[self.owner.opponent] 
     
    def friendly_secrets(self,exclude_self=True):
        targets=[]
        for target in self.owner.secrets:
            targets.append(target)
         
        if exclude_self and self in targets:
            targets.remove(self)
            
        return targets
    
    def friendly_characters(self,race=None,exclude_self=True):
        targets=[]
        for target in self.owner.board.queue:
            if target.side==self.side and target.isMinion() and (race is None or target.has_race(race)):
                targets.append(target)
                
        if exclude_self and self in targets:
            targets.remove(self)
            
        return targets+[self.owner]    
    
    def friendly_minions(self,race=None,exclude_self=True):
        targets=[]
        for target in self.owner.board.queue:
            if target.side==self.side and target.isMinion() and (race is None or target.has_race(race)):
                targets.append(target)
                        
        if exclude_self and self in targets:
            targets.remove(self)
            
        return targets            
     
    def recrue_cost(self):
        previous_mana = self.owner.current_mana
        if not self.owner.board.get_buff(self)['cost health']:
            self.owner.current_mana-=max(self.get_current_cost(),0)
        if self.overload:
            self.overload_mana(self.overload)
        
        return {'mana_spent':previous_mana-self.owner.current_mana,
                'mana_overloaded':self.overload}  

    def all_minions_except(self,race,exclude_self=True):
        targets=[]
        for target in self.owner.board.queue:
            if target.isMinion() and not target.has_race(race):
                targets.append(target)
                
        if exclude_self and self in targets:
            targets.remove(self)
            
        return targets
    
    def friendly_minions_except(self,race,exclude_self=True):
        targets=[]
        for target in self.owner.board.queue:
            if target.side==self.side and target.isMinion() and not target.has_race(race):
                targets.append(target)
                
        if exclude_self and self in targets:
            targets.remove(self)
             
        return targets    
    
    def enemy_minions_except(self,race):
        targets=[]
        for target in self.owner.board.queue:
            if target.side==-self.side and target.isMinion() and not target.has_race(race):
                targets.append(target)
        return targets
                 
    def overload_mana(self,amount=1):
        self.owner.overloaded_mana+=amount
        self.owner.total_overloaded_mana+=amount
        
        #Trigger overload effect if any  
        self.owner.board.activate_triggered_effects("overload",(self,amount))
    
    def modify_cost(self,amount):
        self.current_cost+=amount
        if self.current_cost<0:
            self.current_cost=0
    
    def replace_by(self,card):
        card.initialize_location(self.location)
        card.board_area=self.board_area
        if self.board_area=="Hand":
            self.owner.hand[self.owner.hand.index(self)]=card
            self.board_area="Burn"
        elif self.board_area=="Deck":
            self.owner.deck.cards[self.owner.deck.cards.index(self)]=card
            self.board_area="Burn"
        
                   
    def battlecry(self,target=None):
        pass
    
    def trigger_battlecry(self,target=None):
        self.battlecry(target)
        if self.owner.board.get_buff(self)['battlecry twice'] and not (self.isMinion() and self.transformed):
            if target is None or (target.board_area=="Board" and not (target.isMinion() and target.transformed)):
                self.battlecry(target)
            elif target.isMinion() and target.transformed:
                self.battlecry(target.transformed)

    def deathrattle(self):
        pass
    
    def trigger_deathrattle(self):
        for deathrattle in self.deathrattles:
            deathrattle[0]()
            if self.owner.board.get_buff(self)['deathrattle twice']:
                deathrattle[0]() 
                
    def outcasted(self):
        self.trigger_outcast=False
        return self.board_area=="Hand" and (self.get_index()==0 or self.get_index()==len(self.owner.hand)-1)
    
    def outcast(self):
        pass
        #self.trigger_outcast=False
      
    def on_drawn(self):
        self.always_show_face=True
        on_drawn_animation(self)
        self.invoke()
        self.owner.draw()
    
    def perish(self):
        pass
    
    def start_of_game(self):
        pass
    
    def ongoing_effect(self,target):
        return {}
    
    def overriding_ongoing_effect(self,target):
        return {}
    
    def upgrade(self):
        buff_hand_animation(self.owner,[self])
        card=self.upgrade_target(owner=self.owner)
        card.board_area="Hand"
        if self in self.owner.hand:
            self.owner.hand[self.owner.hand.index(self)]=card
            
    def deal_damage(self,targets,damages,on_hit_effects=[],skip_animation=False):
        if len(targets)==1:
            targets[0].incur_damage(damages[0],on_hit_effects=on_hit_effects,damage_source=self,skip_animation=skip_animation)
        else:# for AOE damage
            incur_aoe_damage_animation(targets,damages)
            i=0
            while i<len(targets):
                target=targets[i]
                target.incur_damage(damages[i],on_hit_effects=on_hit_effects,damage_source=self,skip_animation=True)
                if target in targets: 
                    i+=1
        
        self.owner.board.activate_triggered_effects('deal damage',(self,sum(damages),targets))

            
    def deal_split_damage(self,targets,shots=3,damage=1,effect=None,speed=30,curve=False):
        hits={}
        split_targets=[target for target in targets]
        for k in range(shots):
            if len(split_targets)==0:
                break
            target=random.choice(split_targets)
            split_damage_animation(self,target,effect,speed,curve=curve)
            target.incur_damage(damage,damage_source=self,skip_animation=True)
            #self.deal_damage([target], [damage],skip_animation=True)
            
            if target.get_current_hp()<=0: #target Died amid split
                split_targets.remove(target)
            
            if target not in hits:
                hits[target]=damage
            else:
                hits[target]+=damage
                
        incur_aoe_damage_animation(list(hits.keys()), list(hits.values()))
         
    def heal(self,targets,amounts,skip_animation=False):
        total_amounts=[amount for amount in amounts]
        effect_modifier=self.owner.board.get_buff(self)["double effect"]
        for i in range(effect_modifier):
            total_amounts=[amount*2 for amount in total_amounts]
            
        if not self.owner.board.get_buff(self)['heal reverse']:
            if len(targets)==1:
                targets[0].restore_health(total_amounts[0],heal_source=self,skip_animation=skip_animation)
            else:# for AOE heal
                heal_aoe_animation(targets,total_amounts)
                for i in range(len(targets)):
                    targets[i].restore_health(total_amounts[i],heal_source=self,skip_animation=True)
        else:
            self.deal_damage(targets,total_amounts)
    
    def split_heal(self,targets,shots=3,amount=1,effect=None,speed=30,curve=False):
        hits={}
        split_targets=[target for target in targets]
        for k in range(shots):
            if len(split_targets)==0:
                break
            target=random.choice(split_targets)
            split_damage_animation(self,target,effect,speed,curve=curve)
            self.heal([target],[amount],skip_animation=True)
            
            if target.get_current_hp()<=0 or target.current_hp==target.temp_hp: #target Died or restored to full amid split
                split_targets.remove(target)
            
            if target not in hits:
                hits[target]=amount
            else:
                hits[target]+=amount
         
        heal_aoe_animation(list(hits.keys()), list(hits.values()))       
                                         
    def overkill(self,target):
        pass
                        
    def trigger_effect(self,triggering_entity):
        trigger_effect_animation(self,triggering_entity)

    def trigger_inspire(self):
        inspire_animation(self)
               
    def discard(self,skip_animation=False):
        if self.board_area=="Hand":
            if not skip_animation:
                discard_animation(self)
            self.owner.hand.remove(self)
            sort_hand_animation(self.owner)
        self.owner.discards.append(self)
        self.board_area="Discard"
        self.owner.total_discards+=1
        
        if "On-discard effect" in self.tags:
            self.on_discard()
          
        #Trigger discard effect if any  
        self.owner.board.activate_triggered_effects("on discard",self)
        
        #Trigger quest if any
        self.owner.trigger_quests('on discard',self)
                    
    def on_discard(self):
        pass
    
    def shuffle_cards(self,cards,deck):
        for card in cards:
            deck.cards.append(card)
            move_animation(card, deck.location, speed=80)
        deck.shuffle()
           
    def shuffle_into_deck(self,deck=None,reset_status=True,skip_zoom=False):
        if deck is None:
            deck=self.owner.deck
            
        if (self.isMinion() or isinstance(self,Weapon)) and reset_status:
            self.reset_status()
            
        self.image=self.mini_image
        deck_in_animation(self,deck,skip_zoom=skip_zoom)
        deck.add_card(self,randomize=True)
        if self in self.owner.minions:
            self.owner.minions.remove(self)
        if self in self.owner.board.queue:
            self.owner.board.queue.remove(self)
        if self in self.owner.grave:
            self.owner.grave.remove(self)
        self.board_area="Deck"
        self.owner.board.sort_minions(self.owner.side)
    
    def search_card_by_type(self,card_type):
        card_pool=[]
        for card in self.owner.deck.cards:
            if isinstance(card, card_type):
                s=card_pool.append(card)
                
        if len(card_pool)>0:
            target_card = random.choice(card_pool)
            return target_card 
               
    def get_random_spare_part(self,owner=None):
        spare_parts=["Armor_Plating","Emergency_Coolant","Finicky_Cloakfield","Reversing_Switch","Rusty_Horn","Time_Rewinder","Whirling_Blades"]
        spare_part=getattr(card_collection,database.cleaned(random.choice(spare_parts)))(owner=owner)
        
        return spare_part
    
    def give_random_spare_part(self,player):
        spare_part=self.get_random_spare_part(owner=player)
        spare_part.initialize_location(self.location)
        spare_part.hand_in()
               
    def discover(self,filter_str="[cost]>=0",own_class=True,standard=True,by_ability=False,card_pool=[]):
        if len(card_pool)==0:
            filter_keywords=filter_str
            if own_class:
                filter_keywords+=" AND ([class]='Neutral' OR [class] LIKE '%"+self.owner.class_name+"%')"
            if standard:
                filter_keywords+=" AND [format]='standard'"
            cards = database.get_random_cards(filter_keywords, self.owner, 3,standard=standard,by_ability=by_ability)
        else:
            cards=card_pool
            
        if not self.owner.board.random_select:
            selected_card   = choose_one(cards)
        else:
            selected_card   = cards[0]
        
        for card in cards: #Return card rects to original locations
            if card.board_area=="Deck":
                card.initialize_location(card.owner.deck.location)
        
        return selected_card

    def recruit(self,minion,location="board"):
        if minion in minion.owner.deck.cards and not minion.owner.board.isFull(self.owner):
            minion.owner.deck.cards.remove(minion)
            minion.initialize_location(location)
            minion.location=minion.owner.deck.location
            recruit_animation(minion)
            
            minion.owner.board.add_minion(minion)
            minion.board_area="Board"
            minion.come_on_board()
        
            #Trigger on summon effect if any
            self.owner.board.activate_triggered_effects('summon a minion',minion)
            
            #Trigger quest if any
            minion.owner.trigger_quests('summon a minion',minion)
            
    def hand_in(self,speed=15):
        if len(self.owner.hand)<self.owner.hand_limit:
            if len(self.owner.hand)<=1:
                x,y=SCREEN_WIDTH/2-388,{-1:5,1:820}[self.owner.side]
            else:
                x,y=self.owner.hand[-2].location[0]+self.mini_image.get_width()+100,self.owner.hand[-2].location[1]
    
            move_animation(self, dest=(x,y), speed=speed, zoom=False)
            self.owner.add_hand(self)
            sort_hand_animation(self.owner)
            
    def appear_in_hand(self):
        if len(self.owner.hand)<self.owner.hand_limit:
            if len(self.owner.hand)==0:
                x,y=SCREEN_WIDTH/2-388,{-1:5,1:820}[self.owner.side]
            else:
                x,y=(self.owner.hand[-1].location[0]+self.mini_image.get_width()+20,self.owner.hand[-1].location[1])
    
            self.initialize_location((x,y))
            fade_in_animation(self.image, self, self.location, duration=50, max_opacity=200)
            self.owner.add_hand(self)
            sort_hand_animation(self.owner)

            
    def combo(self):
        pass
    
    def echo(self): 
        card_copy=getattr(card_collection,database.cleaned(self.name))(owner=self.owner)
        card_copy.initialize_location(self.location)
        card_copy.ephemeral=True
        card_copy.appear_in_hand()
      
    def twinspell(self): 
        card_copy=getattr(card_collection,database.cleaned(self.name)+"_Twinspell")(owner=self.owner)
        card_copy.initialize_location(self.location)
        card_copy.appear_in_hand()
          
    def joust(self,card_type):
        winner,loser=None,None
        card1=self.owner.search_card(self.owner.deck.cards,card_type)
        card2=self.owner.opponent.search_card(self.owner.opponent.deck.cards,card_type)
        joust_animation(card1,card2)
        if card1 is not None and card2 is not None:
            if card1.get_current_cost()>card2.get_current_cost():
                winner,loser=card1,card2
                winner_animation(winner,loser)
            elif card2.get_current_cost()>card1.get_current_cost():
                winner,loser=card2,card1
                winner_animation(winner,loser)
            move_multiple_animation([card1,card2], dests=[card1.owner.deck.location,card2.owner.deck.location], speed=80, zoom=False)
        elif card2 is None:
            if card1 is not None:
                winner,loser=card1,card2
                winner_animation(winner,loser)
                move_animation(winner, dest=winner.owner.deck.location, speed=80, zoom=False)
        elif card1 is None:
            winner,loser=card2,card1
            winner_animation(winner,loser)
            move_animation(winner, dest=winner.owner.deck.location, speed=80, zoom=False)

       
        return winner
    
    def reveal(self,deck=1,card_type="Minion"):
        if deck==1:
            source=self.owner.deck.cards
        else:
            source=self.owner.opponent.deck.cards
        card=self.owner.search_card(source,card_type)
        if card is not None:
            reveal_animation(card)
            return card
        else:
            return None
    
    def shapeshift(self,target):
        target.initialize_location(self.location)
        target.board_area=self.board_area
        self.owner.hand[self.get_index()]=target
             
    def trigger_choose_both(self):
        target=None
        self.owner.board.exclude.append(self)
        if "Targeted" in self.tags:
            if self.isSpell:
                chooser=self.owner
            else:
                chooser=self
            
            target=choose_target(chooser, target="character", message="deal combined effect")
           
        option1=self.options[0](owner=self.owner)
        option1.initialize_location((500,500))
        option1.origin=self
        option2=self.options[1](owner=self.owner)
        option2.initialize_location((500,500))
        option2.origin=self
        if option1.is_valid_on(target) and option1.is_valid_on(target):
            option1.invoke(target)
            option2.invoke(target)
        else:
            if self.isMinion() and self.board_area=="Board":
                self.return_hand(reset=False)

        self.owner.board.exclude.remove(self)

        
    def buff_multiple(self,card_type="Minion",atk=0,hp=0):
        targets=[]
        for target in self.friendly_minions():
            if target.card_type==card_type or target.has_race(card_type):
                targets.append(target)
        if len(targets)>0:
            buff_multiple_animation(self, targets)
            for target in targets:
                target.buff_stats(atk,hp)
                        
    def buff_cthun(self,atk,hp):
        cthun=None
        for card in self.owner.minions+self.owner.hand+self.owner.deck.cards:
            if isinstance(card, CThun):
                cthun=card
                break
        if cthun is not None:
            cthun.buff_stats(atk,hp)
            if cthun.board_area!="Board":
                buff_cthun_animation(cthun)
                
        return cthun

    def eval_cthun(self,atk=10):
        cthun=None
        for card in self.owner.minions+self.owner.hand+self.owner.deck.cards:
            if isinstance(card, CThun):
                cthun=card
                break
        if cthun is not None and cthun.get_current_atk()>=atk:
            return True        
        else:
            return False
                    
    def silence(self,minion,skip_animation=False):
        silencer=self
        if self.isSpell:
            silencer=self.owner
            
        if not skip_animation:
            silence_animation(silencer)
        
        minion.current_atk=minion.atk
        minion.temp_atk=minion.atk
        minion.current_hp=min([minion.current_hp,minion.hp])
        minion.temp_hp=minion.hp
        minion.has_taunt=False
        minion.has_divine_shield=False
        minion.has_windfury=False
        minion.has_elusive=False
        minion.has_stealth=False
        minion.has_poisonous=False
        minion.has_charge=False
        minion.has_rush=False
        minion.frozen=False
        minion.frozen_timer = 0
        minion.has_deathrattle=False
        minion.has_trigger=False
        minion.has_inspire=False
        minion.windfury_counter=0
        minion.has_lifesteal=False
        minion.has_reborn=False
        minion.has_immune = False
        minion.corrupted=False
        minion.has_spell_damage=False
        minion.has_opponent_spell_damage=False
        minion.current_spell_damage_boost=0
        minion.current_opponent_spell_damage_boost=0
        minion.trigger_events=[]
        minion.deathrattles=[]
        minion.on_hit_effects=[]
        minion.temporary_effects=minion.get_initial_temporary_effects()
        minion.cannot_attack=False
        minion.attachments=={"Spell History":[]}
        minion.silenced=True

class Enchantment(Card):
    def __init__(self,name="Default Enchantment",owner=None,source=None):#Uncollectible
        super(Enchantment,self).__init__(name,owner,source)
        self.owner.enchantments.append(self)
        self.board_area="Board"
        
        self.trigger_events=[]
        self.trigger_events.append(("end of turn",self.trigger_remove))
            
    def trigger_remove(self, triggering_player):
        if triggering_player is self.owner:
            self.destroy()
            
    def destroy(self):
        self.owner.enchantments.remove(self)
        self.board_area=="Burn"
            
class Hero_Power(Card):
    def __init__(self,name="",owner=None):
        super(Hero_Power,self).__init__(name,owner)
        self.board_image        = get_image("images/card_images/"+name+".png",(108,148))
        self.disabled_image     = hero_power_disabled_image
        self.image              = self.board_image
        self.trigger_image      = trigger_image
        self.owner              = owner
        self.use_count          = 0
        self.usage_cap          = 1
        self.targeted           = False
        self.passive            = False
        self.rect               = get_rect(self.owner.rect.x+self.owner.image.get_width(),self.owner.rect.y+self.owner.image.get_height()*2/7,self.image.get_width(),self.image.get_height())
        self.location           = self.rect.x,self.rect.y
        self.board_area         = "hero_power"
        self.trigger_event_type = ""
        self.trigger_events     = []
        self.activate_while_disabled=False
    
    def isCard(self):
        return True
    
    def isHero(self):
        return False  
     
    def invoke(self,target=None):
        if self.owner.board.get_buff(self)['freeze target']:
            target.get_frozen()
            
        self.use_count+=1
        self.owner.hero_power_count+=1
        self.owner.current_mana-=self.get_current_cost()
        self.owner.board.activate_triggered_effects("use hero power",self)
        if self.disabled():
            disable_hero_power_animation(self)
    
    def is_targeted(self):
        return self.targeted or self.owner.board.get_buff(self.owner)['target minion']
        
    def cancel_target(self):
        pass
     
    def disabled(self):
        if self.owner.board.get_buff(self)['disable hero power']:
            return True
        else:
            return self.use_count>=self.get_usage_cap()
    
    def get_usage_cap(self):
        cap=self.usage_cap
        overriding_cap=self.owner.board.get_overriding_buff(self)["usage cap"]
        if overriding_cap>=0:
            cap=overriding_cap
            
        return cap
    
    def refresh(self):
        self.use_count=0
        enable_hero_power_animation(self)
       
    def get_index(self):
        return 0
    
    def deal_damage(self,targets,amounts,skip_animation=False):
        boost=self.owner.board.get_buff(self.owner)['hero power damage']
        total_damages=[amount+boost for amount in amounts]
        effect_modifier=self.owner.board.get_buff(self)["double effect"]
        for i in range(effect_modifier):
            total_damages=[damage*2 for damage in total_damages]
        super(Hero_Power,self).deal_damage(targets, total_damages,skip_animation=skip_animation)
         
    def upgrade(self):
        self.owner.hero_power.refresh()
           
class Demon_Claws(Hero_Power):
    def __init__(self,name="Demon Claws",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        self.class_name="Demon Hunter"
        
    def invoke(self):
        self.owner.current_atk+=1
        super(self.__class__,self).invoke()
        
    def upgrade(self):
        upgraded_hero_power=Demons_Bite(owner=self.owner)
        self.owner.gain_hero_power(upgraded_hero_power)

class Demons_Bite(Hero_Power):
    def __init__(self,name="Demon's Bite",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        self.class_name="Demon Hunter"
        
    def invoke(self):
        self.owner.current_atk+=2
        super(self.__class__,self).invoke()
                        
class Shapeshift(Hero_Power):
    def __init__(self,name="Shapeshift",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        self.class_name="Druid"
        
    def invoke(self):
        self.owner.current_atk+=1
        self.owner.increase_shield(1)
        super(self.__class__,self).invoke()
        
    def upgrade(self):
        upgraded_hero_power=Dire_Shapeshift(owner=self.owner)
        self.owner.gain_hero_power(upgraded_hero_power)

class Dire_Shapeshift(Hero_Power):
    def __init__(self,name="Dire Shapeshift",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        self.class_name="Druid"
        
    def invoke(self):
        self.owner.current_atk+=2
        self.owner.increase_shield(2)
        super(self.__class__,self).invoke()

class Plague_Lord(Hero_Power):
    def __init__(self,name="Plague Lord",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        self.class_name="Druid"
        self.abilities.append("Choose One")
        self.options=[Spider_Fangs,Scarab_Shell]

    def invoke(self):
        if self.owner.board.get_buff(self)["choose both"]:
            self.trigger_choose_both()
        else:
            self.trigger_choose_one()
        super(self.__class__,self).invoke() 
        
    def trigger_choose_one(self):
        selected_card = choose_one([option(owner=self.owner) for option in self.options])
        selected_card.origin=self
        selected_card.invoke()  
                                               
class Steady_Shot(Hero_Power):
    def __init__(self,name="Steady Shot",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        self.class_name="Hunter"
        self.damage= 2
        
    def invoke(self,target=None):
        if target is None:
            target=self.owner.opponent    
        steady_shot_animation(self.owner,target)
        self.deal_damage([target], [self.damage])
        super(self.__class__,self).invoke(target)
        
    def upgrade(self):
        upgraded_hero_power=Ballista_Shot(owner=self.owner)
        self.owner.gain_hero_power(upgraded_hero_power)
                          
class Ballista_Shot(Hero_Power):
    def __init__(self,name="Ballista Shot",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        self.class_name="Hunter"
        self.damage= 3
        
    def invoke(self,target=None):
        if target is None:
            target=self.owner.opponent    
        steady_shot_animation(self.owner,target)
        self.deal_damage([target], [self.damage])
        super(self.__class__,self).invoke(target)

class Dinomancy_Hero_Power(Hero_Power):
    def __init__(self,name="Dinomancy (Hero Power)",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        self.class_name="Hunter"
        self.targeted =True
        self.effect_message = "Give +2/+2"
        
    def invoke(self,target=None):
        if target is not None and target.has_race("Beast"):
            hunter_buff_animation(self, target)
            target.buff_stats(2,2)
            super(self.__class__,self).invoke(target)

class Build_A_Beast(Hero_Power):
    def __init__(self,name="Build-A-Beast",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        self.class_name="Hunter"
        
    def invoke(self,target=None):
        self.owner.board.background=background_dark
        first_choice = choose_one(database.get_random_cards(filter_str="([class] LIKE '%Hunter%' OR [class]='Neutral') AND [race] ='Beast' AND [cost]<=5 AND DATALENGTH([card_text])>44 AND [card_text] NOT LIKE '%Battlecry%'", owner=self.owner, k=3))
        second_choice = choose_one(database.get_random_cards(filter_str="([class] LIKE '%Hunter%' OR [class]='Neutral') AND [race] ='Beast' AND [cost]<=5 AND DATALENGTH([card_text])<=44 AND [card_text] NOT LIKE '%Battlecry%'", owner=self.owner, k=3))
        for keyword in ["taunt","divine_shield","lifesteal","charge","rush","windfury","poisonous","stealth","Echo"]:
            setattr(first_choice,keyword,getattr(first_choice,keyword) or getattr(second_choice,keyword))
        first_choice.atk+=second_choice.atk
        first_choice.hp+=second_choice.hp
        first_choice.cost+=second_choice.cost
        first_choice.current_cost+=second_choice.current_cost
        first_choice.set_stats(first_choice.atk,first_choice.hp)
        first_choice.spell_damage_boost+=second_choice.spell_damage_boost
        first_choice.card_text+=second_choice.card_text
        
        first_choice.appear_in_hand()
        self.owner.board.background=background
        
        super(self.__class__,self).invoke()
                        
class Fireblast(Hero_Power):
    def __init__(self,name="Fireblast",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        self.class_name="Mage"
        self.targeted =True
        self.damage=1
        self.effect_message = "deal "+str(self.damage)+" damage"
        
    def invoke(self,target):
        fire_blast_animation(self.owner,target)
        self.deal_damage([target], [self.damage])
        super(self.__class__,self).invoke(target)
        
    def upgrade(self):
        upgraded_hero_power=Fireblast_Rank_2(owner=self.owner)
        self.owner.gain_hero_power(upgraded_hero_power)
                
class Fireblast_Rank_2(Hero_Power):
    def __init__(self,name="Fireblast Rank 2",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        self.class_name="Mage"
        self.targeted =True
        self.damage=2
        self.effect_message = "deal "+str(self.damage)+" damage"
        
    def invoke(self,target):
        fire_blast_animation(self.owner,target)
        self.deal_damage([target], [self.damage])
        super(self.__class__,self).invoke(target)

class Icy_Touch(Hero_Power):
    def __init__(self,name="Icy Touch",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        self.class_name="Mage"
        self.targeted =True
        self.damage=1
        self.effect_message = "deal "+str(self.damage)+" damage"
        
    def invoke(self,target):
        glacial_shard_animation(self,target)
        self.deal_damage([target], [self.damage])
        if target.destroyed_by is self:
            minion=Water_Elemental(owner=self.owner,source="board")
            self.owner.recruit(minion)  
        super(self.__class__,self).invoke(target)
        
class Reinforce(Hero_Power):
    def __init__(self,name="Reinforce",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        self.class_name="Paladin"

    def invoke(self):
        if not self.owner.board.isFull(self.owner): 
            minion=getattr(card_collection, "Silver_Hand_Recruit")(owner=self.owner,source="board")
            self.owner.recruit(minion)
            super(self.__class__,self).invoke()
        
    def upgrade(self):
        upgraded_hero_power=The_Silver_Hand(owner=self.owner)
        self.owner.gain_hero_power(upgraded_hero_power)
                
class The_Silver_Hand(Hero_Power):
    def __init__(self,name="The Silver Hand",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        self.class_name="Paladin"

    def invoke(self):
        if not self.owner.board.isFull(self.owner):
            for i in range(2):
                minion=getattr(card_collection, "Silver_Hand_Recruit")(owner=self.owner,source="board")
                self.owner.recruit(minion)
            super(self.__class__,self).invoke()

class The_Tidal_Hand(Hero_Power):
    def __init__(self,name="The Tidal Hand",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        self.class_name="Paladin"

    def invoke(self):
        if not self.owner.board.isFull(self.owner): 
            minion=getattr(card_collection, "Silver_Hand_Murloc")(owner=self.owner,source="board")
            self.owner.recruit(minion)
            super(self.__class__,self).invoke()

class The_Four_Horsemen_Hero_Power(Hero_Power):
    def __init__(self,name="The Four Horsemen (Hero Power)",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        self.class_name="Paladin"
        self.trigger_event_type="summon a minion"

    def invoke(self):
        if not self.owner.board.isFull(self.owner):  
            # Get a list of unsummoned totems
            names         = [minion.name for minion in self.friendly_minions()]
            unsummoned_horsemen = []
            for horseman_name in ["Deathlord Nazgrim","Darion Mograine","Inquisitor Whitemane","Thoras Trollbane"]:
                if horseman_name not in names:
                    unsummoned_horsemen.append(horseman_name)
            
            if len(unsummoned_horsemen)>0:
                horseman_name = random.choice(unsummoned_horsemen)
                minion=getattr(card_collection, database.cleaned(horseman_name))(owner=self.owner,source="board")
                self.owner.recruit(minion)
                super(self.__class__,self).invoke()
            else:
                print("All horsemen are already summoned!")
                show_text(message="All horsemen are already summoned!",flip=True,pause=1)

    def trigger_effect(self, triggering_card=None):
        if self.owner.control_all([Deathlord_Nazgrim,Darion_Mograine,Inquisitor_Whitemane,Thoras_Trollbane]):
            targets=[]
            for minion in self.friendly_minions():
                if minion.name in ["Deathlord Nazgrim","Darion Mograine","Inquisitor Whitemane","Thoras Trollbane"]:
                    targets.append(minion)
            light_buff_multiple_animation(self, targets)
            time.sleep(0.5)
            self.owner.opponent.destroy()
                                        
class Lesser_Heal(Hero_Power):
    def __init__(self,name="Lesser Heal",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        self.class_name="Priest"
        self.targeted =True
        self.strength=2
        self.effect_message = "restore "+str(self.strength)+" health"
        
    def invoke(self,target):
        lesser_heal_animation(self.owner,target)
        self.heal([target],[self.strength],skip_animation=True)
        super(self.__class__,self).invoke(target)
        
    def upgrade(self):
        upgraded_hero_power=Heal(owner=self.owner)
        self.owner.gain_hero_power(upgraded_hero_power)
                
class Heal(Hero_Power):
    def __init__(self,name="Heal",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        self.class_name="Priest"
        self.targeted =True
        self.strength=4
        self.effect_message = "restore "+str(self.strength)+" health"
        
    def invoke(self,target):
        lesser_heal_animation(self.owner,target)
        self.heal([target],[self.strength],skip_animation=True)
        super(self.__class__,self).invoke(target)

class Mind_Spike(Hero_Power):
    def __init__(self,name="Mind Spike",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        self.class_name="Priest"
        self.targeted =True
        self.damage=2
        self.effect_message = "deal "+str(self.damage)+" damage"
        
    def invoke(self,target):
        mind_spike_animation(self,target)
        self.deal_damage([target], [self.damage])
        super(self.__class__,self).invoke(target)
        
    def upgrade(self):
        upgraded_hero_power=Mind_Shatter(owner=self.owner)
        self.owner.gain_hero_power(upgraded_hero_power)

class Mind_Shatter(Hero_Power):
    def __init__(self,name="Mind Shatter",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        self.class_name="Priest"
        self.targeted =True
        self.damage=3
        self.effect_message = "deal "+str(self.damage)+" damage"
        
    def invoke(self,target):
        mind_spike_animation(self,target)
        self.deal_damage([target],[self.damage])
        super(self.__class__,self).invoke(target)

class Voidform(Hero_Power):
    def __init__(self,name="Voidform",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        self.class_name="Priest"
        self.targeted =True
        self.damage=2
        self.effect_message = "deal "+str(self.damage)+" damage"
        self.trigger_event_type="play a card"
        self.activate_while_disabled=True
        
    def invoke(self,target):
        mind_spike_animation(self,target)
        self.deal_damage([target],[self.damage])
        super(self.__class__,self).invoke(target)

    def trigger_effect(self, triggering_card):
        if triggering_card.side==self.side:
            self.refresh()
                                            
class Dagger_Mastery(Hero_Power):
    def __init__(self,name="Dagger Mastery",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        self.class_name="Rogue"
        
    def invoke(self):
        weapon = Wicked_Knife(owner=self.owner)
        if not self.owner.board.get_buff(self)["not replace"]:
            self.owner.equip_weapon(weapon)
        super(self.__class__,self).invoke()                                       
        
    def upgrade(self):
        upgraded_hero_power=Poisoned_Daggers(owner=self.owner)
        self.owner.gain_hero_power(upgraded_hero_power)
                
class Poisoned_Daggers(Hero_Power):
    def __init__(self,name="Poisoned Daggers",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        self.class_name="Rogue"
        
    def invoke(self):
        weapon = Poisoned_Dagger(owner=self.owner)
        if not self.owner.board.get_buff(self)["not replace"]:
            self.owner.equip_weapon(weapon)
        super(self.__class__,self).invoke()

class Deaths_Shadow(Hero_Power):
    def __init__(self,name="Death's Shadow",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        self.class_name="Rogue"
        self.passive=True
        self.trigger_event_type="start of turn"

    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner:
            self.invoke()
        
    def invoke(self):
        card=Shadow_Reflection(owner=self.owner,source=self.owner.hero_power.location)
        card.hand_in()
                
class Totemic_Call(Hero_Power):
    def __init__(self,name="Totemic Call",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        self.class_name="Shaman"

    def invoke(self):
        if not self.owner.board.isFull(self.owner):  
            # Get a list of unsummoned totems
            names         = [minion.name for minion in self.friendly_minions()]
            unsummoned_totems = []
            for totem_name in ["Healing Totem","Searing Totem","Stoneclaw Totem","Wrath of Air Totem"]:
                if totem_name not in names:
                    unsummoned_totems.append(totem_name)
            
            if len(unsummoned_totems)>0:
                totemic_call_animation(self.owner)
                totem_name = random.choice(unsummoned_totems)
                minion=getattr(card_collection, database.cleaned(totem_name))(owner=self.owner,source="board")
                self.owner.recruit(minion)
                super(self.__class__,self).invoke()
            else:
                print("All totems are already summoned!")
                show_text(message="All totems are already summoned!",flip=True,pause=1)
        
    def upgrade(self):
        upgraded_hero_power=Totemic_Slam(owner=self.owner)
        self.owner.gain_hero_power(upgraded_hero_power)
        
class Totemic_Slam(Hero_Power):
    def __init__(self,name="Totemic Call",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        self.class_name="Shaman"

    def invoke(self):
        if not self.owner.board.isFull(self.owner):  
            # Get a list of unsummoned totems
            totem1         = Healing_Totem(owner=self.owner,source="board")
            totem2         = Searing_Totem(owner=self.owner,source="board")
            totem3         = Wrath_of_Air_Totem(owner=self.owner,source="board")
            totem4         = Stoneclaw_Totem(owner=self.owner,source="board")
            selected_totem = choose_one([totem1,totem2,totem3,totem4])
        
            totemic_call_animation(self.owner)
            self.owner.recruit(selected_totem)
            super(self.__class__,self).invoke()

class Lightning_Jolt(Hero_Power):
    def __init__(self,name="Lightning Jolt",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        self.class_name="Shaman"
        self.targeted =True
        self.damage=2
        self.effect_message = "deal "+str(self.damage)+" damage"
        
    def invoke(self,target):
        lightning_jolt_animation(self.owner,target)
        self.deal_damage([target], [self.damage])
        super(self.__class__,self).invoke(target)

class Transmute_Spirit(Hero_Power):
    def __init__(self,name="Transmute Spirit",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        self.class_name="Shaman"
        self.targeted =True
        self.effect_message = "transform"
        
    def invoke(self,target):
        target.evolve()
        super(self.__class__,self).invoke(target)
                     
class Life_Tap(Hero_Power):
    def __init__(self,name="Life Tap",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        self.class_name="Warlock"
        self.damage=2
        
    def invoke(self):
        self.deal_damage([self.owner], [self.damage])
        card=self.owner.draw()
        if self.owner.board.get_buff(self)['Fizzlebang']:
            card.current_cost=0 
        super(self.__class__,self).invoke()
        
    def upgrade(self):
        upgraded_hero_power=Soul_Tap(owner=self.owner)
        self.owner.gain_hero_power(upgraded_hero_power)
        
class Soul_Tap(Hero_Power):
    def __init__(self,name="Soul Tap",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        self.class_name="Warlock"
        
    def invoke(self):
        card=self.owner.draw()
        if self.owner.board.get_buff(self)['Fizzlebang']:
            card.current_cost=0 
        super(self.__class__,self).invoke()

class Siphon_Life(Hero_Power):
    def __init__(self,name="Siphon Life",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        self.class_name="Warlock"
        self.targeted =True
        self.damage=3
        self.effect_message = "deal "+str(self.damage)+" damage"
        self.lifesteal=True
        
    def invoke(self,target):
        mind_spike_animation(self,target)
        self.deal_damage([target],[self.damage])
        super(self.__class__,self).invoke(target)
                
class Armor_Up(Hero_Power):
    def __init__(self,name="Armor Up!",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        self.class_name="Warrior"
        
    def invoke(self):
        self.owner.increase_shield(2)
        super(self.__class__,self).invoke()
        
    def upgrade(self):
        upgraded_hero_power=Tank_Up(owner=self.owner)
        self.owner.gain_hero_power(upgraded_hero_power)

class Tank_Up(Hero_Power):
    def __init__(self,name="Tank Up!",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        self.class_name="Warrior"
        
    def invoke(self):
        self.owner.increase_shield(4)
        super(self.__class__,self).invoke()

class Bladestorm_Hero_Power(Hero_Power):
    def __init__(self,name="Bladestorm (Hero Power)",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        self.class_name="Warrior"
        
    def invoke(self):
        whirlwind_animation(self)
        minions=self.all_minions()
        self.deal_damage(minions,[1]*len(minions))
        super(self.__class__,self).invoke()
              
class INFERNO(Hero_Power):
    def __init__(self,name="INFERNO!",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        self.class_name="Warlock"
    
    def invoke(self):
        minion=Infernal(owner=self.owner,source="board")
        self.owner.recruit(minion)
        super(self.__class__,self).invoke()

class DIE_INSECT(Hero_Power):
    def __init__(self,name="DIE, INSECT!",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        self.class_name="Neutral"
    
    def invoke(self):
        target_pool=self.owner.enemy_characters()
        target=random.choice(target_pool)
        pyroblast_animation(self, target)
        self.deal_damage([target], [8])
        super(self.__class__,self).invoke(target)
                
class Obelisks_Eye(Hero_Power):
    def __init__(self,name="Obelisk's Eye",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        self.class_name="Priest"
        self.targeted = True
        self.strength = 3
        self.effect_message = "restore "+str(self.strength)+" health, +3/+3 for minion"
  
    def invoke(self,target=None):
        lesser_heal_animation(self.owner,target)
        target.restore_health(self.strength,self)
        time.sleep(0.5)
        if target.isMinion():
            target.buff_stats(3,3)
        super(self.__class__,self).invoke(target)
                              
class Spell(Card):
    def __init__(self,name="Null Spell",owner=None,source=None):
        super(Spell,self).__init__(name,owner,source)
        self.isSpell=True

    def is_valid_on(self,target):
        return self.landed_board_area() in ["Board","Opponent"]
    
    def invoke(self):
        #pygame.event.pump()
        
        if self in self.owner.hand:
            self.owner.hand.remove(self)
        if self.board_area=="Hand": 
            fade_out_animation(self.image, self, (self.rect.x,self.rect.y), duration=60)
        self.owner.board.spell_graves[self.owner.side].append(self)
        self.board_area="Grave"
        self.current_cost=self.cost
        self.ephemeral=False
        self.transform_in_hand="Transform in hand" in self.abilities

    def deal_damage(self,targets,amounts,skip_animation=False):
        boost=self.get_spell_damage_boost()
        total_damages=[amount+boost for amount in amounts]
        effect_modifier=self.owner.board.get_buff(self)["double effect"]
        for i in range(effect_modifier):
            total_damages=[damage*2 for damage in total_damages]
        super(Spell,self).deal_damage(targets, total_damages,skip_animation=skip_animation)

    def deal_split_damage(self,targets,shots=3,damage=1,effect=None,speed=30,curve=False):
        total_shots=shots+self.get_spell_damage_boost()
        effect_modifier=self.owner.board.get_buff(self)["double effect"]
        for i in range(effect_modifier):
            total_shots*=2
        super(Spell,self).deal_split_damage(targets, total_shots, damage, effect, speed, curve)

    def get_spell_damage_boost(self):
        self_boost     = sum([card.current_spell_damage_boost for card in self.friendly_minions()+self.owner.board.weapons[self.side]])
        opponent_boost = sum([card.current_opponent_spell_damage_boost for card in self.enemy_minions()+self.owner.board.weapons[-self.side]])
        return self_boost+opponent_boost

    def fizzle(self):
        if self in self.owner.hand:
            self.owner.hand.remove(self)
        fade_out_animation(self.image, self, (self.rect.x,self.rect.y), duration=30)
            
    def cast_on_random_target(self):
        spell=self
        spell.owner.board.random_select=True
        spell.initialize_location((SCREEN_WIDTH/2,SCREEN_HEIGHT/2))
        if "Choose One" in self.abilities or "Choose Twice" in self.abilities:
            spell=random.choice(self.options)(owner=self.owner)
            spell.random_select=True
        if "Targeted" in spell.tags:
            target_pool=[]
            for entity in spell.owner.minions+spell.owner.opponent.minions+[spell.owner,spell.owner.opponent]:
                if spell.is_valid_on(entity) and not (entity is not None and not entity.is_targetable()):
                    target_pool.append(entity)
            if len(target_pool)>0:
                target=random.choice(target_pool)
                spell.invoke(target)
            else:
                spell.fizzle()
        else:
            if spell.is_valid_on(None):
                spell.invoke(target=None)
            else:
                spell.fizzle()
                
        spell.owner.board.random_select=False
                        
class Choose_One_Spell(Spell):
    def __init__(self,name="Choose One Spell",owner=None):#Uncollectible
        super(Choose_One_Spell,self).__init__(name,owner)
        
    def invoke(self,target):
        selected_card = choose_one([option(owner=self.owner) for option in self.options])
        if selected_card is not None:
            self.owner.board.exclude.append(self)
            selected_card.origin=self
            if "Targeted" in selected_card.tags:
                target=selected_card.get_target()
                if target is not None and target!="Empty":
                    super(Choose_One_Spell,self).invoke()
                    selected_card.invoke(target)
            else:
                super(Choose_One_Spell,self).invoke()
                selected_card.invoke()

            if selected_card in self.owner.spell_grave:
                self.owner.spell_grave.remove(selected_card)
            self.owner.board.exclude.remove(self)  

class Choose_Twice_Spell(Spell):
    def __init__(self,name="Choose Twice Spell",owner=None):#Uncollectible
        super(Choose_Twice_Spell,self).__init__(name,owner)
        
    def invoke(self,target):
        self.owner.board.exclude.append(self)
        for i in range(2):
            selected_card = choose_one([option(owner=self.owner) for option in self.options])
            if selected_card is not None:
                selected_card.origin=self
                selected_card.invoke()
                if selected_card.board_area=="Grave": #Successfully cast
                    self.owner.spell_grave.remove(selected_card)
        super(Choose_Twice_Spell,self).invoke()
        self.owner.board.exclude.remove(self)  
                             
class The_Coin(Spell):
    def __init__(self,name="The Coin",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        self.owner.current_mana+=1
            
class Armor_Plating(Spell):
    def __init__(self,name="Armor Plating",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None and target.isMinion()
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        mech_buff_animation(target)
        target.buff_stats(0,1)

class Emergency_Coolant(Spell):
    def __init__(self,name="Emergency Coolant",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None and target.isMinion()
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        mech_buff_animation(target)
        target.get_frozen()

class Finicky_Cloakfield(Spell):
    def __init__(self,name="Finicky Cloakfield",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None and target.isMinion()
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        mech_buff_animation(target)
        target.temporary_effects['stealth']=2

class Reversing_Switch(Spell):
    def __init__(self,name="Reversing Switch",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None and target.isMinion()
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        mech_buff_animation(target)
        target.swap_stats()

class Rusty_Horn(Spell):
    def __init__(self,name="Rusty Horn",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None and target.isMinion()
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        mech_buff_animation(target)
        target.gain_taunt()
        
class Time_Rewinder(Spell):
    def __init__(self,name="Time Rewinder",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None and target.isMinion()
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        mech_buff_animation(target)
        target.return_hand(reset=True)
                                
class Whirling_Blades(Spell):
    def __init__(self,name="Whirling Blades",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None and target.isMinion()
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        mech_buff_animation(target)
        target.buff_stats(1,0)
                
class Crackling_Shield(Spell):
    def __init__(self,name="Crackling Shield",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None and target.isMinion()
    
    def invoke(self,target):
        target.gain_divine_shield()

class Flaming_Claws(Spell):
    def __init__(self,name="Flaming Claws",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None and target.isMinion()
    
    def invoke(self,target):
        buff_animation(target)
        target.buff_stats(3,0)
            
class Rocky_Carapace(Spell):
    def __init__(self,name="Rocky Carapace",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None and target.isMinion()
    
    def invoke(self,target):
        buff_animation(target)
        target.buff_stats(0,3)
                        
class Volcanic_Might(Spell):
    def __init__(self,name="Volcanic Might",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None and target.isMinion()
    
    def invoke(self,target):
        buff_animation(target)
        target.buff_stats(1,1)


#def living_spore_deathrattle(self):
    #plant1=Plant(owner=self.owner,source=self.location)
    #plant2=Plant(owner=self.owner,source=self.location)
    #self.summon(plant1)
    #self.summon(plant2)
                    
class Living_Spores(Spell):

    def __init__(self,name="Living Spores",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion()
    
    def invoke(self,target):
        buff_animation(target)      
        self.location=target.location
        target.deathrattles.append([MethodType(self.deathrattle.__func__,target),"Summon two 1/1 plants"])
        target.has_deathrattle=True
        
    def deathrattle(self):
        plant1=Plant(owner=self.owner,source=self.location)
        plant2=Plant(owner=self.owner,source=self.location)
        self.summon(plant1)
        self.summon(plant2)

class Lightning_Speed(Spell):
    def __init__(self,name="Lightning Speed",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None and target.isMinion()
    
    def invoke(self,target):
        buff_animation(target)
        target.gain_windfury()

class Liquid_Membrane(Spell):
    def __init__(self,name="Liquid Membrane",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None and target.isMinion()
    
    def invoke(self,target):
        buff_animation(target)
        target.gain_elusive()

class Massive(Spell):
    def __init__(self,name="Massive",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None and target.isMinion()
    
    def invoke(self,target):
        buff_animation(target)
        target.gain_taunt()
            
class Shrouding_Mist(Spell):
    def __init__(self,name="Shrouding Mist",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None and target.isMinion()
    
    def invoke(self,target):
        target.gain_stealth()
            
class Poison_Spit(Spell):
    def __init__(self,name="Poison Spit",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None and target.isMinion()
    
    def invoke(self,target):
        buff_animation(target)
        target.gain_poisonous()

'''Demon Hunter Spells'''                        
class Blur(Spell):
    def __init__(self,name="Blur",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        zodiac_animation(self.owner, self.card_class)
        self.owner.temporary_effects['immune']=True

class Twin_Slice(Spell):
    def __init__(self,name="Twin Slice",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        zodiac_animation(self.owner, self.card_class)
        self.owner.current_atk+=1
    
        card=Second_Slice(owner=self.owner)
        card.appear_in_hand()
   
class Second_Slice(Spell):
    def __init__(self,name="Second Slice",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        zodiac_animation(self.owner, self.card_class)
        self.owner.current_atk+=1

class Consume_Magic(Spell):
    def __init__(self,name="Consume Magic",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def is_valid_on(self, target):
        return target is not None and target.isMinion() and target.side==-self.side

    def invoke(self,target):
        super(self.__class__,self).invoke()
        self.silence(target)
            
    def outcast(self):
        super(self.__class__,self).outcast()
        self.owner.draw()
        
class Mana_Burn(Spell):
    def __init__(self,name="Mana Burn",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def invoke(self,target):
        super(self.__class__,self).invoke()
        zodiac_animation(self.owner, self.card_class)
        card=Mana_Burn_Effect(owner=self.owner.opponent)
        
class Mana_Burn_Effect(Enchantment):
    def __init__(self,name="Mana Burn",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_events.append(("start of turn",self.trigger_effect))
        
    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner:
            self.owner.gain_mana(-2)
            
    def trigger_remove(self, triggering_player):
        if triggering_player is self.owner:
            self.destroy()
            self.owner.gain_mana(2,empty=True)

class Embrace_the_Shadow(Spell):
    def __init__(self,name="Embrace the Shadow",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def invoke(self,target):
        super(self.__class__,self).invoke()
        zodiac_animation(self.owner, self.card_class)
        card=Embrace_the_Shadow_Effect(owner=self.owner)
        
class Embrace_the_Shadow_Effect(Enchantment):
    def __init__(self,name="Embrace the Shadow",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

    def ongoing_effect(self,target):
        if target.side==self.side:
            return {'heal reverse':True}
        else:
            return {} 
            
                                                                
class Chaos_Strike(Spell):
    def __init__(self,name="Chaos Strike",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        zodiac_animation(self.owner, zodiac=self.card_class)
        self.owner.current_atk+=2
        self.owner.draw()

class Coordinated_Strike(Spell):
    def __init__(self,name="Coordinated Strike",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        zodiac_animation(self.owner, self.card_class)
        for k in range(3):
            minion = Illidari_Initiate(owner=self.owner,source="board")
            self.owner.recruit(minion)

class Command_the_Illidari(Spell):
    def __init__(self,name="Command the Illidari",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        zodiac_animation(self.owner, self.card_class)
        for k in range(6):
            minion = Illidari_Initiate(owner=self.owner,source="board")
            self.owner.recruit(minion)

class Blade_Dance(Spell):
    def __init__(self,name="Blade Dance",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        target_pool=self.enemy_minions()
        if len(target_pool)>0:
            targets=random.sample(target_pool,k=min(3,len(target_pool)))
            soul_cleave_animation(self, targets)
            self.deal_damage(targets, [self.owner.get_current_atk()]*len(targets))
                        
class Soul_Cleave(Spell):
    def __init__(self,name="Soul Cleave",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.lifesteal=True
     
    def is_valid_on(self, target):
        return len(self.enemy_minions())>0
       
    def invoke(self,target):
        super(self.__class__,self).invoke()
        enemy_minions=self.enemy_minions()
        targets=random.sample(self.enemy_minions(),k=min(2,len(enemy_minions)))
        soul_cleave_animation(self,targets)
        self.deal_damage(targets, [2]*len(targets))

class Feast_of_Souls(Spell):
    def __init__(self,name="Feast of Souls",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        zodiac_animation(self.owner, self.card_class)
        for i in range(len(self.owner.minions_died[self.owner.turn])):
            self.owner.draw()
        
class Soul_Split(Spell):
    def __init__(self,name="Soul Split",owner=None):
        super(self.__class__,self).__init__(name,owner)
  
    def is_valid_on(self, target):
        return target is not None and target.isMinion() and target.side==self.side and target.has_race("Demon")
       
    def invoke(self,target):
        super(self.__class__,self).invoke()
        minion=getattr(card_collection,database.cleaned(target.name))(owner=self.owner,source="board")
        self.owner.recruit(minion)
        minion.copy_stats(target)

class Eye_Beam(Spell):
    def __init__(self,name="Eye Beam",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.lifesteal=True
    
    def is_valid_on(self, target):
        return target is not None and target.isMinion()
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        eye_beam_animation(self,target)
        self.deal_damage([target],[3])
    
    def overriding_ongoing_effect(self,target):
        if target is self and target.board_area=="Hand" and self.outcasted():
            return {'cost':1}
        else:
            return {} 
    
    def outcast(self):
        super(self.__class__,self).outcast()
                                                                  
class Chaos_Nova(Spell):
    def __init__(self,name="Chaos Nova",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        minions=self.all_minions()
        chaos_nova_animation(self)
        self.deal_damage(minions, [4]*len(minions))

class Inner_Demon(Spell):
    def __init__(self,name="Inner Demon",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        inner_demon_animation(self)
        self.owner.current_atk+=8
                
'''Druid Spells'''                        
class Innervate(Spell):
    def __init__(self,name="Innervate",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        wild_growth_animation(self)
        if self.owner.current_mana<10:
            self.owner.current_mana+=1

class Wild_Growth(Spell):
    def __init__(self,name="Wild Growth",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        wild_growth_animation(self)
        if self.owner.mana<10:
            self.owner.gain_mana(empty=True)
        else:
            card=Excess_Mana(owner=self.owner)
            card.initialize_location(self.location)
            card.appear_in_hand()

class Excess_Mana(Spell):
    def __init__(self,name="Excess Mana",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        wild_growth_animation(self)
        self.owner.draw()

class Moonfire(Spell):
    def __init__(self,name="Moonfire",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        moonfire_animation(self,target)
        self.deal_damage([target],[1])

class Claw(Spell):
    def __init__(self,name="Claw",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        claw_animation(self)
        self.owner.current_atk+=2
        self.owner.increase_shield(2)

class Mark_of_the_Wild(Spell):
    def __init__(self,name="Mark of the Wild",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None and target.isMinion()
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        druid_buff_animation(self,target)
        target.buff_stats(2,2)
        target.gain_taunt()

class Naturalize(Spell):
    def __init__(self,name="Naturalize",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None and target.isMinion()
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        wrath_animation(self,target)
        target.destroy()
        self.owner.opponent.draw(2)
                                
class Healing_Touch(Spell):
    def __init__(self,name="Healing Touch",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        healing_touch_animation(self,target)
        self.heal([target],[8])

class Savage_Roar(Spell):
    def __init__(self,name="Savage Roar",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        savage_roar_animation(self,self.friendly_characters())
        for minion in self.friendly_minions():
            minion.current_atk+=2
        self.owner.current_atk+=2
        
class Swipe(Spell):
    def __init__(self,name="Swipe",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None and target.side==-self.side
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        swipe_animation(self)
        targets=self.enemy_characters()
        damages=[1]*len(targets)
        damages[targets.index(target)]=4
        self.deal_damage(targets, damages)

class Starfire(Spell):
    def __init__(self,name="Starfire",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        starfire_animation(self,target)
        self.deal_damage([target], [5])
        self.owner.draw()
                                                                                                               
class Power_of_the_Wild(Choose_One_Spell):
    def __init__(self,name="Power of the Wild",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.options=[Leader_of_the_Pack,Summon_a_Panther]

class Leader_of_the_Pack(Spell):
    def __init__(self,name="Leader of the Pack",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target=None):
        super(self.__class__,self).invoke()
        leader_of_the_pack_animation(self)
        for minion in self.friendly_minions():
            minion.buff_stats(1,1)
            
class Summon_a_Panther(Spell):
    def __init__(self,name="Summon a Panther",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target=None):
        super(self.__class__,self).invoke()
        zodiac_animation(self.owner,zodiac=self.card_class)
        panther=Panther_Power_of_the_Wild(owner=self.owner,source="board")
        self.owner.recruit(panther)

class Wrath(Choose_One_Spell):
    def __init__(self,name="Wrath",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.options=[Solar_Wrath,Natures_Wrath]
            
class Solar_Wrath(Spell):
    def __init__(self,name="Solar Wrath",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self,target):
        return target is not None and target.isMinion() and target.is_targetable()
    
    def invoke(self,target=None):
        if target is None:
            target=choose_target(self.owner, target="minion", message=self.card_text)
        if self.is_valid_on(target):
            super(self.__class__,self).invoke()
            wrath_animation(self,target)
            self.deal_damage([target],[3])

class Natures_Wrath(Spell):
    def __init__(self,name="Nature's Wrath",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self,target):
        return target is not None and target.isMinion() and target.is_targetable()
    
    def invoke(self,target=None):
        if target is None:
            target=choose_target(self.owner, target="minion", message=self.card_text)
        if self.is_valid_on(target):
            super(self.__class__,self).invoke()
            wrath_animation(self,target)
            self.deal_damage([target],[1])
            self.owner.draw()

class Mark_of_Nature(Choose_One_Spell):
    def __init__(self,name="Mark of Nature",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.options=[Tigers_Fury,Thick_Hide]

class Tigers_Fury(Spell):
    def __init__(self,name="Tiger's Fury",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self,target):
        return target is not None and target.isMinion() and target.is_targetable()
    
    def invoke(self,target=None):
        if target is None:
            target=choose_target(self.owner, target="minion", message=self.card_text)
        if self.is_valid_on(target):
            super(self.__class__,self).invoke()
            druid_buff_animation(self,target)
            target.buff_stats(4,0)

class Thick_Hide(Spell):
    def __init__(self,name="Thick Hide",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self,target):
        return target is not None and target.isMinion() and target.is_targetable()
    
    def invoke(self,target=None):
        if target is None:
            target=choose_target(self.owner, target="minion", message=self.card_text)
        if self.is_valid_on(target):
            super(self.__class__,self).invoke()
            druid_buff_animation(self,target)
            target.buff_stats(0,4)
            target.gain_taunt()

class Soul_of_the_Forest(Spell):
    def __init__(self,name="Soul of the Forest",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def invoke(self,target):
        if len(self.friendly_minions())>0:
            super(self.__class__,self).invoke()
            zodiac_animation(self.owner, self.card_class)     
            for minion in self.friendly_minions():
                minion.deathrattles.append([MethodType(self.deathrattle.__func__,minion),"Summon a 2/2 treant"])
                minion.has_deathrattle=True
        
    def deathrattle(self):
        treant=Treant_Classic(owner=self.owner)
        self.summon(treant)
    
class Gift_of_the_Wild(Spell):
    def __init__(self,name="Gift of the Wild",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return len(self.friendly_minions())>0
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        zodiac_animation(self.owner, self.card_class)
        minions=self.friendly_minions()
        gift_of_the_wild_animation(self,minions) 
        for minion in minions:
            minion.buff_stats(2,2)
            minion.gain_taunt()

class Savagery(Spell):
    def __init__(self,name="Savagery",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None and target.isMinion() and self.owner.get_current_atk()>0
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        savagery_animation(self,target)
        self.deal_damage([target],[self.owner.get_current_atk()])
            
class Bite(Spell):
    def __init__(self,name="Bite",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        bite_animation(self)
        self.owner.current_atk+=4
        self.owner.increase_shield(4)

class Starfall(Choose_One_Spell):
    def __init__(self,name="Starfall",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.options=[Starlord,Stellar_Drift]

class Starlord(Spell):
    def __init__(self,name="Starlord",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self,target):
        return target is not None and target.isMinion() and target.is_targetable()
    
    def get_target(self):
        minion=choose_target(chooser=self.owner,target="minion",message="deal 5 damage")
        return minion
        
    def invoke(self,target=None):
        if self.is_valid_on(target):
            super(self.__class__,self).invoke()
            starfire_animation(self,target)
            self.deal_damage([target],[5])

class Stellar_Drift(Spell):
    def __init__(self,name="Stellar Drift",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target=None):
        super(self.__class__,self).invoke()
        targets=self.enemy_minions()
        steller_drift_animation(self)
        self.deal_damage(targets, [2]*len(targets))

class Nourish(Choose_One_Spell):
    def __init__(self,name="Nourish",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.options=[Rampant_Growth,Enrich]

class Rampant_Growth(Spell):
    def __init__(self,name="Rampant Growth",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target=None):
        super(self.__class__,self).invoke()
        wild_growth_animation(self)
        self.owner.gain_mana(2)
            
class Enrich(Spell):
    def __init__(self,name="Enrich",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target=None):
        super(self.__class__,self).invoke()
        wild_growth_animation(self)
        self.owner.draw(3)
        
class Force_of_Nature(Spell):
    def __init__(self,name="Force of Nature",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return not self.owner.board.isFull(self.owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        zodiac_animation(self.owner, self.card_class)
        for i in range(3):
            minion=Treant_Force_of_Nature(owner=self.owner,source="board")
            self.owner.recruit(minion,speed=80)
         
class Poison_Seeds(Spell):
    def __init__(self,name="Poison Seeds",owner=None):
        super(self.__class__,self).__init__(name,owner)
       
    def invoke(self,target):
        super(self.__class__,self).invoke()
        minions=self.all_minions()
        poison_seeds_animation(self)
        destroy_multiple_animation(minions)
        for minion in minions:
            treant=Treant_Poison_Seeds(owner=minion.owner)
            minion.summon(treant)
            minion.destroy(skip_animation=True)
                  
class Recycle(Spell):
    def __init__(self,name="Recycle",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion() and target.side==-self.side
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        recycle_animation(self,target)
        target.shuffle_into_deck()

class Dark_Wispers(Choose_One_Spell):
    def __init__(self,name="Dark Wispers",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.options=[Call_the_Guardians,Natures_Defense]

class Natures_Defense(Spell):
    def __init__(self,name="Nature's Defense",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target=None):
        if not self.owner.board.isFull(self.owner):
            super(self.__class__,self).invoke()
            zodiac_animation(self.owner, self.card_class)
            for i in range(5):
                minion=Wisp(owner=self.owner,source="board")
                self.owner.recruit(minion,speed=180)

class Call_the_Guardians(Spell):
    def __init__(self,name="Call the Guardians",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None and target.isMinion() and target.is_targetable()

    def invoke(self,target=None):
        if target is None:
            target=choose_target(self.owner, target="minion", message=self.card_text)
        if self.is_valid_on(target):
            super(self.__class__,self).invoke()
            druid_buff_animation(self, target)
            target.buff_stats(5,5)
            target.gain_taunt()

class Tree_of_Life(Spell):
    def __init__(self,name="Tree of Life",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target):
        targets=self.all_characters()
        tree_of_life_animation(self,targets)
        self.heal(targets,[target.temp_hp-target.current_hp for target in targets])

class Living_Roots(Choose_One_Spell):
    def __init__(self,name="Living Roots",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.options=[Grasping_Roots,One_Two_Trees]

class Grasping_Roots(Spell):
    def __init__(self,name="Grasping Roots",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None and target.is_targetable()

    def invoke(self,target=None):
        if target is None:
            target=choose_target(self.owner, target="character", message=self.card_text)
        if self.is_valid_on(target):
            super(self.__class__,self).invoke()
            wrath_animation(self, target)
            self.deal_damage([target],[2])
            
class One_Two_Trees(Spell):
    def __init__(self,name="One, Two, Trees!",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target=None):
        super(self.__class__,self).invoke()
        zodiac_animation(self.owner,zodiac=self.card_class)
        for i in range(2):
            minion=Sapling(owner=self.owner,source="board")
            self.owner.recruit(minion)

class Mulch(Spell):
    def __init__(self,name="Mulch",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion()
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        recycle_animation(self,target)
        target.destroy()
        minion = database.get_random_cards("[type]='Minion'", owner=self.owner.opponent, k=1)[0]
        minion.appear_in_hand()

class Astral_Communion(Spell):
    def __init__(self,name="Astral Communion",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        zodiac_animation(self.owner, self.card_class)
        if self.owner.mana<10:
            self.owner.gain_mana(10)
            self.owner.discard_hand()
        else:
            card=Excess_Mana(owner=self.owner)
            card.appear_in_hand()

class Raven_Idol(Choose_One_Spell):
    def __init__(self,name="Raven Idol",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.options=[Break_Free,Awakened]

class Break_Free(Spell):
    def __init__(self,name="Break Free",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target=None):
        super(self.__class__,self).invoke()
        card=self.discover(filter_str="[type]='Minion'")
        if card is not None:
            card.hand_in()

class Awakened(Spell):
    def __init__(self,name="Awakened",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target=None):
        super(self.__class__,self).invoke()
        card=self.discover(filter_str="[type]='Spell'")
        if card is not None:
            card.hand_in()

class Mark_of_YShaarj(Spell):
    def __init__(self,name="Mark of Y'Shaarj",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None and target.isMinion()
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        druid_buff_animation(self,target)
        target.buff_stats(2,2)
        if target.has_race("Beast"):
            self.owner.draw()
            
class Feral_Rage(Choose_One_Spell):
    def __init__(self,name="Feral Rage",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.options=[Evolve_Spines,Evolve_Scales]

class Evolve_Spines(Spell):
    def __init__(self,name="Evolve Spines",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)

    def invoke(self,target=None):
        super(self.__class__,self).invoke()
        self.owner.current_atk+=4
            
class Evolve_Scales(Spell):
    def __init__(self,name="Evolve Scales",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target=None):
        super(self.__class__,self).invoke()
        self.owner.increase_shield(8)

class Wisps_of_the_Old_Gods(Choose_One_Spell):
    def __init__(self,name="Wisps of the Old Gods",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.options=[Many_Wisps,Big_Wisps]

class Many_Wisps(Spell):
    def __init__(self,name="Many Wisps",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target=None):
        if not self.owner.board.isFull(self.owner):
            super(self.__class__,self).invoke()
            zodiac_animation(self.owner, self.card_class)
            for i in range(7):
                minion=Wisp_Wisps_of_the_Old_Gods(owner=self.owner,source="board")
                self.owner.recruit(minion,speed=180)

class Big_Wisps(Spell):
    def __init__(self,name="Big Wisps",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)

    def invoke(self,target=None):
        super(self.__class__,self).invoke()
        zodiac_animation(self.owner, self.card_class)
        minions=self.friendly_minions()
        gift_of_the_wild_animation(self,minions) 
        for minion in minions:
            minion.buff_stats(2,2)

class Moonglade_Portal(Spell):
    def __init__(self,name="Moonglade Portal",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        healing_touch_animation(self,target)
        self.heal([target],[6])
        minion = database.get_random_cards("[type]='Minion' AND [cost]=6", self.owner, 1)[0]
        self.owner.recruit(minion)

class Mark_of_the_Lotus(Spell):
    def __init__(self,name="Mark of the Lotus",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return len(self.friendly_minions())>0
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        zodiac_animation(self.owner, self.card_class)
        minions=self.friendly_minions()
        gift_of_the_wild_animation(self,minions) 
        for minion in minions:
            minion.buff_stats(1,1)

class Jade_Blossom(Spell):
    def __init__(self,name="Jade Blossom",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return len(self.owner.minions)<7 or self.owner.mana<10
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        wild_growth_animation(self)
        self.owner.gain_mana(empty=True)
        minion=Jade_Golem(owner=self.owner,source="board")
        self.owner.recruit(minion)
        
class Jade_Idol(Choose_One_Spell):
    def __init__(self,name="Jade Idol",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.options=[Cut_From_Jade,Jade_Stash]

class Cut_From_Jade(Spell):
    def __init__(self,name="Cut From Jade",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target=None):
        if not self.owner.board.isFull(self.owner):
            super(self.__class__,self).invoke()
            zodiac_animation(self.owner, self.card_class)
            minion=Jade_Golem(owner=self.owner,source="board")
            self.owner.recruit(minion)

class Jade_Stash(Spell):
    def __init__(self,name="Jade Stash",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)

    def invoke(self,target=None):
        super(self.__class__,self).invoke()
        for i in range(3):
            card=Jade_Idol(owner=self.owner)
            card.initialize_location(self.owner.location)
            card.shuffle_into_deck()

class Pilfered_Power(Spell):
    def __init__(self,name="Pilfered Power",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target=None):
        super(self.__class__,self).invoke()
        wild_growth_animation(self)
        self.owner.gain_mana(len(self.friendly_minions()),empty=True)

class Lunar_Visions(Spell):
    def __init__(self,name="Lunar Visions",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        zodiac_animation(self.owner, self.card_class)
        for i in range(2):
            card=self.owner.draw()
            if card.isMinion():
                card.current_cost-=2

class Earthen_Scales(Spell):
    def __init__(self,name="Earthen Scales",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion() and target.side==self.side
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        druid_buff_animation(self, target)
        target.buff_stats(1,1)
        self.owner.increase_shield(target.get_current_atk())

class Evolving_Spores(Spell):
    def __init__(self,name="Evolving Spores",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        minions=self.friendly_minions()
        if len(minions)>0:
            choice=minions[0].adapt()
            minions.remove(minions[0])
            for minion in minions:
                minion.adapt(choice=choice)

class Living_Mana(Spell):
    def __init__(self,name="Living Mana",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        n=7-len(self.owner.minions)
        for i in range(n):
            self.owner.gain_mana(-1,empty=(self.owner.mana>self.owner.current_mana))
            minion=Mana_Treant(owner=self.owner,source="board")
            self.owner.recruit(minion)
            if self.owner.board.isFull(self.owner):
                break

class Gnash(Spell):
    def __init__(self,name="Gnash",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        bite_animation(self)
        self.owner.current_atk+=3
        self.owner.increase_shield(3)

class Webweave(Spell):
    def __init__(self,name="Webweave",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return not self.owner.board.isFull(self.owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        zodiac_animation(self.owner, self.card_class)
        for i in range(2):
            minion=Frost_Widow(owner=self.owner,source="board")
            self.owner.recruit(minion,speed=80)

class Spreading_Plague(Spell):
    def __init__(self,name="Spreading Plague",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def invoke(self,target):
        super(self.__class__,self).invoke()
        minion=Scarab_Beetle(owner=self.owner,source="board")
        self.owner.recruit(minion)
        while len(self.enemy_minions())>len(self.friendly_minions()):
            minion=Scarab_Beetle(owner=self.owner,source="board")
            self.owner.recruit(minion)

class Ultimate_Infestation(Spell):
    def __init__(self,name="Ultimate Infestation",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None
       
    def invoke(self,target):
        super(self.__class__,self).invoke()
        wrath_animation(self, target)
        self.deal_damage([target], [5])
        self.owner.increase_shield(5)
        self.owner.draw(5)
        minion=Ghoul_Infestor(owner=self.owner,source="board")
        self.owner.recruit(minion)

class Barkskin(Spell):
    def __init__(self,name="Barkskin",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None and target.isMinion()
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        druid_buff_animation(self,target)
        target.buff_stats(0,3)
        self.owner.increase_shield(3)

class Oaken_Summons(Spell):
    def __init__(self,name="Oaken Summons",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        shield_block_animation(self)
        self.owner.increase_shield(6)
        
        minion=self.owner.search_card_based_cost(self.owner.deck.cards,card_type="Minion",cost=4,compare="__le__")
        if minion is not None:
            self.recruit(minion)
                
class Lesser_Jasper_Spellstone(Spell):
    def __init__(self,name="Lesser Jasper Spellstone",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.trigger_event_type="gain armor"
        self.upgrade_target=Jasper_Spellstone
        self.counter=0
        self.goal=3

    def is_valid_on(self, target):
        return target is not None and target.isMinion()
       
    def invoke(self,target):
        super(self.__class__,self).invoke()
        wrath_animation(self, target)
        self.deal_damage([target], [2])
        
    def trigger_effect(self, triggering_entity):
        if triggering_entity[0] is self.owner:
            self.counter+=triggering_entity[1]
            if self.counter>=self.goal:
                self.upgrade()

class Jasper_Spellstone(Spell):
    def __init__(self,name="Jasper Spellstone",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        self.trigger_event_type="gain armor"
        self.upgrade_target=Greater_Jasper_Spellstone
        self.counter=0
        self.goal=3

    def is_valid_on(self, target):
        return target is not None and target.isMinion()
       
    def invoke(self,target):
        super(self.__class__,self).invoke()
        wrath_animation(self, target)
        self.deal_damage([target], [4])
        
    def trigger_effect(self, triggering_entity):
        if triggering_entity[0] is self.owner:
            self.counter+=triggering_entity[1]
            if self.counter>=self.goal:
                self.upgrade()

class Greater_Jasper_Spellstone(Spell):
    def __init__(self,name="Greater Jasper Spellstone",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion()
       
    def invoke(self,target):
        super(self.__class__,self).invoke()
        wrath_animation(self, target)
        self.deal_damage([target], [6])

class Branching_Paths(Choose_Twice_Spell):
    def __init__(self,name="Branching Paths",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.options=[Eat_the_Mushroom,Explore_the_Darkness,Loot_the_Chest]

class Eat_the_Mushroom(Spell):
    def __init__(self,name="Eat the Mushroom",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target=None):
        super(self.__class__,self).invoke()
        self.owner.draw()

class Explore_the_Darkness(Spell):
    def __init__(self,name="Explore the Darkness",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target=None):
        super(self.__class__,self).invoke()
        self.buff_multiple(atk=1)

class Loot_the_Chest(Spell):
    def __init__(self,name="Loot the Chest",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target=None):
        super(self.__class__,self).invoke()
        self.owner.increase_shield(6)

class Witchwood_Apple(Spell):
    def __init__(self,name="Witchwood Apple",owner=None):
        super(self.__class__,self).__init__(name,owner)
 
    def invoke(self,target):
        super(self.__class__,self).invoke()
        for i in range(3):
            card=Treant_Witchwood_Apple(owner=self.owner)
            card.appear_in_hand(speed=25)

class Ferocious_Howl(Spell):
    def __init__(self,name="Ferocious Howl",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        self.owner.draw()
        shield_block_animation(self)
        self.owner.increase_shield(len(self.owner.hand))
        
class Witching_Hour(Spell):
    def __init__(self,name="Witching Hour",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def is_valid_on(self, target):
        return len(self.owner.grave)>0
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        minion = self.owner.search_card(self.owner.grave,"Beast")
        minion_copy = minion.get_copy(owner=self.owner)
        minion_copy.initialzie_location("board")
        self.owner.recruit(minion)
        resurrect_animation(minion)

class Wispering_Woods(Spell):
    def __init__(self,name="Wispering_Woods",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target=None):
        super(self.__class__,self).invoke()
        zodiac_animation(self.owner, self.card_class)
        for i in range(len(self.owner.hand)):
            minion=Wisp_Wispering_Woods(owner=self.owner,source="board")
            self.owner.recruit(minion,speed=180)
                                                                                                                                                                                                                                                                                                                                                         
'''Hunter Spells'''                        
class Tracking(Spell):
    def __init__(self,name="Tracking",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        zodiac_animation(self.owner, self.card_class)
        cards=random.sample(self.owner.deck.cards,k=min(3,len(self.owner.deck.cards)))
        selected_card = choose_one(cards)
        for card in cards:
            self.owner.deck.cards.remove(card)
            if card is not selected_card:
                card.discard()
        if selected_card is not None:
            self.owner.deck.cards.insert(0,selected_card)
            self.owner.draw()

class Hunters_Mark(Spell):
    def __init__(self,name="Hunter's Mark",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def is_valid_on(self, target):
        return target is not None and target.isMinion()
    
    def invoke(self,target):
        if target is not None and target.isMinion():
            super(self.__class__,self).invoke()
            hunters_mark_animation(self,target)
            target.temp_hp=1
            target.current_hp=1
            
class Animal_Companion(Spell):
    def __init__(self,name="Animal Companion",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        zodiac_animation(self.owner, self.card_class)
        companions=[Huffer,Huffer,Misha]
        companion = random.choice(companions)
        minion    = companion(owner=self.owner,source="board")
        self.owner.recruit(minion)
        
class Kill_Command(Spell):
    def __init__(self,name="Kill Command",owner=None):
        super(self.__class__,self).__init__(name,owner)
     
    def is_valid_on(self, target):
        return target is not None
       
    def invoke(self,target):
        super(self.__class__,self).invoke()
        damage=3
        if self.owner.control("Beast"):
            damage=5
        kill_command_animation(self,target)
        self.deal_damage([target], [damage])

class Multi_Shot(Spell):
    def __init__(self,name="Multi-Shot",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def is_valid_on(self, target):
        return len(self.enemy_minions())>0
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        enemy_minions=self.enemy_minions()
        minions=random.sample(self.enemy_minions(),k=min(2,len(enemy_minions)))
        multi_shot_animation(self,minions)
        self.deal_damage(minions, [3]*len(minions))
                                                                                          
class Arcane_Shot(Spell):
    def __init__(self,name="Arcane Shot",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        arcane_shot_animation(self,target)
        self.deal_damage([target],[2])

class Deadly_Shot(Spell):
    def __init__(self,name="Deadly Shot",owner=None):
        super(self.__class__,self).__init__(name,owner)
     
    def is_valid_on(self, target):
        return len(self.enemy_minions())>0
       
    def invoke(self,target):
        target_pool = self.enemy_minions()
        if len(target_pool)>0:
            super(self.__class__,self).invoke()
            target=random.choice(target_pool)
            snipe_animation(self,target)
            target.destroy()

class Unleash_the_Hounds(Spell):
    def __init__(self,name="Unleash the Hounds",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def is_valid_on(self, target):
        return len(self.enemy_minions())>0 and not self.owner.board.isFull(self.owner)
    
    def invoke(self,target):
        target_pool = self.enemy_minions()
        if len(target_pool)>0:
            super(self.__class__,self).invoke()
            for i in range(len(target_pool)):
                minion=Hound(owner=self.owner,source="board")
                self.owner.recruit(minion,speed=80)            

class Flare(Spell):
    def __init__(self,name="Flare",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        flare_animation(self)
        
        #All minions lose stealth
        for minion in self.all_minions():
            minion.has_stealth=False
            
        #Destroy all enemy secrets   
        secrets = self.enemy_secrets()
        for secret in secrets:
            secret.destroy()
            
        self.owner.draw()
            
class Explosive_Shot(Spell):
    def __init__(self,name="Explosive Shot",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None and target.isMinion()
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        explosive_shot_animation(self,target)
        targets=target.adjacent_minions()
        self.deal_damage([target]+targets,[5]+[2]*len(targets))
            
class Bestial_Wrath(Spell):
    def __init__(self,name="Bestial Wrath",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None and target.isMinion() and target.side==self.side and target.has_race("Beast")
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        hunter_buff_animation(self,target)
        target.current_atk+=2
        target.temporary_effects['immune']=True

class Cobra_Shot(Spell):
    def __init__(self,name="Cobra Shot",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None and target.isMinion()
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        multi_shot_animation(self,[target,target.owner])
        self.deal_damage([target,target.owner], [3,3])

class Call_Pet(Spell):
    def __init__(self,name="Call Pet",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def invoke(self,target):
        super(self.__class__,self).invoke()
        card = self.owner.draw()
        if card.has_race("Beast"):
            card.modify_cost(-4)

class Feign_Death(Spell):
    def __init__(self,name="Feign Death",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def invoke(self,target):
        super(self.__class__,self).invoke()
        zodiac_animation(self.owner, self.card_class)
        for minion in self.friendly_minions():
            minion.trigger_deathrattle()

class Quick_Shot(Spell):
    def __init__(self,name="Quick Shot",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        arcane_shot_animation(self,target)
        self.deal_damage([target], [3])
        if self.owner.empty_handed():
            self.owner.draw()                 

class Powershot(Spell):
    def __init__(self,name="Powershot",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None and target.isMinion()
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        powershot_animation(self,target)
        targets=target.adjacent_minions()
        self.deal_damage([target]+targets,[2]+[2]*len(targets))

class Ball_of_Spiders(Spell):
    def __init__(self,name="Ball of Spiders",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return not self.owner.board.isFull(self.owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        zodiac_animation(self.owner, self.card_class)
        for i in range(3):
            minion=Webspinner(owner=self.owner,source="board")
            self.owner.recruit(minion,speed=80)

class Lock_and_Load(Spell):
    def __init__(self,name="Lock and Load",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        card=Lock_and_Load_Effect(owner=self.owner)
        self.owner.board.background=background_dark

class Lock_and_Load_Effect(Enchantment):
    def __init__(self,name="Lock and Load",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_events.append(("play a card",self.trigger_effect))

    def trigger_effect(self, triggering_card):
        if triggering_card.isSpell and triggering_card.side==self.side:
            card = database.get_random_cards("[type]='Spell' AND [class] LIKE '%Hunter%'", owner=self.owner, k=1)[0]
            card.appear_in_hand()
    
    def trigger_remove(self, triggering_player):
        if triggering_player is self.owner:
            self.destroy()
            self.owner.board.background=background

class Explorers_Hat(Spell):
    def __init__(self,name="Explorer's Hat",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None and target.isMinion()
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        target.buff_stats(1,1)
        target.attachments["Explorer's Hat"]=self
        target.deathrattles.append([MethodType(self.deathrattle.__func__,target),"Add Explorer's Hat to your hand"])
     
    def deathrattle(self):
        card=Explorers_Hat(owner=self.attachments["Explorer's Hat"].owner)
        card.initialize_location(self.location)
        card.hand_in()
        
class On_the_Hunt(Spell):
    def __init__(self,name="On the Hunt",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None
       
    def invoke(self,target):
        super(self.__class__,self).invoke()
        on_the_hunt_animation(self,target)
        self.deal_damage([target], [1])
        minion=Mastiff(owner=self.owner,source="board")
        self.owner.recruit(minion)

class Infest(Spell):
    def __init__(self,name="Infest",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return len(self.owner.minions)>0
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        for target in self.owner.minions:
            target.deathrattles.append([MethodType(self.deathrattle.__func__,target),"add a random beast to owner's hand"])
            target.has_deathrattle=True
        
    def deathrattle(self):
        minion = database.get_random_cards("[type]='Minion' AND [race]='Beast'", self.owner, 1)[0]
        minion.initialize_location(self.location)
        minion.hand_in()
     
class Call_of_the_Wild(Spell):
    def __init__(self,name="Call of the Wild",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        zodiac_animation(self.owner, self.card_class)
        minion1=Huffer(owner=self.owner,source="board")
        minion2=Leokk(owner=self.owner,source="board")
        minion3=Misha(owner=self.owner,source="board")
        self.owner.recruit(minion1)
        self.owner.recruit(minion2)
        self.owner.recruit(minion3)

class Smugglers_Crate(Spell):
    def __init__(self,name="Smuggler's Crate",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        self.owner.buff_hand("Beast",atk=2,hp=2)

class Stolen_Goods(Spell):
    def __init__(self,name="Stolen Goods",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        targets=[] 
        for card in self.owner.hand:
            if card.isMinion() and "Taunt" in card.abilities:
                targets.append(card)
        minion=random.choice(targets)
        buff_hand_animation(self.owner,[minion])
        minion.buff_stats(3,3)

class Sleep_with_the_Fishes(Spell):
    def __init__(self,name="Sleep with the Fishes",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        warpath_animation(self)
        targets=[]
        minions=self.all_minions()
        for minion in minions:
            if minion.damaged():
                targets.append(minion)
        self.deal_damage(targets,[3]*len(targets))     

class Grievous_Bite(Spell):
    def __init__(self,name="Grievous Bite",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None and target.isMinion()
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        powershot_animation(self, target)
        targets=target.adjacent_minions()
        self.deal_damage([target]+targets,[3]+[2]*len(targets))

class Stampede(Spell):
    def __init__(self,name="Stampede",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        card=Stampede_Effect(owner=self.owner)
        self.owner.board.background=background_dark

class Stampede_Effect(Enchantment):
    def __init__(self,name="Stampede",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_events.append(("play a card",self.trigger_effect))

    def trigger_effect(self, triggering_card):
        if triggering_card.has_race("Beast") and triggering_card.side==self.side:
            card = database.get_random_cards("[race]='Beast'", owner=self.owner, k=1)[0]
            card.appear_in_hand()
    
    def trigger_remove(self, triggering_player):
        if triggering_player is self.owner:
            self.destroy()
            self.owner.board.background=background

class Dinomancy(Spell):
    def __init__(self,name="Dinomancy",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        new_hero_power=Dinomancy_Hero_Power(owner=self.owner)
        self.owner.gain_hero_power(new_hero_power)

class Play_Dead(Spell):
    def __init__(self,name="Play Dead",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion() and target.side==self.side and target.has_deathrattle
            
    def invoke(self,target):
        super(self.__class__,self).invoke()
        target.trigger_deathrattle()

class Toxic_Arrow(Spell):
    def __init__(self,name="Toxic Arrow",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion()
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        steady_shot_animation(self.owner, target)
        self.deal_damage([target], [2])
        if target.board_area=="Board":
            target.gain_poisonous()

class Flanking_Strike(Spell):
    def __init__(self,name="Flanking Strike",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None and target.isMinion()
            
    def invoke(self,target):
        super(self.__class__,self).invoke()
        snipe_animation(self, target)
        self.deal_damage([target], [3])
        minion=Wolf(owner=self.owner,source="board")
        self.owner.recruit(minion)

class Lesser_Emerald_Spellstone(Spell):
    def __init__(self,name="Lesser Emerald Spellstone",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.trigger_event_type="play a card"
        self.upgrade_target=Emerald_Spellstone
        self.counter=0
        self.goal=1

    def invoke(self,target):
        super(self.__class__,self).invoke()
        zodiac_animation(self.owner, self.card_class)
        for i in range(2):
            minion=Wolf(owner=self.owner,source="board")
            self.owner.recruit(minion)
        
    def trigger_effect(self, triggering_card):
        if triggering_card.side==self.side and isinstance(triggering_card, Secret):
            self.counter+=1
            if self.counter>=self.goal:
                self.upgrade()

class Emerald_Spellstone(Spell):
    def __init__(self,name="Emerald Spellstone",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        self.trigger_event_type="play a card"
        self.upgrade_target=Greater_Emerald_Spellstone
        self.counter=0
        self.goal=1

    def invoke(self,target):
        super(self.__class__,self).invoke()
        zodiac_animation(self.owner, self.card_class)
        for i in range(3):
            minion=Wolf(owner=self.owner,source="board")
            self.owner.recruit(minion)
        
    def trigger_effect(self, triggering_card):
        if triggering_card.side==self.side and isinstance(triggering_card, Secret):
            self.counter+=1
            if self.counter>=self.goal:
                self.upgrade()

class Greater_Emerald_Spellstone(Spell):
    def __init__(self,name="Greater Emerald Spellstone",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)

    def invoke(self,target):
        super(self.__class__,self).invoke()
        zodiac_animation(self.owner, self.card_class)
        for i in range(4):
            minion=Wolf(owner=self.owner,source="board")
            self.owner.recruit(minion)

class To_My_Side(Spell):
    def __init__(self,name="To My Side!",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        zodiac_animation(self.owner, self.card_class)
        companions=[Huffer,Huffer,Misha]
        companion = random.choice(companions)
        minion    = companion(owner=self.owner,source="board")
        self.owner.recruit(minion)
        if self.owner.deck.has_no_minions():
            companions.remove(companion)
            minion    = random.choice(companions)(owner=self.owner,source="board")
            self.owner.recruit(minion)

class Crushing_Walls(Spell):
    def __init__(self,name="Crushing Walls",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return len(self.enemy_minions())>0
            
    def invoke(self,target):
        super(self.__class__,self).invoke()
        i=0
        left_minion=self.owner.opponent.minions[i]
        while left_minion.has_dormant:
            i+=1
            left_minion=self.owner.opponent.minions[i]
        i=-1
        right_minion=self.owner.opponent.minions[i]
        while right_minion.has_dormant:
            i-=1
            right_minion=self.owner.opponent.minions[i]
            
        targets=[left_minion]
        if right_minion is not left_minion:
            targets.append(right_minion)
            crushing_wall_animation(self,targets)
        for minion in targets:
            minion.destroy()
            
class Dire_Frenzy(Spell):
    def __init__(self,name="Dire Frenzy",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion() and target.has_race("Beast")
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        hunter_buff_animation(self, target)
        target.buff_stats(3,3)
        for i in range(3):
            minion_copy=target.get_copy(owner=self.owner)
            minion_copy.copy_stats(target)
            minion_copy.initialize_location(target.location)
            minion_copy.shuffle_into_deck(reset_status=False,skip_zoom=(i>=1))

class Wing_Blast(Spell):
    def __init__(self,name="Wing Blast",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.tags.append("In-hand effect")

    def is_valid_on(self, target):
        return target is not None and target.isMinion()
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        razorpetal_animation(self, target)
        self.deal_damage([target], [4])

    def overriding_ongoing_effect(self,target):
        if target is self and target.board_area=="Hand" and self.owner.get_num_minions_died()>0:
            return {'cost':1}
        return {} 
                                                                                                                                                                                                                                                
'''Mage Spells'''                        
class Arcane_Missiles(Spell):
    def __init__(self,name="Arcane Missiles",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        zodiac_animation(self.owner, self.card_class)
        self.deal_split_damage(self.enemy_characters(),shots=3,damage=1,effect=get_image("images/arcane_missile.png",(80,80)),speed=20,curve=True)   
        
class Mirror_Image(Spell):
    def __init__(self,name="Mirror Image",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return not self.owner.board.isFull(self.owner)
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        zodiac_animation(self.owner, self.card_class)
        minion1=Mirror_Image_minion(owner=self.owner,source="board")
        minion2=Mirror_Image_minion(owner=self.owner,source="board")
        self.owner.recruit(minion1)
        self.owner.recruit(minion2)
 
class Arcane_Explosion(Spell):
    def __init__(self,name="Arcane Explosion",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        minions=self.enemy_minions()
        arcane_explosion_animation(self)
        self.deal_damage(minions, [1]*len(minions))
                   
class Frostbolt(Spell):
    def __init__(self,name="Frostbolt",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        frostbolt_animation(self,target)
        self.deal_damage([target],[3])
        target.get_frozen()
         
class Ice_Lance(Spell):
    def __init__(self,name="Ice Lance",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        frostbolt_animation(self,target)
        if target.frozen:
            self.deal_damage([target],[4])
        else:
            target.get_frozen()
        
class Arcane_Intellect(Spell):
    def __init__(self,name="Arcane Intellect",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        zodiac_animation(self.owner, self.card_class)
        self.owner.draw(2)

class Frost_Nova(Spell):
    def __init__(self,name="Frost Nova",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        minions=self.enemy_minions()
        frost_nova_animation(self)
        for minion in minions:
            minion.get_frozen()

class Fireball(Spell):
    def __init__(self,name="Fireball",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        fireball_animation(self,target)
        self.deal_damage([target],[6])

class Polymorph(Spell):
    def __init__(self,name="Polymorph",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion()
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        zodiac_animation(self.owner, self.card_class)
        sheep=Sheep(owner=target.owner,source=target.location)
        target.transform(sheep)

class Flamestrike(Spell):
    def __init__(self,name="Flamestrike",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        minions=self.enemy_minions()
        flamestrike_animation(self)
        self.deal_damage(minions, [4]*len(minions))

class Tome_of_Intellect(Spell):
    def __init__(self,name="Tome of Intellect",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        spell = database.get_random_cards("[type]='Spell' AND [class] LIKE '%Mage%'", self.owner, 1)[0]
        zodiac_animation(self.owner, self.card_class)
        spell.initialize_location(self.owner.location)
        spell.hand_in()
                
class Cone_of_Cold(Spell):
    def __init__(self,name="Cone of Cold",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None and target.isMinion()
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        cone_of_cold_animation(self,target)
        targets=target.adjacent_minions()
        self.deal_damage([target]+targets,[1]+[1]*len(targets))
        for target in [target]+targets:
            target.get_frozen()
            
class Blizzard(Spell):
    def __init__(self,name="Blizzard",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        targets=self.enemy_minions()
        blizzard_animation(self)
        self.deal_damage(targets, [2]*len(targets))
        for target in targets:
            target.get_frozen()

class Icicle(Spell):
    def __init__(self,name="Icicle",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion()
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        frostbolt_animation(self,target)
        self.deal_damage([target], [2])
        if target.frozen:
            self.owner.draw()

class Pyroblast(Spell):
    def __init__(self,name="Pyroblast",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        pyroblast_animation(self,target)
        self.deal_damage([target],[10])

class Flamecannon(Spell):
    def __init__(self,name="Flamecannon",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return len(self.enemy_minions())>0
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        target=random.choice(self.enemy_minions())
        flamecannon_animation(self,target)
        self.deal_damage([target],[4])

class Unstable_Portal(Spell):
    def __init__(self,name="Unstable Portal",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        minion = database.get_random_cards("[type]='Minion'", self.owner, 1)[0]
        unstable_portal_animation(self,minion)
        minion.hand_in()
        minion.modify_cost(-3)

class Echo_of_Medivh(Spell):
    def __init__(self,name="Echo of Medivh",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        targets=self.friendly_minions()
        if len(targets)>0:
            echo_of_medivh_animation(self,targets)
            for target in targets:
                minion = getattr(card_collection,database.cleaned(target.name))(owner=self.owner,source=target.location)
                minion.hand_in()

class Dragons_Breath(Spell):
    def __init__(self,name="Dragon's Breath",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        flamecannon_animation(self,target)
        self.deal_damage([target],[4])
        
    def ongoing_effect(self,target):
        if target is self and target.board_area=="Hand":
            n=self.owner.get_num_minions_died()
            return {'cost':-n}
        else:
            return {} 

class Flame_Lance(Spell):
    def __init__(self,name="Flame Lance",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion()
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        flame_lance_animation(self,target)
        self.deal_damage([target], [8])

class Arcane_Blast(Spell):
    def __init__(self,name="Arcane Blast",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion()
        
    def invoke(self,target): 
        damage=2
        super(self.__class__,self).invoke()
        arcane_blast_animation(target)
        self.deal_damage([target], [damage+self.get_spell_damage_boost()])
                                   
class Polymorph_Boar(Spell):
    def __init__(self,name="Polymorph: Boar",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion()
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        zodiac_animation(self.owner, self.card_class)
        boar=Boar_Polymorph_Boar(owner=target.owner,source=target.location)
        target.transform(boar)

class Forgotten_Torch(Spell):
    def __init__(self,name="Forgotten Torch",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        fireball_animation(self,target)
        self.deal_damage([target],[3])
        card=Roaring_Torch(owner=self.owner)
        card.shuffle_into_deck()

class Roaring_Torch(Spell):
    def __init__(self,name="Roaring Torch",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        fireball_animation(self,target)
        self.deal_damage([target],[6])

class Shatter(Spell):
    def __init__(self,name="Shatter",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion() and target.frozen
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        frostbolt_animation(self,target)
        target.destroy()

class Forbidden_Flame(Spell):
    def __init__(self,name="Forbidden Flame",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion()
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        flame_lance_animation(self,target)
        self.deal_damage([target], [self.owner.current_mana])
        self.owner.current_mana=0

class Cabalists_Tome(Spell):
    def __init__(self,name="Cabalist's Tome",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        zodiac_animation(self.owner, self.card_class)
        
        for i in range(3):
            spell = database.get_random_cards("[type]='Spell' AND [class] LIKE '%Mage%'", self.owner, 1)[0]
            spell.initialize_location(self.owner.location)
            spell.hand_in(speed=40)

class Firelands_Portal(Spell):
    def __init__(self,name="Firelands Portal",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        fireball_animation(self,target)
        self.deal_damage([target],[5])
        minion = database.get_random_cards("[type]='Minion' AND [cost]=5", self.owner, 1)[0]
        self.owner.recruit(minion)
        
class Freezing_Potion(Spell):
    def __init__(self,name="Freezing Potion",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        glacial_shard_animation(self, target)
        target.get_frozen()

class Volcanic_Potion(Spell):
    def __init__(self,name="Volcanic Potion",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        targets=self.all_minions()
        unstable_ghoul_animation(self)
        self.deal_damage(targets, [2]*len(targets))

class Greater_Arcane_Missiles(Spell):
    def __init__(self,name="Greater Arcane Missiles",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        zodiac_animation(self.owner, self.card_class)
        self.deal_split_damage(self.enemy_characters(),shots=3,damage=3,effect=get_image("images/arcane_missile.png",(200,200)),speed=25,curve=True)   
  
class Flame_Geyser(Spell):
    def __init__(self,name="Flame_Geyser",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        fireball_animation(self, target)
        self.deal_damage([target],[2])
        minion=Flame_Elemental(owner=self.owner,source=self.location)
        minion.appear_in_hand()
        
class Molten_Reflection(Spell):
    def __init__(self,name="Molten Reflection",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion() and target.side==self.side
            
    def invoke(self,target):
        super(self.__class__,self).invoke()
        minion_copy=getattr(card_collection,database.cleaned(target.name))(owner=self.owner)
        target.summon(minion_copy)

class Primordial_Glyph(Spell):
    def __init__(self,name="Primordial Glyph",owner=None):
        super(self.__class__,self).__init__(name,owner)
            
    def invoke(self,target):
        super(self.__class__,self).invoke()
        card=self.discover(filter_str="[type]='Spell'")
        if card is not None:
            card.appear_in_hand()
            card.modify_cost(-2)

class Meteor(Spell):
    def __init__(self,name="Meteor",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None and target.isMinion()
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        meteor_animation(self,target)
        targets=target.adjacent_minions()
        self.deal_damage([target]+targets,[15]+[3]*len(targets))

class Breath_of_Sindragosa(Spell):
    def __init__(self,name="Breath of Sindragosa",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return len(self.enemy_minions())>0
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        target=random.choice(self.enemy_minions())
        frostbolt_animation(self, target)
        target.get_frozen()
        self.deal_damage([target],[2])
        
class Simulacrum(Spell):
    def __init__(self,name="Simulacrum",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return self.owner.has_minion_in_hand()
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        targets=[]
        minimum_cost=20
        for card in self.owner.hand:
            if card.isMinion() and card.get_current_cost()<=minimum_cost:
                targets.append(card)
                minimum_cost=card.get_current_cost()
        target=random.choice(targets)        
        minion_copy=target.get_copy(owner=self.owner)
        minion_copy.initialize_location((self.rect.x,self.rect.y))
        minion_copy.copy_stats(target)
        minion_copy.hand_in()

class Glacial_Mysteries(Spell):
    def __init__(self,name="Glacial Mysteries",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        secret_pool=[]
        secret_names=[]
        for card in self.owner.deck.cards:
            if isinstance(card, Secret) and card.is_valid_on():
                if card.name not in secret_names:
                    secret_names.append(card.name)
                    secret_pool.append(card)
                
        secrets=random.sample(secret_pool,k=min(5,len(secret_pool)))
        for secret in secrets:
            secret.invoke()
            self.owner.deck.cards.remove(secret)

class Shifting_Scroll(Spell):
    def __init__(self,name="Shifting Scroll",owner=None):
        super(self.__class__,self).__init__(name,owner) 
        self.trigger_event_type="start of turn"

    def is_valid_on(self, target):
        return False
            
    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner and self.board_area=="Hand":
            spell = database.get_random_cards("[type]='Spell' and [class] LIKE '%Mage%'", self.owner, 1)[0]
            spell.transform_in_hand=True
            spell.trigger_events.append(["start of turn",MethodType(Shifting_Scroll.trigger_effect,spell)])
            spell.copy_target=self
            self.shapeshift(spell)

class Lesser_Ruby_Spellstone(Spell):
    def __init__(self,name="Lesser Ruby Spellstone",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.trigger_event_type="play a card"
        self.upgrade_target=Ruby_Spellstone
        self.counter=0
        self.goal=2

    def invoke(self,target):
        super(self.__class__,self).invoke()
        zodiac_animation(self.owner, self.card_class)
        for i in range(1):
            spell=database.get_random_cards("[type]='Spell' and [class] LIKE '%Mage%'", self.owner, 1)[0]
            spell.initialize_location(self.owner.location)
            spell.hand_in(speed=50)
        
    def trigger_effect(self, triggering_card):
        if triggering_card.side==self.side and triggering_card.has_race("Elemental"):
            self.counter+=1
            if self.counter>=self.goal:
                self.upgrade()

class Ruby_Spellstone(Spell):
    def __init__(self,name="Ruby Spellstone",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        self.trigger_event_type="play a card"
        self.upgrade_target=Greater_Ruby_Spellstone
        self.counter=0
        self.goal=2

    def invoke(self,target):
        super(self.__class__,self).invoke()
        zodiac_animation(self.owner, self.card_class)
        for i in range(2):
            spell=database.get_random_cards("[type]='Spell' and [class] LIKE '%Mage%'", self.owner, 1)[0]
            spell.initialize_location(self.owner.location)
            spell.hand_in(speed=50)
        
    def trigger_effect(self, triggering_card):
        if triggering_card.side==self.side and triggering_card.has_race("Elemental"):
            self.counter+=1
            if self.counter>=self.goal:
                self.upgrade()

class Greater_Ruby_Spellstone(Spell):
    def __init__(self,name="Greater Ruby Spellstone",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)

    def invoke(self,target):
        super(self.__class__,self).invoke()
        zodiac_animation(self.owner, self.card_class)
        for i in range(3):
            spell=database.get_random_cards("[type]='Spell' and [class] LIKE '%Mage%'", self.owner, 1)[0]
            spell.initialize_location(self.owner.location)
            spell.hand_in(speed=50)

class Dragons_Fury(Spell):
    def __init__(self,name="Dragon's Fury",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def invoke(self,target):
        super(self.__class__,self).invoke()
        card=self.reveal(card_type="Spell")
        if card is not None:
            flamestrike_animation(self)
            targets=self.all_minions()
            self.deal_damage(targets, [card.get_current_cost()]*len(targets))

class Deck_of_Wonders(Spell):
    def __init__(self,name="Deck of Wonders",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def invoke(self,target):
        super(self.__class__,self).invoke()
        for i in range(5):
            card=Scroll_of_Wonder(owner=self.owner)
            card.initialize_location(self.owner.location)
            card.shuffle_into_deck(skip_zoom=(i>=1))

class Scroll_of_Wonder(Spell):
    def __init__(self,name="Scroll of Wonder",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        self.casts_when_drawn=True

    def invoke(self,target=None):
        super(self.__class__,self).invoke()
        spell = database.get_random_cards("[type]='Spell'", self.owner, 1)[0]
        scroll_of_wonder_animation(self,spell)
        spell.cast_on_random_target()

class Snap_Freeze(Spell):
    def __init__(self,name="Snap Freeze",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None and target.isMinion()
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        glacial_shard_animation(self, target)
        if target.frozen:
            target.destroy()
        else:
            target.get_frozen()

class Cinderstorm(Spell):
    def __init__(self,name="Cinderstorm",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        zodiac_animation(self.owner, self.card_class)
        self.deal_split_damage(self.enemy_characters(),shots=5,damage=1,effect=get_image("images/fireball2.png",(60,60)),speed=20,curve=True)   
        
class Book_of_Specters(Spell):
    def __init__(self,name="Book of Specters",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        for i in range(3):
            card=self.owner.draw()
            if card.isSpell:
                card.discard()
                                
class Time_Warp(Spell):
    def __init__(self,name="Time Warp",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        time_warp_animation(self)
        self.owner.take_extra_turn+=1
                                                                                                                                                                                                                                                         
'''Paladin Spells'''                        
class Blessing_of_Might(Spell):
    def __init__(self,name="Blessing of Might",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion()
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        paladin_buff_animation(self,target)
        target.buff_stats(3,0)
            
class Hand_of_Protection(Spell):
    def __init__(self,name="Hand of Protection",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def is_valid_on(self, target):
        return target is not None and target.isMinion()
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        paladin_buff_animation(self,target)
        target.gain_divine_shield()

class Humility(Spell):
    def __init__(self,name="Humility",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion()
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        paladin_debuff_animation(self,target)
        target.set_stats(atk=1)

class Holy_Light(Spell):
    def __init__(self,name="Holy Light",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        paladin_buff_animation(self,target)
        self.heal([target],[6])
                                   
class Blessing_of_Kings(Spell):
    def __init__(self,name="Blessing of Kings",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion()
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        blessing_of_kings_animation(self,target)
        target.buff_stats(4,4)

class Consecration(Spell):
    def __init__(self,name="Consecration",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        targets=self.enemy_characters()
        consecration_animation(self,targets)
        self.deal_damage(targets, [2]*len(targets))

class Divine_Favor(Spell):
    def __init__(self,name="Divine Favor",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        zodiac_animation(self.owner, self.card_class)
        while len(self.owner.hand)>len(self.owner.opponent.hand):
            self.owner.draw()
        
class Hammer_of_Wrath(Spell):
    def __init__(self,name="Hammer of Wrath",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        hammer_of_wrath_animation(self,target)
        self.deal_damage([target],[3])
        self.owner.draw()

class Blessing_of_Wisdom(Spell):
    def __init__(self,name="Blessing of Wisdom",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion()
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        paladin_buff_animation(self,target)
        target.trigger_events.append(["attack",MethodType(self.trigger_effect.__func__,target)])
        target.attachments["Blessing of Wisdom"]=self
        target.has_trigger=True
        
    def trigger_effect(self,triggering_entity):
        if triggering_entity is self:
            super(self.__class__,self).trigger_effect(triggering_entity)
            self.attachments["Blessing of Wisdom"].owner.draw()
        
class Equality(Spell):
    def __init__(self,name="Equality",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return len(self.friendly_minions())>0 or len(self.enemy_minions())>0
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        equality_animation(self)
        for minion in self.friendly_minions()+self.enemy_minions():
            minion.set_stats(hp=1)
      
class Blessed_Champion(Spell):
    def __init__(self,name="Blessed Champion",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion()
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        blessing_of_kings_animation(self,target)
        target.buff_stats(target.current_atk,0)

 
class Holy_Wrath(Spell):
    def __init__(self,name="Holy Wrath",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and len(self.owner.deck.cards)>0
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        card=self.owner.deck.cards[0]
        holy_wrath_animation(self,target,card.current_cost)
        self.owner.draw()
        self.deal_damage([target],[card.current_cost])

class Righteousness(Spell):
    def __init__(self,name="Righteousness",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return len(self.friendly_minions())>0
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        zodiac_animation(self.owner, self.card_class)
        minions=self.friendly_minions()
        righteousness_animation(self,minions) 
        for minion in minions:
            minion.gain_divine_shield()
  
class Avenging_Wrath(Spell):
    def __init__(self,name="Avenging Wrath",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        self.owner.board.background=background_dark
        show_board(self.owner.board)
        time.sleep(0.6)
        self.deal_split_damage(self.enemy_characters(),shots=8,damage=1,effect=get_image("images/magic_bolt.png",(80,80)),speed=30)
        time.sleep(0.4)
        self.owner.board.background=background    

class Lay_on_Hands(Spell):
    def __init__(self,name="Lay on Hands",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        zodiac_animation(self.owner, self.card_class)
        paladin_buff_animation(self, target)
        self.heal([target],[8])
        self.owner.draw(3)

class Seal_of_Light(Spell):
    def __init__(self,name="Seal of Light",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        paladin_buff_animation(self, self.owner)
        self.heal([self.owner], [4], skip_animation=True)
        self.owner.current_atk+=2

class Muster_for_Battle(Spell):
    def __init__(self,name="Muster for Battle",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        weapon=Lights_Justice(owner=self.owner)
        self.owner.equip_weapon(weapon)
        for i in range(3):
            minion=Silver_Hand_Recruit(owner=self.owner,source="board")
            self.owner.recruit(minion,speed=80)

class Solemn_Vigil(Spell):
    def __init__(self,name="Solemn Vigil",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        self.owner.draw(2)
        
    def ongoing_effect(self,target):
        if target is self and target.board_area=="Hand":
            n=self.owner.get_num_minions_died()
            return {'cost':-n}
        else:
            return {} 

class Seal_of_Champions(Spell):
    def __init__(self,name="Seal of Champions",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion()
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        paladin_buff_animation(self,target)
        target.buff_stats(3,0)
        target.gain_divine_shield()

class Enter_the_Coliseum(Spell):
    def __init__(self,name="Enter the Coliseum",owner=None):
        super(self.__class__,self).__init__(name,owner)
       
    def invoke(self,target):
        super(self.__class__,self).invoke()
        winners=[]
        losers=[]
        for player in [self.owner,self.owner.opponent]:
            max_atk=0
            minions=player.friendly_minions()
            if len(minions)>0:
                for minion in minions:
                    if minion.get_current_atk()>max_atk:
                        max_atk=minion.get_current_atk()
                        highest_atk_minion=minion
                minions.remove(highest_atk_minion)
                winners.append(highest_atk_minion)
                losers.extend(minions)
        
        enter_the_coliseum_animation(self,winners,losers)
        #Destroy Minions
        for minion in losers:
            minion.destroy(skip_animation=True)
            
class Anyfin_Can_Happen(Spell):
    def __init__(self,name="Anyfin Can Happen",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        target_pool = []
        for minion in self.owner.grave+self.owner.opponent.grave:
            if minion.has_race("Murloc"):
                target_pool.append(minion)
                
        if len(target_pool)>0:
            murlocs=random.sample(target_pool,k=min(7,len(target_pool)))
            for murloc in murlocs:
                murloc_copy=getattr(card_collection,database.cleaned(murloc.name))(owner=self.owner,source="board")
                self.owner.recruit(murloc_copy)

class Divine_Strength(Spell):
    def __init__(self,name="Divine Strength",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion()
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        paladin_buff_animation(self,target)
        target.buff_stats(1,2)

class A_Light_in_the_Darkness(Spell):
    def __init__(self,name="A Light in the Darkness",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        card=self.discover(filter_str="[type]='Minion'")
        if card is not None:
            card.buff_stats(1,1)
            card.appear_in_hand()

class Stand_Against_Darkness(Spell):
    def __init__(self,name="Stand Against Darkness",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        zodiac_animation(self.owner, self.card_class)
        for k in range(5):
            minion = Silver_Hand_Recruit(owner=self.owner,source="board")
            self.owner.recruit(minion,speed=70)

class Forbidden_Healing(Spell):
    def __init__(self,name="Forbidden Healing",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        priest_heal_animation(self,target)
        self.heal([target], [self.owner.current_mana*2])
        self.owner.current_mana=0

class Silvermoon_Portal(Spell):
    def __init__(self,name="Silvermoon Portal",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion()
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        paladin_buff_animation(self,target)
        target.buff_stats(2,2)
        minion = database.get_random_cards("[type]='Minion' AND [cost]=2", self.owner, 1)[0]
        self.owner.recruit(minion)

class Smugglers_Run(Spell):
    def __init__(self,name="Smuggler's Run",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        self.owner.buff_hand(card_type="Minion",multiple=True)

class Small_Time_Recruits(Spell):
    def __init__(self,name="Small-Time Recruits",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        for i in range(3):
            minion=self.owner.search_card_based_cost(self.owner.deck.cards,card_type="Minion",cost=1)
            if minion is not None:
                self.owner.draw(target=minion)
                
class Adaptation(Spell):
    def __init__(self,name="Adaptation",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion() and target.side==self.side
            
    def invoke(self,target):
        super(self.__class__,self).invoke()
        target.adapt()

class Lost_in_the_Jungle(Spell):
    def __init__(self,name="Lost in the Jungle",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target=None):
        super(self.__class__,self).invoke()
        for i in range(2):
            minion=Silver_Hand_Recruit(owner=self.owner,source="board")
            self.owner.recruit(minion)

class Spikeridged_Steed(Spell):
    def __init__(self,name="Spikeridged Steed",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion()
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        light_buff_animation(target)
        target.buff_stats(2,6)
        target.gain_taunt()     
        target.deathrattles.append([MethodType(self.deathrattle.__func__,target),"Summon a 2/6 Stegodon"])
        target.has_deathrattle=True
        
    def deathrattle(self):
        minion=Stegodon(owner=self.owner)
        self.summon(minion)

class Dinosize(Spell):
    def __init__(self,name="Dinosize",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion()
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        dinosize_animation(target)
        target.set_stats(atk=10,hp=10)

class Dark_Conviction(Spell):
    def __init__(self,name="Dark Conviction",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion()
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        paladin_buff_animation(self,target)
        target.set_stats(3,3)

class Desperate_Stand(Spell):
    def __init__(self,name="Desperate Stand",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion()
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        paladin_buff_animation(self,target)
        target.deathrattles.append([MethodType(self.deathrattle.__func__,target),"Return this to life with 1 Health"])
        target.has_deathrattle=True
        
    def deathrattle(self):
        minion=getattr(card_collection,database.cleaned(self.name))(owner=self.owner,source=self.location)
        minion.current_health=1
        self.summon(minion)

class Potion_of_Heroism(Spell):
    def __init__(self,name="Potion of Heroism",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def is_valid_on(self, target):
        return target is not None and target.isMinion()
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        paladin_buff_animation(self,target)
        target.gain_divine_shield()
        self.owner.draw()

class Lesser_Pearl_Spellstone(Spell):
    def __init__(self,name="Lesser Pearl Spellstone",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.trigger_event_type="character healed"
        self.upgrade_target=Pearl_Spellstone
        self.counter=0
        self.goal=3

    def invoke(self,target):
        super(self.__class__,self).invoke()
        minion=Guardian_Spirit_2_2(owner=self.owner,source="board")
        self.owner.recruit(minion)
        
    def trigger_effect(self, triggering_entity):
        if triggering_entity[2] is not None and triggering_entity[2].side==self.side:
            self.counter+=triggering_entity[1]
            if self.counter>=self.goal:
                self.upgrade()
        
class Pearl_Spellstone(Spell):
    def __init__(self,name="Pearl Spellstone",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        self.trigger_event_type="character healed"
        self.upgrade_target=Greater_Pearl_Spellstone
        self.counter=0
        self.goal=3

    def invoke(self,target):
        super(self.__class__,self).invoke()
        minion=Guardian_Spirit_4_4(owner=self.owner,source="board")
        self.owner.recruit(minion)
        
    def trigger_effect(self, triggering_entity):
        if triggering_entity[2] is not None and triggering_entity[2].side==self.side:
            self.counter+=triggering_entity[1]
            if self.counter>=self.goal:
                self.upgrade()

class Greater_Pearl_Spellstone(Spell):
    def __init__(self,name="Greater Emerald Spellstone",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)

    def invoke(self,target):
        super(self.__class__,self).invoke()
        minion=Guardian_Spirit_6_6(owner=self.owner,source="board")
        self.owner.recruit(minion)

class Call_to_Arms(Spell):
    def __init__(self,name="Call to Arms",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def invoke(self,target):
        super(self.__class__,self).invoke()
        for i in range(3):
            minion=self.owner.search_card_based_cost(self.owner.deck.cards,card_type="Minion",cost=2,compare="__le__")
            if minion is not None:
                self.recruit(minion)

class Level_Up(Spell):
    def __init__(self,name="Level Up!",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        minions=self.friendly_minions()
        targets=[]
        for minion in minions:
            if isinstance(minion, Silver_Hand_Recruit):
                targets.append(minion)
        if len(targets)>0: 
            light_buff_multiple_animation(self, targets) 
            for minion in targets:
                minion.buff_stats(2,2)
                minion.gain_taunt()
                                                                                                                                                                                                                                                                          
class Lightforged_Blessing(Spell):
    def __init__(self,name="Lightforged Blessing",owner=None):
        super(Lightforged_Blessing,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion() and target.side==self.side
        
    def invoke(self,target):
        super(Lightforged_Blessing,self).invoke()
        lightforged_blessing_animation(self,target)
        target.has_lifesteal=True          

class Lightforged_Blessing_Twinspell(Lightforged_Blessing):
    def __init__(self,name="Lightforged Blessing (Twinspell)",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return super(self.__class__,self).is_valid_on(target) 
        
    def invoke(self,target):
        super(self.__class__,self).invoke(target)    
        
'''Priest Spells'''
class Power_Word_Shield(Spell):
    def __init__(self,name="Power Word: Shield",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion()
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        priest_buff_animation(self,target)
        target.buff_stats(0,2)

class Holy_Smite(Spell):
    def __init__(self,name="Holy Smite",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None and target.isMinion()
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        holy_smite_animation(self,target)
        self.deal_damage([target],[3])
        
class Mind_Blast(Spell):
    def __init__(self,name="Mind Blast",owner=None):
        super(self.__class__,self).__init__(name,owner)
 
    def invoke(self,target):
        super(self.__class__,self).invoke()
        mind_blast_animation(self)
        self.deal_damage([self.owner.opponent],[5])
                    
class Mind_Vision(Spell):
    def __init__(self,name="Mind Vision",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        if len(self.owner.opponent.hand)>0:
            opponent_card=random.choice(self.owner.opponent.hand)
            mind_vision_animation(self)
            card_copy=getattr(card_collection,database.cleaned(opponent_card.name))(owner=self.owner)
            card_copy.initialize_location(self.owner.location)
            card_copy.copy_enchantments(opponent_card)
            card_copy.appear_in_hand()

class Thoughtsteal(Spell):
    def __init__(self,name="Thoughtsteal",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        if len(self.owner.opponent.deck.cards)>0:
            cards=random.sample(self.owner.opponent.deck.cards,k=min(2,len(self.owner.opponent.deck.cards)))
            mind_vision_animation(self)
            for card in cards:
                card_copy=card.get_copy(owner=self.owner)
                card_copy.appear_in_hand()
            
class Radiance(Spell):
    def __init__(self,name="Radiance",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        self.heal([self.owner],[5])

class Shadow_Word_Death(Spell):
    def __init__(self,name="Shadow Word: Death",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion() and target.side==self.side and target.get_current_atk()>=5
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        shadow_word_animation(self,target)
        target.destroy()

class Shadow_Word_Pain(Spell):
    def __init__(self,name="Shadow Word: Pain",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion() and target.get_current_atk()<=3
            
    def invoke(self,target):
        super(self.__class__,self).invoke()
        shadow_word_animation(self,target)
        target.destroy()

class Shadowform(Spell):
    def __init__(self,name="Shadowform",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        if self.owner.hero_power.name=="Mind Spike":
            new_hero_power=Mind_Shatter(owner=self.owner)
            self.owner.gain_hero_power(new_hero_power)
        elif self.owner.hero_power.name=="Mind Shatter":
            pass
        else:
            new_hero_power=Mind_Spike(owner=self.owner)
            self.owner.gain_hero_power(new_hero_power)
        
class Holy_Nova(Spell):
    def __init__(self,name="Holy Nova",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        
        #Damage Effect
        minions=self.enemy_minions()
        holy_nova_animation(self)
        self.deal_damage(minions, [2]*len(minions))
        
        #Healing Effect
        targets=self.friendly_characters()
        self.heal(targets,[2]*len(targets))
                             
class Power_Infusion(Spell):
    def __init__(self,name="Power Infusion",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion()
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        priest_buff_animation(self,target)
        buff_animation(target, speed=7)
        target.buff_stats(2,6)

class Power_Word_Tentacles(Spell):
    def __init__(self,name="Power Word: Tentacles",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion()
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        priest_buff_animation(self,target)
        buff_animation(target, speed=7)
        target.buff_stats(2,6)
                
class Holy_Fire(Spell):
    def __init__(self,name="Holy Fire",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def is_valid_on(self, target):
        return target is not None
 
    def invoke(self,target):
        super(self.__class__,self).invoke()
        holy_fire_animation(self,target)
        self.deal_damage([target],[5])
        self.heal([self.owner],[5])
                        
class Mind_Control(Spell):
    def __init__(self,name="Mind Control",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion() and target.owner is not self.owner
            
    def invoke(self,target):
        super(self.__class__,self).invoke()
        self.owner.take_control(target)

class Circle_of_Healing(Spell):
    def __init__(self,name="Circle of Healing",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def invoke(self,target):
        super(self.__class__,self).invoke()
        circle_of_healing_animation(self)
        targets=self.friendly_minions()+self.enemy_minions()
        self.heal(targets,[4]*len(targets))
        
class Silence_card(Spell):
    def __init__(self,name="Silence (card)",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion() 
            
    def invoke(self,target):
        super(self.__class__,self).invoke()
        self.silence(target)

class Divine_Spirit(Spell):
    def __init__(self,name="Divine Spirit",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion() 
            
    def invoke(self,target):
        super(self.__class__,self).invoke()
        paladin_buff_animation(self, target)
        target.current_hp*=2
        target.temp_hp+=target.current_hp
                
class Inner_Fire(Spell):
    def __init__(self,name="Inner Fire",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion() 
            
    def invoke(self,target):
        super(self.__class__,self).invoke()
        paladin_buff_animation(self, target)
        target.set_stats(atk=target.current_hp)
                        
class Shadow_Madness(Spell):
    def __init__(self,name="Shadow Madness",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion() and target.owner is not self.owner and target.get_current_atk()<=3
            
    def invoke(self,target):
        super(self.__class__,self).invoke()
        self.owner.take_control(target)
        target.temporary_effects['owned']=self.owner
        target.attacked=False
        target.summoning_sickness=False                

class Mass_Dispel(Spell):
    def __init__(self,name="Mass Dispel",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def invoke(self,target):
        super(self.__class__,self).invoke()
        targets=self.enemy_minions()
        mass_dispel_animation(self)
        for target in targets:
            self.silence(target,skip_animation=True)
        
        self.owner.draw()

class Mindgames(Spell):
    def __init__(self,name="Mindgames",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def invoke(self,target):
        super(self.__class__,self).invoke()
        card = self.owner.search_card(self.owner.opponent.deck.cards,card_type="Minion")
        if card is None:
            minion=Shadow_of_Nothing(owner=self.owner,source="board")
        else:
            minion=getattr(card_collection,database.cleaned(card.name))(owner=self.owner,source="board")
            
        mind_vision_animation(self)
        self.owner.recruit(minion)
 
class Shadow_Word_Ruin(Spell):
    def __init__(self,name="Shadow Word: Ruin",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def invoke(self,target):
        super(self.__class__,self).invoke()
        targets=[]
        for minion in self.all_minions():
            if minion.get_current_atk()>=5:
                targets.append(minion)
         
        shadow_word_ruin_animation(self)
        destroy_multiple_animation(targets)       
        for minion in targets:
            minion.destroy(skip_animation=True)

class Velens_Chosen(Spell):
    def __init__(self,name="Velen's Chosen",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion()
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        priest_buff_animation(self,target)
        buff_animation(target, speed=7)
        target.buff_stats(2,4)
        target.current_spell_damage_boost+=1

class Light_of_the_Naaru(Spell):
    def __init__(self,name="Light of the Naaru",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        self.heal([target], [3])
        if target.damaged():
            minion=Lightwarden(owner=self.owner,source="board")
            self.owner.recruit(minion)

class Lightbomb(Spell):
    def __init__(self,name="Lightbomb",owner=None):
        super(self.__class__,self).__init__(name,owner)


    def invoke(self,target):
        super(self.__class__,self).invoke()
        targets=self.all_minions()
        lightbomb_animation(self,targets)
        self.deal_damage(targets, [minion.get_current_atk() for minion in targets])
        
class Resurrect(Spell):
    def __init__(self,name="Resurrect",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def is_valid_on(self, target):
        return len(self.owner.grave)>0
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        minion = self.owner.search_card(self.owner.grave,"Minion")
        minion_copy = minion.get_copy(owner=self.owner)
        minion_copy.initialzie_location("board")
        self.owner.recruit(minion)
        resurrect_animation(minion)

class Flash_Heal(Spell):
    def __init__(self,name="Flash Heal",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        priest_heal_animation(self,target)
        self.heal([target],[5])

class Power_Word_Glory(Spell):
    def __init__(self,name="Power Word: Glory",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion()
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        priest_heal_animation(self,target)
        target.trigger_events.append(["attack",MethodType(self.trigger_effect.__func__,target)])
        target.attachments["Power Word: Glory"]=self
        target.has_trigger=True
        
    def trigger_effect(self,triggering_entity):
        if triggering_entity is self:
            super(self.__class__,self).trigger_effect(triggering_entity)
            self.heal([self.attachments["Power Word: Glory"].owner],[4])

class Convert(Spell):
    def __init__(self,name="Convert",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion() and target.side==-self.side
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        card=getattr(card_collection,database.cleaned(target.name))(owner=self.owner)
        card.appear_in_hand()

class Confuse(Spell):
    def __init__(self,name="Confuse",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        targets=self.all_minions()
        consecration_animation(self, targets)
        for minion in targets:
            minion.swap_stats()

class Entomb(Spell):
    def __init__(self,name="Entomb",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion() and target.side==-self.side
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        target.owner=self.owner
        target.side=self.side
        recycle_animation(self,target)
        if target in self.owner.opponent.minions:
            self.owner.opponent.minions.remove(target)
        target.shuffle_into_deck()

class Excavated_Evil(Spell):
    def __init__(self,name="Excavated Evil",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        minions=self.all_minions()
        excavated_evil_animation(self)
        self.deal_damage(minions, [3]*len(minions))
        
        self.owner=self.owner.opponent
        self.shuffle_into_deck()

class Shadow_Word_Horror(Spell):
    def __init__(self,name="Shadow Word: Horror",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def invoke(self,target):
        super(self.__class__,self).invoke()
        targets=[]
        for minion in self.all_minions():
            if minion.get_current_atk()<=2:
                targets.append(minion)
         
        shadow_word_ruin_animation(self)
        destroy_multiple_animation(targets)       
        for minion in targets:
            minion.destroy(skip_animation=True)

class Forbidden_Shaping(Spell):
    def __init__(self,name="Forbidden Shaping",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def invoke(self,target):
        super(self.__class__,self).invoke()
        minion = database.get_random_cards("[type]='Minion' AND [cost]="+str(self.owner.current_mana), self.owner, 1)[0]
        minion.initialize_location(source="board")
        self.owner.recruit(minion)
        self.owner.current_mana=0

class Purify(Spell):
    def __init__(self,name="Purify",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion() and target.side==self.side
            
    def invoke(self,target):
        super(self.__class__,self).invoke()
        self.silence(target)
        self.owner.draw()

class Potion_of_Madness(Spell):
    def __init__(self,name="Potion of Madness",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion() and target.owner is not self.owner and target.get_current_atk()<=2
            
    def invoke(self,target):
        super(self.__class__,self).invoke()
        self.owner.take_control(target)
        target.temporary_effects['owned']=self.owner
        target.attacked=False
        target.summoning_sickness=False    

class Pint_Size_Potion(Spell):
    def __init__(self,name="Pint-Size Potion",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        for minion in self.enemy_minions():
            minion.current_atk-=3 

class Greater_Healing_Potion(Spell):
    def __init__(self,name="Greater Healing Potion",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        priest_heal_animation(self, target)
        self.heal([target],[12])

class Dragonfire_Potion(Spell):
    def __init__(self,name="Dragonfire Potion",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        targets=self.all_minions_except("Dragon")
        chillmaw_animation(self)
        self.deal_damage(targets, [5]*len(targets))
        
class Binding_Heal(Spell):
    def __init__(self,name="Binding Heal",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None and target.isMinion()
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        priest_heal_animation(self,target)
        self.heal([target,self.owner],[5,5])

class Free_From_Amber(Spell):
    def __init__(self,name="Free From Amber",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        minion=self.discover(filter_str="[type]='Minion' AND [cost]>=8")
        minion.initialize_location("board")
        if minion is not None:
            self.owner.recruit(minion)

class Shadow_Visions(Spell):
    def __init__(self,name="Shadow Visions",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        cards=self.owner.search_card(self.owner.deck.cards,card_type="Spell",k=3)
        if cards is not None:
            card=self.discover(card_pool=cards)
            if card is not None:
                card_copy=card.get_copy(owner=self.owner)
                card_copy.appear_in_hand()
                    
class Spirit_Lash(Spell):
    def __init__(self,name="Spirit Lash",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.lifesteal=True
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        minions=self.all_minions()
        abomination_animation(self)
        self.deal_damage(minions, [1]*len(minions))

class Eternal_Servitude(Spell):
    def __init__(self,name="Eternal Servitude",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        cards=self.owner.search_card(self.owner.grave,card_type="Minion",k=3)
        if cards is not None:
            card=self.discover(card_pool=cards)
            if card is not None:
                minion_copy=card.get_copy(owner=self.owner)
                minion_copy.initialize_location("board")
                self.owner.recruit(minion_copy)
                resurrect_animation(minion_copy)

class Devour_Mind(Spell):
    def __init__(self,name="Devour Mind",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        if len(self.owner.opponent.deck.cards)>0:
            cards=random.sample(self.owner.opponent.deck.cards,k=min(3,len(self.owner.opponent.deck.cards)))
            mind_vision_animation(self)
            for card in cards:
                card_copy=card.get_copy(owner=self.owner)
                card_copy.appear_in_hand()

class Shadow_Essence(Spell):
    def __init__(self,name="Shadow Essence",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def invoke(self,target):
        super(self.__class__,self).invoke()
        minion = self.owner.search_card(self.owner.deck.cards,card_type="Minion")
        if minion is not None:
            minion_copy=minion.get_copy(owner=self.owner)
            minion_copy.initialize_location("board")
            minion_copy.set_stats(5,5)
            self.owner.recruit(minion_copy)

class Embrace_Darkness(Spell):
    def __init__(self,name="Embrace Darkness",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion() and target.owner is not self.owner
            
    def invoke(self,target):
        super(self.__class__,self).invoke()
        target.trigger_events.append(["start of turn",MethodType(self.trigger_effect.__func__,target)])
        target.attachments["Embrace Darkness"]=self
        target.has_trigger=True
        
    def trigger_effect(self,triggering_player):
        if triggering_player is self.attachments["Embrace Darkness"].owner:
            super(self.__class__,self).trigger_effect(self)
            self.attachments["Embrace Darkness"].owner.take_control(self)

class Psionic_Probe(Spell):
    def __init__(self,name="Psionic Probe",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        if len(self.owner.opponent.deck.cards)>0:
            opponent_card=self.owner.opponent.search_card(self.owner.opponent.deck.cards,card_type="Spell")
            mind_vision_animation(self)
            card_copy=opponent_card.get_copy(owner=self.owner)
            card_copy.initialize_location(self.owner.opponent.deck.location)
            card_copy.hand_in()

class Unidentified_Elixir(Spell):
    def __init__(self,name="Unidentified Elixir",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.trigger_event_type="add to hand"
        self.upgrade_targets=[Elixir_of_Hope,Elixir_of_Life,Elixir_of_Purity,Elixir_of_Shadows]

    def is_valid_on(self, target):
        return target is not None and target.isMinion()
            
    def trigger_effect(self,triggering_card):
        if triggering_card is self:
            self.upgrade_target=random.choice(self.upgrade_targets)
            self.upgrade()
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        priest_buff_animation(self, target)
        target.buff_stats(2,2)

class Elixir_of_Hope(Spell):
    def __init__(self,name="Elixir of Hope",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion()
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        priest_buff_animation(self, target)
        target.buff_stats(2,2)
        target.deathrattles.append([MethodType(self.deathrattle.__func__,target),"Return this minion to hand"])
      
    def deathrattle(self):
        self.return_hand(reset=True)

class Elixir_of_Life(Spell):
    def __init__(self,name="Elixir of Life",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion()
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        priest_buff_animation(self, target)
        target.buff_stats(2,2)
        target.gain_lifesteal()

class Elixir_of_Purity(Spell):
    def __init__(self,name="Elixir of Purity",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion()
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        priest_buff_animation(self, target)
        target.buff_stats(2,2)
        target.gain_divine_shield()

class Elixir_of_Shadows(Spell):
    def __init__(self,name="Elixir of Shadows",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion()
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        priest_buff_animation(self, target)
        target.buff_stats(2,2)
        minion_copy=target.get_copy(owner=self.owner)
        minion_copy.initialize_location("board")
        minion_copy.copy_stats(target)
        minion_copy.set_stats(1,1)
        self.owner.recruit(minion_copy)

class Twilights_Call(Spell):
    def __init__(self,name="Twilight's Call",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def is_valid_on(self, target):
        return len(self.owner.grave)>0
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        minions=self.owner.search_card_based_keyword(self.owner.grave,card_type="Minion",keyword="Deathrattle",k=2)
        for minion in minions:
            minion_copy=minion.get_copy(owner=self.owner)
            minion_copy.initialize_location("board")
            minion_copy.set_stats(1,1)
            self.owner.recruit(minion_copy,speed=40)
            resurrect_animation(minion_copy)

class Lesser_Diamond_Spellstone(Spell):
    def __init__(self,name="Lesser Diamond Spellstone",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.trigger_event_type="play a card"
        self.upgrade_target=Diamond_Spellstone
        self.counter=0
        self.goal=4

    def invoke(self,target):
        super(self.__class__,self).invoke()
        zodiac_animation(self.owner, self.card_class)
        for i in range(2):
            minion = self.owner.search_card(self.owner.grave,"Minion")
            minion_copy = minion.get_copy(owner=self.owner)
            minion_copy.initialzie_location("board")
            self.owner.recruit(minion,speed=40)
            resurrect_animation(minion)
        
    def trigger_effect(self, triggering_card):
        if triggering_card.isSpell and triggering_card.side==self.side:
            self.counter+=1
            if self.counter>=self.goal:
                self.upgrade()

class Diamond_Spellstone(Spell):
    def __init__(self,name="Lesser Diamond Spellstone",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        self.trigger_event_type="play a card"
        self.upgrade_target=Greater_Diamond_Spellstone
        self.counter=0
        self.goal=4

    def invoke(self,target):
        super(self.__class__,self).invoke()
        zodiac_animation(self.owner, self.card_class)
        for i in range(3):
            minion = self.owner.search_card(self.owner.grave,"Minion")
            minion_copy = minion.get_copy(owner=self.owner)
            minion_copy.initialzie_location("board")
            self.owner.recruit(minion,speed=40)
            resurrect_animation(minion)
        
    def trigger_effect(self, triggering_card):
        if triggering_card.isSpell and triggering_card.side==self.side:
            self.counter+=1
            if self.counter>=self.goal:
                self.upgrade()

class Greater_Diamond_Spellstone(Spell):
    def __init__(self,name="Greater Diamond Spellstone",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)

    def invoke(self,target):
        super(self.__class__,self).invoke()
        zodiac_animation(self.owner, self.card_class)
        for i in range(4):
            minion = self.owner.search_card(self.owner.grave,"Minion")
            minion_copy = minion.get_copy(owner=self.owner)
            minion_copy.initialzie_location("board")
            self.owner.recruit(minion,speed=40)
            resurrect_animation(minion)

class Psychic_Scream(Spell):
    def __init__(self,name="Psychic Scream",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return len(self.all_minions())>0
       
    def invoke(self,target):
        super(self.__class__,self).invoke()
        minions=self.all_minions()
        psychic_scream_animation(self,minions)
        for minion in minions:
            minion.owner=self.owner.opponent
            minion.shuffle_into_deck()
                                                                                                                                                                                                                                                                                                                                        
'''Rogue Spells'''
class Backstab(Spell):
    def __init__(self,name="Backstab",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None and target.isMinion() and not target.damaged()
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        backstab_animation(self,target)
        self.deal_damage([target], [2])

class Deadly_Poison(Spell):
    def __init__(self,name="Deadly Poison",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return self.owner.has_weapon()
           
    def invoke(self,target):
        if self.owner.has_weapon():
            super(self.__class__,self).invoke()
            weapon_enchantment_animation(self, self.owner.weapon)
            self.owner.weapon.buff_stats(2,0)

class Sinister_Strike(Spell):
    def __init__(self,name="Sinister Strike",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        sinister_strike_animation(self, self.owner.opponent)
        self.deal_damage([self.owner.opponent], [3])

class Sap(Spell):
    def __init__(self,name="Sap",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion() and target.side==-self.side
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        target.return_hand()

class Shiv(Spell):
    def __init__(self,name="Shiv",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None
       
    def invoke(self,target):
        super(self.__class__,self).invoke()
        sinister_strike_animation(self, target)
        self.deal_damage([target], [1])
        self.owner.draw()
            
class Fan_of_Knives(Spell):
    def __init__(self,name="Fan of Knives",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        minions=self.enemy_minions()
        fan_of_knives_animation(self)
        self.deal_damage(minions, [1]*len(minions))
        self.owner.draw()
        
class Assassinate(Spell):
    def __init__(self,name="Assassinate",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion() and target.side==-self.side
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        assassinate_animation(self,target)
        target.destroy()
            
class Vanish(Spell):
    def __init__(self,name="Vanish",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return len(self.all_minions())>0
       
    def invoke(self,target):
        super(self.__class__,self).invoke()
        minions=self.all_minions()
        vanish_animation(self,minions)
        for minion in minions:
            minion.return_hand(skip_animation=True) 
            
class Sprint(Spell):
    def __init__(self,name="Sprint",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        self.owner.draw(4)

class Shadowstep(Spell):
    def __init__(self,name="Shadowstep",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion() and target.side==self.side
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        rogue_buff_animation(self,target)
        target.return_hand(reset=True)
        target.current_cost=target.cost-2

class Conceal(Spell):
    def __init__(self,name="Conceal",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        targets=self.friendly_minions()
        for minion in targets:
            minion.temporary_effects["stealth"]=2
        
class Pilfer(Spell):
    def __init__(self,name="Pilfer",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        card = database.get_random_cards("[class]!='Rogue'", self.owner, 1)[0]
        zodiac_animation(self.owner, self.card_class)
        card.initialize_location(self.owner.location)
        card.hand_in()
        
class Betrayal(Spell):
    def __init__(self,name="Betrayal",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None and target.isMinion() and target.side==-self.side
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        betrayal_animation(self,target)
        targets=target.adjacent_minions()
        target.deal_damage(targets,[target.get_current_atk()]*len(targets))
                
class Cold_Blood(Spell):
    def __init__(self,name="Cold Blood",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None and target.isMinion()
            
    def invoke(self,target):
        super(self.__class__,self).invoke()
        hunter_buff_animation(self,target)
        target.buff_stats(2,0)
        if len(self.owner.played_cards[self.owner.turn])>0:
            self.combo(target)
            
    def combo(self,target):
        target.buff_stats(2,0)

class Eviscerate(Spell):
    def __init__(self,name="Eviscerate",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None
            
    def invoke(self,target):
        super(self.__class__,self).invoke()
        eviscerate_animation(self,target)
        if len(self.owner.played_cards[self.owner.turn])>0:
            self.combo(target)
        else:
            self.deal_damage([target], [2])
            
    def combo(self,target):
        self.deal_damage([target], [4])

class Blade_Flurry(Spell):
    def __init__(self,name="Blade Flurry",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return self.owner.has_weapon()
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        blade_flurry_animation(self)
        targets=self.enemy_minions()
        self.deal_damage(targets, [self.owner.weapon.get_current_atk()]*len(targets))
        self.owner.weapon.destroy()
                                            
class Headcrack(Spell):
    def __init__(self,name="Headcrack",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        headcrack_animation(self)
        self.deal_damage([self.owner.opponent],[2])
        if len(self.owner.played_cards[self.owner.turn])>0:
            self.combo()
            
    def combo(self):
        self.owner.board.spell_graves[self.owner.side].remove(self)
        self.owner.board.temps[self.owner.side].append(self)
        self.board_area="Temp"

class Preparation(Spell):
    def __init__(self,name="Preparation",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        card=Preparation_Effect(owner=self.owner)
        card.origin=self
        
class Preparation_Effect(Enchantment):
    def __init__(self,name="Preparation",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_events.append(("play a card",self.trigger_effect))

    def ongoing_effect(self,target):
        if target.side==self.side and target.isSpell:
            return {'cost':-2}
        else:
            return {}            
        
    def trigger_effect(self, triggering_card):
        if triggering_card.side==self.side and triggering_card.isSpell and triggering_card is not self.origin:
            self.destroy()

class Tinkers_Sharpsword_Oil(Spell): 
    def __init__(self,name="Tinker's Sharpsword Oil",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        if self.owner.has_weapon():
            weapon_enchantment_animation(self,self.owner.weapon)
            self.owner.weapon.buff_stats(3,0)
        
        if len(self.owner.played_cards[self.owner.turn])>0:
            self.combo()
 
    def combo(self):
        target_pool=self.friendly_minions()
        if len(target_pool)>0:
            minion=random.choice(target_pool)
            minion.buff_stats(3,0)

class Sabotage(Spell): 
    def __init__(self,name="Sabotage",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        targets=self.enemy_minions()
        if len(targets)>0:
            target=random.choice(targets)
            assassinate_animation(self, target)
            target.destroy()
        
        if len(self.owner.played_cards[self.owner.turn])>0:
            self.combo()
 
    def combo(self):
        if self.owner.opponent.has_weapon():
            assassinate_animation(self, self.owner.opponent.weapon)
            self.owner.opponent.weapon.destroy()

class Gang_Up(Spell):
    def __init__(self,name="Gang Up",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None and target.isMinion()
            
    def invoke(self,target):
        super(self.__class__,self).invoke()
        for i in range(3):
            card=getattr(card_collection,database.cleaned(target.name))(owner=self.owner)
            card.initialize_location(target.location)
            card.shuffle_into_deck()
            
class Burgle(Spell):
    def __init__(self,name="Burgle",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        zodiac_animation(self.owner, self.card_class)
        for i in range(2):
            card = database.get_random_cards("[class] LIKE '%"+self.owner.opponent.class_name+"%'", self.owner, 1)[0]
            card.initialize_location(self.owner.location)
            card.hand_in(speed=30)

class Beneath_the_Grounds(Spell):
    def __init__(self,name="Beneath the Grounds",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def invoke(self,target):
        super(self.__class__,self).invoke()
        for i in range(3):
            card=Nerubian_Ambush(owner=self.owner.opponent)
            card.initialize_location(self.owner.location)
            card.shuffle_into_deck(skip_zoom=(i>=1))

class Nerubian_Ambush(Spell):
    def __init__(self,name="Nerubian Ambush!",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        self.casts_when_drawn=True

    def invoke(self,target=None):
        super(self.__class__,self).invoke()
        minion=Nerubian_Beneath_the_Grounds(owner=self.owner.opponent,source="board")
        self.owner.opponent.recruit(minion)

class Shadow_Strike(Spell):
    def __init__(self,name="Shadow Strike",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None and not target.damaged()
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        backstab_animation(self,target)
        self.deal_damage([target], [5])

class Journey_Below(Spell):
    def __init__(self,name="Journey Below",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        card=self.discover(by_ability="Deathrattle")
        if card is not None:
            card.hand_in()  

class Thistle_Tea(Spell):
    def __init__(self,name="Thistle Tea",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        card=self.owner.draw()
        for i in range(2):
            card_copy=card.get_copy(owner=self.owner)
            card_copy.initialize_location(self.owner.location)
            card_copy.hand_in(speed=40)

class Jade_Shuriken(Spell):
    def __init__(self,name="Jade Shuriken",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None
            
    def invoke(self,target):
        super(self.__class__,self).invoke()
        eviscerate_animation(self,target)
        self.deal_damage([target], [2])
        if len(self.owner.played_cards[self.owner.turn])>0:
            self.combo(target)
            
    def combo(self,target):
        minion=Jade_Golem(owner=self.owner,source="board")
        self.owner.recruit(minion)

class Counterfeit_Coin(Spell):
    def __init__(self,name="Counterfeit Coin",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        self.owner.current_mana+=1

class Hallucination(Spell):
    def __init__(self,name="Hallucination",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        card=self.discover(filter_str="[class] LIKE '%"+self.owner.opponent.class_name+"%'")
        if card is not None:
            card.appearin_hand()

class Razorpetal(Spell):
    def __init__(self,name="Razorpetal",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None
       
    def invoke(self,target):
        super(self.__class__,self).invoke()
        razorpetal_animation(self, target)
        self.deal_damage([target], [1])

class Razorpetal_Volley(Spell):
    def __init__(self,name="Razorpetal Volley",owner=None):
        super(self.__class__,self).__init__(name,owner)
 
    def invoke(self,target):
        super(self.__class__,self).invoke()
        for i in range(2):
            card=Razorpetal(owner=self.owner)
            card.appear_in_hand()
                                                                                                                                                                                                      
class Envenom_Weapon(Spell):
    def __init__(self,name="Envenom Weapon",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return self.owner.has_weapon()
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        self.owner.weapon.gain_poisonous()
        self.owner.draw()

class Mimic_Pod(Spell):
    def __init__(self,name="Mimic Pod",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        card=self.owner.draw()
        card_copy=card.get_copy(owner=self.owner)
        card_copy.initialize_location(self.owner.location)
        card_copy.hand_in(speed=40)

class Leeching_Poison(Spell):
    def __init__(self,name="Leeching Poison",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return self.owner.has_weapon()
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        self.owner.weapon.temporary_effects["lifesteal"]=True

class Roll_the_Bones(Spell):
    def __init__(self,name="Roll the Bones",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        card=self.owner.draw()
        while "Deathrattle" in card.abilities and len(self.owner.hand)<self.owner.hand_limit:
            card=self.owner.draw()

class Doomerang(Spell):
    def __init__(self,name="Doomerang",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion() and self.owner.has_weapon()
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        shiv_animation(self, target)
        self.owner.weapon.deal_damage([target], [self.owner.weapon.get_current_atk()])
        card_copy=self.owner.weapon.get_copy(owner=self.owner)
        
        self.owner.board.weapons[self.owner.side].remove(self.owner.weapon)
        self.owner.board.queue.remove(self.owner.weapon)
        self.owner.weapon=None
        
        card_copy.appear_in_hand()

class Lesser_Onyx_Spellstone(Spell):
    def __init__(self,name="Lesser Onyx Spellstone",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.trigger_event_type="play a card"
        self.upgrade_target=Onyx_Spellstone
        self.counter=0
        self.goal=3

    def invoke(self,target):
        super(self.__class__,self).invoke()
        target_pool=self.enemy_minions()
        if len(target_pool)>0:
            targets=random.sample(target_pool,k=min(1,len(target_pool)))
            for target in targets: 
                assassinate_animation(self, target)
                target.destroy()
        
    def trigger_effect(self, triggering_card):
        if triggering_card.Deathrattle and triggering_card.side==self.side:
            self.counter+=1
            if self.counter>=self.goal:
                self.upgrade()
        
class Onyx_Spellstone(Spell):
    def __init__(self,name="Onyx Spellstone",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.trigger_event_type="play a card"
        self.upgrade_target=Greater_Onyx_Spellstone
        self.counter=0
        self.goal=3

    def invoke(self,target):
        super(self.__class__,self).invoke()
        target_pool=self.enemy_minions()
        if len(target_pool)>0:
            targets=random.sample(target_pool,k=min(2,len(target_pool)))
            for target in targets: 
                assassinate_animation(self, target)
                target.destroy()
        
    def trigger_effect(self, triggering_card):
        if triggering_card.Deathrattle and triggering_card.side==self.side:
            self.counter+=1
            if self.counter>=self.goal:
                self.upgrade()

class Greater_Onyx_Spellstone(Spell):
    def __init__(self,name="Greater Onyx Spellstone",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)

    def invoke(self,target):
        super(self.__class__,self).invoke()
        target_pool=self.enemy_minions()
        if len(target_pool)>0:
            targets=random.sample(target_pool,k=min(3,len(target_pool)))
            for target in targets: 
                assassinate_animation(self, target)
                target.destroy()
                        
class Crystal_Core(Spell):
    def __init__(self,name="Crystal Core",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        time_warp_animation(self)
        for card in self.friendly_minions()+self.owner.hand+self.owner.deck.cards:
            if isinstance(card,Minion):
                card.set_stats(atk=4,hp=4)
        enchantment=Crystal_Core_Effect(owner=self.owner)

class Crystal_Core_Effect(Enchantment):
    def __init__(self,name="Crystal Core",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_events=[]

    def ongoing_effect(self,target):
        if target.side==self.side and isinstance(target, Minion):
            return {'cost':0}
        else:
            return {}            


                           
'''Shaman Spells'''
class Ancestral_Healing(Spell):
    def __init__(self,name="Ancestral Healing",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion()
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        shaman_buff_animation(self,target)
        self.heal([target], [target.temp_hp])
        target.gain_taunt()

class Totemic_Might(Spell):
    def __init__(self,name="Totemic Might",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        zodiac_animation(self.owner, self.card_class)
        for minion in self.friendly_minions():
            if minion.has_race("Totem"):
                minion.buff_stats(0,2)

class Frost_Shock(Spell):
    def __init__(self,name="Frost Shock",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.side==-self.side
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        frostbolt_animation(self,target)
        self.deal_damage([target], [1])
        target.get_frozen()

class Rockbiter_Weapon(Spell):
    def __init__(self,name="Rockbiter Weapon",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None and target.side==-self.side
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        shaman_buff_animation(self,target)
        target.current_atk+=3

class Windfury_card(Spell):
    def __init__(self,name="Windfury (card)",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion()
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        shaman_buff_animation(self,target)
        target.gain_windfury()

class Hex(Spell):
    def __init__(self,name="Hex",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion()
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        zodiac_animation(self.owner, self.card_class)
        frog=Frog(owner=target.owner,source=target.location)
        target.transform(frog)

class Bloodlust(Spell):
    def __init__(self,name="Bloodlust",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return len(self.friendly_minions())>0
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        bloodlust_animation(self,self.friendly_minions())
        for minion in self.friendly_minions():
            minion.current_atk+=3

class Earth_Shock(Spell):
    def __init__(self,name="Earth Shock",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None and target.isMinion()
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        lightning_spell_animation(self,target)
        self.silence(target,skip_animation=True)
        self.deal_damage([target], [1])

class Forked_Lightning(Spell):
    def __init__(self,name="Forked Lightning",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.overload=2
    
    def is_valid_on(self, target):
        return len(self.enemy_minions())>0
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        enemy_minions=self.enemy_minions()
        minions=random.sample(self.enemy_minions(),k=min(2,len(enemy_minions)))
        forked_lightning_animation(self,minions)
        self.deal_damage(minions, [2]*len(minions))
        
class Lightning_Bolt(Spell):
    def __init__(self,name="Lightning Bolt",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.overloaded=1
    
    def is_valid_on(self, target):
        return target is not None
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        lightning_spell_animation(self,target)
        self.deal_damage([target], [3])

class Lava_Burst(Spell):
    def __init__(self,name="Lava Burst",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.overload=2
    
    def is_valid_on(self, target):
        return target is not None
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        fire_spell_animation(self,target)
        self.deal_damage([target], [5])

class Far_Sight(Spell):
    def __init__(self,name="Far Sight",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def invoke(self,target):
        super(self.__class__,self).invoke()
        card=self.owner.draw()
        if card is not None:
            card.modify_cost(-3)
        
class Ancestral_Spirit(Spell):
    def __init__(self,name="Ancestral Spirit",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None and target.isMinion()
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        ancestral_spirit_animation(self,target)
        target.deathrattles.append([MethodType(self.deathrattle.__func__,target),"resummon this minion"])
        target.has_deathrattle=True
        
    def deathrattle(self):
        minion=getattr(card_collection,database.cleaned(self.name))(owner=self.owner,source=self.location)
        self.summon(minion)

class Feral_Spirit(Spell):
    def __init__(self,name="Feral Spirit",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.overload=2
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        for i in range(2):
            minion=Spirit_Wolf(owner=self.owner,source="board")
            self.owner.recruit(minion)
                                
class Lightning_Storm(Spell):
    def __init__(self,name="Lightning Storm",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.overload=2
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        lightning_storm_animation(self)
        damages = [random.randint(2,3) for minion in self.enemy_minions()]
        self.deal_damage(self.enemy_minions(),damages)
            
class Reincarnate(Spell):
    def __init__(self,name="Reincarnate",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None and target.isMinion()
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        ancestral_spirit_animation(self,target)
        target.destroy()
        minion=getattr(card_collection,database.cleaned(target.name))(owner=target.owner,source="board")
        self.owner.recruit(minion)

class Crackle(Spell):
    def __init__(self,name="Crackle",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.overload=1
    
    def is_valid_on(self, target):
        return target is not None
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        lightning_spell_animation(self,target)
        self.deal_damage([target], [random.randint(3,6)])
        
class Ancestors_Call(Spell):
    def __init__(self,name="Ancestor's Call",owner=None):
        super(self.__class__,self).__init__(name,owner)
  
    def invoke(self,target):
        super(self.__class__,self).invoke()
        zodiac_animation(self.owner, self.card_class)
        for player in [self.owner,self.owner.opponent]:
            minion = player.search_card(player.hand,card_type="Minion")
            if minion is not None:
                player.put_into_battlefield(minion)

class Lava_Shock(Spell):
    def __init__(self,name="Lava Shock",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        fire_spell_animation(self,target)
        self.deal_damage([target], [2])
        self.owner.overloaded_mana=0
        
class Ancestral_Knowledge(Spell):
    def __init__(self,name="Ancestral Knowledge",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.overload=2
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        zodiac_animation(self.owner, self.card_class)
        self.owner.draw(2)

class Healing_Wave(Spell):
    def __init__(self,name="Healing Wave",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        amount=7
        winner = self.joust("Minion")
        if winner is not None and winner.owner is self.owner:
            amount+=7
            healing_touch_animation(self, target)
        self.heal([target],[amount])

class Elemental_Destruction(Spell):
    def __init__(self,name="Elemental Destruction",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.overload=5
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        minions=self.all_minions()
        elemental_destruction_animation(self)
        damages = [random.randint(4,5) for minion in minions]
        self.deal_damage(minions, damages)

class Everyfin_is_Awesome(Spell):
    def __init__(self,name="Everyfin is Awesome",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return len(self.friendly_minions())>0
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        zodiac_animation(self.owner, self.card_class)
        minions=self.friendly_minions()
        bloodlust_animation(self, minions)
        for minion in minions:
            minion.buff_stats(2,2)

    def ongoing_effect(self,target):
        if target is self and target.board_area=="Hand":
            targets=self.friendly_minions("Murloc")
            return {'cost':-len(targets)}
        else:
            return {} 

class Primal_Fusion(Spell):
    def __init__(self,name="Primal Fusion",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None and target.isMinion()
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        buff_animation(self,target)
        n=len(self.friendly_minions("Totem"))
        target.buff_stats(n,n)

class Stormcrack(Spell):
    def __init__(self,name="Stormcrack",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.overload=1
    
    def is_valid_on(self, target):
        return target is not None and target.isMinion()
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        lightning_spell_animation(self,target)
        self.deal_damage([target], [4])

class Evolve(Spell):
    def __init__(self,name="Evolve",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        for minion in self.friendly_minions():
            minion.evolve()

class Maelstrom_Portal(Spell):
    def __init__(self,name="Maelstrom Portal",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        minions=self.enemy_minions()
        arcane_explosion_animation(self)
        self.deal_damage(minions, [1]*len(minions))
        minion = database.get_random_cards("[type]='Minion' AND [cost]=1", self.owner, 1)[0]
        self.owner.recruit(minion)

class Call_in_the_Finishers(Spell):
    def __init__(self,name="Call in the Finishers",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        for k in range(4):
            minion = Murloc_Razorgill(owner=self.owner,source="board")
            self.owner.recruit(minion,speed=70)

class Jade_Lightning(Spell):
    def __init__(self,name="Jade Lightning",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None
            
    def invoke(self,target):
        super(self.__class__,self).invoke()
        lightning_spell_animation(self, target)
        self.deal_damage([target], [4])
        minion=Jade_Golem(owner=self.owner,source="board")
        self.owner.recruit(minion)

class Devolve(Spell):
    def __init__(self,name="Devolve",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        for minion in self.enemy_minions():
            minion.evolve(-1)

class Finders_Keepers(Spell):
    def __init__(self,name="Finders Keepers",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.overload=1
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        card=self.discover(by_ability="Overload")
        if card is not None:
            card.appear_in_hand()

class Tidal_Surge(Spell):
    def __init__(self,name="Tidal Surge",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None and target.isMinion()
            
    def invoke(self,target):
        super(self.__class__,self).invoke()
        water_spell_animation(self, target)
        self.deal_damage([target], [4])
        self.heal([self.owner], [4])

class Volcano(Spell):
    def __init__(self,name="Volcano",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.overload=2
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        self.owner.board.background=background_dark
        show_board(self.owner.board)
        time.sleep(0.6)
        self.deal_split_damage(self.all_minions(),shots=15,damage=1,effect=get_image("images/fireball2.png",(80,80)),speed=25)
        time.sleep(0.4)
        self.owner.board.background=background    
        
class Spirit_Echo(Spell):
    def __init__(self,name="Spirit Echo",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return len(self.owner.minions)>0
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        for target in self.owner.minions:
            target.deathrattles.append([MethodType(self.deathrattle.__func__,target),"return this to yoru hand"])
            target.has_deathrattle=True
        
    def deathrattle(self):
        minion = self.get_copy(owner=self.owner)
        minion.initialize_location(self.location)
        minion.hand_in()

class Ice_Fishing(Spell):
    def __init__(self,name="Ice Fishing",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        for i in range(2):
            card = self.owner.search_card(self.owner.deck.cards,card_type="Murloc")
            if card is not None:
                self.owner.draw(target=card)

class Avalanche(Spell):
    def __init__(self,name="Avalanche",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None and target.isMinion()
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        cone_of_cold_animation(self, target)
        target.get_frozen()
        targets=target.adjacent_minions()
        self.deal_damage(targets,[3]*len(targets))

class Cryostasis(Spell):
    def __init__(self,name="Cryostasis",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None and target.isMinion()
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        glacial_shard_animation(self, target)
        target.buff_stats(3,3)
        target.get_frozen()

class Crushing_Hand(Spell):
    def __init__(self,name="Crushing Hand",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.overload=3

    def is_valid_on(self, target):
        return target is not None and target.isMinion()
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        fist_of_jaraxxus_animation(self,target)
        self.deal_damage([target], [8])

class Healing_Rain(Spell):
    def __init__(self,name="Healing Rain",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        targets=self.friendly_characters()
        self.split_heal(targets, shots=12, amount=1, effect=get_image("images/heal.png",(80,80)), speed=20, curve=True)

class Primal_Talismans(Spell):
    def __init__(self,name="Primal Talismans",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return len(self.owner.minions)>0
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        for target in self.owner.minions:
            target.deathrattles.append([MethodType(self.deathrattle.__func__,target),"summon a random basic Totem"])
            target.has_deathrattle=True
        
    def deathrattle(self):
        totem=random.choice([Healing_Totem,Searing_Totem,Stoneclaw_Totem,Wrath_of_Air_Totem])(owner=self.owner)
        self.summon(totem)

class Lesser_Sapphire_Spellstone(Spell):
    def __init__(self,name="Lesser Sapphire Spellstone",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.trigger_event_type="overload"
        self.upgrade_target=Sapphire_Spellstone
        self.counter=0
        self.goal=3

    def is_valid_on(self, target):
        return target is not None and target.isMinion() and target.side==self.side
       
    def invoke(self,target):
        super(self.__class__,self).invoke()
        zodiac_animation(self.owner, self.card_class)
        for i in range(1):
            minion_copy=target.get_copy(owner=self.owner)
            minion_copy.initialize_location("board")
            self.owner.recruit(minion_copy,speed=40)
        
    def trigger_effect(self, triggering_entity):
        if triggering_entity[0].side==self.side:
            self.counter+=triggering_entity[1]
            if self.counter>=self.goal:
                self.upgrade()

class Sapphire_Spellstone(Spell):
    def __init__(self,name="Sapphire Spellstone",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        self.trigger_event_type="overload"
        self.upgrade_target=Greater_Sapphire_Spellstone
        self.counter=0
        self.goal=3

    def is_valid_on(self, target):
        return target is not None and target.isMinion() and target.side==self.side
       
    def invoke(self,target):
        super(self.__class__,self).invoke()
        zodiac_animation(self.owner, self.card_class)
        for i in range(2):
            minion_copy=target.get_copy(owner=self.owner)
            minion_copy.initialize_location("board")
            self.owner.recruit(minion_copy,speed=40)
        
    def trigger_effect(self, triggering_entity):
        if triggering_entity[0].side==self.side:
            self.counter+=triggering_entity[1]
            if self.counter>=self.goal:
                self.upgrade()

class Greater_Sapphire_Spellstone(Spell):
    def __init__(self,name="Greater Jasper Spellstone",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion() and target.side==self.side
       
    def invoke(self,target):
        super(self.__class__,self).invoke()
        zodiac_animation(self.owner, self.card_class)
        for i in range(3):
            minion_copy=target.get_copy(owner=self.owner)
            minion_copy.initialize_location("board")
            self.owner.recruit(minion_copy,speed=40)

class Unstable_Evolution(Spell):
    def __init__(self,name="Unstable Evolution",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.Echo=True

    def is_valid_on(self, target):
        return target is not None and target.isMinion() and target.side==self.side
       
    def invoke(self,target):
        super(self.__class__,self).invoke()
        target.evolve()
                                                                                                                                                                                                                            
'''Warlock Spells'''

class Sacrificial_Pact(Spell):
    def __init__(self,name="Sacrificial Pact",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion() and target.side==self.side and target.has_race("Demon")
   
    def invoke(self,target):
        super(self.__class__,self).invoke()
        sacrificial_pact_animation(self,target)
        self.heal([self.owner], [5])
        target.destroy()

class Corruption(Spell):
    def __init__(self,name="Corruption",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def is_valid_on(self, target):
        return target is not None and target.isMinion() and target.side==-self.side
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        sacrificial_pact_animation(self, target)
        target.attachments["Corruption"]=self
        target.trigger_events.append(["start of turn",MethodType(self.trigger_effect.__func__,target)])

    def trigger_effect(self,triggering_player):
        if triggering_player is self.attachments["Corruption"].owner:
            if self.board_area=="Board":
                self.destroy()

class Power_Overwhelming(Spell):
    def __init__(self,name="Power_Overwhelming",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion() and target.side==self.side
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        mortal_coil_animation(self,target)
        target.buff_stats(4,4)
        target.trigger_events.append(["end of turn",MethodType(self.trigger_effect.__func__,target)])

    def trigger_effect(self,triggering_player):
        self.destroy()
            
class Mortal_Coil(Spell):
    def __init__(self,name="Mortal Coil",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion()
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        mortal_coil_animation(self,target)
        self.deal_damage([target], [1])
        if target.destroyed_by is self:
            self.owner.draw()
            
class Soulfire(Spell):
    def __init__(self,name="Soulfire",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        soulfire_animation(self,target)
        self.deal_damage([target], [4])
        self.owner.discard()

class Drain_Life(Spell):
    def __init__(self,name="Drain Life",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        drain_life_animation(self,target)
        self.deal_damage([target], [2])
        self.heal([self.owner],[2])
                        
class Shadow_Bolt(Spell):
    def __init__(self,name="Shadow Bolt",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        #Why is the following invalid?
        #return target.isMinion()   
        return target is not None and target.isMinion()

        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        shadow_bolt_animation(self,target)
        self.deal_damage([target], [4])

class Hellfire(Spell):
    def __init__(self,name="Hellfire",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        targets=self.all_characters()
        hellfire_animation(self)
        self.deal_damage(targets, [3]*len(targets))

class Call_of_the_Void(Spell):
    def __init__(self,name="Call of the Void",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        minion = database.get_random_cards("[type]='Minion' AND [race]='Demon'", self.owner, 1)[0]
        zodiac_animation(self.owner, self.card_class)
        minion.initialize_location(self.owner.location)
        minion.hand_in()

class Demonfire(Spell):
    def __init__(self,name="Demonfire",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion()
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        mortal_coil_animation(self,target)
        if target.side==self.side and target.has_race("Demon"):
            target.buff_stats(2,2)
        else:
            self.deal_damage([target], [2])

class Sense_Demons(Spell):
    def __init__(self,name="Sense Demons",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        for i in range(2):
            card = self.owner.search_card(self.owner.deck.cards,card_type="Demon")
            if card is not None:
                self.owner.draw(target=card)
            else:
                minion=Worthless_Imp(owner=self.owner)
                minion.appear_in_hand()

class Shadowflame(Spell):
    def __init__(self,name="Shadowflame",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion() and target.side==self.side
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        targets=self.enemy_minions()
        shadowflame_animation(self,target)
        self.deal_damage(targets, [target.get_current_atk()]*len(targets))
        target.destroy()

class Siphon_Soul(Spell):
    def __init__(self,name="Siphon Soul",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion()
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        mortal_coil_animation(self,target)
        target.destroy()
        self.heal([self.owner], [3])

class Bane_of_Doom(Spell):
    def __init__(self,name="Bane of Doom",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        mortal_coil_animation(self,target)
        self.deal_damage([target], [2])
        if target.destroyed_by is self:
            minion = database.get_random_cards("[type]='Minion' AND [race]='Demon'", self.owner, 1)[0]
            minion.initialize_location("board")
            self.owner.recruit(minion)
                       
class Twisting_Nether(Spell):
    def __init__(self,name="Twisting Nether",owner=None):
        super(self.__class__,self).__init__(name,owner)
       
    def invoke(self,target):
        super(self.__class__,self).invoke()
        minions=self.all_minions()
        twisting_nether_animation(self,minions)
        destroy_multiple_animation(minions)
        for minion in minions:
            minion.destroy(skip_animation=True)
                       
class Darkbomb(Spell):
    def __init__(self,name="Darkbomb",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        shadow_bolt_animation(self,target)
        self.deal_damage([target], [3])

class Imp_losion(Spell):
    def __init__(self,name="Imp-losion",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion()
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        soulfire_animation(self,target)
        damage=random.randint(2,4)
        self.deal_damage([target], [damage])
        for i in range(damage):
            minion=Imp_Imp_losion(owner=self.owner,source="board")
            self.owner.recruit(minion,speed=80)

class Demonheart(Spell):
    def __init__(self,name="Demonheart",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion()
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        demonheart_animation(self,target)
        if target.side==self.side and target.has_race("Demon"):
            warrior_buff_animation(self, target)
            target.buff_stats(5,5)
        else:
            self.deal_damage([target], [5])

class Demonwrath(Spell):
    def __init__(self,name="Demonwrath",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        targets=self.all_minions_except("Demon")
        abomination_animation(self)
        self.deal_damage(targets, [2]*len(targets))

class Demonfuse(Spell):
    def __init__(self,name="Demonfuse",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion() and target.has_race("Demon")
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        demonheart_animation(self, target)
        target.buff_stats(3,3)
        self.owner.opponent.gain_mana()
            
class Fist_of_Jaraxxus(Spell):
    def __init__(self,name="Fist of Jaraxxus",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def on_discard(self):
        self.invoke(target=None)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        target=random.choice(self.enemy_characters())
        fist_of_jaraxxus_animation(self,target)
        self.deal_damage([target], [4])
        
class Dark_Bargain(Spell):
    def __init__(self,name="Dark Bargain",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return len(self.enemy_minions())>0
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        minion_targets=random.sample(self.enemy_minions(),k=min(2,len(self.enemy_minions())))
        card_targets=random.sample(self.owner.hand,k=min(2,len(self.owner.hand)))
        void_crusher_animation(self, minion_targets)
        for minion in minion_targets:
            minion.destroy(skip_animation=True)

        discard_multiple_animation(card_targets)
        for card in card_targets:
            card.discard(skip_animation=True)

class Curse_of_Rafaam(Spell):
    def __init__(self,name="Curse of Rafaam",owner=None):
        super(self.__class__,self).__init__(name,owner)
 
    def invoke(self,target):
        super(self.__class__,self).invoke()
        card=Cursed(owner=self.owner.opponent)
        card.appear_in_hand()
        
class Cursed(Spell):
    def __init__(self,name="Cursed!",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        self.trigger_event_type="start of turn"
 
    def invoke(self,target):
        super(self.__class__,self).invoke()

    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner:
            shadow_word_animation(self, self.owner)
            self.deal_damage([self.owner], [2])

class Forbidden_Ritual(Spell):
    def __init__(self,name="Forbidden Ritual",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def invoke(self,target):
        super(self.__class__,self).invoke()
        for i in range(self.owner.current_mana):
            minion=Icky_Tentacle(owner=self.owner,source="board")
            self.owner.recruit(minion,speed=50)
        self.owner.current_mana=0

class Spreading_Madness(Spell):
    def __init__(self,name="Spreading Madness",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        self.deal_split_damage(self.all_characters(),shots=9,damage=1,effect=get_image("images/shadow_bolt.png",(50,50)),speed=15,curve=True)   

class Renounce_Darkness(Spell):
    def __init__(self,name="Renounce Darkness",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        hero_power=random.choice([Armor_Up,Dagger_Mastery,Demon_Claws,Fireblast,Lesser_Heal,Reinforce,Shapeshift,Steady_Shot,Totemic_Call])(owner=self.owner)
        self.owner.gain_hero_power(hero_power)
        
        replace_hand_animation(self)
        for card in self.owner.hand+self.owner.deck.cards:
            if card.card_class=="Warlock":
                new_card = database.get_random_cards("[class] LIKE '%"+hero_power.class_name+"%'", self.owner, 1)[0]
                card.replace_by(new_card)
        

class DOOM(Spell):
    def __init__(self,name="DOOM!",owner=None):
        super(self.__class__,self).__init__(name,owner)
       
    def invoke(self,target):
        super(self.__class__,self).invoke()
        minions=self.all_minions()
        DOOM_animation(self,minions)
        destroy_multiple_animation(minions)
        for minion in minions:
            minion.destroy(skip_animation=True)
            
        if len(minions)>0:
            self.owner.draw(len(minions))
    
class Kara_Kazham(Spell):
    def __init__(self,name="Kara Kazham!",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        minion1=Candle(owner=self.owner,source="board")
        self.owner.recruit(minion1)
        minion2=Broom(owner=self.owner,source="board")
        self.owner.recruit(minion2)
        minion3=Teapot(owner=self.owner,source="board")
        self.owner.recruit(minion3)

class Blastcrystal_Potion(Spell):
    def __init__(self,name="Blastcrystal Potion",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion()
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        soulfire_animation(self,target)
        target.destroy()
        self.owner.gain_mana(-1,empty=(self.owner.mana>self.owner.current_mana))

class Bloodfury_Potion(Spell):
    def __init__(self,name="Bloodfury Potion",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion()
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        weapon_enchantment_animation(self, target)
        target.buff_stats(3,0)
        if target.has_race("Demon"):
            target.buff_stats(0,3)

class Felfire_Potion(Spell):
    def __init__(self,name="Felfire Potion",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        targets=self.all_characters()
        chaos_nova_animation(self)
        self.deal_damage(targets, [5]*len(targets))

class Corrupting_Mist(Spell):
    def __init__(self,name="Corrupting Mist",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        corrupting_mist_animation(self)
        for minion in self.all_minions():
            minion.attachments["Corruption"]=self
            minion.trigger_events.append(["start of turn",MethodType(self.trigger_effect.__func__,minion)])

    def trigger_effect(self,triggering_player):
        if triggering_player is self.attachments["Corruption"].owner:
            if self.board_area=="Board":
                self.destroy()

class Feeding_Time(Spell):
    def __init__(self,name="Feeding Time",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion()
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        soulfire_animation(self,target)
        self.deal_damage([target], [3])
        for i in range(3):
            minion=Pterrordax(owner=self.owner,source="board")
            self.owner.recruit(minion,speed=80)

class Bloodbloom(Spell):
    def __init__(self,name="Bloodbloom",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        card=Chogall_Effect(owner=self.owner)
        card.origin=self

class Drain_Soul(Spell):
    def __init__(self,name="Drain_Soul",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.lifesteal=True
    
    def is_valid_on(self, target):
        return target is not None and target.isMinion()
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        mortal_coil_animation(self, target)
        self.deal_damage([target], [2])

class Defile(Spell):
    def __init__(self,name="Defile",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        CONTINUE=True
        counter=0
        while CONTINUE:
            CONTINUE=False
            counter+=1
            minions=self.all_minions()
            abomination_animation(self)
            self.deal_damage(minions,[1]*len(minions))
            
            for minion in minions:
                if minion.destroyed_by is self:
                    CONTINUE=True
            if counter>13:
                CONTINUE=False

class Unwilling_Sacrifice(Spell):
    def __init__(self,name="Unwilling Sacrifice",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion() and target.side==self.side
            
    def invoke(self,target):
        super(self.__class__,self).invoke()
        zodiac_animation(self.owner, self.card_class)
        target_pool=self.enemy_minions()
        if len(target_pool)>0:
            opponent_minion=random.choice(target_pool)
            unwilling_sacrifice_animation(self,target,opponent_minion)
            destroy_multiple_animation([target,opponent_minion])
            target.destroy(skip_animation=True)
            opponent_minion.destroy(skip_animation=True)
        else:
            unwilling_sacrifice_animation(self,target,target)
            target.destroy()

class Treachery(Spell):
    def __init__(self,name="Treachery",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion() and target.side==self.side and not self.owner.board.isFull(self.owner.opponent)
            
    def invoke(self,target):
        zodiac_animation(self.owner, self.card_class)
        self.owner.opponent.take_control(target)

class Dark_Pact(Spell):
    def __init__(self,name="Dark Pact",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion() and target.side==self.side
   
    def invoke(self,target):
        super(self.__class__,self).invoke()
        sacrificial_pact_animation(self,target)
        target.destroy()
        self.heal([self.owner], [4])

class Lesser_Amethyst_Spellstone(Spell):
    def __init__(self,name="Lesser Amethyst Spellstone",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.lifesteal=True
        self.trigger_event_type="hero damage"
        self.upgrade_target=Amethyst_Spellstone
        self.counter=0
        self.goal=1

    def is_valid_on(self, target):
        return target is not None and target.isMinion()
       
    def invoke(self,target):
        super(self.__class__,self).invoke()
        shadow_bolt_animation(self, target)
        self.deal_damage([target], [3])
        
    def trigger_effect(self,triggering_entity):
        if triggering_entity[0].owner is self.owner:
            self.counter+=1
            if self.counter>=self.goal:
                self.upgrade()

class Amethyst_Spellstone(Spell):
    def __init__(self,name="Amethyst Spellstone",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.lifesteal=True
        self.trigger_event_type="hero damage"
        self.upgrade_target=Greater_Amethyst_Spellstone
        self.counter=0
        self.goal=1

    def is_valid_on(self, target):
        return target is not None and target.isMinion()
       
    def invoke(self,target):
        super(self.__class__,self).invoke()
        shadow_bolt_animation(self, target)
        self.deal_damage([target], [5])
        
    def trigger_effect(self,triggering_entity):
        if triggering_entity[0].owner is self.owner:
            self.counter+=1
            if self.counter>=self.goal:
                self.upgrade()

class Greater_Amethyst_Spellstone(Spell):
    def __init__(self,name="Greater Amethyst Spellstone",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        self.lifesteal=True

    def is_valid_on(self, target):
        return target is not None and target.isMinion()
       
    def invoke(self,target):
        super(self.__class__,self).invoke()
        shadow_bolt_animation(self, target)
        self.deal_damage([target], [7])

class Cataclysm(Spell):
    def __init__(self,name="Cataclysm",owner=None):
        super(self.__class__,self).__init__(name,owner)
       
    def invoke(self,target):
        super(self.__class__,self).invoke()
        minions=self.all_minions()
        meteor_animation(self, self.owner.board)
        destroy_multiple_animation(minions)
        for minion in minions:
            minion.destroy(skip_animation=True)
            
        self.owner.discard_hand()
                                                                
class Nether_Portal(Spell):
    def __init__(self,name="Nether Portal",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return not self.owner.board.isFull(self.owner)
            
    def invoke(self,target):
        super(self.__class__,self).invoke()
        portal=Nether_Portal_minion(owner=self.owner,source="board")
        self.owner.recruit(portal)
        self.owner.enchantments.append(portal)
                                                                                                                                                                                                                                                      
'''Warrior Spell'''
class Whirlwind(Spell):
    def __init__(self,name="Whirlwind",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        whirlwind_animation(self)
        minions=self.all_minions()
        self.deal_damage(minions,[1]*len(minions))

class Charge_card(Spell):
    def __init__(self,name="Charge (card)",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion() and target.side==self.side
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        charge_card_animation(self,target)
        target.gain_rush()

class Execute(Spell):
    def __init__(self,name="Execute",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion() and target.side==-self.side and target.damaged()
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        execute_animation(self,target)
        target.destroy()

class Cleave(Spell):
    def __init__(self,name="Cleave",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return len(self.enemy_minions())>0
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        enemy_minions=self.enemy_minions()
        minions=random.sample(enemy_minions,k=min(2,len(enemy_minions)))
        cleave_animation(self,minions)
        self.deal_damage(minions, [2]*len(minions))

class Heroic_Strike(Spell):
    def __init__(self,name="Heroic Strike",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        heroic_strike_animation(self)
        self.owner.current_atk+=4

class Shield_Block(Spell):
    def __init__(self,name="Shield Block",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        self.owner.increase_shield(5)
        shield_block_animation(self)
        self.owner.draw()

class Inner_Rage(Spell):
    def __init__(self,name="Inner Rage",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion()
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        charge_animation(target)
        self.deal_damage([target], [1])
        target.buff_stats(2,0)

class Battle_Rage(Spell):
    def __init__(self,name="Battle Rage",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        targets=[]
        for target in self.friendly_characters():
            if target.damaged():
                targets.append(target)
            
        battle_rage_animation(self,targets)
        self.owner.draw(len(targets))

class Rampage(Spell):
    def __init__(self,name="Rampage",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion() and target.damaged()
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        warrior_buff_animation(self,target)
        target.buff_stats(3,3)

class Slam(Spell):
    def __init__(self,name="Slam",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion()
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        charge_shot_animation(self.owner, target)
        self.deal_damage([target], [2])
        if target.board_area=="Board":
            self.owner.draw()

class Upgrade(Spell):
    def __init__(self,name="Upgrade!",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        if self.owner.has_weapon():
            self.owner.weapon.buff_stats(1,1)
        else:
            weapon=Heavy_Axe(owner=self.owner)
            self.owner.equip_weapon(weapon)

class Commanding_Shout(Spell):
    def __init__(self,name="Commanding Shout",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        card=Commanding_Shout_Effect(owner=self.owner)
        self.owner.draw()
 
class Commanding_Shout_Effect(Enchantment):
    def __init__(self,name="Commanding Shout",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

    def ongoing_effect(self,target):
        if target.isMinion() and target.side==self.side:
            return {'shout':True}
        else:
            return {}            

class Mortal_Strike(Spell):
    def __init__(self,name="Mortal Strike",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        charge_shot_animation(self.owner,target)
        damage=4
        if self.owner.current_hp<=12:
            damage+=2
        self.deal_damage([target],[damage])

class Shield_Slam(Spell):
    def __init__(self,name="Shield Slam",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion()
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        charge_shot_animation(self.owner, target)
        self.deal_damage([target], [self.owner.shield])

class Brawl(Spell):
    def __init__(self,name="Brawl",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return len(self.all_minions())>0
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        
        targets=self.all_minions()
        survivor=random.choice(targets)
        brawl_animation(self,targets,survivor)
        for minion in targets:
            if minion is not survivor:
                minion.destroy(skip_animation=True)

class Bouncing_Blade(Spell):
    def __init__(self,name="Bouncing Blade",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        count=0
        while count<80:
            target_pool=[]
            for minion in self.all_minions():
                if minion.is_immunized() or (self.owner.board.get_buff(minion)['shout'] and minion.get_current_hp()==1):
                    continue
                target_pool.append(minion)
            if len(target_pool)>0:
                target=random.choice(target_pool)
                bouncing_blade_animation(self,target)
                self.deal_damage([target], [1],skip_animation=True)
                count+=1
                if target.board_area!="Board":
                    break
            else:
                break
                       
class Crush(Spell):
    def __init__(self,name="Crush",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion()
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        crush_animation(self,target)
        target.destroy()

    def ongoing_effect(self,target):
        if target is self and target.board_area=="Hand":
            reduction=0
            targets=self.friendly_minions()
            for minion in targets:
                if minion.damaged():
                    reduction=4
            return {'cost':-reduction}
        else:
            return {} 

class Revenge(Spell):
    def __init__(self,name="Revenge",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        whirlwind_animation(self)
        minions=self.all_minions()
        damage=1
        if self.owner.current_hp<=12:
            damage=3
        self.deal_damage(minions,[damage]*len(minions))
                                                                                                                                                              
class Warpath(Spell):
    def __init__(self,name="Warpath",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        warpath_animation(self)
        minions=self.all_minions()
        self.deal_damage(minions,[1]*len(minions))        

class Bolster(Spell):
    def __init__(self,name="Bolster",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        targets=[]
        for minion in self.friendly_minions():
            if minion.has_taunt:
                targets.append(minion)
                
        return len(targets)>0
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        targets=[]
        for minion in self.friendly_minions():
            if minion.has_taunt:
                minion.buff_stats(2,2)
                targets.append(minion)
        buff_multiple_animation(self, targets)
            
class Bash(Spell):
    def __init__(self,name="Bash",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        charge_shot_animation(self.owner, target)
        self.deal_damage([target], [3])
        self.owner.increase_shield(3)         

class Blood_To_Ichor(Spell):
    def __init__(self,name="Blood To Ichor",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion()
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        shiv_animation(self, target)
        self.deal_damage([target], [1])
        if target.board_area=="Board":
            minion=Slime_Blood_To_Ichor(owner=self.owner,source="board")
            self.owner.recruit(minion)

class Blood_Warriors(Spell):
    def __init__(self,name="Blood Warriors",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        targets=[]
        for target in self.friendly_minions():
            if target.damaged():
                targets.append(target)
            
        battle_rage_animation(self,targets)
        for target in targets:
            minion_copy=getattr(card_collection,database.cleaned(target.name))(owner=self.owner,source=target.location)
            minion_copy.hand_in(speed=40)  

class Ironforge_Portal(Spell):
    def __init__(self,name="Ironforge Portal",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        self.owner.increase_shield(4)
        minion = database.get_random_cards("[type]='Minion' AND [cost]=4", self.owner, 1)[0]
        self.owner.recruit(minion)

class Protect_the_King(Spell):
    def __init__(self,name="Protect the King!",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def is_valid_on(self, target):
        return len(self.enemy_minions())>0 and not self.owner.board.isFull(self.owner)
    
    def invoke(self,target):
        target_pool = self.enemy_minions()
        if len(target_pool)>0:
            super(self.__class__,self).invoke()
            for i in range(len(target_pool)):
                minion=Pawn(owner=self.owner,source="board")
                self.owner.recruit(minion,speed=80)  

class I_Know_a_Guy(Spell):
    def __init__(self,name="I Know a Guy",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        card=self.discover(by_ability="Taunt")
        if card is not None:
            card.appear_in_hand()

class Iron_Hide(Spell):
    def __init__(self,name="Iron Hide",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        self.owner.increase_shield(5)

class Explore_UnGoro(Spell):
    def __init__(self,name="Explore Un'Goro",owner=None):
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        explore_ungoro_animation(self)
        for card in self.owner.deck.cards:
            spell=Choose_Your_Path(owner=self.owner)
            card.replace_by(spell)
            
class Choose_Your_Path(Spell):
    def __init__(self,name="Choose Your Path",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        card=self.discover()
        if card is not None:
            card.hand_in()  

class Sudden_Genesis(Spell):
    def __init__(self,name="Sudden Genesis",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        targets=[]
        for minion in self.friendly_minions():
            if minion.damaged():
                targets.append(minion)
            
        battle_rage_animation(self,targets)
        for minion in targets:
            minion_copy=minion.get_copy(owner=self.owner)
            minion_copy.initialize_location(minion.location)
            minion_copy.copy_stats(minion)
            self.owner.recruit(minion_copy)

class Forge_of_Souls(Spell):
    def __init__(self,name="Forge of Souls",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        for i in range(2):
            card = self.owner.search_card(self.owner.deck.cards,card_type="Weapon")
            if card is not None:
                self.owner.draw(target=card)

class Bring_It_On(Spell):
    def __init__(self,name="Bring It On!",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        self.owner.increase_shield(10)
        for card in self.owner.opponent.hand:
            if card.isMinions():
                card.modify_cost(-2)

class Dead_Mans_Hand(Spell):
    def __init__(self,name="Dead Man's Hand",owner=None):
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        card_copies=[]
        for card in self.owner.hand:
            card_copy=card.get_copy(owner=self.owner)
            card_copy.initialize_location(card.location)
            card_copies.append(card_copy)
        self.shuffle_cards(card_copies,self.owner.deck)

class Unidentified_Shield(Spell):
    def __init__(self,name="Unidentified Shield",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.trigger_event_type="add to hand"
        self.upgrade_targets=[Runed_Shield,Serrated_Shield,Spiked_Shield,Tower_Shield_10]
          
    def trigger_effect(self,triggering_card):
        if triggering_card is self:
            self.upgrade_target=random.choice(self.upgrade_targets)
            self.upgrade()
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        shield_block_animation(self)
        self.owner.increase_shield(5)

class Runed_Shield(Spell):
    def __init__(self,name="Runed Shield",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
   
    def invoke(self,target):
        super(self.__class__,self).invoke()
        shield_block_animation(self)
        self.owner.increase_shield(5)
        minion=Iron_Golem(owner=self.owner,source="board")
        self.owner.recruit(minion)

class Serrated_Shield(Spell):
    def __init__(self,name="Serrated Shield",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        self.tags.append("Targeted")

    def is_valid_on(self, target):
        return target is not None
       
    def invoke(self,target):
        super(self.__class__,self).invoke()
        shield_block_animation(self)
        self.owner.increase_shield(5)
        charge_shot_animation(self, target)
        self.deal_damage([target],[5])

class Spiked_Shield(Spell):
    def __init__(self,name="Spiked Shield",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)

    def invoke(self,target):
        super(self.__class__,self).invoke()
        shield_block_animation(self)
        self.owner.increase_shield(5)
        weapon=Spiked_Shield_weapon(owner=self.owner)
        self.owner.equip_weapon(weapon)

class Tower_Shield_10(Spell):
    def __init__(self,name="Tower Shield %2B10",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        shield_block_animation(self)
        self.owner.increase_shield(5)
        rage_buff_animation(self.owner)
        shield_block_animation(self)
        self.owner.increase_shield(10)

class Gather_Your_Party(Spell):
    def __init__(self,name="Gather Your Party",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def invoke(self,target):
        super(self.__class__,self).invoke()
        minion=self.owner.search_card(self.owner.deck.cards,card_type="Minion")
        if minion is not None:
            self.recruit(minion)

class Lesser_Mithril_Spellstone(Spell):
    def __init__(self,name="Lesser Mithril Spellstone",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.trigger_event_type="equip weapon"
        self.upgrade_target=Mithril_Spellstone
        self.counter=0
        self.goal=1

    def invoke(self,target):
        super(self.__class__,self).invoke()
        for i in range(1):
            minion=Mithril_Golem(owner=self.owner,source="board")
            self.owner.recruit(minion)
        
    def trigger_effect(self, triggering_weapon):
        if triggering_weapon.side==self.side:
            self.counter+=1
            if self.counter>=self.goal:
                self.upgrade()
        
class Mithril_Spellstone(Spell):
    def __init__(self,name="Mithril Spellstone",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.trigger_event_type="equip weapon"
        self.upgrade_target=Greater_Mithril_Spellstone
        self.counter=0
        self.goal=1

    def invoke(self,target):
        super(self.__class__,self).invoke()
        for i in range(2):
            minion=Mithril_Golem(owner=self.owner,source="board")
            self.owner.recruit(minion)
        
    def trigger_effect(self, triggering_weapon):
        if triggering_weapon.side==self.side:
            self.counter+=1
            if self.counter>=self.goal:
                self.upgrade()

class Greater_Mithril_Spellstone(Spell):
    def __init__(self,name="Greater Mithril Spellstone",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)

    def invoke(self,target):
        super(self.__class__,self).invoke()
        for i in range(3):
            minion=Mithril_Golem(owner=self.owner,source="board")
            self.owner.recruit(minion)

class Reckless_Flurry(Spell):
    def __init__(self,name="Reckless Flurry",owner=None):
        super(self.__class__,self).__init__(name,owner)

    def invoke(self,target):
        super(self.__class__,self).invoke()
        blade_flurry_animation(self)
        targets=self.all_minions()
        self.deal_damage(targets, [self.owner.shield]*len(targets))
        self.owner.shield=0
                                                                            
'''Quests'''                                                                                                                                                                                                                                                                                                                                                                                                                
class Quest(Spell):
    def __init__(self,name="Default Quest",owner=None):
        super(Quest,self).__init__(name,owner)
        self.board_image=get_image("images/quest.png",(30,30))
        self.counter=0

    def is_valid_on(self, target):
        # Secret with same name invoked already cannot be invoked at the same time.
        for quest in self.owner.quests:
            if quest.name==self.name:
                self.rect.x,self.rect.y=self.location
                show_text(message="Same quest cannot be started!",flip=True, pause=1)
                return False
            
        return True
    
    def invoke(self,target=None):
 
        #Register quest from hand to board   
        self.owner.quests.append(self)
        if self in self.owner.hand:
            self.owner.hand.remove(self)
        self.board_area="Board"
        self.owner.current_mana-=max(0,self.get_current_cost())
        self.image=self.board_image
        sort_triggerables_animation(self.owner.quests+self.owner.secrets)
        
    def trigger(self):
        trigger_quest_animation(self)
        if self.counter>=self.goal:
            self.complete()
    
    def complete(self):
        complete_quest_animation(self)
        self.owner.quests.remove(self)
        self.owner.board.spell_graves[self.owner.side].append(self)
        self.board_area="Grave"
        self.current_cost=self.cost
        sort_triggerables_animation(self.owner.quests+self.owner.secrets)

class Jungle_Giants(Quest):
    def __init__(self,name="Jungle Giants",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.quest_type="summon a minion"
        self.goal=5
    
    def trigger(self,trigger_source):
        if trigger_source.isMinion() and trigger_source.temp_atk>=5:
            self.counter+=1
            super(self.__class__,self).trigger()
    
    def complete(self):
        super(self.__class__,self).complete()
        minion=Barnabus_the_Stomper(owner=self.owner,source=(self.rect.x,self.rect.y))
        minion.hand_in()
        
class The_Marsh_Queen(Quest):
    def __init__(self,name="The Marsh Queen",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.quest_type="play a card"
        self.goal=7
    
    def trigger(self,trigger_source):
        if trigger_source.isMinion() and trigger_source.cost==1:
            self.counter+=1
            super(self.__class__,self).trigger()
    
    def complete(self):
        super(self.__class__,self).complete()
        minion=Queen_Carnassa(owner=self.owner,source=(self.rect.x,self.rect.y))
        minion.hand_in()

class Open_the_Waygate(Quest):
    def __init__(self,name="Open the Waygate",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.quest_type="play a card"
        self.goal=8
    
    def trigger(self,trigger_source):
        if trigger_source.isSpell and not trigger_source.started_in_deck:
            self.counter+=1
            super(self.__class__,self).trigger()
    
    def complete(self):
        super(self.__class__,self).complete()
        spell=Time_Warp(owner=self.owner,source=(self.rect.x,self.rect.y))
        spell.hand_in()

class The_Last_Kaleidosaur(Quest):
    def __init__(self,name="The Last Kaleidosaur",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.quest_type="play a card"
        self.goal=6
    
    def trigger(self,trigger_source):
        if trigger_source.isSpell and trigger_source.target is not None and trigger_source.target.isMinion() and trigger_source.side==self.side and trigger_source.target.side==self.side:
            self.counter+=1
            super(self.__class__,self).trigger()
    
    def complete(self):
        super(self.__class__,self).complete()
        minion=Galvadon(owner=self.owner,source=(self.rect.x,self.rect.y))
        minion.hand_in()

class Awaken_the_Makers(Quest):
    def __init__(self,name="Awaken the Makers",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.quest_type="summon a minion"
        self.goal=7
    
    def trigger(self,trigger_source):
        if trigger_source.isMinion() and trigger_source.has_deathrattle:
            self.counter+=1
            super(self.__class__,self).trigger()
    
    def complete(self):
        super(self.__class__,self).complete()
        minion=Amara_Warden_of_Hope(owner=self.owner,source=(self.rect.x,self.rect.y))
        minion.hand_in()
                        
class Activate_the_Obelisk(Quest):
    def __init__(self,name="Activate the Obelisk",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.quest_type="restore health"
        self.goal=15
    
    def trigger(self,trigger_source):
        self.counter+=int(trigger_source)
        super(self.__class__,self).trigger()
    
    def complete(self):
        super(self.__class__,self).complete()
        new_hero_power=Obelisks_Eye(owner=self.owner)
        self.owner.gain_hero_power(new_hero_power)

class The_Caverns_Below(Quest):
    def __init__(self,name="The Caverns Below",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.quest_type="play a card"
        self.goal=5
        self.max_num=0
        self.card_factory={}
    
    def trigger(self,trigger_source):
        if trigger_source.name not in self.card_factory:
            self.card_factory[trigger_source.name]=1
        else:
            self.card_factory[trigger_source.name]+=1
        if self.card_factory[trigger_source.name]>self.max_num:
            self.counter+=1
            super(self.__class__,self).trigger()
            self.max_num+=1
    
    def complete(self):
        super(self.__class__,self).complete()
        spell=Crystal_Core(owner=self.owner,source=(self.rect.x,self.rect.y))
        spell.hand_in()

class Unite_the_Murlocs(Quest):
    def __init__(self,name="Unite_the_Murlocs",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.quest_type="summon a minion"
        self.goal=10
    
    def trigger(self,trigger_source):
        if trigger_source.has_race("Murloc"):
            self.counter+=1
            super(self.__class__,self).trigger()
    
    def complete(self):
        super(self.__class__,self).complete()
        spell=Nether_Portal(owner=self.owner,source=(self.rect.x,self.rect.y))
        spell.hand_in()

class Lakkari_Sacrifice(Quest):
    def __init__(self,name="Lakkari Sacrifice",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.quest_type="on discard"
        self.goal=6
    
    def trigger(self,trigger_source):
        if trigger_source.owner is self.owner:
            self.counter+=1
            super(self.__class__,self).trigger()
    
    def complete(self):
        super(self.__class__,self).complete()
        minion=Amara_Warden_of_Hope(owner=self.owner,source=(self.rect.x,self.rect.y))
        minion.hand_in()

class Fire_Plumes_Heart(Quest):
    def __init__(self,name="Fire Plume's Heart",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.quest_type="play a card"
        self.goal=3
    
    def trigger(self,trigger_source):
        if trigger_source.isMinion() and trigger_source.taunt:
            self.counter+=1
            super(self.__class__,self).trigger()
    
    def complete(self):
        super(self.__class__,self).complete()
        weapon=Sulfuras(owner=self.owner,source=(self.rect.x,self.rect.y))
        weapon.hand_in()
                                                                                               
class Secret(Spell):
    def __init__(self,name="Default Secret",owner=None):
        super(Secret,self).__init__(name,owner)
        self.board_image=get_image("images/hero_images/"+self.card_class+"_secret_b.png",(30,30))
        self.trigger_on_owner_turn=False

    def is_valid_on(self, target=None):
        # Secret with same name invoked already cannot be invoked at the same time.
        for secret in self.owner.secrets:
            if secret.name==self.name:
                self.rect.x,self.rect.y=self.location
                #show_text(message="Same secret cannot be invoked!",flip=True, pause=1)
                return False
            
        return True
    
    def invoke(self,target=None):
        #Register secret to board
        self.trigger_events.append([self.trigger_event_type,self.trigger_effect])
        self.owner.secrets.append(self)
        self.owner.board.queue.append(self)
        if self in self.owner.hand:
            self.owner.hand.remove(self)
        self.board_area="Board"
        self.image=self.board_image
        sort_triggerables_animation(self.owner.secrets+self.owner.quests)

    
    def trigger(self):
        trigger_secret_animation(self)
        self.owner.secrets.remove(self)
        self.owner.board.queue.remove(self)
        self.owner.board.spell_graves[self.owner.side].append(self)
        self.board_area="Grave"
        self.current_cost=self.cost
        self.trigger_events=[]
        sort_triggerables_animation(self.owner.secrets+self.owner.quests)
    
        #Trigger reveal secret effect if any
        self.owner.board.activate_triggered_effects('secret revealed',self)
            
    def destroy(self,skip_animation=False):
        if not skip_animation:
            destroy_secret_animation(self)
        self.owner.secrets.remove(self)
        self.owner.board.queue.remove(self)
        self.owner.board.spell_graves[self.owner.side].append(self)
        self.board_area="Grave"
        self.current_cost=self.cost
        self.trigger_events=[]
        sort_triggerables_animation(self.owner.secrets+self.owner.quests)
        
'''Mage Secrets'''            
class Mirror_Entity(Secret):
    def __init__(self,name="Mirror Entity",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.trigger_event_type="summon from hand"
    
    def trigger_effect(self,triggering_card):
        if len(self.owner.minions)<=6 and triggering_card.side==-self.side and triggering_card.board_area=="Board":
            super(self.__class__,self).trigger()
            minion=getattr(card_collection,database.cleaned(triggering_card.name))(owner=self.owner,source="board")
            self.owner.recruit(minion)
            minion.copy_stats(triggering_card)
                      
class Ice_Barrier(Secret):
    def __init__(self,name="Ice Barrier",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.trigger_event_type="attack"
    
    def trigger_effect(self,triggering_entity):
        if triggering_entity.target is self.owner:
            super(self.__class__,self).trigger()
            ice_block_animation(self)
            self.owner.increase_shield(8)

class Ice_Block(Secret):
    def __init__(self,name="Ice Block",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.trigger_event_type="modify damage"
    
    def trigger_effect(self,triggering_entity):
        damage_source=triggering_entity[0]
        amount=triggering_entity[1]
        player=triggering_entity[2]
        if player is self.owner and self.owner.current_hp+self.owner.shield<=triggering_entity[1]:
            super(self.__class__,self).trigger()
            ice_block_animation(self)
            #self.owner.temporary_effects['immune']=True
            self.owner.modified_damage=0
            card=Ice_Block_Effect(owner=self.owner)
                    
class Ice_Block_Effect(Enchantment):
    def __init__(self,name="Ice Block",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_events=[("start of turn",self.trigger_effect)]
        self.activate=False

    def ongoing_effect(self,target):
        if target is self.owner:
            return {'immune':True}
        else:
            return {}            
        
    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner:
            self.destroy()

class Counterspell(Secret):
    def __init__(self,name="Counterspell",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.trigger_event_type="cast a spell"
    
    def trigger_effect(self,triggering_entity):
        Spell.invoke(triggering_entity)
        super(self.__class__,self).trigger()

class Vaporize(Secret):
    def __init__(self,name="Vaporize",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.trigger_event_type="attack"
    
    def trigger_effect(self,triggering_entity):
        if triggering_entity.isMinion() and triggering_entity.target is self.owner:
            super(self.__class__,self).trigger()
            vaporize_animation(self,triggering_entity)
            triggering_entity.destroy()
            
class Spellbender(Secret):
    def __init__(self,name="Spellbender",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.trigger_event_type="cast a spell"
    
    def trigger_effect(self,triggering_entity):
        if triggering_entity.target is not None and triggering_entity.target.isMinion() and not self.owner.board.isFull(self.owner):
            super(self.__class__,self).trigger()
            minion=Spellbender_minion(owner=self.owner)
            self.owner.summon(minion)
            triggering_entity.invoke(minion)

class Duplicate(Secret):
    def __init__(self,name="Duplicate",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.trigger_event_type="minion dies"
    
    def trigger_effect(self,triggering_minion):
        if triggering_minion.side==self.side:
            super(self.__class__,self).trigger()
            for i in range(2):
                minion=getattr(card_collection,database.cleaned(triggering_minion.name))(owner=self.owner,source=triggering_minion.location)
                minion.appear_in_hand()

class Potion_of_Polymorph(Secret):
    def __init__(self,name="Potion of Polymorph",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.trigger_event_type="summon from hand"
    
    def trigger_effect(self,triggering_entity):
        if triggering_entity.board_area=="Board":#Not mortally wounded
            super(self.__class__,self).trigger()
            sheep=Sheep(owner=triggering_entity.owner)
            triggering_entity.transform(sheep)

class Effigy(Secret):
    def __init__(self,name="Effigy",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.trigger_event_type="minion dies"
    
    def trigger_effect(self,triggering_minion):
        if triggering_minion.side==self.side:
            super(self.__class__,self).trigger()
            minion = database.get_random_cards("[type]='Minion' AND [cost]="+str(triggering_minion.cost), self.owner, 1)[0]
            minion.initialize_location(triggering_minion.location)
            self.owner.recruit(minion)

class Mana_Bind(Secret):
    def __init__(self,name="Mana Bind",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.trigger_event_type="cast a spell"
    
    def trigger_effect(self,triggering_entity):
        super(self.__class__,self).trigger()
        spell_copy=getattr(card_collection,database.cleaned(triggering_entity.name))(owner=self.owner)
        spell_copy.current_cost=0
        spell_copy.appear_in_hand()

class Frozen_Clone(Secret):
    def __init__(self,name="Frozen Clone",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.trigger_event_type="summon from hand"
    
    def trigger_effect(self,triggering_card):
        if self.owner.hand<self.owner.hand_limit:
            super(self.__class__,self).trigger()
            for i in range(2):
                minion=triggering_card.get_copy(owner=self.owner)
                minion.appear_in_hand()

class Explosive_Runes(Secret):
    def __init__(self,name="Explosive Runes",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.trigger_event_type="summon from hand"
    
    def trigger_effect(self,triggering_card):
        if triggering_card.side==-self.side and triggering_card.board_area=="Board":
            super(self.__class__,self).trigger()
            fireball_animation(self, triggering_card)
            self.deal_damage([triggering_card,triggering_card.owner],[min(6,triggering_card.get_current_hp()),6-min(6,triggering_card.get_current_hp())])
                                                           
'''Hunter Secrets'''                                                
class Explosive_Trap(Secret):
    def __init__(self,name="Explosive Trap",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.trigger_event_type="attack"
    
    def trigger_effect(self,triggering_entity):
        if triggering_entity.target is self.owner:
            super(self.__class__,self).trigger()
            explosive_trap_animation(self)
            targets=self.enemy_characters()
            self.deal_damage(targets,[2]*len(targets))

class Freezing_Trap(Secret):
    def __init__(self,name="Freezing Trap",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.trigger_event_type="attack"
    
    def trigger_effect(self,triggering_entity):
        if triggering_entity.isMinion() and triggering_entity.side==-self.side:
            super(self.__class__,self).trigger()
            triggering_entity.return_hand()
            triggering_entity.modify_cost(2)

class Snipe(Secret):
    def __init__(self,name="Snipe",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.trigger_event_type="summon from hand"
    
    def trigger_effect(self,triggering_entity):
        if triggering_entity.board_area=="Board":#Not mortally wounded
            super(self.__class__,self).trigger()
            snipe_animation(self,triggering_entity)
            self.deal_damage([triggering_entity], [4])
              
class Misdirection(Secret):
    def __init__(self,name="Misdirection",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.trigger_event_type="attack"
    
    def trigger_effect(self,triggering_entity):
        target_pool=triggering_entity.friendly_characters()+triggering_entity.enemy_minions()
        if triggering_entity in target_pool:
            target_pool.remove(triggering_entity)
            
        if triggering_entity.side==-self.side and triggering_entity.target is self.owner and len(target_pool)>0:
            super(self.__class__,self).trigger()
            target = random.choice(target_pool)
            misdirection_animation(self,target)
            triggering_entity.target=target                     

class Snake_Trap(Secret):
    def __init__(self,name="Snake Trap",owner=None):  
        super(self.__class__,self).__init__(name,owner)
        self.trigger_event_type="attack"
    
    def trigger_effect(self,triggering_entity):
        if not self.owner.board.isFull(self.owner) and triggering_entity.target.isMinion() and triggering_entity.target.side==self.side:
            super(self.__class__,self).trigger()
            for i in range(3):
                minion=Snake(owner=self.owner,source="board")
                self.owner.recruit(minion,speed=80)
                   
class Bear_Trap(Secret):
    def __init__(self,name="Bear Trap",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.trigger_event_type="after attack"
    
    def trigger_effect(self,triggering_entity):
        if triggering_entity.target is self.owner:
            super(self.__class__,self).trigger()
            minion=Ironfur_Grizzly(owner=self.owner,source="board")
            self.owner.recruit(minion) 

class Dart_Trap(Secret):
    def __init__(self,name="Dart Trap",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.trigger_event_type="use hero power"
    
    def trigger_effect(self,triggering_entity):
        super(self.__class__,self).trigger()
        target_pool=self.enemy_characters()
        target=random.choice(target_pool)
        snipe_animation(self,target)
        self.deal_damage([target], [5])

class Cat_Trick(Secret):
    def __init__(self,name="Cat Trick",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.trigger_event_type="play a card"
    
    def trigger_effect(self,triggering_entity):
        if triggering_entity.isSpell:
            super(self.__class__,self).trigger()
            minion=Cat_in_a_Hat(owner=self.owner,source="board")
            self.owner.recruit(minion)

class Hidden_Cache(Secret):
    def __init__(self,name="Hidden Cache",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.trigger_event_type="play a card"
    
    def trigger_effect(self,triggering_entity):
        if triggering_entity.isMinion():
            super(self.__class__,self).trigger()
            self.owner.buff_hand("Minion")

class Venomstrike_Trap(Secret):
    def __init__(self,name="Venomstrike Trap",owner=None):  
        super(self.__class__,self).__init__(name,owner)
        self.trigger_event_type="attack"
    
    def trigger_effect(self,triggering_entity):
        if not self.owner.board.isFull(self.owner) and triggering_entity.target.isMinion() and triggering_entity.target.side==self.side:
            super(self.__class__,self).trigger()
            minion=Emperor_Cobra(owner=self.owner,source="board")
            self.owner.recruit(minion)

class Wandering_Monster(Secret):
    def __init__(self,name="Wandering Monster",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.trigger_event_type="attack"
    
    def trigger_effect(self,triggering_entity):    
        if triggering_entity.side==-self.side and triggering_entity.target is self.owner:
            super(self.__class__,self).trigger()
            minion = database.get_random_cards("[type]='Minion' AND [cost]=3", self.owner, 1)[0]
            minion.initialize_location("board")
            self.owner.recruit(minion)
            triggering_entity.target=minion

class Rat_Trap(Secret):
    def __init__(self,name="Rat Trap",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.trigger_event_type="play a card"
    
    def trigger_effect(self,triggering_card):    
        if triggering_card.side==-self.side and len(triggering_card.owner.played_cards[triggering_card.owner.turn])==2:
            super(self.__class__,self).trigger()
            minion = Doom_Rat(owner=self.owner,source="board")
            self.owner.recruit(minion)
                                                                                      
'''Paladin Secrets'''                        
class Noble_Sacrifice(Secret):
    def __init__(self,name="Noble Sacrifice",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.trigger_event_type="attack"
    
    def trigger_effect(self,triggering_entity):
        if not self.owner.board.isFull(self.owner):
            super(self.__class__,self).trigger()
            minion=getattr(card_collection, "Defender")(owner=self.owner,source=(0,480))
            self.owner.recruit(minion)
            triggering_entity.target=minion   

class Eye_for_an_Eye(Secret):
    def __init__(self,name="Eye for an Eye",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.trigger_event_type="hero damage"
    
    def trigger_effect(self,triggering_entity):
        super(self.__class__,self).trigger()
        eye_for_an_eye_animation(self)
        self.deal_damage([self.owner.opponent], [triggering_entity[1]])
        
class Redemption(Secret):
    def __init__(self,name="Redemption",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.trigger_event_type="minion dies"
    
    def trigger_effect(self,triggering_minion):
        super(self.__class__,self).trigger()
        minion=getattr(card_collection,database.cleaned(triggering_minion.name))(owner=self.owner,source=triggering_minion.location)
        self.owner.recruit(minion)
        priest_buff_animation(self,minion)
        minion.current_hp=1
         
class Repentance(Secret):
    def __init__(self,name="Repentance",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.trigger_event_type="summon from hand"
    
    def trigger_effect(self,triggering_entity):
        if triggering_entity.board_area=="Board":#Not mortally wounded
            super(self.__class__,self).trigger()
            paladin_debuff_animation(self,triggering_entity)
            triggering_entity.set_stats(hp=1)

class Avenge(Secret):
    def __init__(self,name="Avenge",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.trigger_event_type="minion dies"
    
    def trigger_effect(self,triggering_minion):
        targets = self.friendly_minions()
        if triggering_minion in targets:
            targets.remove(triggering_minion)
        if len(targets)>0:
            super(self.__class__,self).trigger()
            target=random.choice(targets)
            paladin_buff_animation(self, target)
            target.buff_stats(3,2)
            
class Sacred_Trial(Secret):
    def __init__(self,name="Sacred Trial",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.trigger_event_type="summon from hand"
    
    def trigger_effect(self,triggering_entity):
        if len(triggering_entity.friendly_minions())>=4 and triggering_entity.board_area=="Board":#Not mortally wounded
            super(self.__class__,self).trigger()
            vaporize_animation(self, triggering_entity)
            triggering_entity.destroy()

class Competitive_Spirit(Secret):
    def __init__(self,name="Competitive Spirit",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.trigger_event_type="start of turn"
        self.trigger_on_owner_turn=True
    
    def trigger_effect(self,triggering_player):
        minions=self.friendly_minions()
        if triggering_player is self.owner and len(minions)>0:
            super(self.__class__,self).trigger()
            light_buff_multiple_animation(self,minions)
            for minion in minions:
                minion.buff_stats(1,1)
                
class Getaway_Kodo(Secret):
    def __init__(self,name="Getaway Kodo",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.trigger_event_type="minion dies"
    
    def trigger_effect(self,triggering_minion):
        super(self.__class__,self).trigger()
        minion=getattr(card_collection,database.cleaned(triggering_minion.name))(owner=self.owner,source=triggering_minion.location)
        minion.return_hand(reset=True)
                         
'''Rogue Secrets'''   
class Cheat_Death(Secret):
    def __init__(self,name="Cheat Death",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.trigger_event_type="minion dies"
    
    def trigger_effect(self,triggering_minion):
        if triggering_minion.side==self.side:
            super(self.__class__,self).trigger()
            triggering_minion.return_hand(reset=True)
            triggering_minion.modify_cost(-2)           

class Sudden_Betrayal(Secret):
    def __init__(self,name="Sudden Betrayal",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.trigger_event_type="attack"
    
    def trigger_effect(self,triggering_entity):
        if triggering_entity.isMinion() and triggering_entity.side==-self.side and triggering_entity.target is self.owner and len(triggering_entity.adjacent_minions())>0:
            super(self.__class__,self).trigger()
            target = random.choice(triggering_entity.adjacent_minions())
            misdirection_animation(self,target)
            triggering_entity.target=target 

class Evasion(Secret):
    def __init__(self,name="Evasion",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.trigger_event_type="hero damage"
    
    def trigger_effect(self,triggering_entity):
        super(self.__class__,self).trigger()
        card=Ice_Block_Effect(owner=self.owner)

                                           
class Weapon(Card):
    def __init__(self,name="Default Weapon",owner=None,source=None):
        super(Weapon,self).__init__(name,owner,source)
        self.board_image=pygame.transform.scale(self.big_image.subsurface((60, 20, 140, 175)),(103,128))
        self.windfury_image = windfury_image
        self.poisonous_image = poisonous_image
        self.lifesteal_image = lifesteal_image
        self.deathrattle_image = deathrattle_image
        self.inspire_image = inspire_image
        self.inspire2_image = inspire2_image
        self.trigger_image = trigger_image
        self.trigger2_image = trigger2_image
        self.overkill_image = overkill_image
        self.dormant_image=dormant_image
        self.current_atk=self.atk
        self.temp_atk=self.atk
        self.current_durability=self.durability
        self.temp_durability=self.durability
        self.spell_damage_boost=0
        self.current_spell_damage_boost=0
        self.opponent_spell_damage_boost=0
        self.current_opponent_spell_damage_boost=0
        self.cannot_attack_hero=False
        self.has_windfury=False
        self.windfury=False
        self.has_poisonous=False
        self.poisonous=False
        self.has_trigger=False
        self.inspire=False
        self.has_inspire=False
        self.dormant=False
        self.has_dormant=False
        self.silenced=False
        self.dormant_cap=2
        self.dormant_counter=0
        self.trigger_event_type=""
        self.trigger_events=[]
        self.has_deathrattle=False
        self.deathrattles=[]
        self.on_hit_effects=[]
        self.deathrattle_msg="-"
        if "Deathrattle" in self.abilities:
            self.deathrattle_msg=self.card_text

    def is_valid_on(self,target):
        return self.landed_board_area()=="Board"
                
    def trigger_after_effect(self,target=None):
        if not self.owner.board.get_buff(self)['durability immune']:
            self.decrease_durability()
            
    def decrease_durability(self,amount=1):
        self.current_durability-=amount
        if self.current_durability<=0:
            self.destroy()
            
    def destroy(self,skip_deathrattle=False,skip_animation=False):
        if not skip_animation:
            destroy_animation(self)
        self.owner.weapon=None
        self.owner.board.weapons[self.owner.side].remove(self)
        self.owner.board.queue.remove(self)
        self.owner.board.weapon_graves[self.owner.side].append(self)
        self.board_area="Grave" 
        
        if not skip_deathrattle: 
            self.trigger_deathrattle()
        
        #Trigger any weapon destroy effects if any    
        self.owner.board.activate_triggered_effects('weapon destroyed',self) 
                
        self.on_hit_effects=[]
        self.reset_status()
        
    def return_hand(self,reset=True):
        self.owner.weapon=None
        if self in self.owner.board.queue:
            self.owner.board.queue.remove(self)
        if self in self.owner.board.weapons[self.owner.side]:
            self.owner.board.weapons[self.owner.side].remove(self)
        if self in self.owner.board.weapon_graves[self.owner.side]:
            self.owner.board.weapon_graves[self.owner.side].append(self)
        self.image=self.mini_image
        self.hand_in()
        
        if reset:
            self.reset_status()
             
    def reset_status(self):
        self.current_atk                         = self.atk
        self.current_durability                  = self.durability
        self.current_cost                        = self.cost
        self.has_poisonous                       = self.poisonous 
        self.current_spell_damage_boost          = self.spell_damage_boost
        self.current_opponent_spell_damage_boost = self.opponent_spell_damage_boost
        self.has_trigger                         = bool(self.trigger_event_type)
        self.has_deathrattle                     = 'Deathrattle' in self.abilities
        self.deathrattles                        = []
        self.trigger_events                      = []
    
    def get_current_atk(self):
        return self.current_atk+self.owner.board.get_buff(self)['atk']
    
    def buff_stats(self,atk,durability):
        self.current_atk+= atk
        self.current_durability+= durability
        if self.current_atk<=0:
            self.current_atk=0
        self.temp_atk+=atk
        self.temp_durability+=durability   
             
    def gain_poisonous(self):
        poisonous_animation(self)
        self.has_poisonous=True
        self.on_hit_effects.append(MethodType(on_hit_poison,self))
      
    def gain_windfury(self):
        poisonous_animation(self)
        self.has_windfury=True
   
    def battlecry(self,target):
        pass
         
    def deathrattle(self):
        pass
    
    def on_hit_effect(self,target):
        pass
    
    def end_of_turn_effect(self):
        pass


#Neutral Weapons
class Atiesh(Weapon):
    def __init__(self,name="Atiesh",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="play a card"
        
    def trigger_effect(self,triggering_card):
        if triggering_card.isSpell and triggering_card.side==self.side:
            super(self.__class__,self).trigger_effect(triggering_card)
            minion = database.get_random_cards("[type]='Minion' AND [cost]="+str(triggering_card.get_current_cost()), owner=self.owner, k=1)[0]
            minion.initialize_location("board")
            self.decrease_durability(1)
            self.owner.recruit(minion)
                
#Demon Hunter Weapons     
class Aldrachi_Warblades(Weapon):
    def __init__(self,name="Aldrachi Warblades",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.lifesteal=True

class Umberwing(Weapon):
    def __init__(self,name="Umberwing",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
    
    def battlecry(self,target):
        for i in range(2):
            minion=Felwing(owner=self.owner,source="board")
            self.owner.recruit(minion)

class Flamereaper(Weapon):
    def __init__(self,name="Flamereaper",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="during attack"
    
    def trigger_effect(self,triggering_entity):
        if triggering_entity is self.owner and self.owner.target.isMinion():
            self.owner.attack_adjacent_minions(self.owner.target)

#Druid Weapons
class Twig_of_the_World_Tree(Weapon):
    def __init__(self,name="Twig of the World Tree",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
    
    def deathrattle(self):
        self.owner.gain_mana(10)
                                      
#Hunter Weapons
class Eaglehorn_Bow(Weapon):
    def __init__(self,name="Eaglehorn Bow",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="secret revealed"
        
    def trigger_effect(self, triggering_secret):
        if triggering_secret.side==self.side:
            super(self.__class__,self).trigger_effect(triggering_secret)
            self.buff_stats(0, 1)
                       
class Gladiators_Longbow(Weapon):
    def __init__(self,name="Gladiator's Longbow",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="attack"
        
    def trigger_effect(self,triggering_entity):
        if triggering_entity is self.owner:
            super(self.__class__,self).trigger_effect(self)
            self.owner.has_immune=True
            
    def trigger_after_effect(self, target=None):
        self.owner.has_immune=False
        super(self.__class__,self).trigger_after_effect(target)

class Glaivezooka(Weapon):
    def __init__(self,name="Glaivezooka",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def battlecry(self,target):
        targets=self.friendly_minions()
        if len(targets)>0:
            target=random.choice(targets)
            hunter_buff_animation(self, target)
            target.buff_stats(1,0)

class Piranha_Launcher(Weapon):
    def __init__(self,name="Piranha Launcher",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def trigger_after_effect(self, target=None):
        minion = Piranha(owner=self.owner,source="board")
        self.owner.recruit(minion)
        super(self.__class__,self).trigger_after_effect(target)

class Candleshot(Weapon):
    def __init__(self,name="Candleshot",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="attack"
        
    def trigger_effect(self,triggering_entity):
        if triggering_entity is self.owner:
            super(self.__class__,self).trigger_effect(self)
            self.owner.has_immune=True
            
    def trigger_after_effect(self, target=None):
        self.owner.has_immune=False
        super(self.__class__,self).trigger_after_effect(target)

class Rhokdelar(Weapon):
    def __init__(self,name="Rhok'delar",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def battlecry(self,target):
        if self.owner.deck.has_no_minions():
            for i in range(self.owner.hand_limit):
                card = database.get_random_cards("[type]='Spell' AND [class] LIKE '%Hunter%'", owner=self.owner, k=1)[0]
                card.initialize_location(self.owner.location)
                card.hand_in(speed=60)
            
#Mage Weapons
class Aluneth(Weapon):
    def __init__(self,name="Aluneth",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="end of turn"

    def trigger_effect(self,triggering_player):
        if triggering_player is self.owner:
            super(self.__class__,self).trigger_effect(self)
            self.owner.draw(3)
                                               
#Paladin Weapons
class Lights_Justice(Weapon):
    def __init__(self,name="Light's Justice",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

class Truesilver_Champion(Weapon):
    def __init__(self,name="Truesilver Champion",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="attack"
        
    def trigger_effect(self,triggering_entity):
        if triggering_entity is self.owner:
            super(self.__class__,self).trigger_effect(self)
            self.heal([self.owner],[2])

class Sword_of_Justice(Weapon):
    def __init__(self,name="Sword of Justice",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="summon a minion"
        
    def trigger_effect(self, triggering_minion):
        if triggering_minion.side==self.side:
            super(self.__class__,self).trigger_effect(triggering_minion)
            light_buff_animation(triggering_minion)
            triggering_minion.buff_stats(1,1)
            self.decrease_durability()
            
class Coghammer(Weapon):
    def __init__(self,name="Coghammer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def battlecry(self,target):
        targets=self.friendly_minions()
        if len(targets)>0:
            target=random.choice(targets)
            target.gain_divine_shield()
            target.gain_taunt()

class Argent_Lance(Weapon):
    def __init__(self,name="Argent Lance",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        winner = self.joust("Minion")
        if winner is not None and winner.owner is self.owner:
            light_buff_animation(self)
            self.buff_stats(0, 1)
            
class Rallying_Blade(Weapon):
    def __init__(self,name="Rallying Blade",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def battlecry(self,target=None):
        target_pool=self.friendly_minions()
        targets=[]
        for minion in target_pool:
            if minion.has_divine_shield:
                targets.append(minion)
                minion.buff_stats(1,1)
                
        light_buff_multiple_animation(self, targets)

class Vinecleaver(Weapon):
    def __init__(self,name="Vinecleaver",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def trigger_after_effect(self, target=None):
        for i in range(2):
            minion=Silver_Hand_Recruit(owner=self.owner,source="board")
            self.owner.recruit(minion)
        super(self.__class__,self).trigger_after_effect(target)

class Lights_Sorrow(Weapon):
    def __init__(self,name="Light's Sorrow",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="lose divine shield"
        
    def trigger_effect(self,triggering_entity):
        if triggering_entity.side==self.side:
            super(self.__class__,self).trigger_effect(self)
            self.buff_stats(1, 0)

class Unidentified_Maul(Weapon):
    def __init__(self,name="Unidentified Maul",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="add to hand"
        self.upgrade_targets=[Blessed_Maul,Champions_Maul,Purifiers_Maul,Sacred_Maul]
        
    def trigger_effect(self,triggering_card):
        if triggering_card is self:
            self.upgrade_target=random.choice(self.upgrade_targets)
            self.upgrade()

class Blessed_Maul(Weapon):
    def __init__(self,name="Blessed Maul",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

    def battlecry(self,target=None):
        self.buff_multiple(atk=1)

class Champions_Maul(Weapon):
    def __init__(self,name="Champion's Maul",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

    def battlecry(self,target=None):
        for i in range(2):
            minion=Silver_Hand_Recruit(owner=self.owner,source="board")
            self.owner.recruit(minion)

class Purifiers_Maul(Weapon):
    def __init__(self,name="Purifier's Maul",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

    def battlecry(self,target=None):
        for minion in self.friendly_minions():
            minion.gain_divine_shield()

class Sacred_Maul(Weapon):
    def __init__(self,name="Sacred Maul",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

    def battlecry(self,target=None):
        for minion in self.friendly_minions():
            minion.gain_taunt()
                                                                            
class Ashbringer(Weapon):
    def __init__(self,name="Ashbringer",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Grave_Vengeance(Weapon):
    def __init__(self,name="Grave Vengeance",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.lifesteal=True

class Valanyr(Weapon):
    def __init__(self,name="Val'anyr",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
    
    def deathrattle(self):
        minion=self.owner.search_card(self.owner.hand,card_type="Minion")
        if minion is not None:
            buff_hand_animation(self.owner, [minion])
            minion.buff_stats(4,2)
            minion.deathrattles.append([MethodType(self.deathrattle2.__func__,minion),"Equip Val'anyr"])
            minion.has_deathrattle=True
            
    def deathrattle2(self):
        weapon=Valanyr(owner=self.owner)
        self.owner.equip_weapon(weapon)

#Priest Weapons
class Dragon_Soul(Weapon):
    def __init__(self,name="Dragon Soul",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="play a card"
        self.trigger_events=[("end of turn",self.trigger_effect2)]
        self.counter=0
        self.goal=3
        
    def trigger_effect(self,triggering_card):
        if triggering_card.isSpell and triggering_card.side==self.side:
            super(self.__class__,self).trigger_effect(self)
            self.counter+=1
            if self.counter==3:
                minion=Dragon_Spirit(owner=self.owner,source="board")
                self.owner.recruit(minion)
                self.counter=0

    def trigger_effect2(self, triggering_player):
        if triggering_player is self.owner:
            self.counter=0
                                                                   
#Rogue Weapons
class Wicked_Knife(Weapon):
    def __init__(self,name="Wicked Knife",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        
class Poisoned_Dagger(Weapon):
    def __init__(self,name="Poisoned Dagger",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
                        
class Assassins_Blade(Weapon):
    def __init__(self,name="Assassin's Blade",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)          

class Perditions_Blade(Weapon):
    def __init__(self,name="Perdition's Blade",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
    
    def is_valid_on(self,target):
        return target is not None and target.is_targetable()
        
    def battlecry(self,target):
        perditions_blade_animation(self,target)
        if len(self.owner.played_cards[self.owner.turn])>0:
            self.combo(target)
        else:
            self.deal_damage([target], [1])

    def combo(self,target):
            self.deal_damage([target], [2])

class Cogmasters_Wrench(Weapon):
    def __init__(self,name="Cogmaster's Wrench",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)   

    def ongoing_effect(self,target):
        if target is self and self.owner.control("Mech"):
            return {'atk':2}
        else:
            return {}

class Poisoned_Blade(Weapon):
    def __init__(self,name="Poisoned Blade",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)   
        self.trigger_event_type="use hero power"

    def ongoing_effect(self,target):
        if (isinstance(target,Dagger_Mastery) or isinstance(target,Poisoned_Daggers)) and target.side==self.side:
            return {'not replace':True}
        else:
            return {}
        
    def trigger_effect(self, triggering_entity):
        if triggering_entity.side==self.side:
            super(self.__class__,self).trigger_effect(triggering_entity)
            weapon_enchantment_animation(self.owner.hero_power, self)
            self.buff_stats(1, 0)

class Sharp_Fork(Weapon):
    def __init__(self,name="Sharp Fork",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)  

class Obsidian_Shard(Weapon):
    def __init__(self,name="Obsidian Shard",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def ongoing_effect(self,target):
        if target is self and target.board_area=="Hand":
            count=0
            for i in range(self.owner.turn):
                for card in self.owner.played_cards[i+1]:
                    if card.card_class!=self.owner.class_name:
                        count+=1
            return {'cost':-count}
        else:
            return {} 

class Shadowblade(Weapon):
    def __init__(self,name="Shadowblade",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        self.owner.temporary_effects['immune']=True

class Kingsbane(Weapon):
    def __init__(self,name="Kingsbane",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def destroy(self,skip_deathrattle=False,skip_animation=False):
        self.owner.weapon=None
        self.owner.board.weapons[self.owner.side].remove(self)
        self.owner.board.queue.remove(self)
        self.trigger_deathrattle()
        
        #Trigger any weapon destroy effects if any    
        self.owner.board.activate_triggered_effects('weapon destroyed',self) 


    def deathrattle(self):
        self.shuffle_into_deck(self.owner.deck,reset_status=False)
        self.current_durability=self.temp_durability
                                                        
#Shaman Weapons
class Stormforged_Axe(Weapon):
    def __init__(self,name="Stormforged Axe",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.overload=1

class Doomhammer(Weapon):
    def __init__(self,name="Doomhammer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.windfury=True
        self.overload=2

class Powermace(Weapon):
    def __init__(self,name="Powermace",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
    
    def deathrattle(self):
        targets=self.friendly_minions("Mech")
        if len(targets)>0:
            minion=random.choice(targets)
            buff_animation(minion)
            minion.buff_stats(2,2)

class Charged_Hammer(Weapon):
    def __init__(self,name="Charged Hammer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
    
    def deathrattle(self):
        new_hero_power=Lightning_Jolt(owner=self.owner)
        self.owner.gain_hero_power(new_hero_power)

class Hammer_of_Twilight(Weapon):
    def __init__(self,name="Hammer of Twilight",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
    
    def deathrattle(self):
        minion=Twilight_Elemental(owner=self.owner,source="board")
        self.owner.recruit(minion)

class Spirit_Claws(Weapon):
    def __init__(self,name="Spirit Claws",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)   

    def ongoing_effect(self,target):
        if target is self and self.owner.has_weapon() and self.owner.weapon is self and self.owner.has_spell_damage():
            return {'atk':2}
        else:
            return {}

class Jade_Claws(Weapon):
    def __init__(self,name="Jade Claws",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.overload=1

    def battlecry(self,target):
        minion=Jade_Golem(owner=self.owner,source="board")
        self.owner.recruit(minion)

class Ice_Breaker(Weapon):
    def __init__(self,name="Ice Breaker",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.killed_minions=[]

    def trigger_after_effect(self, target=None):
        if target.frozen:
            target.destroy()
        super(self.__class__,self).trigger_after_effect(target)

class The_Runespear(Weapon):
    def __init__(self,name="The Runespear",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def trigger_after_effect(self, target=None):
        spell=self.discover(filter_str="[type]='Spell'")
        if spell is not None:
            spell.cast_on_random_target()
                                                            
#Warlock Weapons 
class Blood_Fury(Weapon):
    def __init__(self,name="Blood Fury",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Skull_of_the_Manari(Weapon):
    def __init__(self,name="Skull of the Man'ari",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="start of turn"

    def trigger_effect(self,triggering_player):
        if triggering_player is self.owner:
            super(self.__class__,self).trigger_effect(self)
            demon=self.owner.search_card(self.owner.hand,"Demon")
            if demon is not None:
                self.owner.put_into_battlefield(demon,location="board")
                            
#Warrior Weapons                            
class Fiery_War_Axe(Weapon):
    def __init__(self,name="Fiery War Axe",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source) 

class Arcanite_Reaper(Weapon):
    def __init__(self,name="Arcanite Reaper",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source) 

class Battle_Axe(Weapon):
    def __init__(self,name="Battle Axe",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        
class Heavy_Axe(Weapon):
    def __init__(self,name="Heavy Axe",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Gorehowl(Weapon):
    def __init__(self,name="Gorehowl",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def trigger_after_effect(self,target=None):
        if target.isMinion():
            self.buff_stats(-1, 0)
        else:
            self.decrease_durability()

class Deaths_Bite(Weapon):
    def __init__(self,name="Death's Bite",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
    
    def deathrattle(self):
        targets=self.all_minions()
        whirlwind_animation(self)
        self.deal_damage(targets, [1]*len(targets))

class Ogre_Warmaul(Weapon):
    def __init__(self,name="Ogre Warmaul",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="attack"
        
    def trigger_effect(self,triggering_entity):
        if triggering_entity is self.owner:
            self.owner.attack_wrong_enemy(0.5)   

class Kings_Defender(Weapon):
    def __init__(self,name="King's Defender",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        if self.owner.is_taunted():
            self.buff_stats(0, 1)

class Cursed_Blade(Weapon):
    def __init__(self,name="Cursed Blade",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)   

    def ongoing_effect(self,target):
        if target is self.owner and target.weapon is self:
            return {'double damage':True}
        else:
            return {}

class Rusty_Hook(Weapon):
    def __init__(self,name="Rusty Hook",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)  

class Tentacles_for_Arms(Weapon):
    def __init__(self,name="Tentacles for Arms",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
    
    def deathrattle(self):
        self.return_hand()
                                                                
class Sulthraze(Weapon):
    def __init__(self,name="Sul'thraze",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def overkill(self,target):
        overkill_animation(target)
        self.owner.remaining_attack+=1

class Fools_Bane(Weapon):
    def __init__(self,name="Fool's Bane",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.cannot_attack_hero=True
        
    def trigger_after_effect(self, target=None):
        super(self.__class__,self).trigger_after_effect(target)
        if self.durability>0:
            self.owner.remaining_attack+=1

class Brass_Knuckles(Weapon):
    def __init__(self,name="Brass Knuckles",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def trigger_after_effect(self, target=None):
        super(self.__class__,self).trigger_effect(self)
        self.owner.buff_hand(card_type="Minion",atk=1,hp=1)
        super(self.__class__,self).trigger_after_effect(target)

class Molten_Blade(Weapon):
    def __init__(self,name="Molten Blade",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="start of turn"
        
    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner and self.board_area=="Hand":
            weapon = database.get_random_cards("[type]='Weapon'", self.owner, 1)[0]
            weapon.transform_in_hand=True
            weapon.trigger_events.append(["start of turn",MethodType(Molten_Blade.trigger_effect,weapon)])
            weapon.copy_target=self
            self.shapeshift(weapon)

class Blood_Razor(Weapon):
    def __init__(self,name="Blood Razor",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def battlecry(self,target=None):
        targets=self.all_minions()
        whirlwind_animation(self)
        self.deal_damage(targets, [1]*len(targets))
                
    def deathrattle(self):
        targets=self.all_minions()
        whirlwind_animation(self)
        self.deal_damage(targets, [1]*len(targets))

class Spiked_Shield_weapon(Weapon):
    def __init__(self,name="Spiked Shield (weapon)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Bladed_Gauntlet(Weapon):
    def __init__(self,name="Bladed Gauntlet",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.cannot_attack_hero=True

    def ongoing_effect(self,target):
        if target is self:
            return {'atk':self.owner.shield-self.current_atk}
        else:
            return {}    
        
                        
class Sulfuras(Weapon):
    def __init__(self,name="Sulfuras",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        new_hero_power=DIE_INSECT(owner=self.owner)
        self.owner.gain_hero_power(new_hero_power)

class Shadowmourne(Weapon):
    def __init__(self,name="Shadowmourne",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="during attack"
    
    def trigger_effect(self,triggering_entity):
        if triggering_entity is self.owner and self.owner.target.isMinion():
            self.owner.attack_adjacent_minions(self.owner.target)
                                                                                        
class Woecleaver(Weapon):
    def __init__(self,name="Woecleaver",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def trigger_after_effect(self, target=None):
        minion = self.owner.search_card(self.owner.deck.cards,"Minion")
        if minion is not None:
            super(self.__class__,self).trigger_effect(self)
            self.recruit(minion)
        super(self.__class__,self).trigger_after_effect(target)
        

            
'''Minions'''                                  
class Minion(Card):
    def __init__(self,name="Default Minion",owner=None,source=None):
        super(Minion,self).__init__(name,owner,source)
        self.board_image=pygame.transform.scale(self.big_image.subsurface((60, 20, 140, 175)),(103,128))
        self.taunt_image = taunt_image
        self.divine_shield_image = divine_shield_image
        self.immune_image = immune_image
        self.windfury_image = windfury_image
        self.elusive_image = elusive_image
        self.enrage_image = enrage_image
        self.spell_damage_boost_image = spell_damage_boost_image
        self.stealth_image = stealth_image
        self.poisonous_image = poisonous_image
        self.freeze_image = freeze_image
        self.lifesteal_image = lifesteal_image
        self.reborn_image = reborn_image
        self.corrupted_image = corrupted_image
        self.deathrattle_image = deathrattle_image
        self.inspire_image = inspire_image
        self.inspire2_image = inspire2_image
        self.trigger_image = trigger_image
        self.trigger2_image = trigger2_image
        self.overkill_image = overkill_image
        self.silence_image=silence_image
        self.dormant_image=dormant_image
        self.target=None
        self.current_atk=self.atk
        self.temp_atk=self.current_atk
        self.current_hp=self.hp
        self.temp_hp=self.current_hp
        self.has_taunt=False
        self.has_divine_shield=False
        self.has_windfury=False
        self.has_elusive=False
        self.has_stealth=False
        self.has_poisonous=False
        self.has_charge=False
        self.has_rush=False
        self.enrage=False
        self.frozen=False
        self.frozen_timer = 0
        self.has_deathrattle=False
        self.has_trigger=False
        self.inspire=False
        self.has_inspire=False
        self.taunt=False
        self.divine_shield=False
        self.windfury=False
        self.windfury_counter=0
        self.elusive=False
        self.stealth=False
        self.poisonous=False
        self.mega_windfury=False
        self.charge=False
        self.rush=False
        self.summoning_sickness=False
        self.immune=False
        self.lifesteal=False
        self.has_lifesteal=False
        self.reborn=False
        self.has_reborn=False
        self.magnetic       = False
        self.has_immune        = False
        self.has_spell_damage=False
        self.has_opponent_spell_damage=False
        self.spell_damage_boost=0
        self.current_spell_damage_boost=0
        self.opponent_spell_damage_boost=0
        self.current_opponent_spell_damage_boost=0
        self.attacked=False
        self.attacks=0
        self.cannot_attack_hero=False
        self.has_effect_each_turn=False
        self.cannot_attack=False
        self.silenced=False
        self.dormant=False
        self.has_dormant=False
        self.dormant_cap=2
        self.dormant_counter=0
        self.transformed=False
        self.last_damage_source = None
        self.destroyed_by = None
        self.attachments={"Spell History":[]}
        self.trigger_event_type=""
        self.trigger_events=[]
        self.deathrattle_msg=""
        self.deathrattles=[]
        self.deathrattle_msg="-"
        if "Deathrattle" in self.abilities:
            self.deathrattle_msg=self.card_text
        
        self.on_hit_effects=[]
        self.has_special_summon_effect=False
    
        if self.owner is not None and self.owner.board is not None and self.owner.board.get_buff(self)["Crystal Core"]:
            self.set_stats(atk=4, hp=4)
    
    def refresh_status(self):#Start of a turn
        self.attacked           = False
        self.attacks            = 0
        self.summoning_sickness = False
            
        if self.frozen_timer>0:
            self.frozen_timer-=1
            if self.frozen_timer==0:
                self.frozen=False
                
        if self.has_dormant:
            self.increment_dormant_counter()
                
    
    def restore_status(self):#end of turn
        self.current_atk = self.temp_atk
        #self.current_hp  = self.temp_hp
        
        if self.temporary_effects['owned']:
            old_location=self.location
            self.owner=self.owner.opponent
            self.side=self.owner.side
            self.owner.opponent.minions.remove(self)
            self.owner.minions.append(self)
            self.owner.board.sort_minions(self.side)
            self.owner.board.sort_minions(-self.side)
            self.location=old_location
            move_animation(self,dest=(self.rect.x,self.rect.y),speed=20,zoom=False)
            
        for attribute in self.temporary_effects:
            if isinstance(self.temporary_effects[attribute],int):
                if self.temporary_effects[attribute]>0:
                    self.temporary_effects[attribute]-=1
            else:
                if self.temporary_effects[attribute]:
                    self.temporary_effects[attribute]=False
                    
    def reset_status(self):
        self.current_atk                         = self.atk
        self.temp_atk                            = self.atk
        self.current_hp                          = self.hp
        self.temp_hp                             = self.hp
        self.current_cost                        = self.cost
        self.has_taunt                           = self.taunt
        self.has_divine_shield                   = self.divine_shield 
        self.has_windfury                        = self.windfury
        self.has_elusive                         = self.elusive
        self.has_stealth                         = self.stealth
        self.has_poisonous                       = self.poisonous
        self.has_charge                          = self.charge
        self.has_rush                            = self.rush
        self.has_lifesteal                       = self.lifesteal
        self.has_reborn                          = self.reborn
        self.has_immune                          = self.immune
        self.cannot_attack                       = "Can't attack" in self.abilities
        self.has_dormant                         = False
        self.dormant_counter                     = 0
        self.frozen                              = False
        self.frozen_timer                        = 0
        self.attacked                            = False
        self.corrupted                           = False
        self.has_trigger                         = bool(self.trigger_event_type)
        self.has_inspire                         = self.inspire
        self.has_deathrattle                     = False
        self.current_spell_damage_boost          = self.spell_damage_boost
        self.current_opponent_spell_damage_boost = self.opponent_spell_damage_boost
        self.silenced                            = False
        
        self.deathrattles                        = []
        self.trigger_events                      = []
        self.on_hit_effects                      = []
        for attribute in self.temporary_effects:
            self.temporary_effects[attribute]=False
    
    def copy_stats(self,target_minion):
        self.current_atk                         = target_minion.current_atk 
        self.temp_atk                            = target_minion.temp_atk
        self.current_hp                          = target_minion.current_hp 
        self.temp_hp                             = target_minion.temp_hp
        self.current_cost                        = target_minion.current_cost
        self.has_taunt                           = target_minion.has_taunt 
        self.has_divine_shield                   = target_minion.has_divine_shield   
        self.has_windfury                        = target_minion.has_windfury 
        self.has_elusive                         = target_minion.has_elusive  
        self.has_stealth                         = target_minion.has_stealth 
        self.has_poisonous                       = target_minion.has_poisonous
        self.has_lifesteal                       = target_minion.has_lifesteal
        self.has_reborn                          = target_minion.has_reborn
        self.frozen                              = target_minion.frozen
        self.frozen_timer                        = target_minion.frozen_timer
        self.has_charge                          = target_minion.has_charge
        self.has_rush                            = target_minion.has_rush
        self.has_deathrattle                     = target_minion.has_deathrattle
        self.has_trigger                         = target_minion.has_trigger
        self.has_inspire                         = target_minion.has_inspire
        self.has_immune                          = target_minion.has_immune
        self.silenced                            = target_minion.silenced
        self.has_dormant                         = target_minion.has_dormant
        self.dormant_counter                     = target_minion.dormant_counter  
        self.current_spell_damage_boost          = target_minion.current_spell_damage_boost
        self.current_opponent_spell_damage_boost = target_minion.current_opponent_spell_damage_boost
        self.attachments                         = target_minion.attachments
        self.deathrattles                        = []
        self.trigger_events                      = []
        self.on_hit_effects                      = []
        
        self.destroy=MethodType(target_minion.destroy.__func__,self)
        for deathrattle in target_minion.deathrattles:
            d = MethodType(deathrattle[0].__func__,self)
            self.deathrattles.append([d,deathrattle[1]])
        #self.deathrattle                         = MethodType(target_minion.deathrattle.__func__,self)
         
        for trigger in target_minion.trigger_events:
            t = MethodType(trigger[1].__func__,self)
            self.trigger_events.append([trigger[0],t])
        
        for on_hit_effect in target_minion.on_hit_effects:
            e = MethodType(on_hit_effect.__func__,self)
            self.on_hit_effects.append(e)
    
    def copy_enchantments(self,target):
        self.current_cost=target.current_cost
        self.current_atk=target.current_atk
        self.current_hp=target.current_hp
        self.temp_atk=target.temp_atk
        self.temp_hp=target.temp_hp
    
    def get_1_1_copy(self,owner):
        minion_copy=self.get_copy(owner=owner)
        minion_copy.initialize_location(self.location)
        minion_copy.set_stats(1,1)
        return minion_copy
        
    def summon(self,minion,left=-1,speed=30):
        #Summon minion for player
        if self.side==minion.side:
            if not self.owner.board.isFull(self.owner):
                minion.initialize_location(source=self.location)
                minion.rect.x+=-left*minion.image.get_width()/2
            else:
                return None
                
        #Summon minion for Opponent
        else:
            if not self.owner.board.isFull(self.owner.opponent):
                temp_x,temp_y     = self.location
                minion.initialize_location(source="board")
                minion.location   = temp_x,temp_y
            else:
                return None
        
        #Prepare the destination of summoned minion
        minion.owner.board.add_minion(minion)
        minion.board_area="Board"
        if minion in minion.owner.hand:
            minion.owner.hand.remove(minion)       
        summon_animation(minion,speed=speed,skip_zoom=True)
        minion.come_on_board()
        
        #Trigger on summon effect if any
        self.owner.board.activate_triggered_effects('summon a minion',minion)
        
        #Trigger quest if any
        self.owner.trigger_quests('summon a minion',minion)

 
    def come_on_board(self):
        
        if self.dormant and self.dormant_counter<self.dormant_cap:
            self.has_dormant=True
            return None
         
        if "Can't attack" in self.abilities:
            self.cannot_attack=True
            
        if "Deathrattle" in self.abilities:
            self.deathrattles.append([self.deathrattle,self.deathrattle_msg])
            self.has_deathrattle=True
        
        if "Triggered effect" in self.tags+self.abilities:
            self.trigger_events.append([self.trigger_event_type,self.trigger_effect])
            self.has_trigger=True
        
        if "Inspire" in self.abilities:
            self.trigger_events.append(["use hero power",self.trigger_inspire])
            self.has_inspire=True
                
        self.on_hit_effects.append(self.on_hit_effect)
            
        #Gain taunt if it is a taunt minion
        if self.taunt:
            self.gain_taunt()
        
        #Gain divine shield if it is a divine shield minion   
        if self.divine_shield:
            self.gain_divine_shield()
        
        #Gain elusive if it is a elusive minion   
        if self.elusive:
            self.gain_elusive()
               
        #Gain windfury if it is a windfury minion   
        if self.windfury:
            self.gain_windfury()
        
        #Gain stealth if it is a stealth minion   
        if self.stealth:
            self.gain_stealth()
            
        #Gain stealth if it is a stealth minion   
        if self.poisonous:
            self.gain_poisonous()
            
        #Gain mega_windfury if it is a mega_windfury minion   
        if self.mega_windfury:
            self.gain_windfury(4)
      
        #Gain immune if it is an immune minion   
        if self.immune:
            self.gain_immune()
            
        #Gain Lifesteal if it is a lifesteal minion   
        if self.lifesteal:
            self.gain_lifesteal()
            
        if self.reborn:
            self.gain_reborn()
            
        if self.charge:
            self.gain_charge()
            
        if self.rush:
            self.gain_rush()

        if self.spell_damage_boost:
            self.gain_spell_damage_boost(self.spell_damage_boost)
         
        if self.opponent_spell_damage_boost:
            self.gain_spell_damage_boost(-self.spell_damage_boost)
               
        self.current_cost=self.cost
        self.summoning_sickness=True
        self.attacked=False
        self.attacks=0
        self.destroyed_by=None
        self.ephemeral=False
        self.copy_target=None
        self.transform_in_hand="Transform in hand" in self.abilities
        
        self.owner.board.queue.append(self)
     

    '''                       
    def attack(self,target):
        #Disable stealth
        self.has_stealth=False
        self.temporary_effects['stealth']=False
        
        get_player(target).trigger_secrets("attack",self)
        target=self.target
        if self.get_current_hp()>0 and self.board_area=="Board" and not self.attacked:
           
            #Trigger minion attack effect if any
            self.owner.board.activate_triggered_effects("attack",self,target)

            get_player(target).trigger_secrets("minion attack",self)
            if self.get_current_hp()>0 and self.board_area=="Board" and not self.attacked:
                if target.isHero():
                    target.trigger_secrets("hero attacked",self)
                elif target.isMinion():
                    target.owner.trigger_secrets("minion attacked",self)
                    
                if self.get_current_hp()>0 and self.board_area=="Board" and not self.attacked:
                    attack_animation(self,target)
                    self.attacked=True
                    self.attacks+=1
                    print(self.name+" attacked "+target.name)
                    
                    target_current_atk = target.get_current_atk() # Record the value in case target dies
                    target_on_hit_effects=target.on_hit_effects
                    target.incur_damage(self.get_current_atk(),on_hit_effects=self.on_hit_effects,damage_source=self)
                    if target_current_atk+self.owner.board.get_buff(self)['atk']>0 and not target.isHero():
                        self.incur_damage(target_current_atk,on_hit_effects=target_on_hit_effects,damage_source=target)
'''
    def attack(self,target):
        self.target=target
        #Trigger attack effect if any
        self.owner.board.activate_triggered_effects("attack",self)
        
        if self.get_current_hp()>0 and self.board_area=="Board":
            #Disable stealth
            self.has_stealth=False
            self.temporary_effects['stealth']=False
            
            attack_animation(self,self.target)
            self.attacked=True
            self.attacks+=1
            print(self.name+" attacked "+self.target.name)
            
            target_current_atk = self.target.get_current_atk() # Record the value in case target dies
            target_on_hit_effects=self.target.on_hit_effects
            

            
            self.deal_damage([self.target], [self.get_current_atk()], on_hit_effects=self.on_hit_effects)
            #Trigger minion during attack effect if any
            self.owner.board.activate_triggered_effects("during attack",self)
            
            #self.target.incur_damage(self.get_current_atk(),on_hit_effects=self.on_hit_effects,damage_source=self)
            if target_current_atk>0 and not self.target.isHero() and self.board_area=="Board": #Not dead due to target deathrattle
                self.target.deal_damage([self],[target_current_atk],on_hit_effects=target_on_hit_effects)
                #self.incur_damage(target_current_atk,on_hit_effects=target_on_hit_effects,damage_source=self.target)

            if self.target.get_current_hp()<=0:
                self.target.destroyed_by=self
                
            #Trigger minion after attack effect if any
            self.owner.board.activate_triggered_effects("after attack",self)
            
    def attack_wrong_enemy(self,chance=0.5):
        original_target=self.target
        target_pool=self.enemy_characters()
        if original_target in target_pool:
            target_pool.remove(original_target)
        if random.uniform(0,1)<chance and len(target_pool)>0:
            super(self.__class__,self).trigger_effect(self)
            new_target=random.choice(target_pool)
            self.target=new_target

    def attack_adjacent_minions(self,target):
        super(self.__class__,self).trigger_effect(self)
        minions=target.adjacent_minions()
        attack_adjacent_animation(self,target)
        self.deal_damage(minions, [self.get_current_atk()]*len(minions))
        
    def unable_to_attack(self):
        return self.get_current_atk()<=0 or (self.cannot_attack and not self.temporary_effects["can attack"] and not self.owner.board.get_buff(self)['can attack'])
                                
    def damaged(self):
        return self.current_hp<self.temp_hp
                
    def incur_damage(self,amount,on_hit_effects=[],damage_source=None,skip_animation=False):
        damage=amount
        
        if self.is_immunized() or self.current_hp<-128:
            pass
        else:
            #Divine Shield Logic
            
            if self.has_divine_shield:
                damage=0
                self.has_divine_shield=False
                self.owner.board.activate_triggered_effects('lose divine shield',self)
  
            if not skip_animation:
                incur_damage_animation(self,damage)
                     
            if (damage_source is not None and damage_source.isCard()) and damage_source.has_keyword("lifesteal"):
                trigger_lifesteal_animation(damage_source)
                lifesteal_animation(damage_source.owner)
                damage_source.heal([damage_source.owner],[damage])
            
            #Damage updated by commanding shout effect if any
            original_health=self.current_hp
            self.current_hp-=damage
            if self.get_current_hp()<=0 and self.owner.board.get_buff(self)['shout']:# Does not die if commanding shout is activated
                while self.get_current_hp()<=0:
                    self.current_hp+=1
            damage=original_health-self.current_hp    
               
            self.last_damage_source=damage_source
            
            #Trigger minion damage effect if any   
            if damage>0:
                self.owner.board.activate_triggered_effects('minion damage',(self,damage))

            #Destroy Logic
            
            '''
            resulting_hp=self.get_current_hp()
            if resulting_hp<=0:
                if self.owner.board.get_buff(self)['shout']:# Does not die if commanding shout is activated
                    while self.get_current_hp()<=0:
                        self.current_hp+=1
                else:
                    if damage_source.isCard() and resulting_hp<0:
                        damage_source.overkill(self)
                    self.destroyed_by=damage_source
                    self.destroy()'''

                
            for on_hit in on_hit_effects:
                if self in self.owner.minions:
                    on_hit(self)
               
    def trigger_destroy(self):
        #Destroy Logic
        resulting_hp=self.get_current_hp()
        if resulting_hp<=0:
            if self.owner.board.get_buff(self)['shout']:# Does not die if commanding shout is activated
                while self.get_current_hp()<=0:
                    self.current_hp+=1
            else:
                if self.last_damage_source is not None and self.last_damage_source.isCard() and resulting_hp<0:
                    self.last_damage_source.overkill(self)
                self.destroyed_by=self.last_damage_source
                self.destroy()
            

            
    def restore_health(self,amount,heal_source=None,skip_animation=False):  
        previous_hp=self.current_hp
        self.current_hp+=amount
        hp_limit=max([self.hp,self.temp_hp])
        if self.current_hp>hp_limit:
            self.current_hp=hp_limit  
            
        if not skip_animation:
            heal_animation(self,self.current_hp-previous_hp)
            
        #Trigger restore health effect if any
        healing_amount=self.current_hp-previous_hp
        if healing_amount>0:
            self.owner.board.activate_triggered_effects("character healed",(self,healing_amount,heal_source))
            
        get_player(heal_source).trigger_quests("restore health",self.current_hp-previous_hp)
        #self.owner.play_logs["Health Restored"].append(self.current_hp-previous_hp)
    
    def buff_stats(self,atk=0,hp=0):
        self.current_atk+= atk
        self.current_hp+= hp
        if self.current_atk<=0:
            self.current_atk=0
        self.temp_atk+=atk
        self.temp_hp+=hp   
    
    def set_stats(self,atk=None,hp=None):
        if atk is not None:
            self.temp_atk=atk
            self.current_atk=atk
            
        if hp is not None:
            self.temp_hp=hp
            self.current_hp=hp
        
    def swap_stats(self):
        self.current_atk,self.current_hp = self.current_hp,self.current_atk
        self.temp_hp=self.current_hp
        self.temp_atk=self.current_atk
        if self.get_current_hp()<=0:
            self.destroy()

        
    def get_another_friendly_minion(self,race=None):
        target_pool=self.friendly_minions(race=race)
        if self in target_pool:
            target_pool.remove(self)
        if len(target_pool)>0:
            minion=random.choice(target_pool)
        else:
            minion=None
            
        return minion
        
    def adjacent_minions(self):
        targets=[]

        index=self.get_index()
        if 0<=index-1<=len(self.owner.minions)-1:
            targets.append(self.owner.minions[index-1])
        if 0<=index+1<=len(self.owner.minions)-1:
            targets.append(self.owner.minions[index+1])
            
        return targets
        
    def rebirth(self,index):
        minion = getattr(card_collection,database.cleaned(self.name))(owner=self.owner)
        self.owner.minions.insert(index,minion)
        minion.come_on_board()
        minion.image=self.board_image
        minion.board_area="Board"
        minion.rect=get_rect(self.rect.x,self.rect.y,self.image.get_width(),self.image.get_height())
        minion.location=self.location
        
        minion.current_hp=1
        minion.has_reborn=False
        
        reborn_animation(self)

    def magnetizable(self):
        index = self.get_index()  
        if index+1<len(self.owner.minions):
            minion_right=self.owner.minions[index+1]
            if minion_right.has_race("Mech") and not minion_right.has_dormant:
                return True
            
        return False
    
    def magnetize(self):
        target=self.owner.minions[self.get_index()+1]
        
        self.owner.minions.remove(self)
        self.owner.board.queue.remove(self)
        self.board_area=""
        
        self.owner.board.sort_minions(self.side)
        
        target.current_atk+=self.get_current_atk()
        target.temp_atk+=self.get_current_atk()
        target.current_hp+=self.get_current_hp()
        target.temp_hp+=self.get_current_hp()
        
        target.spell_damage_boost+=self.spell_damage_boost
        
        target.has_taunt=target.has_taunt or self.has_taunt
        target.has_divine_shield=target.has_divine_shield or self.has_divine_shield
        target.has_poisonous=target.has_poisonous or self.has_poisonous
        target.has_rush=target.has_rush or self.has_rush
        target.has_charge=target.has_charge or self.has_charge
        target.has_lifesteal=target.has_lifesteal or self.has_lifesteal
        target.has_elusive=target.has_elusive or self.has_elusive
        target.has_stealth=target.has_stealth or self.has_stealth
        target.has_immune=target.has_immune or self.has_immune
        target.has_windfury=target.has_windfury or self.has_windfury
        target.windfury_counter=max(target.windfury_counter,self.windfury_counter)
        target.has_reborn=target.has_reborn or self.has_reborn
        target.frozen=target.frozen or self.frozen
        target.inspire=target.inspire or self.inspire

        
        for deathrattle in self.deathrattles:
            d = MethodType(deathrattle[0].__func__,target)
            target.deathrattles.append([d,deathrattle[1]])

        for trigger in self.trigger_events:
            t = MethodType(trigger[1].__func__,target)
            target.trigger_events.append([trigger[0],t])
        
        for on_hit_effect in self.on_hit_effects:
            e = MethodType(on_hit_effect.__func__,target)
            target.on_hit_effects.append(e)
        
                   
    def destroy(self,skip_animation=False,skip_deathrattle=False):
        if not skip_animation:
            destroy_animation(self)
        
        self.owner.board.activate_triggered_effects('minion dies',self) 

        if self.board_area=="Board":#If the minion did not disappear due to triggered effects
            index=self.owner.minions.index(self)
            self.owner.minions.remove(self)
            self.owner.board.queue.remove(self)
            self.owner.board.graves[self.owner.side].append(self)
        
            self.board_area="Grave" 
            
            if not skip_deathrattle: 
                self.trigger_deathrattle()
                
            self.reset_status()
            
            '''Register died minions this turn'''
            controlling_player=self.owner.board.players[self.side]
            controlling_player.minions_died[controlling_player.turn].append(self)
            
            if self.has_reborn:
                self.rebirth(index)
                
            self.owner.board.sort_minions(self.owner.side)
                                       
    def return_hand(self,reset=True,skip_animation=False):  # reset when sapped or returned volationally
        if self in self.owner.minions:
            self.owner.minions.remove(self)
        if self in self.owner.board.queue:
            self.owner.board.queue.remove(self)
        self.image=self.mini_image
        if not skip_animation:
            return_hand_animation(self)
            
        if len(self.owner.hand)<self.owner.hand_limit:
            if reset: 
                self.reset_status()
            self.owner.board.hands[self.owner.side].append(self)
            self.board_area="Hand"
            sort_hand_animation(self.owner)
        else:
            self.destroy()
            
        self.owner.board.sort_minions(self.owner.side)
        

    
    def gain_immune(self):
        self.has_immune=True
       
    def gain_divine_shield(self):
        divine_shield_animation(self)
        self.has_divine_shield=True
         
    def gain_taunt(self):
        taunt_animation(self)
        self.has_taunt=True
        
    def gain_lifesteal(self):
        self.has_lifesteal=True  
    
    def gain_reborn(self):
        self.has_reborn=True  
    
    def gain_charge(self):
        self.has_charge=True  
    
    def gain_rush(self):
        self.has_rush=True  
            
    def gain_windfury(self,amount=2):
        windfury_animation(self)
        self.has_windfury=True
        self.windfury_counter=amount
    
    def gain_elusive(self):
        elusive_animation(self)
        self.has_elusive=True
    
    def gain_stealth(self):
        stealth_animation(self)
        self.has_stealth=True
    
    def gain_poisonous(self):
        poisonous_animation(self)
        self.has_poisonous=True
        self.on_hit_effects.append(MethodType(on_hit_poison,self))
     
    def gain_spell_damage_boost(self,amount):
        if amount>=0:
            self.current_spell_damage_boost=amount
        else:
            self.opponent_spell_damage_boost=-amount   
               
    def get_frozen(self,timer=2):
        self.frozen=True
        self.frozen_timer=timer
        if self.owner.board.control==self.side and self.attacked==False:
            self.frozen_timer-=1
            
        #Trigger frozen effect if any
        self.owner.board.activate_triggered_effects("frozen",self)
                   
    def adapt(self,times=1,choice=None):
        if choice is None:
            adaptations=[Crackling_Shield,Flaming_Claws,Living_Spores,Lightning_Speed,Liquid_Membrane,Massive,Volcanic_Might,Rocky_Carapace,Shrouding_Mist,Poison_Spit]
            for k in range(times):
                adaptation_options=random.sample(adaptations,3)
                adapt1=adaptation_options[0](owner=self.owner)
                adapt2=adaptation_options[1](owner=self.owner)
                adapt3=adaptation_options[2](owner=self.owner)
                if self.owner.board.random_select:
                    adapt_choice=random.choice([adapt1,adapt2,adapt3])
                else:
                    adapt_choice=choose_one([adapt1,adapt2,adapt3])
                if adapt_choice is not None:
                    adapt_choice.invoke(self)
            return adapt_choice
        else:
            choice.invoke(self)
    
    def increment_dormant_counter(self):
        self.dormant_counter+=1
        trigger_dormant_animation(self)
        if self.dormant_counter==self.dormant_cap:
            awake_animation(self)
            self.awake()
        
    def awake(self):
        self.has_dormant=False
        awake_animation(self)
        self.come_on_board()
                 
    def transform(self,minion,come_onto_board=True):
        '''
        for attr in dir(minion):
            if attr[:2]!="__":
                setattr(self,attr,getattr(minion,attr))
        setattr(self,"__init__",getattr(minion,"__init__")) 
        '''
        minion.rect=get_rect(self.rect.x,self.rect.y,self.image.get_width(),self.image.get_height())
        minion.location=self.location
        minion.image=minion.board_image
        minion.board_area=self.board_area
        minions=self.owner.minions
        minions[minions.index(self)]=minion
        if self in self.owner.board.queue:#Some minions transform before come on board
            self.owner.board.queue.remove(self)
        
        transform_animation(self,minion)
        self.transformed=minion
        if come_onto_board:
            minion.come_on_board()
            
        self.board_area="Burn"

    '''       
    def transform(self,minion):
        self.name               = minion.name
        self.big_image          = minion.big_image
        self.raw_image          = minion.raw_image
        self.mini_image         = minion.mini_image
        self.board_image        = minion.board_image
        self.taunt_image        = minion.taunt_image
        self.image              = minion.image
        self.owner              = minion.owner
        self.side               = minion.side
        self.card_type          = minion.card_type
        self.card_class         = minion.card_class
        self.race               = minion.race
        self.cardset            = minion.cardset
        self.rarity             = minion.rarity
        self.cost               = minion.cost
        self.atk                = minion.atk
        self.hp                 = minion.hp
        self.craft_cost         = minion.craft_cost
        self.disenchant_cost    = minion.disenchant_cost
        self.artist             = minion.artist
        self.card_text          = minion.card_text
        self.back_text          = minion.back_text
        self.lore               = minion.lore
        self.abilities          = minion.abilities
        self.tags               = minion.tags
        self.current_atk        = minion.atk
        self.temp_atk           = minion.current_atk
        self.current_hp         = minion.hp
        self.temp_hp            = minion.current_hp
        self.attacked           = minion.attacked
        self.has_taunt          = minion.has_taunt
        self.taunt              = minion.taunt
        self.has_divine_shield  = minion.has_divine_shield
        self.divine_shield      = minion.divine_shield
        self.spell_damage_boost = minion.spell_damage_boost
        self.current_spell_damage_boost = minion.current_spell_damage_boost
        self.opponent_spell_damage_boost=minion.opponent_spell_damage_boost
        self.current_opponent_spell_damage_boost=minion.current_opponent_spell_damage_boost
        self.has_effect_each_turn=minion.has_effect_each_turn
      ''' 
            
    def evolve(self,increased_cost=1):
        new_cost=max(0,min(self.cost+increased_cost,12))
        minion = database.get_random_cards("[type]='Minion' AND [cost]="+str(new_cost), owner=self.owner, k=1,standard=True)[0]
        minion.initialize_location(self.location)
        self.transform(minion)
         
    def is_attackable_by(self,attacker): 
        return not self.is_taunted() and not self.is_stealthed() and not self.has_dormant
    
    def is_targetable(self):
        return not self.has_keyword("elusive") and not (self.has_keyword("stealth") and self.side==-self.owner.board.control) and not self.has_dormant
    
    def is_stealthed(self):
        return self.has_keyword("stealth")
    
    def is_taunted(self):
        if self.has_taunt:
            return False
        
        for minion in self.friendly_minions():
            if minion.has_taunt and not minion.has_stealth and not self.temporary_effects["stealth"] and minion is not self:
                print("A Taunt Minion is in the way!")
                show_text("A Taunt Minion is in the way!", flip=True,pause=1)
                return True
        return False
 
    def is_immunized(self):
        return self.has_immune or self.temporary_effects["immune"] or self.owner.board.get_buff(self)['immune']
    
    def windfury_active(self):
        return ((self.has_windfury and self.attacks < self.windfury_counter) or 0<self.owner.board.get_buff(self)['windfury']<2 or self.attacks<self.temporary_effects['windfury'])
    
    def first_summoned(self):
        cards=self.owner.played_cards[self.owner.turn]
        for card in cards:
            if card.card_type=="Minion":
                return False
        return True
           
    def deathrattle(self):
        pass
    
    def end_of_turn_effect(self):
        if self.frozen_timer>0 and self.attacked==False and self.summoning_sickness==False:
            self.frozen=False
            
    def on_hit_effect(self,target):
        pass


class Murloc_Raider(Minion):
    def __init__(self,name="Murloc Raider",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
class Bloodfen_Raptor(Minion):
    def __init__(self,name="Bloodfen Raptor",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

class River_Crocolisk(Minion):
    def __init__(self,name="River Crocolisk",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

class Magma_Rager(Minion):
    def __init__(self,name="Magma Rager",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

class Chillwind_Yeti(Minion):
    def __init__(self,name="Chillwind_Yeti",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

class Oasis_Snapjaw(Minion):
    def __init__(self,name="Oasis Snapjaw",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
 
class Boulderfist_Ogre(Minion):
    def __init__(self,name="Boulderfist Ogre",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

class Core_Hound(Minion):
    def __init__(self,name="Core Hound",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

class War_Golem(Minion):
    def __init__(self,name="War Golem",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

class Sheep(Minion):
    def __init__(self,name="Sheep",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Boar_Polymorph_Boar(Minion):
    def __init__(self,name="Boar (Polymorph: Boar)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.charge=True
        
class Wisp(Minion):
    def __init__(self,name="Wisp",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

class Wisp_Wisps_of_the_Old_Gods(Minion):
    def __init__(self,name="Wisp (Wisps of the Old Gods)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
                                                                                
class Goldshire_Footman(Minion):
    def __init__(self,name="Goldshire Footman",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        
class Frostwolf_Grunt(Minion):
    def __init__(self,name="Frostwolf Grunt",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True

class Ironfur_Grizzly(Minion):
    def __init__(self,name="Ironfur Grizzly",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True

class Silverback_Patriarch(Minion):
    def __init__(self,name="Silverback Patriarch",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True

class Senjin_Shieldmasta(Minion):
    def __init__(self,name="Sen'jin Shieldmasta",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True

class Booty_Bay_Bodyguard(Minion):
    def __init__(self,name="Booty Bay Bodyguard",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
                                       
class Lord_of_the_Arena(Minion):
    def __init__(self,name="Lord of the Arena",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True

class Shieldbearer(Minion):
    def __init__(self,name="Shieldbearer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
                
class Stonetusk_Boar(Minion):
    def __init__(self,name="Stonetusk Boar",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.charge=True

class Bluegill_Warrior(Minion):
    def __init__(self,name="Bluegill Warrior",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.charge=True

class Wolfrider(Minion):
    def __init__(self,name="Wolfrider",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.charge=True

class Stormwind_Knight(Minion):
    def __init__(self,name="Stormwind Knight",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.charge=True

class Reckless_Rocketeer(Minion):
    def __init__(self,name="Reckless Rocketeer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.charge=True
                      
class Kobold_Geomancer(Minion):
    def __init__(self,name="Kobold Geomancer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.spell_damage_boost=1

class Dalaran_Mage(Minion):
    def __init__(self,name="Dalaran Mage",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.spell_damage_boost=1

class Ogre_Magi(Minion):
    def __init__(self,name="Ogre Magi",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.spell_damage_boost=1

class Archmage(Minion):
    def __init__(self,name="Archmage",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.spell_damage_boost=1
                                                               
class Shattered_Sun_Cleric(Minion):
    def __init__(self,name="Shattered Sun Cleric",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def get_target(self):
        minion=choose_target(chooser=self,target="friendly minion",message="+1/+1")
        return minion
    
    def battlecry(self,target):
        buff_animation(target)
        target.buff_stats(1,1)
                            
class Novice_Engineer(Minion):
    def __init__(self,name="Novice Engineer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        self.owner.draw()
        
class Gnomish_Inventor(Minion):
    def __init__(self,name="Gnomish Inventor",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        self.owner.draw()

class Captains_Parrot(Minion):
    def __init__(self,name="Captain's Parrot",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        card = self.owner.search_card(self.owner.deck.cards,card_type="Pirate")
        if card is not None:
            self.owner.draw(target=card)
        
class Azure_Drake(Minion):
    def __init__(self,name="Azure Drake",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.spell_damage_boost=1
        
    def battlecry(self,target=None):
        self.owner.draw()
        
class Coldlight_Oracle(Minion):
    def __init__(self,name="Coldlight Oracle",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        self.owner.draw(2)
        self.owner.opponent.draw(2)
                
class Murloc_Tidehunter(Minion):
    def __init__(self,name="Murloc Tidehunter",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        minion = Murloc_Scout(owner=self.owner)
        self.summon(minion)

class Murloc_Scout(Minion):
    def __init__(self,name="Murloc Scout",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Razorfen_Hunter(Minion):
    def __init__(self,name="Razorfen Hunter",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        minion = Boar_Razorfen_Hunter(owner=self.owner)
        self.summon(minion)

class Boar_Razorfen_Hunter(Minion):
    def __init__(self,name="Boar (Razorfen Hunter)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Dragonling_Mechanic(Minion):
    def __init__(self,name="Dragonling Mechanic",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        minion = Mechanical_Dragonling(owner=self.owner)
        self.summon(minion)

class Mechanical_Dragonling(Minion):
    def __init__(self,name="Mechanical Dragonling",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
                        
class Acidic_Swamp_Ooze(Minion):
    def __init__(self,name="Acidic Swamp Ooze",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def battlecry(self,target=None):
        if self.owner.opponent.has_weapon():
            acidic_swamp_ooze_animation(self,self.owner.opponent.weapon)
            self.owner.opponent.weapon.destroy()        

class Elven_Archer(Minion):
    def __init__(self,name="Elven Archer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(chooser=self,target="character",message="deal 1 damage")
        return target
    
    def battlecry(self,target):
        elven_archer_animation(self, target)
        self.deal_damage([target], [1])
                        
class Ironforge_Rifleman(Minion):
    def __init__(self,name="Ironforge Rifleman",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(chooser=self,target="character",message="deal 1 damage")
        return target
    
    def battlecry(self,target):
        ironforge_rifleman_animation(self, target)
        self.deal_damage([target], [1])
        
class Stormpike_Commando(Minion):
    def __init__(self,name="Stormpike Commando",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(chooser=self,target="character",message="deal 2 damage")
        return target
    
    def battlecry(self,target):
        stormpike_commando_animation(self, target)
        self.deal_damage([target], [2])
                    
class Nightblade(Minion):
    def __init__(self,name="Nightblade",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
    
    def battlecry(self,target=None):
        nightblade_animation(self,self.owner.opponent)
        self.deal_damage([self.owner.opponent], [3])
                        
class Voodoo_Doctor(Minion):
    def __init__(self,name="Voodoo Doctor",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def get_target(self):
        target=choose_target(chooser=self,target="character",message="restore 2 health")
        return target
    
    def battlecry(self,target):
        lesser_heal_animation(self, target)
        self.heal([target],[2])
        
class Darkscale_Healer(Minion):
    def __init__(self,name="Darkscale Healer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        targets=self.friendly_characters()
        self.heal(targets,[2]*len(targets))

class Frostwolf_Warlord(Minion):
    def __init__(self,name="Frostwolf Warlord",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        n=len(self.friendly_minions())-1  #(exclude itself)
        self.buff_stats(n, n)
                 
class Gurubashi_Berserker(Minion):
    def __init__(self,name="Gurubashi Berserker",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="minion damage"
        
    def trigger_effect(self,triggering_entity):
        if triggering_entity[0] is self:
            super(self.__class__,self).trigger_effect(self)
            self.buff_stats(3, 0)
         
class Acolyte_of_Pain(Minion):
    def __init__(self,name="Acolyte of Pain",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="minion damage"
        
    def trigger_effect(self,triggering_entity):
        if triggering_entity[0] is self:
            super(self.__class__,self).trigger_effect(self)
            self.owner.draw()
                                    
class Stormwind_Champion(Minion):
    def __init__(self,name="Stormwind Champion",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def ongoing_effect(self,target):
        if target.isMinion() and target.board_area=="Board" and target.side==self.side and target is not self:
            return {'atk':1,'hp':1}
        else:
            return {}
        
    def destroy(self,skip_animation=False,skip_deathrattle=False):
        super(self.__class__,self).destroy(skip_animation,skip_deathrattle)
        for minion in self.friendly_minions():
            if minion.current_hp<=0:
                minion.current_hp=1

class Grimscale_Oracle(Minion):
    def __init__(self,name="Grimscale Oracle",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def ongoing_effect(self,target):
        if target.isMinion() and target.board_area=="Board" and target.side==self.side and target is not self and target.has_race("Murloc"):
            return {'atk':1}
        else:
            return {}

class Raid_Leader(Minion):
    def __init__(self,name="Raid Leader",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def ongoing_effect(self,target):
        if target.isMinion() and target.board_area=="Board" and target.side==self.side and target is not self:
            return {'atk':1}
        else:
            return {}

class Abusive_Sergeant(Minion):
    def __init__(self,name="Abusive Sergeant",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(chooser=self,target="minion",message="give +2 attack this turn")
        return target
    
    def battlecry(self,target):
        target.current_atk+=2
           
class Argent_Squire(Minion):
    def __init__(self,name="Argent Squire",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.divine_shield=True 
      
class Leper_Gnome(Minion):
    def __init__(self,name="Leper Gnome",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        leper_gnome_animation(self)
        self.deal_damage([self.owner.opponent], [2])
            
class Southsea_Deckhand(Minion):
    def __init__(self,name="Southsea Deckhand",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def ongoing_effect(self,target):
        if target is self and target.owner.has_weapon() :
            return {'charge':True}
        else:
            return {}
                
class Worgen_Infiltrator(Minion):
    def __init__(self,name="Worgen Infiltrator",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.stealth=True 

class Young_Dragonhawk(Minion):
    def __init__(self,name="Young Dragonhawk",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.windfury=True 

class Amani_Berserker(Minion):
    def __init__(self,name="Amani Berserker",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.enrage=True
        
    def ongoing_effect(self,target):
        if target is self and target.damaged():
            return {'atk':3}
        else:
            return {}
        
class Bloodsail_Raider(Minion):
    def __init__(self,name="Bloodsail Raider",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        if self.owner.has_weapon():
            self.buff_stats(self.owner.weapon.current_atk, 0)
                                                   
class Dire_Wolf_Alpha(Minion):
    def __init__(self,name="Dire Wolf Alpha",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def ongoing_effect(self,target):
        if target.isMinion() and target.board_area=="Board" and target.side==self.side and abs(target.get_index()-self.get_index())==1:
            return {'atk':1}
        else:
            return {} 

class Faerie_Dragon(Minion):
    def __init__(self,name="Faerie Dragon",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.elusive=True 

class Loot_Hoarder(Minion):
    def __init__(self,name="Loot Hoarder",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        self.owner.draw()

class Dark_Cultist(Minion):
    def __init__(self,name="Dark Cultist",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        targets=self.friendly_minions()
        if len(targets>0):
            minion=random.choice(targets)
            priest_buff_animation(self, minion)
            minion.buff_stats(0,3)
              
class Mind_Control_Tech(Minion):
    def __init__(self,name="Mind Control Tech",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        if len(self.enemy_minions())>=4:
            minion=random.choice(self.enemy_minions())
            self.owner.take_control(minion)
            
class Mad_Bomber(Minion):
    def __init__(self,name="Mad Bomber",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def battlecry(self,target=None):
        self.deal_split_damage(self.all_characters(), shots=3, damage=1, effect=get_image("images/barrel.png",(90,90)), speed=12, curve=False)

class Youthful_Brewmaster(Minion):
    def __init__(self,name="Youthful Brewmaster",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(chooser=self,target="friendly minion",message="return to your hand")
        return target
    
    def battlecry(self,target):
        youthful_brewmaster_animation(self,target)
        target.return_hand(reset=True)
        
class Earthen_Ring_Farseer(Minion):
    def __init__(self,name="Earthen Ring Farseer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(chooser=self,target="character",message="restore 3 health")
        return target
    
    def battlecry(self,target):
        lesser_heal_animation(self, target)
        target.restore_health(3,self)
        
class Flesheating_Ghoul(Minion):
    def __init__(self,name="Flesheating Ghoul",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="minion dies"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card is not self:
            super(self.__class__,self).trigger_effect(triggering_card)
            self.buff_stats(1, 0)

class Harvest_Golem(Minion):
    def __init__(self,name="Harvest Golem",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        minion=Damaged_Golem(owner=self.owner)
        self.summon(minion)
            
class Damaged_Golem(Minion):
    def __init__(self,name="Damaged Golem",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Ironbeak_Owl(Minion):
    def __init__(self,name="Ironbeak Owl",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
      
    def get_target(self):
        target=choose_target(chooser=self,target="minion",message="silence")
        return target
    
    def battlecry(self,target):
        self.silence(target)
        
class Spellbreaker(Minion):
    def __init__(self,name="Spellbreaker",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def get_target(self):
        target=choose_target(chooser=self,target="minion",message="silence")
        return target
    
    def battlecry(self,target):
        self.silence(target)
            
class Jungle_Panther(Minion):
    def __init__(self,name="Jungle Panther",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.stealth=True 

class Raging_Worgen(Minion):
    def __init__(self,name="Raging Worgen",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.enrage=True
        
    def ongoing_effect(self,target):
        if target is self and target.damaged():
            return {'atk':1,'windfury':(2-self.attacks)}
        else:
            return {}
        
class Scarlet_Crusader(Minion):
    def __init__(self,name="Scarlet Crusader",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.divine_shield=True 

class Tauren_Warrior(Minion):
    def __init__(self,name="Tauren Warrior",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        self.enrage=True
        
    def ongoing_effect(self,target):
        if target is self and target.damaged():
            return {'atk':3}
        else:
            return {}

class Thrallmar_Farseer(Minion):
    def __init__(self,name="Thrallmar Farseer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.windfury=True 

class Ancient_Brewmaster(Minion):
    def __init__(self,name="Ancient Brewmaster",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(chooser=self,target="friendly minion",message="return to your hand")
        return target
    
    def battlecry(self,target):
        youthful_brewmaster_animation(self,target)
        target.return_hand(reset=True)
        
class Cult_Master(Minion):
    def __init__(self,name="Cult Master",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="minion dies"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.side==self.side and triggering_card is not self:
            super(self.__class__,self).trigger_effect(triggering_card)
            self.owner.draw()
                                                
class Dark_Iron_Dwarf(Minion):
    def __init__(self,name="Dark Iron Dwarf",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(chooser=self,target="minion",message="give +2 attack this turn")
        return target
    
    def battlecry(self,target):
        target.current_atk+=2
        
class Dread_Corsair(Minion):
    def __init__(self,name="Dread Corsair",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        
    def ongoing_effect(self,target):
        if target is self and target.board_area=="Hand" and self.owner.has_weapon():
            return {'cost':-self.owner.weapon.current_atk}
        else:
            return {} 

class Mogushan_Warden(Minion):
    def __init__(self,name="Mogu'shan Warden",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True

class Silvermoon_Guardian(Minion):
    def __init__(self,name="Silvermoon Guardian",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.divine_shield=True 

class Fen_Creeper(Minion):
    def __init__(self,name="Fen Creeper",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True 

class Silver_Hand_Knight(Minion):
    def __init__(self,name="Silver Hand Knight",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        minion = Squire(owner=self.owner)
        self.summon(minion)

class Squire(Minion):
    def __init__(self,name="Squire",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
                                                                                                                                                                
class Spiteful_Smith(Minion):
    def __init__(self,name="Spiteful Smith",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.enrage=True
        
    def ongoing_effect(self,target):
        if target.isWeapon() and target.side==self.side and self.damaged():
            return {'atk':2}
        else:
            return {}    

class Stranglethorn_Tiger(Minion):
    def __init__(self,name="Stranglethorn Tiger",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.stealth=True 

class Venture_Co_Mercenary(Minion):
    def __init__(self,name="Venture Co. Mercenary",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def ongoing_effect(self,target):
        if target.isMinion() and target.side==self.side and target.board_area=="Hand" and target is not self:
            return {'cost':3}
        else:
            return {}    
  
class Frost_Elemental(Minion):
    def __init__(self,name="Frost Elemental",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(chooser=self,target="character",message="freeze")
        return target
    
    def battlecry(self,target):
        target.get_frozen()
        
class Priestess_of_Elune(Minion):
    def __init__(self,name="Priestess of Elune",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        self.heal([self.owner], [4])

class Windfury_Harpy(Minion):
    def __init__(self,name="Windfury Harpy",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.windfury=True 

class Angry_Chicken(Minion):
    def __init__(self,name="Angry Chicken",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.enrage=True
        
    def ongoing_effect(self,target):
        if target is self and target.damaged():
            return {'atk':5}
        else:
            return {}

class Bloodsail_Corsair(Minion):
    def __init__(self,name="Bloodsail Corsair",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def battlecry(self,target=None):
        if self.owner.opponent.has_weapon():
            bloodsail_corsair_animation(self)
            self.owner.opponent.weapon.decrease_durability()

class Lightwarden(Minion):
    def __init__(self,name="Lightwarden",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="character healed"
        
    def trigger_effect(self,triggering_entity):
        super(self.__class__,self).trigger_effect(triggering_entity[0])
        self.buff_stats(2, 0)
        
class Murloc_Tidecaller(Minion):
    def __init__(self,name="Murloc Tidecaller",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="summon a minion"
        
    def trigger_effect(self,triggering_minion):
        if triggering_minion.side==self.side and triggering_minion.has_race("Murloc") and triggering_minion is not self:
            super(self.__class__,self).trigger_effect(triggering_minion)
            self.buff_stats(1, 0)

class Secretkeeper(Minion):
    def __init__(self,name="Secretkeeper",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="play a card"
        
    def trigger_effect(self,triggering_card):
        if isinstance(triggering_card,Secret):
            super(self.__class__,self).trigger_effect(triggering_card)
            self.buff_stats(1, 1)

class Young_Priestess(Minion):
    def __init__(self,name="Young Priestess",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source) 
        self.trigger_event_type="end of turn"
       
    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner:
            super(self.__class__,self).trigger_effect(triggering_player)
            minion=self.get_another_friendly_minion()
            if minion is not None:
                minion.buff_stats(0,1)

class Ancient_Watcher(Minion):
    def __init__(self,name="Ancient Watcher",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source) 
        self.cannot_attack=True
                    
class Crazed_Alchemist(Minion):
    def __init__(self,name="Crazed Alchemist",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(chooser=self,target="minion",message="swap attack and health")
        return target
    
    def battlecry(self,target):
        crazed_alchemist_animation(self,target)
        target.swap_stats()
        
class Knife_Juggler(Minion):
    def __init__(self,name="Knife Juggler",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="summon a minion"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.side==self.side and triggering_card is not self:
            super(self.__class__,self).trigger_effect(self)
            target=random.choice(self.enemy_characters())
            knife_juggler_animation(self,target)
            self.deal_damage([target], [1])
                  
class Mana_Addict(Minion):
    def __init__(self,name="Mana Addict",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="cast a spell"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.owner is self.owner:
            super(self.__class__,self).trigger_effect(triggering_card)
            self.current_atk+=2

class Mana_Wraith(Minion):
    def __init__(self,name="Mana Wraith",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def ongoing_effect(self,target):
        if target.isMinion() and target.board_area=="Hand" and target is not self:
            return {'cost':1}
        else:
            return {}    
      
class Master_Swordsmith(Minion):
    def __init__(self,name="Master Swordsmith",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source) 
        self.trigger_event_type="end of turn"
       
    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner:
            super(self.__class__,self).trigger_effect(triggering_player)
            minion=self.get_another_friendly_minion()
            if minion is not None:
                minion.buff_stats(1,0)

class Pint_Sized_Summoner(Minion):
    def __init__(self,name="Pint-Sized Summoner",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def ongoing_effect(self,target):
        if target.isMinion() and target.side==self.side and target.board_area=="Hand" and target.first_summoned():
            return {'cost':-1}
        else:
            return {}    
        
class Sunfury_Protector(Minion):
    def __init__(self,name="Sunfury Protector",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        targets=self.adjacent_minions()
        for target in targets:
            target.gain_taunt()

class Wild_Pyromancer(Minion):
    def __init__(self,name="Wild Pyromancer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="play a card"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.isSpell and triggering_card.owner is self.owner:
            super(self.__class__,self).trigger_effect(triggering_card)
            wild_pyromancer_animation(self)
            targets=self.all_minions()
            self.deal_damage(targets, [1]*len(targets))

class Alarm_o_Bot(Minion):
    def __init__(self,name="Alarm-o-Bot",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source) 
        self.trigger_event_type="start of turn"
       
    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner:
            minion=self.owner.search_card(self.owner.hand,card_type="Minion")
            if minion is not None:
                super(self.__class__,self).trigger_effect(triggering_player)
                target_location=self.location
                self.return_hand(reset=True)
                self.owner.put_into_battlefield(minion,target_location)

class Arcane_Golem(Minion):
    def __init__(self,name="Arcane Golem",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        self.owner.opponent.gain_mana()

class Coldlight_Seer(Minion):
    def __init__(self,name="Coldlight Seer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        self.buff_multiple(race="Murloc", atk=0, hp=2)

class Demolisher(Minion):
    def __init__(self,name="Demolisher",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source) 
        self.trigger_event_type="start of turn"
       
    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner:
            super(self.__class__,self).trigger_effect(triggering_player)
            targets=self.enemy_characters()
            target = random.choice(targets)
            demolisher_animation(self,target)
            self.deal_damage([target], [2])
                       
class Emperor_Cobra(Minion):
    def __init__(self,name="Emperor Cobra",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source) 
        self.poisonous=True

class Imp_Master(Minion):
    def __init__(self,name="Imp Master",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source) 
        self.trigger_event_type="end of turn"
       
    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner:
            super(self.__class__,self).trigger_effect(triggering_player)
            self.deal_damage([self], [1])
            minion=Imp_Imp_Master(owner=self.owner)
            self.summon(minion)
            
class Imp_Imp_Master(Minion):
    def __init__(self,name="Imp (Imp Master)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source) 

class Imp_Imp_losion(Minion):
    def __init__(self,name="Imp (Imp-losion)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source) 

class Imp_Imp_Gang_Boss(Minion):
    def __init__(self,name="Imp (Imp Gang Boss)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source) 
                        
class Injured_Blademaster(Minion):
    def __init__(self,name="Injured Blademaster",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        self.deal_damage([self], [4])

class Questing_Adventurer(Minion):
    def __init__(self,name="Questing Adventurer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="play a card"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.owner is self.owner and triggering_card is not self:
            super(self.__class__,self).trigger_effect(triggering_card)
            self.buff_stats(1, 1)
            
class Ancient_Mage(Minion):
    def __init__(self,name="Ancient Mage",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        index=self.get_index()
        if 0<=index-1<=len(self.owner.minions)-1:
            self.owner.minions[index-1].gain_spell_damage_boost(1)
        if 0<=index+1<=len(self.owner.minions)-1:
            self.owner.minions[index+1].gain_spell_damage_boost(1)

class Defender_of_Argus(Minion):
    def __init__(self,name="Defender of Argus",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        targets=self.adjacent_minions()
        for target in targets:
            target.buff_stats(1,1)
            target.gain_taunt()

class Twilight_Drake(Minion):
    def __init__(self,name="Twilight Drake",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        handsize=len(self.owner.hand)
        self.buff_stats(0, handsize)

class SI7_Infiltrator(Minion):
    def __init__(self,name="SI:7 Infiltrator",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        if len(self.owner.opponent.secrets)>0:
            secret = random.choice(self.owner.opponent.secrets)
            if secret is not None:
                secret.destroy()

class Violet_Teacher(Minion):
    def __init__(self,name="Violet Teacher",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="cast a spell"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.owner is self.owner:
            super(self.__class__,self).trigger_effect(triggering_card)
            minion=Violet_Apprentice(owner=self.owner)
            self.summon(minion)

class Violet_Apprentice(Minion):
    def __init__(self,name="Violet Apprentice",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
  
class Abomination(Minion):
    def __init__(self,name="Abomination",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        
    def deathrattle(self):
        abomination_animation(self)
        targets=self.all_characters()
        self.deal_damage(targets, [2]*len(targets))

class Stampeding_Kodo(Minion):
    def __init__(self,name="Stampeding Kodo",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        minions=self.enemy_minions()
        targets=[]
        for minion in minions:
            if minion.get_current_atk()<=2:
                targets.append(minion)
        if len(targets)>0:
            target=random.choice(targets)
            charge_shot_animation(self,target)
            target.destroy()
 
class Argent_Commander(Minion):
    def __init__(self,name="Argent Commander",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.charge=True
        self.divine_shield=True
                                                                                                                                                                                                                                                           
class Gadgetzan_Auctioneer(Minion):
    def __init__(self,name="Gadgetzan Auctioneer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="cast a spell"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.side==self.side:
            super(self.__class__,self).trigger_effect(triggering_card)
            gadgetzan_auctioneer_animation(self)
            self.owner.draw() 
                  
class Sunwalker(Minion):
    def __init__(self,name="Sunwalker",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        self.divine_shield=True

class Ravenholdt_Assassin(Minion):
    def __init__(self,name="Ravenholdt_Assassin",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.stealth=True
 
class Arcane_Devourer(Minion):
    def __init__(self,name="Arcane Devourer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="cast a spell"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.owner is self.owner:
            super(self.__class__,self).trigger_effect(triggering_card)
            self.buff_stats(2, 2)

class Hungry_Crab(Minion):
    def __init__(self,name="Hungry Crab",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(chooser=self,target="minion",target_type="Murloc",message="destroy and gain +2/+2")
        return target
    
    def battlecry(self,target):
        target.destroy()
        self.buff_stats(2, 2)
        
class Doomsayer(Minion):
    def __init__(self,name="Doomsayer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source) 
        self.trigger_event_type="start of turn"
       
    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner:
            super(self.__class__,self).trigger_effect(triggering_player)
            doomsayer_animation(self)
            targets=self.all_minions()
            destroy_multiple_animation(targets)
            for target in targets:
                if target.board_area=="Board":
                    target.destroy(skip_animation=True)

class Blood_Knight(Minion):
    def __init__(self,name="Blood Knight",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        targets=self.all_minions()
        count=0
        for target in targets:
            if target.has_divine_shield:
                target.has_divine_shield=False
                count+=1
        buff_animation(self)
        self.buff_stats(3*count, 3*count)

class Murloc_Warleader(Minion):
    def __init__(self,name="Murloc Warleader",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def ongoing_effect(self,target):
        if target.isMinion() and target.board_area=="Board" and target.side==self.side and target.has_race("Murloc") and target is not self:
            return {'atk':2}
        else:
            return {} 

class Southsea_Captain(Minion):
    def __init__(self,name="Southsea Captain",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def ongoing_effect(self,target):
        if target.isMinion() and target.board_area=="Board" and target.side==self.side and target.has_race("Pirate") and target is not self:
            return {'atk':1,'hp':1}
        else:
            return {} 
                           
    def destroy(self,skip_animation=False,skip_deathrattle=False):
        super(self.__class__,self).destroy(skip_animation,skip_deathrattle)
        for minion in self.friendly_minions():
            if minion.current_hp<=0:
                minion.current_hp=1

class Big_Game_Hunter(Minion):
    def __init__(self,name="Big Game Hunter",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(chooser=self,target="minion",target_type="get_current_atk __ge__ 7", message="destroy")
        return target
    
    def battlecry(self,target):
        big_game_hunter_animation(self,target)
        target.destroy()
                                   
class Faceless_Manipulator(Minion):
    def __init__(self,name="Faceless Manipulator",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(chooser=self,target="minion",message="become a copy of it")
        return target
    
    def battlecry(self,target):
        minion_copy=target.get_copy(owner=self.owner)
        minion_copy.initialize_location(self.location)
        minion_copy.copy_stats(target)
        self.transform(minion_copy)
        
class Barrens_Stablehand(Minion):
    def __init__(self,name="Barrens Stablehand",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        minion = database.get_random_cards("[type]='Minion' AND [race]='Beast'", self.owner, 1)[0]
        self.summon(minion)

class Sea_Giant(Minion):
    def __init__(self,name="Sea Giant",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def ongoing_effect(self,target):
        if target is self and target.board_area=="Hand":
            targets=self.all_minions()
            if self in targets:
                targets.remove(self)   # Keep the cost when entering battlefield
            return {'cost':-len(targets)}
        else:
            return {} 
             
class Mountain_Giant(Minion):
    def __init__(self,name="Mountain Giant",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def ongoing_effect(self,target):
        if target is self and target.board_area=="Hand":
            n=len(self.owner.hand)
            if self in self.owner.hand:
                n-=1
            return {'cost':-n}
        else:
            return {} 

class Molten_Giant(Minion):
    def __init__(self,name="Molten Giant",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def ongoing_effect(self,target):
        if target is self and target.board_area=="Hand":
            return {'cost':-(self.owner.hp-self.owner.current_hp)}
        else:
            return {} 

class Dancing_Swords(Minion):
    def __init__(self,name="Dancing Swords",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        self.owner.opponent.draw()

class Haunted_Creeper(Minion):
    def __init__(self,name="Haunted Creeper",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        for i in range(2):
            minion=Spectral_Spider(owner=self.owner)
            self.summon(minion)
            
class Spectral_Spider(Minion):
    def __init__(self,name="Spectral Spider",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Mad_Scientist(Minion):
    def __init__(self,name="Mad Scientist",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        secret_pool=[]
        for card in self.owner.deck.cards:
            if isinstance(card, Secret) and card.is_valid_on():
                secret_pool.append(card)
                
        if len(secret_pool)>0:
            target_secret = random.choice(secret_pool)
            target_secret.invoke()
            self.owner.deck.cards.remove(target_secret)
                    
class Nerubar_Weblord(Minion):
    def __init__(self,name="Nerub'ar Weblord",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def ongoing_effect(self,target):
        if target.isMinion() and target.board_area=="Hand" and "Battlecry" in target.abilities:
            return {'cost':2}
        else:
            return {}    

class Spectral_Knight(Minion):
    def __init__(self,name="Spectral Knight",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.elusive=True
        
class Stoneskin_Gargoyle(Minion):
    def __init__(self,name="Stoneskin Gargoyle",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source) 
        self.trigger_event_type="start of turn"
       
    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner:
            super(self.__class__,self).trigger_effect(triggering_player)
            self.heal([self],[self.temp_hp])

class Undertaker(Minion):
    def __init__(self,name="Undertaker",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="summon a minion"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.side==self.side and triggering_card.has_deathrattle and triggering_card is not self:
            super(self.__class__,self).trigger_effect(triggering_card)
            buff_animation(self)
            self.buff_stats(1, 0)
                                          
class Unstable_Ghoul(Minion):
    def __init__(self,name="Unstable Ghoul",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        
    def deathrattle(self):
        unstable_ghoul_animation(self)
        targets=self.all_minions()
        self.deal_damage(targets, [1]*len(targets))

class Zombie_Chow(Minion):
    def __init__(self,name="Zombie Chow",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        zombie_chow_animation(self)
        self.heal([self.owner.opponent],[5])
                
class Deathlord(Minion):
    def __init__(self,name="Deathlord",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        
    def deathrattle(self):
        minion = self.owner.opponent.search_card(self.owner.opponent.deck.cards,card_type="Minion")
        if minion is not None:
            self.recruit(minion)
            
class Nerubian_Egg(Minion):
    def __init__(self,name="Nerubian Egg",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        minion=Nerubian_Nerubian_Egg(owner=self.owner)
        self.summon(minion)

class Nerubian_Nerubian_Egg(Minion):
    def __init__(self,name="Nerubian (Nerubian Egg)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Nerubian_Beneath_the_Grounds(Minion):
    def __init__(self,name="Nerubian (Beneath the Grounds)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        
class Sludge_Belcher(Minion):
    def __init__(self,name="Sludge Belcher",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        
    def deathrattle(self):
        minion=Slime_Sludge_Belcher(owner=self.owner)
        self.summon(minion)
    
class Slime_Sludge_Belcher(Minion):
    def __init__(self,name="Slime (Sludge Belcher)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
                
class Wailing_Soul(Minion):
    def __init__(self,name="Wailing Soul",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        mass_dispel_animation(self)
        targets=self.friendly_minions()
        for minion in targets:
            self.silence(minion, skip_animation=True)

class Echoing_Ooze(Minion):
    def __init__(self,name="Echoing Ooze",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        self.trigger_events.append(["end of turn",MethodType(self.trigger_effect.__func__,self)])

    def trigger_effect(self,triggering_player):
        if triggering_player is self.owner:
            self.trigger_events.remove(["end of turn",MethodType(self.trigger_effect.__func__,self)])
            minion=Echoing_Ooze(owner=self.owner)
            echoing_ooze_animation(self)
            self.summon(minion)
            minion.copy_stats(self)
                                                     
class Shade_of_Naxxramas(Minion):
    def __init__(self,name="Shade of Naxxramas",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.stealth=True
        self.trigger_event_type="start of turn"
        
    def trigger_effect(self,triggering_player):
        if triggering_player is self.owner:
            super(self.__class__,self).trigger_effect(triggering_player)
            buff_animation(self,speed=8)
            self.buff_stats(1,1)

class Clockwork_Gnome(Minion):
    def __init__(self,name="Clockwork Gnome",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        self.give_random_spare_part(self.owner)

class Cogmaster(Minion):
    def __init__(self,name="Cogmaster",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def ongoing_effect(self,target):
        if target is self and self.owner.control("Mech"):
            return {'atk':2}
        else:
            return {}

class Annoy_o_Tron(Minion):
    def __init__(self,name="Annoy-o-Tron",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        self.divine_shield=True

class Explosive_Sheep(Minion):
    def __init__(self,name="Explosive Sheep",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
 
    def deathrattle(self):
        unstable_ghoul_animation(self)
        targets=self.all_minions()
        self.deal_damage(targets, [2]*len(targets))

class Gilblin_Stalker(Minion):
    def __init__(self,name="Gilblin Stalke",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.stealth=True

class Mechwarper(Minion):
    def __init__(self,name="Mechwarper",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def ongoing_effect(self,target):
        if target.isMinion() and target.side==self.side and target.board_area=="Hand" and target is not self and target.has_race("Mech"):
            return {'cost':-1}
        else:
            return {}  
            
class Micro_Machine(Minion):
    def __init__(self,name="Micro Machine",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source) 
        self.trigger_event_type="start of turn"
       
    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner:
            super(self.__class__,self).trigger_effect(triggering_player)
            mech_buff_animation(self)
            self.buff_stats(1, 0)

class Puddlestomper(Minion):
    def __init__(self,name="Puddlestomper",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source) 
                                                                                                           
class Ships_Cannon(Minion):
    def __init__(self,name="Ship's Cannon",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="summon a minion"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.side==self.side and triggering_card.has_race("Pirate"):
            super(self.__class__,self).trigger_effect(triggering_card)
            target=random.choice(self.enemy_characters())
            stormpike_commando_animation(self,target)
            self.deal_damage([target], [2])

class Stonesplinter_Trogg(Minion):
    def __init__(self,name="Stonesplinter Trogg",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="cast a spell"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.side==-self.side:
            super(self.__class__,self).trigger_effect(triggering_card)
            buff_animation(self)
            self.buff_stats(1, 0)

class Flying_Machine(Minion):
    def __init__(self,name="Flying Machine",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.windfury=True

class Gnomeregan_Infantry(Minion):
    def __init__(self,name="Gnomeregan Infantry",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.charge=True
        self.taunt=True

class Ogre_Brute(Minion):
    def __init__(self,name="Ogre Brute",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="attack"
        
    def trigger_effect(self,triggering_minion):
        if triggering_minion is self:
            self.attack_wrong_enemy(0.5)       
            
class Spider_Tank(Minion):
    def __init__(self,name="Spider Tank",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

class Tinkertown_Technician(Minion):
    def __init__(self,name="Tinkertown Technician",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        if self.owner.control("Mech"):
            mech_buff_animation(self)
            self.buff_stats(1, 1)
            self.give_random_spare_part(self.owner)
                                          
class Burly_Rockjaw_Trogg(Minion):
    def __init__(self,name="Burly Rockjaw Trogg",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="cast a spell"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.side==-self.side:
            super(self.__class__,self).trigger_effect(triggering_card)
            buff_animation(self)
            self.buff_stats(2, 0)
            
class Lost_Tallstrider(Minion):
    def __init__(self,name="Lost Tallstrider",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

class Mechanical_Yeti(Minion):
    def __init__(self,name="Mechanical Yeti",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        self.give_random_spare_part(self.owner)
        self.give_random_spare_part(self.owner.opponent)

class Piloted_Shredder(Minion):
    def __init__(self,name="Piloted Shredder",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        minion = database.get_random_cards("[type]='Minion' AND [cost]=2", self.owner, 1)[0]
        self.summon(minion)

class Antique_Healbot(Minion):
    def __init__(self,name="Antique Healbot",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        self.heal([self.owner],[8])
                            
class Salty_Dog(Minion):
    def __init__(self,name="Salty Dog",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

class Force_Tank_MAX(Minion):
    def __init__(self,name="Forc-Tank MAX",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.divine_shield=True

class Target_Dummy(Minion):
    def __init__(self,name="Target Dummy",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True

class Gnomish_Experimenter(Minion):
    def __init__(self,name="Gnomish Experimenter",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        card=self.owner.draw(1)
        if card.isMinion():
            chicken=Chicken_Gnomish_Experimenter(owner=self.owner)
            gnomish_experimenter_animation(card,chicken)
            self.owner.hand.remove(card)
            self.owner.add_hand(chicken)
            
class Chicken_Gnomish_Experimenter(Minion):
    def __init__(self,name="Chicken (Gnomish Experimenter)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Goblin_Sapper(Minion):
    def __init__(self,name="Goblin Sapper",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def ongoing_effect(self,target):
        if target is self and len(self.owner.opponent.hand)>=6:
            return {'atk':4}
        else:
            return {}
        
class Illuminator(Minion):
    def __init__(self,name="Illuminator",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="end of turn"
        
    def trigger_effect(self,triggering_player):
        if triggering_player is self.owner and len(self.owner.secrets)>0:
            super(self.__class__,self).trigger_effect(triggering_player)

class Lil_Exorcist(Minion):
    def __init__(self,name="Lil' Exorcist",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        
    def battlecry(self,target=None):
        pool=self.enemy_minions()
        count=0
        for minion in pool:
            if minion.has_deathrattle:
                count+=1
        if count>0:
            buff_animation(self)
            self.buff_stats(count, count)

class Arcane_Nullifier_X_21(Minion):
    def __init__(self,name="Arcane Nullifier X-21",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        self.elusive=True
                
class Jeeves(Minion):
    def __init__(self,name="Jeeves",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="end of turn"
        
    def trigger_effect(self,triggering_player):
        while len(triggering_player.hand)<3:
            triggering_player.draw()

class Kezan_Mystic(Minion):
    def __init__(self,name="Kezan Mystic",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        if len(self.owner.opponent.secrets)>0:
            secret=random.choice(self.owner.opponent.secrets)
            self.owner.take_control_secret(secret)

class Bomb_Lobber(Minion):
    def __init__(self,name="Bomb Lobber",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        targets=self.enemy_minions()
        if len(targets)>0:
            target=random.choice(targets)
            bomb_lobber_animation(self,target)
            self.deal_damage([target], [4])

class Madder_Bomber(Minion):
    def __init__(self,name="Madder Bomber",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        self.deal_split_damage(self.all_characters(), shots=6, damage=1, effect=get_image("images/bomb2.png",(124,124)), speed=15, curve=False)

class Recombobulator(Minion):
    def __init__(self,name="Recombobulator",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(self, target="friendly minion", message="transform into a random minion with the same cost")
        return target
    
    def battlecry(self,target):
        target.evolve(0)
        
class Hobgoblin(Minion):
    def __init__(self,name="Hobgoblin",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="play a card"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.owner is self.owner and triggering_card.isMinion() and triggering_card.atk==1:
            super(self.__class__,self).trigger_effect(triggering_card)
            hobgoblin_animation(self,triggering_card)
            triggering_card.buff_stats(2, 2)

class Enhance_o_Mechano(Minion):
    def __init__(self,name="Enhance-o Mechano",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        targets=self.friendly_minions()
        enhance_o_mechano_animation(self, targets)
        for minion in targets:
            random.choice([minion.gain_taunt,minion.gain_windfury,minion.gain_divine_shield])()
            
class Mini_Mage(Minion):
    def __init__(self,name="Mini Mage",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.stealth=True
        self.spell_damage_boost=1

class Fel_Reaver(Minion):
    def __init__(self,name="Fel Reaver",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="play a card"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.owner is self.owner.opponent:
            super(self.__class__,self).trigger_effect(triggering_card)
            for i in range(3):
                card=self.owner.deck.top()
                if not card.isFatigue():
                    card.burn()

class Junkbot(Minion):
    def __init__(self,name="Junkbot",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="minion dies"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card is not self and triggering_card.has_race("Mech"):
            super(self.__class__,self).trigger_effect(triggering_card)
            self.buff_stats(2, 2)
                                                                                                                                                                
class Piloted_Sky_Golem(Minion):
    def __init__(self,name="Piloted Sky Golem",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        minion = database.get_random_cards("[type]='Minion' AND [cost]=4", self.owner, 1)[0]
        self.summon(minion)

class Clockwork_Giant(Minion):
    def __init__(self,name="Clockwork Giant",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def ongoing_effect(self,target):
        if target is self and target.board_area=="Hand":
            n=len(self.owner.opponent.hand)
            return {'cost':-n}
        else:
            return {} 

class Dragon_Egg(Minion):
    def __init__(self,name="Dragon Egg",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="minion damage"
        
    def trigger_effect(self,triggering_entity):
        if triggering_entity[0] is self:
            super(self.__class__,self).trigger_effect(self)
            minion=Black_Whelp(owner=self.owner)
            self.summon(minion)

class Black_Whelp(Minion):
    def __init__(self,name="Black Whelp",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
                            
class Blackwing_Technician(Minion):
    def __init__(self,name="Blackwing Technician",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        if self.owner.holding("Dragon"):
            buff_animation(self)
            self.buff_stats(1, 1)

class Dragonkin_Sorcerer(Minion):
    def __init__(self,name="Dragonkin Sorcerer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="cast a spell"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.side==self.side and triggering_card.target is self:
            super(self.__class__,self).trigger_effect(triggering_card)
            buff_animation(self)
            self.buff_stats(1, 1)

class Hungry_Dragon(Minion):
    def __init__(self,name="Hungry Dragon",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        minion = database.get_random_cards("[type]='Minion' AND [cost]=1", self.owner.opponent, 1)[0]
        self.summon(minion)

class Blackwing_Corruptor(Minion):
    def __init__(self,name="Blackwing Corruptor",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=None
        if self.owner.holding("Dragon"):
            target=choose_target(chooser=self,target="character",message="deal 3 damage")
        return target
    
    def battlecry(self,target):
        fel_cannon_animation(self, target)
        self.deal_damage([target], [3])
        
class Drakonid_Crusher(Minion):
    def __init__(self,name="Drakonid Crusher",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        if self.owner.opponent.current_hp<=15:
            rage_buff_animation(self)
            self.buff_stats(3, 3)

class Volcanic_Drake(Minion):
    def __init__(self,name="Volcanic Drake",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def ongoing_effect(self,target):
        if target is self and target.board_area=="Hand":
            n=self.owner.get_num_minions_died()
            return {'cost':-n}
        else:
            return {} 

class Grim_Patron(Minion):
    def __init__(self,name="Grim Patron",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="minion damage"
        
    def trigger_effect(self,triggering_entity):
        if triggering_entity[0] is self and self.get_current_hp()>0:
            super(self.__class__,self).trigger_effect(self)
            minion=Grim_Patron(owner=self.owner)
            self.summon(minion)

class Gadgetzan_Jouster(Minion):
    def __init__(self,name="Gadgetzan Jouster",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        winner = self.joust("Minion")
        if winner is not None and winner.owner is self.owner:
            buff_animation(self)
            self.buff_stats(1, 1)

class Lowly_Squire(Minion):
    def __init__(self,name="Lowly Squire",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.inspire=True
         
    def trigger_inspire(self, hero_power=None):
        if hero_power.owner is self.owner:
            super(self.__class__,self).trigger_inspire()
            light_buff_animation(self)
            self.buff_stats(1, 0)

class Tournament_Attendee(Minion):
    def __init__(self,name="Tournament Attendee",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True

class Boneguard_Lieutenant(Minion):
    def __init__(self,name="Boneguard Lieutenant",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.inspire=True
         
    def trigger_inspire(self, hero_power=None):
        if hero_power.owner is self.owner:
            super(self.__class__,self).trigger_inspire()
            light_buff_animation(self)
            self.buff_stats(0, 1)

class Flame_Juggler(Minion):
    def __init__(self,name="Flame Juggler",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        target_pool=self.enemy_characters()
        target=random.choice(target_pool)
        flame_juggler_animation(self,target)
        self.deal_damage([target], [1]) 

class Lance_Carrier(Minion):
    def __init__(self,name="Lance Carrier",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(chooser=self,target="friendly minion",message="give +2 Attack")
        return target
    
    def battlecry(self,target):
        target.buff_stats(2,0)
        
class Argent_Horserider(Minion):
    def __init__(self,name="Argent Horserider",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.charge=True
        self.divine_shield=True

class Dragonhawk_Rider(Minion):
    def __init__(self,name="Dragonhawk Rider",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.inspire=True
         
    def trigger_inspire(self, hero_power=None):
        if hero_power.owner is self.owner:
            super(self.__class__,self).trigger_inspire()
            self.temporary_effects['windfury']=2

class Ice_Rager(Minion):
    def __init__(self,name="Ice Rager",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

class Silent_Knight(Minion):
    def __init__(self,name="Silent Knight",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.stealth=True
        self.divine=True

class Silver_Hand_Regent(Minion):
    def __init__(self,name="Silver Hand Regent",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.inspire=True
         
    def trigger_inspire(self, hero_power=None):
        if hero_power.owner is self.owner:
            super(self.__class__,self).trigger_inspire()
            minion=Silver_Hand_Recruit(owner=self.owner)
            self.summon(minion)

class Evil_Heckler(Minion):
    def __init__(self,name="Evil Heckler",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True

class Frigid_Snobold(Minion):
    def __init__(self,name="Frigid Snobold",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.spell_damage_boost=1

class Maiden_of_the_Lake(Minion):
    def __init__(self,name="Maiden of the Lake",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def overriding_ongoing_effect(self,target):
        if isinstance(target, Hero_Power) and target.side==self.side:
            return {'cost':1}
        else:
            return {}    

class Refreshment_Vendor(Minion):
    def __init__(self,name="Refreshment Vendor",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        refreshment_vendor_animation(self)
        self.heal([self.owner,self.owner.opponent],[4,4])

class Tournament_Medic(Minion):
    def __init__(self,name="Tournament Medic",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.inspire=True
         
    def trigger_inspire(self, hero_power=None):
        if hero_power.owner is self.owner:
            super(self.__class__,self).trigger_inspire()
            self.heal([self.owner], [2])

class Clockwork_Knight(Minion):
    def __init__(self,name="Clockwork Knight",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(chooser=self,target="friendly minion",target_type="Mech",message="give +1/+1")
        return target
    
    def battlecry(self,target):
        mech_buff_animation(target)
        target.buff_stats(1,1) 
        
class Kvaldir_Raider(Minion):
    def __init__(self,name="Kvaldir Raider",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.inspire=True
         
    def trigger_inspire(self, hero_power=None):
        if hero_power.owner is self.owner:
            super(self.__class__,self).trigger_inspire()
            rage_buff_animation(self)
            self.buff_stats(2, 2)

class Muklas_Champion(Minion):
    def __init__(self,name="Mukla's Champion",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.inspire=True
         
    def trigger_inspire(self, hero_power=None):
        if hero_power.owner is self.owner:
            super(self.__class__,self).trigger_inspire()
            targets=self.friendly_minions()
            if self in targets:
                targets.remove(self)
            
            muklas_champion_animation(self,targets)
            for minion in targets:
                minion.buff_stats(1,1)

class Pit_Fighter(Minion):
    def __init__(self,name="Pit Fighter",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

class Captured_Jormungar(Minion):
    def __init__(self,name="Captured Jormungar",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
class North_Sea_Kraken(Minion):
    def __init__(self,name="North Sea Kraken",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(chooser=self,target="character",message="deal 4 damage")
        return target
    
    def battlecry(self,target):
        north_sea_kraken_animation(self, target)
        self.deal_damage([target], [4])
        
class Injured_Kvaldir(Minion):
    def __init__(self,name="Injured Kvaldir",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        self.deal_damage([self], [3])

class Argent_Watchman(Minion):
    def __init__(self,name="Argent Watchman",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.cannot_attack=True
        self.inspire=True
         
    def trigger_inspire(self, hero_power=None):
        if hero_power.owner is self.owner:
            super(self.__class__,self).trigger_inspire()
            self.temporary_effects["can attack"]=True

class Coliseum_Manager(Minion):
    def __init__(self,name="Coliseum Manager",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.inspire=True
         
    def trigger_inspire(self, hero_power=None):
        if hero_power.owner is self.owner:
            super(self.__class__,self).trigger_inspire()
            self.return_hand(reset=True)

class Fencing_Coach(Minion):
    def __init__(self,name="Fencing Coach",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def battlecry(self,target=None):
        mage_minion_animation(self)
        card=Fencing_Coach_Effect(owner=self.owner)
                                       
class Fencing_Coach_Effect(Enchantment):
    def __init__(self,name="Fencing Coach",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_events=[("use hero power",self.trigger_effect)]

    def ongoing_effect(self,target):
        if isinstance(target, Hero_Power) and target.side==self.side:
            return {'cost':-2}
        else:
            return {}            
        
    def trigger_effect(self, target):
        if isinstance(target, Hero_Power) and target.side==self.side:
            self.destroy()

class Lights_Champion(Minion):
    def __init__(self,name="Light's Champion",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def get_target(self):
        target=choose_target(chooser=self,target="minion",target_type="Demon", message="silence")
        return target
    
    def battlecry(self,target):
        self.silence(target)
        
class Saboteur(Minion): 
    def __init__(self,name="Saboteur",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def battlecry(self,target=None):
        saboteur_animation(self)
        card=Saboteur_Effect(owner=self.owner.opponent)
        
class Saboteur_Effect(Enchantment):
    def __init__(self,name="Saboteur",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_events.append(("start of turn",self.trigger_effect))
        self.activate=False

    def ongoing_effect(self,target):
        if isinstance(target, Hero_Power) and target.side==self.side and self.activate:
            return {'cost':5}
        else:
            return {}            
        
    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner:
            self.activate=True
                                                                                                                                                                                                                                                                                                                                                                    
class Armored_Warhorse(Minion):
    def __init__(self,name="Armored Warhorse",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        winner = self.joust("Minion")
        if winner is not None and winner.owner is self.owner:
            self.gain_charge()        

class Master_Jouster(Minion):
    def __init__(self,name="Master Jouster",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        winner = self.joust("Minion")
        if winner is not None and winner.owner is self.owner:
            self.gain_taunt()
            self.gain_divine_shield()  

class Mogors_Champion(Minion):
    def __init__(self,name="Mogor's Champion",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="attack"
        
    def trigger_effect(self,triggering_minion):
        if triggering_minion is self:
            self.attack_wrong_enemy(0.5)    

class Garrison_Commander(Minion):
    def __init__(self,name="Garrison Commander",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def overriding_ongoing_effect(self,target):
        if isinstance(target, Hero_Power) and target.side==self.side:
            return {'usage cap':2}
        else:
            return {}
        
class Master_of_Ceremonies(Minion):
    def __init__(self,name="Master of Ceremonies",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        if self.owner.has_spell_damage():
            light_buff_animation(self)
            self.buff_stats(2, 2)

class Crowd_Favorite(Minion):
    def __init__(self,name="Crowd Favorite",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="play a card"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.owner is self.owner and "Battlecry" in triggering_card.abilities:
            super(self.__class__,self).trigger_effect(triggering_card)
            light_buff_animation(self)
            self.buff_stats(1, 1)

class Twilight_Guardian(Minion):
    def __init__(self,name="Twilight Guardian",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        if self.owner.holding("Dragon"):
            light_buff_animation(self)
            self.buff_stats(1, 0)
            self.gain_taunt()

class Recruiter(Minion):
    def __init__(self,name="Recruiter",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.inspire=True
         
    def trigger_inspire(self, hero_power=None):
        if hero_power.owner is self.owner:
            super(self.__class__,self).trigger_inspire()
            minion=Squire(owner=self.owner,source=self.location)
            minion.hand_in()

class Grand_Crusader(Minion):
    def __init__(self,name="Grand Crusader",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        light_buff_animation(self)
        card = database.get_random_cards("[class] LIKE '%Paladin%", self.owner, 1)[0]
        card.initialize_location(self.location)
        card.hand_in()

class Kodorider(Minion):
    def __init__(self,name="Kodorider",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.inspire=True
         
    def trigger_inspire(self, hero_power=None):
        if hero_power.owner is self.owner:
            super(self.__class__,self).trigger_inspire()
            minion=War_Kodo(owner=self.owner)
            self.summon(minion)

class War_Kodo(Minion):
    def __init__(self,name="War Kodo",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
         
class Sideshow_Spelleater(Minion):
    def __init__(self,name="Sideshow Spelleater",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None): 
        sideshow_spelleater_animation(self)
        hero_power=getattr(card_collection,database.cleaned(self.owner.opponent.hero_power.name))(owner=self.owner)
        self.owner.gain_hero_power(hero_power)

class Frost_Giant(Minion):
    def __init__(self,name="Frost Giant",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def ongoing_effect(self,target):
        if target is self and target.board_area=="Hand":
            return {'cost':-self.owner.hero_power_count}
        else:
            return {} 

class Murloc_Tinyfin(Minion):
    def __init__(self,name="Murloc Tinyfin",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
class Huge_Toad(Minion):
    def __init__(self,name="Huge Toad",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        target_pool=self.enemy_characters()
        target=random.choice(target_pool)
        acidic_swamp_ooze_animation(self,target)
        self.deal_damage([target], [1]) 

class Jeweled_Scarab(Minion):
    def __init__(self,name="Jeweled Scarab",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        card=self.discover(filter_str="[cost]=3")
        if card is not None:
            card.hand_in()
            
class Tomb_Spider(Minion):
    def __init__(self,name="Tomb Spider",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        card=self.discover(filter_str="[race]='Beast'")
        if card is not None:
            card.hand_in()

class Gorillabot_A_3(Minion):
    def __init__(self,name="Gorillabot A-3",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        if self.owner.control("Mech"):
            card=self.discover(filter_str="[race]='Mech'")
            if card is not None:
                card.hand_in()

class Anubisath_Sentinel(Minion):
    def __init__(self,name="Anubisath Sentinel",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        target_pool=self.friendly_minions()
        if len(target_pool)>0:
            target=random.choice(target_pool)
            resurrect_animation(target)
            target.buff_stats(3,3)

class Fossilized_Devilsaur(Minion):
    def __init__(self,name="Fossilized Devilsaur",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        if self.owner.control("Beast"):
            self.gain_taunt()

class Ancient_Shade(Minion):
    def __init__(self,name="Ancient Shade",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        card=Ancient_Curse(owner=self.owner)
        card.initialize_location(self.location)
        card.shuffle_into_deck()

class Ancient_Curse(Spell):
    def __init__(self,name="Ancient Curse",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.casts_when_drawn=True
        
    def invoke(self,target=None):
        super(self.__class__,self).invoke()
        shadow_word_animation(self, self.owner)
        self.deal_damage([self.owner], [7])  

class Eerie_Statue(Minion):
    def __init__(self,name="Eerie Statue",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source) 
        self.cannot_attack=True

    def ongoing_effect(self,target):
        if target is self and len(self.all_minions())==1:
            return {'can attack':True}
        else:
            return {}      

class Summoning_Stone(Minion):
    def __init__(self,name="Summoning Stone",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="cast a spell"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.side==self.side:
            super(self.__class__,self).trigger_effect(triggering_card)
            minion=database.get_random_cards("[type]='Minion' AND [cost]="+str(triggering_card.get_current_cost()), self.owner, 1)[0]
            if minion is not None:
                self.summon(minion)

class Wobbling_Runts(Minion):
    def __init__(self,name="Wobbling Runts",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        minions=[Grumbly_Runt(owner=self.owner),Rascally_Runt(owner=self.owner),Wily_Runt(owner=self.owner)]
        for minion in minions:
            self.summon(minion)
     
class Grumbly_Runt(Minion):
    def __init__(self,name="Grumbly Runt",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Rascally_Runt(Minion):
    def __init__(self,name="Rascally Runt",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Wily_Runt(Minion):
    def __init__(self,name="Wily Runt",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Djinni_of_Zephyrs(Minion):
    def __init__(self,name="Djinni of Zephyrs",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="play a card"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.isSpell and triggering_card.side==self.side and triggering_card.target is not None and triggering_card.target.isMinion() and triggering_card.target.side==self.side and triggering_card.target is not self:
            super(self.__class__,self).trigger_effect(triggering_card)
            spell=getattr(card_collection,database.cleaned(triggering_card.name))(owner=triggering_card.owner)
            spell.invoke(self)
            
class Naga_Sea_Witch(Minion):
    def __init__(self,name="Naga Sea Witch",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source) 

    def overriding_ongoing_effect(self,target):
        if target.side==self.side and target.board_area=="Hand":
            return {'cost':5}
        else:
            return {} 

class Tentacle_of_NZoth(Minion):
    def __init__(self,name="Tentacle of N'Zoth",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        unstable_ghoul_animation(self)
        targets=self.all_minions()
        self.deal_damage(targets, [1]*len(targets))

class Zealous_Initiate(Minion):
    def __init__(self,name="Zealous Initiate",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        target=self.get_another_friendly_minion()
        buff_animation(target)
        target.buff_stats(1,1)
                    
class Beckoner_of_Evil(Minion):
    def __init__(self,name="Beckoner of Evil",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        self.buff_cthun(2,2)

class Bilefin_Tidehunter(Minion):
    def __init__(self,name="Bilefin Tidehunter",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        minion = Ooze_Bilefin_Tidehunter(owner=self.owner)
        self.summon(minion)

class Ooze_Bilefin_Tidehunter(Minion):
    def __init__(self,name="Ooze (Bilefin Tidehunter)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True

class Duskboar(Minion):
    def __init__(self,name="Duskboar",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

class Twilight_Geomancer(Minion):
    def __init__(self,name="Twilight Geomancer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        
    def battlecry(self,target=None):
        cthun=self.buff_cthun(0,0)
        if cthun is not None:
            cthun.has_taunt=True
        
class Twisted_Worgen(Minion):
    def __init__(self,name="Twisted Worgen",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.stealth=True        

class Amgam_Rager(Minion):
    def __init__(self,name="Am'gam_Rager",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

class Spawn_of_NZoth(Minion):
    def __init__(self,name="Spawn of N'Zoth",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        targets=self.friendly_minions()
        buff_multiple_animation(self, targets)
        for minion in targets:
            minion.buff_stats(1,1)

class Squirming_Tentacle(Minion):
    def __init__(self,name="Squirming Tentacle",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True

class Twilight_Elder(Minion):
    def __init__(self,name="Twilight Elder",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source) 
        self.trigger_event_type="end of turn"
       
    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner:
            super(self.__class__,self).trigger_effect(triggering_player)
            self.buff_cthun(1, 1)

class Aberrant_Berserker(Minion):
    def __init__(self,name="Aberrant Berserker",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.enrage=True
        
    def ongoing_effect(self,target):
        if target is self and target.damaged():
            return {'atk':2}
        else:
            return {}

class CThuns_Chosen(Minion):
    def __init__(self,name="C'Thun's Chosen",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.divine_shield=True
        
    def battlecry(self,target=None):
        self.buff_cthun(2,2)

class Evolved_Kobold(Minion):
    def __init__(self,name="Evolved Kobold",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.spell_damage_boost=2

class Infested_Tauren(Minion):
    def __init__(self,name="Infested Tauren",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        
    def deathrattle(self):
        minion=Slime_Infested_Tauren(owner=self.owner)
        self.summon(minion)

class Slime_Infested_Tauren(Minion):
    def __init__(self,name="Slime (Infested Tauren)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
             
class Polluted_Hoarder(Minion):
    def __init__(self,name="Polluted Hoarder",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        self.owner.draw()

class Cult_Apothecary(Minion):
    def __init__(self,name="Cult Apothecary",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        self.heal([self.owner],[2*len(self.enemy_minions())])

class Psych_o_Tron(Minion):
    def __init__(self,name="Psych-o-Tron",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        self.divine_shield=True

class Nerubian_Prophet(Minion):
    def __init__(self,name="Nerubian Prophet",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source) 
        self.trigger_event_type="start of turn"
       
    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner and self.board_area=="Hand":
            self.modify_cost(-1)

class Bog_Creeper(Minion):
    def __init__(self,name="Bog Creeper",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True

class Grotesque_Dragonhawk(Minion):
    def __init__(self,name="Grotesque Dragonhawk",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.windfury=True

class Eldritch_Horror(Minion):
    def __init__(self,name="Eldritch Horror",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

class Faceless_Behemoth(Minion):
    def __init__(self,name="Faceless Behemoth",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

class Disciple_of_CThun(Minion):
    def __init__(self,name="Disciple of C'Thun",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(chooser=self,target="character",message="deal 2 damage")
        return target
    
    def battlecry(self,target):
        murkspark_eel_animation(self, target)
        self.deal_damage([target], [2])
        self.buff_cthun(2, 2)

class Silithid_Swarmer(Minion):
    def __init__(self,name="Silithid Swarmer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source) 
        self.cannot_attack=True

    def ongoing_effect(self,target):
        if target is self and self.owner.attacked:
            return {'can attack':True}
        else:
            return {}      

class Blackwater_Pirate(Minion):
    def __init__(self,name="Blackwater Pirate",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def ongoing_effect(self,target):
        if isinstance(target,Weapon) and target.side==self.side and target.board_area=="Hand":
            return {'cost':-2}
        else:
            return {}  

class Eater_of_Secrets(Minion):
    def __init__(self,name="Eater of Secrets",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def battlecry(self,target):
        n=len(self.enemy_secrets())
        for secret in self.enemy_secrets():
            secret.destroy()
        buff_animation(self)
        self.buff_stats(n, n)
        
class Midnight_Drake(Minion):
    def __init__(self,name="Midnight Drake",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        handsize=len(self.owner.hand)
        self.buff_stats(handsize,0)

class Corrupted_Healbot(Minion):
    def __init__(self,name="Corrupted Healbot",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        zombie_chow_animation(self)
        self.heal([self.owner.opponent],[8])

class Corrupted_Seer(Minion):
    def __init__(self,name="Corrupted Seer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        targets=self.all_minions_except("Murloc")
        abomination_animation(self)
        self.deal_damage(targets, [2]*len(targets))

class Skeram_Cultist(Minion):
    def __init__(self,name="Skeram Cultist",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        self.buff_cthun(2,2)

class Doomcaller(Minion):
    def __init__(self,name="Doomcaller",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        for minion in self.owner.grave:
            if isinstance(minion,CThun):
                minion.shuffle_into_deck()
                break
            
        self.buff_cthun(2,2)

class Faceless_Shambler(Minion):
    def __init__(self,name="Faceless Shambler",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True

    def get_target(self):
        target=choose_target(chooser=self,target="friendly minion",message="copy its Attack and Health")
        return target
            
    def battlecry(self,target=None):
        self.set_stats(target.current_atk, target.current_hp)

class Cyclopian_Horror(Minion):
    def __init__(self,name="Cyclopian Horror",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        
    def battlecry(self,target=None):
        self.buff_stats(0, len(self.enemy_minions()))

class Twilight_Summoner(Minion):
    def __init__(self,name="Twilight Summoner",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        minion=Faceless_Destroyer(owner=self.owner)
        self.summon(minion)

class Faceless_Destroyer(Minion):
    def __init__(self,name="Faceless Destroyer",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Crazed_Worshipper(Minion):
    def __init__(self,name="Crazed Worshipper",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        self.trigger_event_type="minion damage"
        
    def trigger_effect(self,triggering_entity):
        if triggering_entity[0] is self:
            super(self.__class__,self).trigger_effect(self)
            self.buff_cthun(1, 1)

class Darkspeaker(Minion):
    def __init__(self,name="Darkspeaker",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(chooser=self,target="friendly minion",message="swap stats")
        return target
            
    def battlecry(self,target=None):
        self.temp_atk,self.temp_hp,target.temp_atk,target.temp_hp = target.temp_atk,target.temp_hp,self.temp_atk,self.temp_hp
        self.current_atk,self.current_hp,target.current_atk,target.current_hp = target.current_atk,target.current_hp,self.current_atk,self.current_hp

class Validated_Doomsayer(Minion):
    def __init__(self,name="Validated Doomsayer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source) 
        self.trigger_event_type="start of turn"
       
    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner:
            super(self.__class__,self).trigger_effect(triggering_player)
            self.set_stats(atk=7)

class Ancient_Harbinger(Minion):
    def __init__(self,name="Ancient Harbinger",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source) 
        self.trigger_event_type="start of turn"
       
    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner:
            super(self.__class__,self).trigger_effect(triggering_player)
            card=self.owner.search_card_based_cost(self.owner.deck.cards,card_type="Minion",cost=10)
            if card is not None:
                self.owner.draw(target=card)

class Scaled_Nightmare(Minion):
    def __init__(self,name="Scaled Nightmare",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source) 
        self.trigger_event_type="start of turn"
       
    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner:
            super(self.__class__,self).trigger_effect(triggering_player)
            self.buff_stats(self.current_atk, 0)

class Blood_of_The_Ancient_One(Minion):
    def __init__(self,name="Blood of The Ancient One",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source) 
        self.trigger_event_type="start of turn"
       
    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner:
            super(self.__class__,self).trigger_effect(triggering_player)
            for minion in self.friendly_minions():
                if minion is not self and isinstance(minion,Blood_of_The_Ancient_One):
                    self.destroy()
                    minion.destroy()
                    destroy_multiple_animation([self,minion])
                    ancient_one=The_Ancient_One(owner=self.owner,source="board")
                    self.owner.recruit(ancient_one)
                    the_ancient_one_animation(ancient_one)
                    break
                
class The_Ancient_One(Minion):
    def __init__(self,name="The Ancient One",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source) 

class Arcane_Anomaly(Minion):
    def __init__(self,name="Arcane Anomaly",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="cast a spell"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.owner is self.owner:
            super(self.__class__,self).trigger_effect(triggering_card)
            buff_animation(self)
            self.buff_stats(0, 1)

class Runic_Egg(Minion):
    def __init__(self,name="Runic Egg",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        self.owner.draw()

class Netherspite_Historian(Minion):
    def __init__(self,name="Netherspite Historian",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        if self.owner.holding("Dragon"):
            card=self.discover(filter_str="[race]='Dragon'")
            if card is not None:
                card.hand_in()

class Pompous_Thespian(Minion):
    def __init__(self,name="Pompous Thespian",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True

class Pantry_Spider(Minion):
    def __init__(self,name="Pantry Spider",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        minion = Cellar_Spider(owner=self.owner)
        self.summon(minion)

class Cellar_Spider(Minion):
    def __init__(self,name="Cellar Spider",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        
class Violet_Illusionist(Minion):
    def __init__(self,name="Violet Illusionist",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def ongoing_effect(self,target):
        if target is self.owner and target.board.control==target.side:
            return {'immune':True}
        else:
            return {}

class Zoobot(Minion):
    def __init__(self,name="Zoobot",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        targets=[]
        for race in ["Beast","Dragon","Murloc"]:
            target_pool=self.friendly_minions(race)
            if len(target_pool)>0:
                targets.append(random.choice(target_pool))
        
        muklas_champion_animation(self,targets)
        light_buff_multiple_animation(self, targets)        
        for minion in targets:
            minion.buff_stats(1,1)

class Arcanosmith(Minion):
    def __init__(self,name="Arcanosmith",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        minion = Animated_Shield(owner=self.owner)
        self.summon(minion)

class Animated_Shield(Minion):
    def __init__(self,name="Animated Shield",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True

class Menagerie_Magician(Minion):
    def __init__(self,name="Menagerie Magician",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        targets=[]
        for race in ["Beast","Dragon","Murloc"]:
            target_pool=self.friendly_minions(race)
            if len(target_pool)>0:
                targets.append(random.choice(target_pool))
        
        muklas_champion_animation(self,targets)
        light_buff_multiple_animation(self, targets)        
        for minion in targets:
            minion.buff_stats(2,2)

class Avian_Watcher(Minion):
    def __init__(self,name="Avian Watcher",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        if len(self.owner.secrets)>0:
            light_buff_animation(self)
            self.buff_stats(1, 1)
            self.gain_taunt()

class Book_Wyrm(Minion):
    def __init__(self,name="Book Wyrm",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def get_target(self):
        target=choose_target(self, target="enemy minion", target_type="get_current_atk __le__ 2", message="destroy")
        return target
    
    def battlecry(self,target):
        if self.owner.holding("Dragon"):
            silence_animation(self)
            target.destroy()

class Moat_Lurker(Minion):
    def __init__(self,name="Moat Lurker",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def get_target(self):
        target=choose_target(self, target="minion", message="destroy")
        return target
    
    def battlecry(self,target):
        target.destroy()
        self.attachments["incorporate"]=target
        
    def deathrattle(self):
        if "incorporate" in self.attachments:
            minion=getattr(card_collection,database.cleaned(self.attachments["incorporate"].name))(owner=self.attachments["incorporate"].owner)
            self.summon(minion)

class Arcane_Giant(Minion):
    def __init__(self,name="Arcane Giant",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def ongoing_effect(self,target):
        if target is self and target.board_area=="Hand":
            count=0
            for i in range(self.owner.turn):
                for card in self.owner.played_cards[i+1]:
                    if card.isSpell:
                        count+=1
            return {'cost':-count}
        else:
            return {} 

class Mistress_of_Mixtures(Minion):
    def __init__(self,name="Mistress of Mixtures",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        refreshment_vendor_animation(self)
        self.heal([self.owner,self.owner.opponent],[2,2])

class Blowgill_Sniper(Minion):
    def __init__(self,name="Blowgill Sniper",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(chooser=self,target="character",message="deal 1 damage")
        return target
    
    def battlecry(self,target):
        elven_archer_animation(self, target)
        self.deal_damage([target], [1])

class Friendly_Bartender(Minion):
    def __init__(self,name="Friendly Bartender",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source) 
        self.trigger_event_type="end of turn"
       
    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner:
            super(self.__class__,self).trigger_effect(triggering_player)
            youthful_brewmaster_animation(self, self.owner)
            self.heal([self.owner],[1])

class Gadgetzan_Socialite(Minion):
    def __init__(self,name="Gadgetzan Socialite",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def get_target(self):
        target=choose_target(chooser=self,target="character",message="restore 2 health")
        return target
    
    def battlecry(self,target):
        lesser_heal_animation(self, target)
        self.heal([target],[2])

class Backstreet_Leper(Minion):
    def __init__(self,name="Backstreet Leper",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        leper_gnome_animation(self)
        self.deal_damage([self.owner.opponent], [2])

class Hired_Gun(Minion):
    def __init__(self,name="Hired Gun",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True

class Street_Trickster(Minion):
    def __init__(self,name="Street Trickster",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.spell_damage_boost=1

class Toxic_Sewer_Ooze(Minion):
    def __init__(self,name="Toxic Sewer Ooze",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def battlecry(self,target=None):
        if self.owner.opponent.has_weapon():
            acidic_swamp_ooze_animation(self,self.owner.opponent.weapon)
            self.owner.opponent.weapon.decrease_durability()

class Daring_Reporter(Minion):
    def __init__(self,name="Daring Reporter",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="draw a card"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.side==-self.side:
            super(self.__class__,self).trigger_effect(triggering_card)
            light_buff_animation(self)
            self.buff_stats(1, 1)

class Hozen_Healer(Minion):
    def __init__(self,name="Hozen Healer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def get_target(self):
        target=choose_target(chooser=self,target="minion",message="restore to full health")
        return target
    
    def battlecry(self,target):
        lesser_heal_animation(self, target)
        self.heal([target],[target.temp_hp-target.current_hp])

class Kooky_Chemist(Minion):
    def __init__(self,name="Kooky Chemist",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(chooser=self,target="minion",message="swap attack and health")
        return target
    
    def battlecry(self,target):
        crazed_alchemist_animation(self,target)
        target.swap_stats()

class Naga_Corsair(Minion):
    def __init__(self,name="Naga Corsair",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        if self.owner.has_weapon():
            self.owner.weapon.buff_stats(1,0)

class Tanaris_Hogchopper(Minion):
    def __init__(self,name="Tanaris Hogchopper",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        if self.owner.opponent.empty_handed():
            gain_charge_animation(self)
            self.gain_charge()

class Worgen_Greaser(Minion):
    def __init__(self,name="Worgen Greaser",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

class Grook_Fu_Master(Minion):
    def __init__(self,name="Grook Fu Master",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.windfury=True

class Red_Mana_Wyrm(Minion):
    def __init__(self,name="Red Mana Wyrm",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="cast a spell"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.owner is self.owner:
            super(self.__class__,self).trigger_effect(triggering_card)
            buff_animation(self)
            self.buff_stats(2, 0)

class Streetwise_Investigator(Minion):
    def __init__(self,name="Streetwise Investigator",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
    
    def battlecry(self,target):
        for minion in self.enemy_minions():
            minion.has_stealth=False

class Ancient_of_Blossoms(Minion):
    def __init__(self,name="Ancient of Blossoms",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True

class Big_Time_Racketeer(Minion):
    def __init__(self,name="Big-Time Racketeer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        minion = Little_Friend(owner=self.owner)
        self.summon(minion)
                     
class Little_Friend(Minion):
    def __init__(self,name='"Little Friend"',owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        
class Small_Time_Buccaneer(Minion):
    def __init__(self,name="Small-Time Buccanee",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def ongoing_effect(self,target):
        if target is self and self.owner.has_weapon():
            return {'atk':2}
        else:
            return {}

class Backroom_Bouncer(Minion):
    def __init__(self,name="Backroom_Bouncer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="minion dies"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.side==self.side and triggering_card is not self:
            super(self.__class__,self).trigger_effect(triggering_card)
            self.buff_stats(1, 0)

class Bomb_Squad(Minion):
    def __init__(self,name="Bomb Squad",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(chooser=self,target="enemy minion",message="deal 5 damage")
        return target
    
    def battlecry(self,target):
        bomb_lobber_animation(self, target)
        self.deal_damage([target], [5])
        
    def deathrattle(self):
        Minion.deathrattle(self)
        bomb_lobber_animation(self, self.owner)
        self.deal_damage([self.owner], [5])

class Doppelgangster(Minion):
    def __init__(self,name="Doppelgangster",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        minion = Doppelgangster_first_copy(owner=self.owner)
        self.summon(minion,left=1)
        minion = Doppelgangster_second_copy(owner=self.owner)
        self.summon(minion)
                     
class Doppelgangster_first_copy(Minion):
    def __init__(self,name="Doppelgangster (first copy)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        minion = Doppelgangster(owner=self.owner)
        self.summon(minion,left=1)
        minion = Doppelgangster_second_copy(owner=self.owner)
        self.summon(minion)

class Doppelgangster_second_copy(Minion):
    def __init__(self,name="Doppelgangster (second copy)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

    def battlecry(self,target=None):
        minion = Doppelgangster_first_copy(owner=self.owner)
        self.summon(minion,left=1)
        minion = Doppelgangster(owner=self.owner)
        self.summon(minion)

class Second_Rate_Bruiser(Minion):
    def __init__(self,name="Second-Rate Bruiser",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        
    def ongoing_effect(self,target):
        if target is self and len(self.enemy_minions())>=3 and self.board_area=="Hand":
            return {'cost':-2}
        else:
            return {}

class Spiked_Hogrider(Minion):
    def __init__(self,name="Spiked Hogrider",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        if self.owner.opponent.is_taunted():
            gain_charge_animation(self)
            self.gain_charge()

class Weasel_Tunneler(Minion):
    def __init__(self,name="Weasel Tunneler",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def destroy(self,skip_animation=False,skip_deathrattle=False):
        for deathrattle in self.deathrattles:
            deathrattle[0]()

        if self.board_area!="Deck":
            super(self.__class__,self).destroy(skip_animation=skip_animation,skip_deathrattle=True)
     
    def deathrattle(self):
        if self.board_area=="Board":
            self.shuffle_into_deck(self.owner.opponent.deck)

class Dirty_Rat(Minion):
    def __init__(self,name="Dirty Rat",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True

    def battlecry(self,target):
        minion = self.owner.opponent.search_card(self.owner.opponent.hand,card_type="Minion")
        if minion is not None:
            self.owner.opponent.put_into_battlefield(minion)

class Blubber_Baron(Minion):
    def __init__(self,name="Blubber Baron",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="summon a minion"
        
    def trigger_effect(self,triggering_minion):
        if self.board_area=="Hand" and triggering_minion.side==self.side and "Battlecry" in triggering_minion.abilities:
            buff_hand_animation(self.owner, [self])
            self.buff_stats(1, 1)

class Fel_Orc_Soulfiend(Minion):
    def __init__(self,name="Fel Orc Soulfiend",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source) 
        self.trigger_event_type="start of turn"
       
    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner:
            super(self.__class__,self).trigger_effect(triggering_player)
            self.deal_damage([self], [2])

class Burgly_Bully(Minion):
    def __init__(self,name="Burgly Bully",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="cast a spell"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.side==-self.side:
            super(self.__class__,self).trigger_effect(triggering_card)
            self.owner.get_coin()

class Defias_Cleaner(Minion):
    def __init__(self,name="Defias Cleaner",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
      
    def get_target(self):
        target=choose_target(chooser=self,target="minion",target_type="has_deathrattle attr",message="silence")
        return target
    
    def battlecry(self,target):
        self.silence(target)

class Fight_Promoter(Minion):
    def __init__(self,name="Fight Promoter",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
    
    def battlecry(self,target):
        trigger=False
        for minion in self.friendly_minions():
            if minion.get_current_hp()>=6:
                trigger=True
        
        if trigger:
            self.owner.draw(2)

class Leatherclad_Hogleader(Minion):
    def __init__(self,name="Leatherclad Hogleader",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        if len(self.owner.opponent.hand)>=6:
            gain_charge_animation(self)
            self.gain_charge()

class Wind_up_Burglebot(Minion):
    def __init__(self,name="Wind-up Burglebot",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="after attack"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card is self and self.target.isMinion() and self.get_current_hp()>=0:
            super(self.__class__,self).trigger_effect(triggering_card)
            self.owner.draw()

class Emerald_Reaver(Minion): 
    def __init__(self,name="Emerald Reaver",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        emerald_reaver_animation(self)
        self.deal_damage([self.owner.opponent,self.owner], [1,1])

class Fire_Fly(Minion): 
    def __init__(self,name="Fire Fly",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        minion=Flame_Elemental(owner=self.owner,source=self.location)
        minion.hand_in()

class Flame_Elemental(Minion): 
    def __init__(self,name="Flame Elemental",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Glacial_Shard(Minion):
    def __init__(self,name="Glacial Shard",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(chooser=self,target="character",message="freeze")
        return target
    
    def battlecry(self,target):
        glacial_shard_animation(self, target)
        target.get_frozen()

class Ravasaur_Runt(Minion):
    def __init__(self,name="Ravasaur Runt",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def battlecry(self,target=None):
        if len(self.friendly_minions())>=2:
            self.adapt()
                             
class Plant(Minion):
    def __init__(self,name="Plant",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        
class Rockpool_Hunter(Minion):
    def __init__(self,name="Rockpool Hunter",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(chooser=self,target="friendly minion",target_type="Murloc",message="+2/+2 and Taunt")
        return target
    
    def battlecry(self,target):
        target.buff_stats(1,1)

class Stubborn_Gastropod(Minion):
    def __init__(self,name="Stubborn Gastropod",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        self.poisonous=True

class Volatile_Elemental(Minion):
    def __init__(self,name="Volatile Elemental",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        target_pool=self.enemy_minions()
        target=random.choice(target_pool)
        murkspark_eel_animation(self, target)
        self.deal_damage([target], [3]) 

class Eggnapper(Minion):
    def __init__(self,name="Eggnapper",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        for i in range(2):
            minion=Raptor_1_1(owner=self.owner)
            self.summon(minion,speed=50)
            
class Raptor_1_1(Minion):
    def __init__(self,name="Raptor (1-1)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Giant_Wasp(Minion):
    def __init__(self,name="Giant Wasp",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.stealth=True
        self.poisonous=True

class Igneous_Elemental(Minion):
    def __init__(self,name="Igneous Elemental",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        for i in range(2):
            minion=Flame_Elemental(owner=self.owner,source=self.location)
            minion.hand_in()

class Primalfin_Lookout(Minion):
    def __init__(self,name="Primalfin Lookout",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        if self.owner.control("Murloc"):
            card=self.discover(filter_str="[race]='Murloc'")
            if card is not None:
                card.hand_in()

class Pterrodax_Hatchling(Minion):
    def __init__(self,name="Pterrodax Hatchling",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        self.adapt()

class Tar_Creeper(Minion):
    def __init__(self,name="Tar Creeper",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        
    def ongoing_effect(self,target):
        if target is self and self.owner.board.control==-self.side:
            return {'atk':2}
        else:
            return {}

class Thunder_Lizard(Minion):
    def __init__(self,name="Thunder Lizard",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        if self.owner.played_before("Elemental"):
            self.adapt()

class Fire_Plume_Phoenix(Minion):
    def __init__(self,name="Fire Plume Phoenix",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(chooser=self,target="character",message="deal 2 damage")
        return target
    
    def battlecry(self,target):
        fire_bolt_animation(self, target)
        self.deal_damage([target], [2])

class Stegodon(Minion):
    def __init__(self,name="Stegodon",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True

class Nesting_Roc(Minion):
    def __init__(self,name="Nesting Roc",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def battlecry(self,target=None):
        if len(self.friendly_minions())>=2:
            self.gain_taunt()

class Sabretooth_Stalker(Minion):
    def __init__(self,name="Sabretooth Stalker",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.stealth=True

class Sated_Threshadon(Minion):
    def __init__(self,name="Sated Threshadon",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        for i in range(3):
            minion=Primalfin(owner=self.owner)
            self.summon(minion,speed=50)

class Primalfin(Minion):
    def __init__(self,name="Primalfin",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Stormwatcher(Minion):
    def __init__(self,name="Stormwatcher",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.windfury=True

class Giant_Mastodon(Minion):
    def __init__(self,name="Giant Mastodon",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True

class Ultrasaur(Minion):
    def __init__(self,name="Ultrasaur",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

class Golakka_Crawler(Minion):
    def __init__(self,name="Golakka Crawler",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(chooser=self,target="minion",target_type="Pirate",message="destroy and gain +1/+1")
        return target
    
    def battlecry(self,target):
        target.destroy()
        self.buff_stats(1, 1)

class Devilsaur_Egg(Minion):
    def __init__(self,name="Devilsaur Egg",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        minion=Devilsaur_Devilsaur_Egg(owner=self.owner)
        self.summon(minion)
                    
class Devilsaur_Devilsaur_Egg(Minion):
    def __init__(self,name="Devilsaur (Devilsaur Egg)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Humongous_Razorleaf(Minion):
    def __init__(self,name="Humongous Razorleaf",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source) 
        self.cannot_attack=True

class Vicious_Fledgling(Minion):
    def __init__(self,name="Vicious Fledgling",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="after attack"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card is self and self.target.isHero():
            super(self.__class__,self).trigger_effect(triggering_card)
            self.adapt()
                    
class Stonehill_Defender(Minion):
    def __init__(self,name="Stonehill Defender",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        
    def battlecry(self,target=None):
        card=self.discover(by_ability="Taunt")
        if card is not None:
            card.hand_in()

class Tolvir_Stoneshaper(Minion):
    def __init__(self,name="Tol'vir Stoneshaper",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        if self.owner.played_before("Elemental"):
            self.gain_taunt()
            self.gain_divine_shield()

class Servant_of_Kalimos(Minion):
    def __init__(self,name="Servant of Kalimos",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        if self.owner.played_before("Elemental"):
            card=self.discover(filter_str="[race]='Elemental'")

class Frozen_Crusher(Minion):
    def __init__(self,name="Frozen Crusher",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="after attack"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card is self:
            super(self.__class__,self).trigger_effect(triggering_card)
            self.get_frozen()
                                    
class Volcanosaur(Minion):
    def __init__(self,name="Volcanosaur",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
    
    def battlecry(self,target=None):
        self.adapt(2) 

class Emerald_Hive_Queen(Minion):
    def __init__(self,name="Emerald Hive Queen",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def ongoing_effect(self,target):
        if target.isMinion() and target.side==self.side and target.board_area=="Hand" and target is not self:
            return {'cost':2}
        else:
            return {}  

class Gluttonous_Ooze(Minion):
    def __init__(self,name="Gluttonous Ooze",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def battlecry(self,target=None):
        if self.owner.opponent.has_weapon():
            acidic_swamp_ooze_animation(self,self.owner.opponent.weapon)
            self.owner.increase_shield(self.owner.opponent.weapon.get_current_atk())
            self.owner.opponent.weapon.destroy()  

class Bright_Eyed_Scout(Minion):
    def __init__(self,name="Bright-Eyed Scout",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        card=self.owner.draw()
        if card is not None:
            card.current_cost=5

class Gentle_Megasaur(Minion):
    def __init__(self,name="Gentle Megasaur",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        minions=self.friendly_minions(race="Murloc")
        if len(minions)>0:
            choice=minions[0].adapt()
            minions.remove(minions[0])
            for minion in minions:
                minion.adapt(choice=choice)
        
class Bittertide_Hydra(Minion):
    def __init__(self,name="Bittertide Hydra",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="minion damage"
        
    def trigger_effect(self,triggering_entity):
        if triggering_entity[0] is self:
            super(self.__class__,self).trigger_effect(self)
            self.deal_damage([self.owner],[3])

class Blazecaller(Minion):
    def __init__(self,name="Blazecaller",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=None
        if self.owner.played_before("Elemental"):
            target=choose_target(chooser=self,target="character",message="deal 5 damage")
        return target
    
    def battlecry(self,target):
        fire_bolt_animation(self, target)
        self.deal_damage([target], [5])

class Charged_Devilsaur(Minion):
    def __init__(self,name="Charged Devilsaur",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.charge=True

    def battlecry(self,target):
        self.temporary_effects["cannot attack hero"]=True
            
class Primordial_Drake(Minion):
    def __init__(self,name="Primordial Drake",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        
    def battlecry(self,target=None):
        unstable_ghoul_animation(self)
        targets=self.all_minions()
        self.deal_damage(targets, [2]*len(targets))

class Tortollan_Primalist(Minion):
    def __init__(self,name="Tortollan Primalist",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        card=self.discover(filter_str="[type]='Spell'")
        if card is not None:
            card.cast_on_random_target()

class Snowflipper_Penguin(Minion):
    def __init__(self,name="Snowflipper Penguin",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

class Acherus_Veteran(Minion):
    def __init__(self,name="Acherus Veteran",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(chooser=self,target="friendly minion",message="give +1 Attack")
        return target
    
    def battlecry(self,target):
        target.buff_stats(1,0)

class Deadscale_Knight(Minion):
    def __init__(self,name="Deadscale Knight",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.lifesteal=True

class Wretched_Tiller(Minion):
    def __init__(self,name="Wretched Tiller",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="attack"
        
    def trigger_effect(self,triggering_minion):
        if triggering_minion is self:
            super(self.__class__,self).trigger_effect(triggering_minion)
            charge_shot_animation(self, self.owner.opponent)
            self.deal_damage([self.owner.opponent],[3])

class Fallen_Sun_Cleric(Minion):
    def __init__(self,name="Fallen Sun Cleric",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(chooser=self,target="friendly minion",message="give +1/+1")
        return target
    
    def battlecry(self,target):
        target.buff_stats(1,1)

class Tainted_Zealot(Minion):
    def __init__(self,name="Tainted Zealot",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.divine_shield=True
        self.spell_damage_boost=1

class Tuskarr_Fisherman(Minion):
    def __init__(self,name="Tuskarr Fisherman",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(chooser=self,target="friendly minion",message="give Spell Damage +1")
        return target
    
    def battlecry(self,target):
        target.gain_spell_damage_boost(1)

class Hyldnir_Frostrider(Minion):
    def __init__(self,name="Hyldnir Frostrider",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
    
    def battlecry(self,target):
        frost_nova_animation(self)
        for minion in self.friendly_minions():
            minion.get_frozen()
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              
class Deathspeaker(Minion):
    def __init__(self,name="Deathspeaker",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(chooser=self,target="friendly minion",message="give immune")
        return target
    
    def battlecry(self,target):
        target.temporary_effects['immune']=True

class Vryghoul(Minion):
    def __init__(self,name="Vryghoul",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        if self.owner.board.control==-self.side:
            minion=Ghoul(owner=self.owner)
            self.summon(minion)
            
class Ghoul(Minion):
    def __init__(self,name="Ghoul",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Grave_Shambler(Minion):
    def __init__(self,name="Grave Shambler",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="weapon destroyed"
        
    def trigger_effect(self,triggering_weapon):
        if triggering_weapon.side==self.side:
            super(self.__class__,self).trigger_effect(self)
            buff_animation(self)
            self.buff_stats(1, 1)

class Grim_Necromancer(Minion):
    def __init__(self,name="Grim Necromancer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def battlecry(self,target):
        for i in range(2):
            minion=Skeleton_1_1(owner=self.owner)
            self.summon(minion,left=(-1)**i,speed=40)

class Skeleton_1_1(Minion):
    def __init__(self,name="Skeleton (1-1)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Night_Howler(Minion):
    def __init__(self,name="Night Howler",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="minion damage"
        
    def trigger_effect(self,triggering_entity):
        if triggering_entity[0] is self:
            super(self.__class__,self).trigger_effect(self)
            self.buff_stats(2, 0)

class Wicked_Skeleton(Minion):
    def __init__(self,name="Wicked Skeleton",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def battlecry(self,target):
        n=self.owner.get_num_minions_died()
        light_buff_animation(self)
        self.buff_stats(n, n)

class Bloodworm(Minion):
    def __init__(self,name="Bloodworm",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.lifesteal=True

class Cobalt_Scalebane(Minion):
    def __init__(self,name="Cobalt Scalebane",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source) 
        self.trigger_event_type="end of turn"
       
    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner:
            super(self.__class__,self).trigger_effect(triggering_player)
            minion=self.get_another_friendly_minion()
            if minion is not None:
                cobalt_scalebane_animation(self,minion)
                minion.buff_stats(3,0)

class Skelemancer(Minion):
    def __init__(self,name="Skelemancer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        if self.owner.board.control==-self.side:
            minion=Skeletal_Frayer(owner=self.owner)
            self.summon(minion)
            
class Skeletal_Frayer(Minion):
    def __init__(self,name="Skeletal Frayer",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Sunborne_Valkyr(Minion):
    def __init__(self,name="Sunborne Val'kyr",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        targets=self.adjacent_minions()
        light_buff_multiple_animation(self, targets)
        for target in targets:
            target.buff_stats(0,2)

class Venomancer(Minion):
    def __init__(self,name="Venomancer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source) 
        self.poisonous=True

class Spellweaver(Minion):
    def __init__(self,name="Spellweaver",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source) 
        self.spell_damage_boost=2

class Necrotic_Geist(Minion):
    def __init__(self,name="Necrotic Geist",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="minion dies"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.side==self.side and triggering_card is not self:
            super(self.__class__,self).trigger_effect(triggering_card)
            minion=Ghoul(owner=self.owner)
            self.summon(minion)

class Bonemare(Minion):
    def __init__(self,name="Bonemare",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.tags.append("Targeted")

    def get_target(self):
        target=choose_target(chooser=self,target="friendly minion",message="give +4/+4 and Taunt")
        return target
    
    def battlecry(self,target):
        target.buff_stats(4,4)
        target.gain_taunt()

class Happy_Ghoul(Minion):
    def __init__(self,name="Happy Ghoul",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def overriding_ongoing_effect(self,target):
        if target is self and self.owner.healed:
            return {'cost':0}
        else:
            return {}

class Mindbreaker(Minion):
    def __init__(self,name="Mindbreaker",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def come_on_board(self):
        super(self.__class__,self).come_on_board()
        for hero_power in [self.owner.hero_power,self.owner.opponent.hero_power]:
            disable_hero_power_animation(hero_power)
        
    def ongoing_effect(self,target):
        if isinstance(target,Hero_Power):
            return {'disable hero power':True}
        else:
            return {}

class Shallow_Gravedigger(Minion):
    def __init__(self,name="Shallow Gravedigger",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        minion = database.get_random_cards(owner=self.owner,k=1,by_ability="Deathrattle")[0]
        minion.initialize_location(self.location)
        minion.hand_in()

class Keening_Banshee(Minion):
    def __init__(self,name="Keening Banshee",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="play a card"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.owner is self.owner:
            super(self.__class__,self).trigger_effect(triggering_card)
            for i in range(3):
                card=self.owner.deck.top()
                if not card.isFatigue():
                    card.burn()

class Phantom_Freebooter(Minion):
    def __init__(self,name="Phantom Freebooter",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        if self.owner.has_weapon():
            self.buff_stats(self.owner.weapon.get_current_atk(), self.owner.weapon.current_durability)

class Saronite_Chain_Gang(Minion):
    def __init__(self,name="Saronite Chain_Gang",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        
    def battlecry(self,target=None):
        minion = Saronite_Chain_Gang(owner=self.owner)
        self.summon(minion)

class Ticking_Abomination(Minion):
    def __init__(self,name="Ticking Abomination",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        unstable_ghoul_animation(self)
        targets=self.friendly_minions()
        self.deal_damage(targets, [5]*len(targets))

class Corpse_Raiser(Minion):
    def __init__(self,name="Corpse Raiser",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        minion=choose_target(chooser=self,target="friendly minion",message="give Deathrattle:Resummon this minion")
        return minion
    
    def battlecry(self,target=None):
        target.deathrattles.append([MethodType(Ancestral_Spirit.deathrattle,target),"resummon this minion"])
        target.has_deathrattle=True

class Bone_Drake(Minion):
    def __init__(self,name="Bone Drake",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        card = database.get_random_cards("[race]='Dragon'", self.owner, 1)[0]
        card.initialize_location(self.location)
        card.hand_in()

class Runeforge_Haunter(Minion):
    def __init__(self,name="Runeforge Haunter",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def ongoing_effect(self,target):
        if target.isWeapon() and target.side==self.side and self.owner.board.control==self.side:
            return {'durability immune':True}
        else:
            return {}    
        
class Drakkari_Enchanter(Minion):
    def __init__(self,name="Drakkari Enchanter",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def ongoing_effect(self,target):
        if target is self.owner:
            return {'double end turn':True}
        else:
            return {}    
          
class Corpsetaker(Minion):
    def __init__(self,name="Corpsetaker",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
    
    def battlecry(self,target=None):
        for ability in ["taunt","divine_shield","lifesteal","windfury"]:
            for card in self.owner.deck.cards:
                if card.isMinion() and getattr(card,ability):
                    getattr(self,"gain_"+ability)()
                    break

class Deathaxe_Punisher(Minion):
    def __init__(self,name="Deathaxe Punisher",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        targets=[] 
        for card in self.owner.hand:
            if card.isMinion() and card.lifesteal:
                targets.append(card)
        target=random.choice(targets)
        target.buff_stats(2,2)
        buff_hand_animation(self.owner,[target])

class Meat_Wagon(Minion):
    def __init__(self,name="Meat Wagon",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        atk=self.get_current_atk()
        target_pool=[]
        for card in self.owner.deck.cards:
            if card.isMinion() and card.atk<atk:
                target_pool.append(card)
                
        if len(target_pool)>0:
            minion = random.choice(target_pool)
            self.recruit(minion)

class Rattling_Rascal(Minion):
    def __init__(self,name="Rattling Rascal",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        minion = Skeletal_Enforcer(owner=self.owner)
        self.summon(minion)

    def deathrattle(self):
        minion = Skeletal_Enforcer(owner=self.owner.opponent)
        self.summon(minion)

class Skeletal_Enforcer(Minion):
    def __init__(self,name="Skeletal Enforcer",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Tomb_Lurker(Minion):
    def __init__(self,name="Tomb Lurker",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        minion = self.owner.search_card(self.owner.grave+self.owner.opponent.grave,"Minion")
        if minion is not None:
            minion_copy = minion.get_copy(owner=self.owner)
            minion_copy.initialize_locaiton(self.location)
            minion_copy.hand_in()

class Furnacefire_Colossus(Minion):
    def __init__(self,name="Furnacefire Colossus",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        targets=[]
        for card in self.owner.hand:
            if isinstance(card,Weapon):
                targets.append(card)
        if len(targets)>0:        
            discard_multiple_animation(targets)
            light_buff_animation(self)
            for weapon in targets:
                weapon.discard(skip_animation=True)
                self.buff_stats(weapon.current_atk,weapon.current_durability)

class Nerubian_Unraveler(Minion):
    def __init__(self,name="Nerubian Unraveler",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def ongoing_effect(self,target):
        if target.isSpell and target.board_area=="Hand":
            return {'cost':2}
        else:
            return {}  

class Skulking_Geist(Minion):
    def __init__(self,name="Skulking Geist",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        targets=[]
        for card in self.owner.hand+self.owner.opponent.hand+self.owner.deck.cards+self.owner.opponent.deck.cards:
            if card.cost==1:
                targets.append(card)
        if len(targets)>0:
            skulking_geist_animation(self,targets)
            for card in targets:
                card.burn(skip_animation=True)       

class Dire_Mole(Minion):
    def __init__(self,name="Dire Mole",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

class Wax_Elemental(Minion):
    def __init__(self,name="Wax Elemental",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        self.divine_shield=True

class Plated_Beetle(Minion):
    def __init__(self,name="Plated Beetle",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        self.owner.increase_shield(3)

class Fungal_Enchanter(Minion):
    def __init__(self,name="Fungal Enchanter",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        targets=self.friendly_characters()
        self.heal(targets,[2]*len(targets))

class Toothy_Chest(Minion):
    def __init__(self,name="Toothy Chest",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source) 
        self.trigger_event_type="start of turn"
       
    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner:
            super(self.__class__,self).trigger_effect(triggering_player)
            self.set_stats(atk=4)

class Dragonslayer(Minion):
    def __init__(self,name="Dragonslayer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(chooser=self,target="minion",target_type="Dragon", message="deal 6 damage")
        return target
    
    def battlecry(self,target):
        nightblade_animation(self, target)
        self.deal_damage([target], [6])

class Kobold_Apprentice(Minion):
    def __init__(self,name="Kobold Apprentice",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def battlecry(self,target):
        self.deal_split_damage(self.enemy_characters(),shots=3,damage=1,effect=get_image("images/fireball2.png",(80,80)),speed=20,curve=False)   

class Sewer_Crawler(Minion):
    def __init__(self,name="Sewer Crawler",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        minion = Giant_Rat(owner=self.owner)
        self.summon(minion)

class Giant_Rat(Minion):
    def __init__(self,name="Giant Rat",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Stoneskin_Basilisk(Minion):
    def __init__(self,name="Stoneskin Basilisk",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.divine_shield=True
        self.poisonous=True
        
class Boisterous_Bard(Minion):
    def __init__(self,name="Boisterous Bard",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        self.buff_multiple(hp=1)

class Sneaky_Devil(Minion):
    def __init__(self,name="Sneaky Devil",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.stealth=True
        
    def ongoing_effect(self,target):
        if target.isMinion() and target.board_area=="Board" and target.side==self.side and target is not self:
            return {'atk':1}
        else:
            return {}

class Shroom_Brewer(Minion):
    def __init__(self,name="Shroom Brewer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def get_target(self):
        target=choose_target(chooser=self,target="character",message="restore 4 health")
        return target
    
    def battlecry(self,target):
        lesser_heal_animation(self, target)
        self.heal([target],[4])

class Hoarding_Dragon(Minion): 
    def __init__(self,name="Hoarding Dragon",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        for i in range(2):
            card=The_Coin(owner=self.owner)
            card.initialize_location(self.location)
            card.hand_in()

class Cursed_Disciple(Minion):
    def __init__(self,name="Cursed Disciple",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        minion=Cursed_Revenant(owner=self.owner)
        self.summon(minion)
            
class Cursed_Revenant(Minion):
    def __init__(self,name="Cursed Revenant",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Corrosive_Sludge(Minion):
    def __init__(self,name="Corrosive Sludge",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def battlecry(self,target=None):
        if self.owner.opponent.has_weapon():
            acidic_swamp_ooze_animation(self,self.owner.opponent.weapon)
            self.owner.opponent.weapon.destroy()  

class Trogg_Gloomeater(Minion):
    def __init__(self,name="Trogg Gloomeater",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        self.poisonous=True

class Green_Jelly(Minion):
    def __init__(self,name="Green Jelly",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="end of turn"
        
    def trigger_effect(self,triggering_player):
        if triggering_player is self.owner:
            super(self.__class__,self).trigger_effect(triggering_player)
            minion=Green_Ooze(owner=self.owner)
            self.summon(minion)
             
class Green_Ooze(Minion):
    def __init__(self,name="Green_Ooze",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        
class Fungalmancer(Minion):
    def __init__(self,name="Fungalmancer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        targets=self.adjacent_minions()
        for target in targets:
            target.buff_stats(2,2)

class Guild_Recruiter(Minion):
    def __init__(self,name="Guild Recruiter",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        minion=self.owner.search_card_based_cost(self.owner.deck.cards,card_type="Minion",cost=4,compare="__le__")
        if minion is not None:
            self.recruit(minion)
        
class Silver_Vanguard(Minion): 
    def __init__(self,name="Silver Vanguard",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        minion=self.owner.search_card_based_cost(self.owner.deck.cards,card_type="Minion",cost=8)
        if minion is not None:
            self.recruit(minion)

class Violet_Wurm(Minion): 
    def __init__(self,name="Violet Wurm",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        for i in range(7):
            minion=Grub(owner=self.owner)
            self.summon(minion)

class Grub(Minion): 
    def __init__(self,name="Grub",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Sleepy_Dragon(Minion): 
    def __init__(self,name="Sleepy Dragon",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True

class Feral_Gibberer(Minion):
    def __init__(self,name="Feral Gibberer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="attack"
        
    def trigger_effect(self,triggering_minion):
        if triggering_minion is self and self.target is self.owner.opponent:
            super(self.__class__,self).trigger_effect(triggering_minion)
            minion=Feral_Gibberer(owner=self.owner)
            minion.appear_in_hand()

class Gravelsnout_Knight(Minion):
    def __init__(self,name="Gravelsnout Knight",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        minion = database.get_random_cards("[type]='Minion' AND [cost]=1", self.owner.opponent, 1)[0]
        self.summon(minion)

class Scorp_o_matic(Minion):
    def __init__(self,name="Scorp-o-matic",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(chooser=self,target="minion",target_type="get_current_atk __le__ 1", message="destroy")
        return target
    
    def battlecry(self,target):
        target.destroy()

class Shrieking_Shroom(Minion):
    def __init__(self,name="Shrieking Shroom",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="end of turn"
        
    def trigger_effect(self,triggering_player):
        if triggering_player is self.owner:
            super(self.__class__,self).trigger_effect(triggering_player)
            minion = database.get_random_cards("[type]='Minion' AND [cost]=1", self.owner, 1)[0]
            self.summon(minion)

class Lone_Champion(Minion):
    def __init__(self,name="Lone Champion",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def battlecry(self,target):
        if len(self.friendly_minions())==0:
            self.gain_taunt()
            self.gain_divine_shield()

class Kobold_Monk(Minion):
    def __init__(self,name="Kobold Monk",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def ongoing_effect(self,target):
        if target is self.owner:
            return {'elusive':True}
        else:
            return {}

class Ebon_Dragonsmith(Minion):
    def __init__(self,name="Ebon Dragonsmith",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def battlecry(self,target):
        weapon=self.owner.search_card(self.owner.hand,"Weapon")
        if weapon is not None:
            weapon.modify_cost(-2)

class Furbolg_Mossbinder(Minion):
    def __init__(self,name="Furbolg Mossbinder",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def get_target(self):
        minion=choose_target(chooser=self,target="friendly minion",message="transform into a 6/6 elemental")
        return minion
    
    def battlecry(self,target):
        minion=Moss_Elemental(owner=self.owner)
        target.transform(minion)

class Moss_Elemental(Minion):
    def __init__(self,name="Moss Elemental",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Hungry_Ettin(Minion):
    def __init__(self,name="Hungry Ettin",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        
    def battlecry(self,target=None):
        minion = database.get_random_cards("[type]='Minion' AND [cost]=2", self.owner.opponent, 1)[0]
        self.summon(minion)

class Rummaging_Kobold(Minion):
    def __init__(self,name="Rummaging Kobold",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        weapon=self.owner.search_card(self.owner.weapon_grave,"Weapon")
        if weapon is not None:
            weapon_copy=weapon.get_copy(owner=self.owner)
            weapon_copy.appear_in_hand()

class Void_Ripper(Minion):
    def __init__(self,name="Void Ripper",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        targets=self.all_minions()
        consecration_animation(self, targets)
        for minion in targets:
            minion.swap_stats()

class Shimmering_Courser(Minion):
    def __init__(self,name="Shimmering Courser",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def ongoing_effect(self,target):
        if target is self and self.owner.board.control==-self.side:
            return {'elusive':True}
        else:
            return {}

class Arcane_Tyrant(Minion):
    def __init__(self,name="Arcane Tyrant",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def overriding_ongoing_effect(self,target):
        if target is self and target.board_area=="Hand":
            for card in self.owner.played_cards[self.owner.turn]:
                if card.isSpell and card.cost>=5:  
                    return {'cost':0}
        
        return {} 

class Carnivorous_Cube(Minion):
    def __init__(self,name="Carnivorous Cube",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.tags.append("Targeted")
        
    def get_target(self):
        target=choose_target(self, target="friendly minion", message="destroy")
        return target
    
    def battlecry(self,target):
        target.destroy()
        self.attachments["incorporate"]=target
        
    def deathrattle(self):
        if "incorporate" in self.attachments:
            for i in range(2):
                minion_copy=self.attachments["incorporate"].get_copy(owner=self.owner)
                self.summon(minion_copy)

class Corridor_Creeper(Minion):
    def __init__(self,name="Corridor Creeper",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="minion dies"
        
    def trigger_effect(self, triggering_card=None):
        if self.board_area=="Hand":
            self.modify_cost(-1)

class Spiteful_Summoner(Minion):
    def __init__(self,name="Spiteful Summoner",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        card=self.reveal(card_type="Spell")
        if card is not None:
            minion = database.get_random_cards("[type]='Minion' AND [cost]="+str(card.get_current_cost()), self.owner, 1)[0]
            self.summon(minion)

class Grand_Archivist(Minion):
    def __init__(self,name="Grand Archivist",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="end of turn"
        
    def trigger_effect(self,triggering_player):
        if triggering_player is self.owner:
            super(self.__class__,self).trigger_effect(triggering_player)
            spell=self.reveal(card_type="Spell")
            if spell is not None:
                self.owner.deck.cards.remove(spell)
                spell.board_area="Board"
                spell.cast_on_random_target()

class Dragonhatcher(Minion):
    def __init__(self,name="Dragonhatcher",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="end of turn"
        
    def trigger_effect(self,triggering_player):
        if triggering_player is self.owner:
            super(self.__class__,self).trigger_effect(triggering_player)
            minion=self.owner.search_card(self.owner.cards,card_type="Dragon",k=1)
            if minion is not None:
                self.recruit(minion)

class Swamp_Dragon_Egg(Minion):
    def __init__(self,name="Swamp Dragon Egg",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        card = database.get_random_cards("[race]='Dragon'", self.owner, 1)[0]
        card.initialize_location(self.location)
        card.hand_in()

class Swamp_Leech(Minion):
    def __init__(self,name="Swamp Leech",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.lifesteal=True

class Lost_Spirit(Minion):
    def __init__(self,name="Lost Spirit",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        self.buff_multiple(atk=1)

class Vicious_Scalehide(Minion):
    def __init__(self,name="Vicious Scalehide",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.lifesteal=True
        self.rush=True
 
class Spellshifter(Minion):
    def __init__(self,name="Spellshifter",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.spell_damage_boost=1
        self.trigger_event_type="start of turn"
        
    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner and self.board_area=="Hand":
            minion = Spellshifter_4_1(owner=self.owner)
            minion.initialize_location(self.location)
            minion.board_area="Hand"
            self.owner.hand[self.get_index()]=minion

class Spellshifter_4_1(Minion):
    def __init__(self,name="Spellshifter (4-1)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.spell_damage_boost=1
        self.trigger_event_type="start of turn"
        
    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner and self.board_area=="Hand":
            minion = Spellshifter(owner=self.owner)
            minion.initialize_location(self.location)
            minion.board_area="Hand"
            self.owner.hand[self.get_index()]=minion

class Blackwald_Pixie(Minion):
    def __init__(self,name="Blackwald Pixie",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.spell_damage_boost=1

    def battlecry(self,target=None):
        self.owner.hero_power.refresh()

class Hench_Clan_Thug(Minion):
    def __init__(self,name="Hench Clan Thug",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="after attack"
        
    def trigger_effect(self, triggering_entity=None):
        if triggering_entity is self.owner:
            super(self.__class__,self).trigger_effect(triggering_entity)
            rage_buff_animation(self)
            self.buff_stats(1, 1)

class Marsh_Drake(Minion):
    def __init__(self,name="Marsh Drake",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        minion = Drakeslayer(owner=self.owner.opponent)
        self.summon(minion)

class Drakeslayer(Minion):
    def __init__(self,name="Drakeslayer",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Pumpkin_Peasant(Minion):
    def __init__(self,name="Pumpkin Peasant",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.lifesteal=True
        self.trigger_event_type="start of turn"
        
    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner and self.board_area=="Hand":
            minion = Pumpkin_Peasant_4_2(owner=self.owner)
            self.shapeshift(minion)

class Pumpkin_Peasant_4_2(Minion):
    def __init__(self,name="Pumpkin Peasant (4-2)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.lifesteal=True
        self.trigger_event_type="start of turn"
        
    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner and self.board_area=="Hand":
            minion = Pumpkin_Peasant(owner=self.owner)
            self.shapeshift(minion)

class Tanglefur_Mystic(Minion):
    def __init__(self,name="Tanglefur Mystic",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        for player in [self.owner,self.owner.opponent]:
            minion = database.get_random_cards("[type]='Minion' AND [cost]=2", player, 1)[0]
            minion.appear_in_hand()

class Ravencaller(Minion):
    def __init__(self,name="Ravencaller",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        for i in range(2):
            minion = database.get_random_cards("[type]='Minion' AND [cost]=1", self.owner, 1)[0]
            minion.initialize_location(self.location)
            minion.hand_in()

class Walnut_Sprite(Minion):
    def __init__(self,name="Ravencaller",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

class Felsoul_Inquisitor(Minion):
    def __init__(self,name="Felsoul Inquisitor",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.lifesteal=True
        self.taunt=True

class Swift_Messenger(Minion):
    def __init__(self,name="Swift Messenger",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.rush=True
        self.trigger_event_type="start of turn"
        
    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner and self.board_area=="Hand":
            minion = Swift_Messenger_6_2(owner=self.owner)
            self.shapeshift(minion)

class Swift_Messenger_6_2(Minion):
    def __init__(self,name="Swift Messenger (6-2)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.rush=True
        self.trigger_event_type="start of turn"
        
    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner and self.board_area=="Hand":
            minion = Swift_Messenger(owner=self.owner)
            self.shapeshift(minion)

class Unpowered_Steambot(Minion):
    def __init__(self,name="Unpowered Steambot",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True

class Clockwork_Automaton(Minion):
    def __init__(self,name="Clockwork Automaton",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
                
    def ongoing_effect(self,target):
        if target.side==self.side and isinstance(target, Hero_Power):
            return {'double effect':1}
        else:
            return {}

class Rotten_Applebaum(Minion):
    def __init__(self,name="Rotten Applebaum",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        
    def deathrattle(self):
        self.heal([self.owner],[4])
        
class Darkmire_Moonkin(Minion):
    def __init__(self,name="Darkmire Moonkin",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.spell_damage_boost=2

class Furius_Ettin(Minion):
    def __init__(self,name="Furius Ettin",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True

class Wyrmguard(Minion):
    def __init__(self,name="Wyrmguard",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        if self.owner.holding("Dragon"):
            buff_animation(self)
            self.buff_stats(1, 0)
            self.gain_taunt()

class Cauldron_Elemental(Minion):
    def __init__(self,name="Cauldron_Elemental",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def ongoing_effect(self,target):
        if target.isMinion() and target.board_area=="Board" and target.side==self.side and target is not self and target.has_race("Beast"):
            return {'atk':2}
        else:
            return {}   

class Deranged_Doctor(Minion):
    def __init__(self,name="Deranged Doctor",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        self.heal([self.owner],[8])

class Phantom_Militia(Minion):
    def __init__(self,name="Phantom Militia",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True

class Lifedrinker(Minion):
    def __init__(self,name="Lifedrinker",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
    
    def battlecry(self,target=None):
        lifedrinker_animation(self)
        self.deal_damage([self.owner.opponent], [3])
        self.heal([self.owner],[3])

class Mad_Hatter(Minion):
    def __init__(self,name="Mad Hatter",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def battlecry(self,target=None):
        target_pool=self.all_minions()
        for i in range(3):
            target=random.choice(target_pool)
            mad_hatter_animation(self,target)
            target.buff_stats(1,1)

class Night_Prowler(Minion):
    def __init__(self,name="Night Prowler",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def battlecry(self,target=None):
        if len(self.all_minions())==0:
            rage_buff_animation(self)
            self.buff_stats(3, 3)

class Scaleworm(Minion):
    def __init__(self,name="Scaleworm",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        if self.owner.holding("Dragon"):
            rage_buff_animation(self)
            self.buff_stats(1, 0)
            self.gain_rush()

class Witchwood_Piper(Minion):
    def __init__(self,name="Witchwood Piper",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        for k in range(26):
            minion=self.owner.search_card_based_cost(self.owner.deck.cards,card_type="Minion",cost=k)
            if minion is not None:
                self.owner.draw(target=minion)
                break

class Chief_Inspector(Minion):
    def __init__(self,name="Chief Inspector",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        targets=[]
        for secret in self.owner.opponent.secrets:
            targets.append(secret)
            
        destroy_multiple_secret_animation(targets)
        for secret in targets:
            secret.destroy(skip_animation=True)

class Witchwood_Grizzly(Minion):
    def __init__(self,name="Witchwood Grizzly",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
    
    def battlecry(self,target=None):
        rage_buff_animation(self)
        self.buff_stats(0, -len(self.owner.opponent.hand))

class Gilnean_Royal_Guard(Minion):
    def __init__(self,name="Gilnean Royal Guard",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.divine_shield=True
        self.rush=True
        self.trigger_event_type="start of turn"
        
    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner and self.board_area=="Hand":
            minion = Gilnean_Royal_Guard_8_3(owner=self.owner)
            self.shapeshift(minion)

class Gilnean_Royal_Guard_8_3(Minion):
    def __init__(self,name="Gilnean Royal Guard (8-3)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.divine_shield=True
        self.rush=True
        self.trigger_event_type="start of turn"
        
    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner and self.board_area=="Hand":
            minion = Gilnean_Royal_Guard(owner=self.owner)
            self.shapeshift(minion)

class Baleful_Banker(Minion):
    def __init__(self,name="Baleful Banker",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def get_target(self):
        minion=choose_target(chooser=self,target="friendly minion",message="get a Golden copy of it")
        return minion
    
    def battlecry(self,target):
        minion_copy=target.get_copy(owner=self.owner)
        minion_copy.initialize_location(target.location)
        minion_copy.shuffle_into_deck()

class Nightmare_Amalgam(Minion):
    def __init__(self,name="Nightmare Amalgam",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

class Voodoo_Doll(Minion):
    def __init__(self,name="Voodoo Doll",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def get_target(self):
        target=choose_target(self, target="minion", message="curse")
        return target
    
    def battlecry(self,target):
        voodoo_doll_animation(self, target)
        self.attachments["incorporate"]=target
        
    def deathrattle(self):
        if "incorporate" in self.attachments:
            if self.attachments["incorporate"].board_area=="Board":
                self.attachments["incorporate"].destroy()

class Witchs_Cauldron(Minion):
    def __init__(self,name="Witch's Cauldron",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="minion dies"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.side==self.side and triggering_card is not self:
            super(self.__class__,self).trigger_effect(triggering_card)
            spell = database.get_random_cards("[type]='Spell' AND [class] LIKE '%Shaman%'", self.owner, 1)[0]
            spell.initialize_location(self.owner.location)
            spell.hand_in()

class Sandbinder(Minion):
    def __init__(self,name="Sandbinder",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def battlecry(self,target):
        minion=self.owner.search_card(self.owner.deck.cards,"Elemental")
        if minion is not None:
            self.owner.draw(target=minion)

class Muck_Hunter(Minion):
    def __init__(self,name="Muck Hunter",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.rush=True
        
    def battlecry(self,target=None):
        for i in range(2):
            minion = Muckling(owner=self.owner.opponent,source="board")
            self.summon(minion)

class Muckling(Minion):
    def __init__(self,name="Muckling",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Mossy_Horror(Minion):
    def __init__(self,name="Mossy Horror",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        targets=[]
        for minion in self.all_minions():
            if minion.get_current_atk()<=2:
                targets.append(minion)
        
        mossy_horror_animation(self,targets)     
        for minion in targets:
            minion.destroy(skip_animation=True)

class Worgen_Abomination(Minion):
    def __init__(self,name="Worgen Abomination",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source) 
        self.trigger_event_type="end of turn"
       
    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner:
            super(self.__class__,self).trigger_effect(triggering_player)
            targets=[]
            for minion in self.all_minions():
                if minion.damaged():
                    targets.append(minion)
            if len(targets)>0:
                swipe_multiple_animation(self,targets)
                self.deal_damage(targets, [2]*len(targets), skip_animation=True)

class Splitting_Festeroot(Minion):
    def __init__(self,name="Splitting Festeroot",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        for i in range(2):
            minion=Splitting_Sapling(owner=self.owner)
            self.summon(minion)

class Splitting_Sapling(Minion):
    def __init__(self,name="Splitting_Sapling",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        for i in range(2):
            minion=Woodchip(owner=self.owner)
            self.summon(minion)
                          
class Woodchip(Minion):
    def __init__(self,name="Woodchip",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
class Gyrocopter(Minion):
    def __init__(self,name="Gyrocopter",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.rush=True
        self.windfury=True

class Living_Dragonbreath(Minion):
    def __init__(self,name="Living Dragonbreath",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def ongoing_effect(self,target):
        if target.isMinion() and target.side==self.side:
            return {'defrozen':True}
        else:
            return {}
            
class Cheaty_Anklebiter(Minion):
    def __init__(self,name="Cheaty Anklebiter",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.lifesteal=True

    def get_target(self):
        target=choose_target(chooser=self,target="character",message="deal 1 damage")
        return target
    
    def battlecry(self,target):
        cheaty_anklebiter_animation(self,target)
        self.gain_lifesteal()  #Need manual activation here because it happens before minion coming on board
        self.deal_damage([target], [1])
                                  
class Generous_Mummy(Minion):
    def __init__(self,name="Generous Mummy",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.reborn=True
        
    def ongoing_effect(self,target):
        if target.side!=self.side and target.board_area=="Hand":
            return {'cost':-1}
        else:
            return {}
        
class Missile_Launcher(Minion):
    def __init__(self,name="Missile Launcher",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source) 
        self.magnetic=True
        self.trigger_event_type="end of turn"
       
    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner:
            super(self.__class__,self).trigger_effect(triggering_player)
            missile_launcher_animation(self)
            targets=self.all_characters()
            targets.remove(self)
            self.deal_damage(targets, [1]*len(targets))
                 
class Sightless_Ranger(Minion):
    def __init__(self,name="Sightless Ranger",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source) 
        self.rush=True
        
    def overkill(self,target):
        overkill_animation(target)
        for i in range(2):
            minion=Bat(owner=self.owner)
            self.summon(minion,left=(-1)**i,speed=40)

class Bat(Minion):
    def __init__(self,name="Bat",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source) 

                                                                                                                                                                                                                                                 
class Imprisoned_Vilefiend(Minion):
    def __init__(self,name="Imprisoned Vilefiend",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.dormant=True 
        self.rush=True
                                                                    
class Bloodmage_Thalnos(Minion):
    def __init__(self,name="Bloodmage Thalnos",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.spell_damage_boost=1
        
    def deathrattle(self):
        self.owner.draw()

class Lorewalker_Cho(Minion):
    def __init__(self,name="Lorewalker Cho",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="cast a spell"
        
    def trigger_effect(self, triggering_card=None):
        super(self.__class__,self).trigger_effect(triggering_card)
        card_copy = getattr(card_collection,database.cleaned(triggering_card.name))(owner=triggering_card.owner.opponent)
        card_copy.appear_in_hand()
                                                        
class Millhouse_Manastorm(Minion):
    def __init__(self,name="Millhouse Manastorm",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def battlecry(self,target=None):
        mage_minion_animation(self)
        card=Millhouse_Effect(owner=self.owner.opponent)
                    
class Millhouse_Effect(Enchantment):
    def __init__(self,name="Millhouse Manastorm",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_events.append(("start of turn",self.trigger_effect))
        self.activate=False

    def overriding_ongoing_effect(self,target):
        if target.side==self.side and target.isSpell and self.activate:
            return {'cost':0}
        else:
            return {}            
        
    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner:
            self.activate=True
            
class Nat_Pagle(Minion):
    def __init__(self,name="Nat Pagle",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="start of turn"
                
    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner:
            if random.uniform(0,1)>=0.5:
                super(self.__class__,self).trigger_effect(triggering_player)
                nat_pagle_animation(self)
                self.owner.draw()

class Brightwing(Minion):
    def __init__(self,name="Brightwing",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        brightwing_animation(self)
        minion = database.get_random_cards("[type]='Minion' AND [rarity]='Legendary'", self.owner, 1)[0]
        minion.initialize_location(self.location)
        minion.hand_in()

class King_Mukla(Minion):
    def __init__(self,name="King Mukla",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        king_mukla_animation(self)
        for k in range(2):
            banana=Bananas(owner=self.owner.opponent)
            banana.initialize_location(self.location)
            banana.hand_in()
      
class Bananas(Spell):
    def __init__(self,name="Bananas",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target):
        if target is not None and target.isMinion():
            super(self.__class__,self).invoke()
            paladin_buff_animation(self, target)
            target.buff_stats(1,1)             
             
class Tinkmaster_Overspark(Minion):
    def __init__(self,name="Tinkmaster Overspark",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        targets=self.all_minions()
        if len(targets)>0:
            target_minion=random.choice(targets)
            option1=Devilsaur(owner=target_minion.owner,source=target_minion.location)
            option2=Squirrel(owner=target_minion.owner,source=target_minion.location)
            minion=random.choice([option1,option2])
            target_minion.transform(minion)

class Devilsaur(Minion):
    def __init__(self,name="Devilsaur",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Squirrel(Minion):
    def __init__(self,name="Squirrel",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Old_Murk_Eye(Minion):
    def __init__(self,name="Old Murk-Eye",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.charge=True
        
    def ongoing_effect(self,target):
        if target is self:
            pool=self.all_minions("Murloc")
            if self in pool:
                pool.remove(self)
            return {'atk':len(pool)}
        else:
            return {} 

class Leeroy_Jenkins(Minion):
    def __init__(self,name="Leeroy Jenkins",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.charge=True
        
    def battlecry(self,target=None):
        for i in range(2):
            minion = Whelp_Classic(owner=self.owner.opponent)
            self.summon(minion)
            
class Elite_Tauren_Chieftain(Minion):
    def __init__(self,name="Elite Tauren Chieftain",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        elite_tauren_chieftain_animation(self)
        for i in [1,-1]:
            player=self.owner.board.players[i]
            rock_card_name=random.choice(["I Am Murloc","Power of the Horde","Rogues Do It..."])
            card = getattr(card_collection,database.cleaned(rock_card_name))(owner=player)
            card.initialize_location(self.location)
            card.hand_in()
                
class I_Am_Murloc(Spell):
    def __init__(self,name="I Am Murloc",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        n=random.randint(2,4)
        for i in range(n):
            minion=Murloc_minion(owner=self.owner,source="board")
            self.owner.recruit(minion)
            
class Murloc_minion(Minion):
    def __init__(self,name="Murloc (minion)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)            

class Power_of_the_Horde(Spell):
    def __init__(self,name="Power of the Horde",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        horde_minion_name=random.choice(["Frostwolf Grunt","Tauren Warrior","Thrallmar Farseer","Silvermoon Guardian","Sen'jin Shieldmasta","Cairne Bloodhoof"])
        minion = getattr(card_collection,database.cleaned(horde_minion_name))(owner=self.owner,source="board")
        self.owner.recruit(minion)

class Rogues_Do_It(Spell):
    def __init__(self,name="Rogues Do It...",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None
       
    def invoke(self,target):
        super(self.__class__,self).invoke()
        charge_shot_animation(self.owner,target)
        self.deal_damage([target], [4])
        self.owner.draw()
                                
class Captain_Greenskin(Minion):
    def __init__(self,name="Captain Greenskin",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        if self.owner.has_weapon():
            captain_greenskin_animation(self)
            self.owner.weapon.buff_stats(1,1)

class Harrison_Jones(Minion):
    def __init__(self,name="Harrison Jones",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        if self.owner.opponent.has_weapon():
            harrison_jones_animation(self)
            durability=self.owner.opponent.weapon.current_durability
            self.owner.opponent.weapon.destroy()
            self.owner.draw(durability)
            
class Cairne_Bloodhoof(Minion):
    def __init__(self,name="Cairne Bloodhoof",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
       
    def deathrattle(self):
        minion=Baine_Bloodhoof(owner=self.owner)
        self.summon(minion)

class Baine_Bloodhoof(Minion):
    def __init__(self,name="Baine Bloodhoof",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Sylvanas_Windrunner(Minion):
    def __init__(self,name="Sylvanas Windrunner",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
       
    def deathrattle(self):
        target_pool=[]
        for minion in self.enemy_minions():
            if minion.get_current_hp()>0:
                target_pool.append(minion)
        if len(target_pool)>0:
            target=random.choice(target_pool)
            sylvanas_windrunner_animation(self,target)
            self.owner.take_control(target)
            
class Hogger(Minion):
    def __init__(self,name="Hogger",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="end of turn"
        
    def trigger_effect(self,triggering_player):
        if triggering_player is self.owner:
            super(self.__class__,self).trigger_effect(triggering_player)
            minion=Gnoll_Hogger(owner=self.owner)
            self.summon(minion)
 
class Gnoll_Hogger(Minion):
    def __init__(self,name="Gnoll (Hogger)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True

class The_Beast(Minion):
    def __init__(self,name="The Beast",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
       
    def deathrattle(self):
        minion=Finkle_Einhorn(owner=self.owner.opponent)
        self.summon(minion)

class Finkle_Einhorn(Minion):
    def __init__(self,name="Finkle Einhorn",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class The_Black_Knight(Minion):
    def __init__(self,name="The Black Knight",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
  
    def get_target(self):
        target=choose_target(self, target="enemy minion", target_type="has_taunt attr", message="destroy")
        return target
    
    def battlecry(self,target):
        the_black_knight_animation(self,target)
        target.destroy()
        
class Gelbin_Mekkatorque(Minion):
    def __init__(self,name="Gelbin Mekkatorque",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        card_name=random.choice(["Emboldener 3000","Homing Chicken","Poultryizer","Repair Bot"])
        minion = getattr(card_collection,database.cleaned(card_name))(owner=self.owner)
        self.summon(minion)

class Emboldener_3000(Minion):
    def __init__(self,name="Emboldener 3000",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source) 
        self.trigger_event_type="end of turn"
       
    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner:
            super(self.__class__,self).trigger_effect(triggering_player)
            targets=self.all_minions()
            target=random.choice(targets)
            buff_animation(target)
            target.buff_stats(1,1)
            
class Homing_Chicken(Minion):
    def __init__(self,name="Homing Chicken",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source) 
        self.trigger_event_type="start of turn"
       
    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner:
            super(self.__class__,self).trigger_effect(triggering_player)
            self.destroy()
            self.owner.draw(3)

class Poultryizer(Minion):
    def __init__(self,name="Poultryizer",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source) 
        self.trigger_event_type="start of turn"
       
    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner:
            super(self.__class__,self).trigger_effect(triggering_player)
            targets=self.all_minions()
            target=random.choice(targets)
            chicken=Chicken(owner=target.owner)
            target.transform(chicken)
            
class Chicken(Minion):
    def __init__(self,name="Chicken",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source) 

class Repair_Bot(Minion):
    def __init__(self,name="Repair Bot",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source) 
        self.trigger_event_type="end of turn"
       
    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner:
            super(self.__class__,self).trigger_effect(triggering_player)
            targets=[]
            pool=self.all_characters()
            for target in pool:
                if target.damaged():
                    targets.append(target)
                    
            if len(targets)>0:        
                repair_target=random.choice(targets)
                self.heal([repair_target], [6])
                                                                    
class Xavius(Minion):
    def __init__(self,name="Xavius",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="play a card"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.owner is self.owner and triggering_card is not self:
            super(self.__class__,self).trigger_effect(triggering_card)
            xavius_animation(self)
            minion=Xavian_Satyr(owner=self.owner)
            self.summon(minion)
            
class Xavian_Satyr(Minion):
    def __init__(self,name="Xavian Satyr",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Baron_Geddon(Minion):
    def __init__(self,name="Baron Geddon",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="end of turn"
        
    def trigger_effect(self,triggering_player):
        if triggering_player is self.owner:
            super(self.__class__,self).trigger_effect(triggering_player)
            baron_geddon_animation(self)
            targets=self.all_characters()
            if self in targets:
                targets.remove(self)
            self.deal_damage(targets, [2]*len(targets))

class High_Inquisitor_Whitemane(Minion):
    def __init__(self,name="High Inquisitor Whitemane",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        high_inquisitor_whitemane_animation1(self)
        summoned_minions=[]
        for minion in self.owner.minions_died[self.owner.turn]:
            minion_copy=getattr(card_collection,database.cleaned(minion.name))(owner=self.owner)
            self.summon(minion_copy)
            summoned_minions.append(minion_copy)
        high_inquisitor_whitemane_animation2(self,summoned_minions)
                                                                                   
class Gruul(Minion):
    def __init__(self,name="Gruul",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="end of turn"
        
    def trigger_effect(self,triggering_player):
        super(self.__class__,self).trigger_effect(triggering_player)
        buff_animation(self,speed=8)
        self.buff_stats(1,1)

class Ragnaros_the_Firelord(Minion):
    def __init__(self,name="Ragnaros the Firelord",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source) 
        self.cannot_attack=True
        self.trigger_event_type="end of turn"
        self.has_special_summon_effect=True
    
    def special_summoning_effect(self):
        ragnaros_the_firelord_summon_animation(self)   
             
    def trigger_effect(self,triggering_player):
        if triggering_player is self.owner:
            super(self.__class__,self).trigger_effect(triggering_player)
            target=random.choice(self.enemy_characters())
            ragnaros_the_firelord_animation(self,target)  
            self.deal_damage([target], [8])
       
class Alexstrasza(Minion):
    def __init__(self,name="Alexstrasza",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
             
    def get_target(self):
        target=choose_target(self, target="hero", message="set health to 15")
        return target
    
    def battlecry(self,target):
        alexstrasza_animation(self,target)
        target.current_hp=15
        if target.hp<15:
            target.hp=15
        
class Malygos(Minion):
    def __init__(self,name="Malygos",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.spell_damage_boost=5
        self.has_special_summon_effect=True
    
    def special_summoning_effect(self):
        malygos_animation(self)

class Nozdormu(Minion):
    def __init__(self,name="Nozdormu",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.has_special_summon_effect=True
    
    def special_summoning_effect(self):
        nozdormu_animation(self)
        
    def ongoing_effect(self,target):
        if target.isHero():
            return {'time_limit':15-time.perf_counter()+self.owner.board.start_time}
        else:
            return {} 
    
    def come_on_board(self):
        super(self.__class__,self).come_on_board()
        self.owner.board.start_time=time.perf_counter()
                  
'''    def battlecry(self,target=None):
        self.owner.board.starting_time=time.perf_counter()
        self.owner.board.turn_time_limit=15
        self.owner.remaining_time=15'''

class Onyxia(Minion):
    def __init__(self,name="Onyxia",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        count=1
        while not self.owner.board.isFull(self.owner):
            minion=Whelp_Classic(owner=self.owner)
            self.summon(minion, left=(-1)**count,speed=150)
            count+=1
            
class Whelp_Classic(Minion):
    def __init__(self,name="Whelp (Classic)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Ysera(Minion):
    def __init__(self,name="Ysera",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="end of turn"
        
    def trigger_effect(self,triggering_player):
        if triggering_player is self.owner:
            super(self.__class__,self).trigger_effect(triggering_player)
            dream_card1=Dream(owner=self.owner)
            dream_card2=Emerald_Drake(owner=self.owner)
            dream_card3=Laughing_Sister(owner=self.owner)
            dream_card4=Nightmare(owner=self.owner)
            dream_card5=Ysera_Awakens(owner=self.owner)
            dream_card=random.choice([dream_card1,dream_card2,dream_card3,dream_card4,dream_card5])
            dream_card.initialize_location(self.location)
            ysera_animation(self)
            dream_card.hand_in()
        
class Dream(Spell):
    def __init__(self,name="Dream",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target):
        if target is not None and target.isMinion():
            super(self.__class__,self).invoke()
            target.return_hand()
            
class Emerald_Drake(Minion):
    def __init__(self,name="Emerald Drake",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Laughing_Sister(Minion):
    def __init__(self,name="Laughing Sister",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.elusive=True

class Nightmare(Spell):
    def __init__(self,name="Nightmare",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target):
        if target is not None and target.isMinion():
            super(self.__class__,self).invoke()
            target.buff_stats(5,5)
            target.attachments["Corruption"]=self
            target.trigger_events.append(["start of turn",MethodType(self.trigger_effect.__func__,target)])

    def trigger_effect(self,triggering_player):
        if triggering_player is self.attachments["Corruption"].owner:
            if self.board_area=="Board":
                self.destroy()
 
class Ysera_Awakens(Spell):
    def __init__(self,name="Ysera Awakens",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        targets=[self.owner,self.owner.opponent]
        for minion in self.owner.minions+self.owner.opponent.minions:
            if not minion.has_dormant and not minion.name=="Ysera":
                targets.append(minion)
        ysera_awakens_animation(self)
        self.deal_damage(targets, [5]*len(targets))
 
class Deathwing(Minion):
    def __init__(self,name="Deathwing",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.has_special_summon_effect=True
        
    def special_summoning_effect(self):
        deathwing_animation(self)
        
    def battlecry(self,target=None):
        minions=self.all_minions()
        
        #Discard Hand
        self.owner.discard_hand()
        
        #Destroy Minions
        destroy_multiple_animation(minions)
        for minion in minions:
            minion.destroy(skip_animation=True)
'''
Deathwing_without_OOP(Minion):
    scan the screen to find minions on the board
    identify 1st minion
    if 1st minion is not self:
        reduce 1st minion's hp to 0
        display destroy effect image onto 1st minion
        put 1st minion into grave
        adjust the display positions of the remaining minions

    check whether there are minions left, if yes:
    identify 2nd minion
    if 2nd minion is not self:
        reduce 2nd minion's hp to 0
        display destroy effect image onto 2nd minion
        put 2nd minion into grave
        adjust the display positions of the remaining minions
        
    ...
    ...
    check whether there are minions left, if yes:
    identify Nth minion
    if Nth minion is not self:
        reduce Nth minion's hp to 0
        display destroy effect image onto Nth minion
        put Nth minion into grave
        adjust the display positions of the remaining minions
        
    scan the screen to find cards on hand
    check whether there are cards left, if yes:
    identify 1st card
    move the card upwards
    remove the card from hand
    adjust the display positions of the remaining minions
    
    ...
    ...
    
    check whether there are cards left, if yes:
    identify Nth card
    move the card upwards
    remove the card from hand
    adjust the display positions of the remaining minions
'''           
class Baron_Rivendare(Minion):
    def __init__(self,name="Baron Rivendare",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def ongoing_effect(self,target):
        if target.side==self.side:
            return {'deathrattle twice':True}
        else:
            return {}        

class Feugen(Minion):
    def __init__(self,name="Feugen",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        trigger=False
        for minion in self.owner.grave+self.owner.opponent.grave:
            if minion.name=="Stalagg":
                trigger=True
        if trigger:
            thaddius_animation(self)
            minion=Thaddius(owner=self.owner)
            self.summon(minion)

class Stalagg(Minion):
    def __init__(self,name="Stalagg",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        trigger=False
        for minion in self.owner.grave+self.owner.opponent.grave:
            if minion.name=="Feugen":
                trigger=True
        if trigger:
            thaddius_animation(self)
            minion=Thaddius(owner=self.owner)
            self.summon(minion)
            
class Thaddius(Minion):
    def __init__(self,name="Thaddius",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)


class Loatheb(Minion):
    def __init__(self,name="Loatheb",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def battlecry(self,target=None):
        loatheb_animation(self)
        card=Loatheb_Effect(owner=self.owner.opponent)
        
class Loatheb_Effect(Enchantment):
    def __init__(self,name="Loatheb",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_events.append(("start of turn",self.trigger_effect))
        self.activate=False

    def ongoing_effect(self,target):
        if target.side==self.side and target.isSpell and self.activate:
            return {'cost':5}
        else:
            return {}            
        
    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner:
            self.activate=True
            
class Maexxna(Minion):
    def __init__(self,name="Maexxna",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.poisonous=True

class KelThuzad(Minion):
    def __init__(self,name="Kel'Thuzad",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="end of turn"
        
    def trigger_effect(self,triggering_player):
        super(self.__class__,self).trigger_effect(triggering_player)
        
        summoned_minions=[]
        index=0
        if "@" in self.owner.minions_died[self.owner.turn]:
            index=self.owner.minions_died[self.owner.turn].index("@")+1
        for minion in self.owner.minions_died[self.owner.turn][index:]:
            minion_copy=getattr(card_collection,database.cleaned(minion.name))(owner=self.owner)
            self.summon(minion_copy)
            summoned_minions.append(minion_copy)
        
        kelthuzad_animation(self,summoned_minions)

class Rend_Blackhand(Minion):
    def __init__(self,name="Rend Blackhand",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=None
        if self.owner.holding("Dragon"):
            target=choose_target(chooser=self,target="minion",target_type="is_legendary", message="destroy")
        return target
    
    def battlecry(self,target):
        big_game_hunter_animation(self,target)
        target.destroy()
            
class Chromaggus(Minion):
    def __init__(self,name="Chromaggus",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="draw a card"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.side==self.side and len(self.owner.hand)<self.owner.hand_limit:
            super(self.__class__,self).trigger_effect(triggering_card)
            card=triggering_card.get_copy(owner=self.owner)
            card.initialize_location(self.location)
            card.hand_in()

class Nefarian(Minion):
    def __init__(self,name="Nefarian",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        nefarian_animation(self)
        cards = database.get_random_cards("[type]='Spell' AND [class] LIKE '%"+self.owner.opponent.class_name+"%'", self.owner, k=2)
        if len(cards)==0:
            cards=[Tail_Swipe(owner=self.owner),Tail_Swipe(owner=self.owner)]
        for card in cards:
            card.initialize_location(self.location)
            card.hand_in()

class Tail_Swipe(Spell):
    def __init__(self,name="Tail Swipe",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        swipe_animation(self)
        self.deal_damage([target], [4])

class Majordomo_Executus(Minion):
    def __init__(self,name="Majordomo Executus",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.health=8
             
    def deathrattle(self):
        #Hero replacement
        replace_hero_animation(self)
        self.owner.hero_name="Ragnaros the Firelord"
        self.owner.class_name="Neutral"
        self.owner.image=get_image("images/hero_images/"+self.name+".png",(170,236))
        self.owner.hp=self.health
        self.owner.current_hp=self.health
        
        #Get new hero power
        new_hero_power=DIE_INSECT(owner=self.owner)
        self.owner.gain_hero_power(new_hero_power)

class Eydis_Darkbane(Minion):
    def __init__(self,name="Eydis Darkbane",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="cast a spell"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.side==self.side and triggering_card.target is self:
            super(self.__class__,self).trigger_effect(triggering_card)
            target_pool=self.enemy_characters()
            target=random.choice(target_pool)
            eydis_darkbane_animation(self,target)
            self.deal_damage([target], [3])

class Fjola_Lightbane(Minion): 
    def __init__(self,name="Fjola Lightbane",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="cast a spell"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.side==self.side and triggering_card.target is self:
            super(self.__class__,self).trigger_effect(triggering_card)
            fjola_lightbane_animation(self)
            self.gain_divine_shield()

class Gormok_the_Impaler(Minion):
    def __init__(self,name="Gormok the Impaler",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=None
        if len(self.friendly_minions())>=4:
            target=choose_target(chooser=self,target="character",message="deal 4 damage")
        return target
    
    def battlecry(self,target):
        gormok_the_gmpaler_animation(self, target)
        self.deal_damage([target], [2])
        
class Nexus_Champion_Saraad(Minion):
    def __init__(self,name="Nexus-Champion Saraad",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.inspire=True
        
    def trigger_inspire(self, hero_power=None):
        if hero_power.owner is self.owner:
            super(self.__class__,self).trigger_inspire()
            card = database.get_random_cards("[type]='Spell'", owner=self.owner, k=1)[0]
            if card is not None:
                card.initializa_location(self.location)
                nexus_champion_saraad_animation(self)
                card.hand_in()

class Bolf_Ramshield(Minion): 
    def __init__(self,name="Bolf Ramshield",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="modify damage"
        
    def trigger_effect(self, triggering_entity):
        damage_source=triggering_entity[0]
        amount=triggering_entity[1]
        player=triggering_entity[2]
        if player is self.owner and amount>0:
            super(self.__class__,self).trigger_effect(self)
            bolf_ramshield_animation(self)
            damage_source.deal_damage([self],[amount])
            #self.incur_damage(amount,on_hit_effects=damage_source.on_hit_effects,damage_source=damage_source)
            self.owner.modified_damage=0

class Justicar_Trueheart(Minion):
    def __init__(self,name="Justicar Trueheart",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        light_buff_animation(self)
        light_buff_animation(self.owner.hero_power)
        self.owner.hero_power.upgrade()

class The_Skeleton_Knight(Minion):
    def __init__(self,name="The Skeleton Knight",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def destroy(self,skip_animation=False,skip_deathrattle=False):
        for deathrattle in self.deathrattles:
            deathrattle[0]()

        if self.board_area!="Hand":
            super(self.__class__,self).destroy(skip_animation=skip_animation,skip_deathrattle=True)

    def deathrattle(self):
        winner = self.joust("Minion")
        if winner is not None and winner.owner is self.owner:
            if self.board_area=="Board":
                self.return_hand(reset=True)

class Chillmaw(Minion):
    def __init__(self,name="Chillmaw",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        
    def deathrattle(self):
        if self.owner.holding("Dragon"):
            chillmaw_animation(self)
            targets=self.all_minions()
            self.deal_damage(targets, [3]*len(targets))
        
class Skycapn_Kragg(Minion):
    def __init__(self,name="Skycap'n Kragg",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.charge=True
        
    def ongoing_effect(self,target):
        if target is self:
            pool=self.all_minions("Pirate")
            if self in pool:
                pool.remove(self)
            return {'atk':len(pool)}
        else:
            return {} 

class Icehowl(Minion):
    def __init__(self,name="Icehowl",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.charge=True
        self.cannot_attack_hero=True
        self.has_special_summon_effect=True
    
    def special_summoning_effect(self):
        icehowl_animation(self) 

class Blingtron_3000(Minion):
    def __init__(self,name="Blingtron 3000",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        for player in [self.owner,self.owner.opponent]:
            weapon=database.get_random_cards("[type]='Weapon'", owner=player, k=1)[0]
            player.equip_weapon(weapon)
              
class Hemet_Nesingwary(Minion):
    def __init__(self,name="Hemet Nesingwary",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(chooser=self,target="minion",target_type="Beast", message="destroy")
        return target
    
    def battlecry(self,target):
        big_game_hunter_animation(self,target)
        target.destroy()
        
class Mimirons_Head(Minion):
    def __init__(self,name="Mimiron's Head",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source) 
        self.trigger_event_type="start of turn"
       
    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner:
            mechs=[]
            targets=self.friendly_minions()
            for minion in targets:
                if minion.has_race("Mech"):
                    mechs.append(minion)
            if len(mechs)>=3:
                super(self.__class__,self).trigger_effect(triggering_player)
                robot=V_07_TR_0N(owner=self.owner,source=self.location)
                mimirons_head_animation(self,mechs,robot)
                for mech in mechs:
                    mech.destroy(skip_animation=True)
                self.summon(robot)

class V_07_TR_0N(Minion):
    def __init__(self,name="V-07-TR-0N",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source) 
        self.charge=True
        self.windfury=True
    
    def come_on_board(self):
        super(self.__class__,self).come_on_board()
        self.gain_windfury(4)

class Gazlowe(Minion):
    def __init__(self,name="Gazlowe",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="cast a spell"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.side==self.side and triggering_card.get_current_cost()==1:
            super(self.__class__,self).trigger_effect(triggering_card)
            minion = database.get_random_cards("[type]='Minion' AND [race]='Mech'", self.owner, 1)[0]
            minion.initialize_location(self.location)
            minion.hand_in()
        
class Mogor_the_Ogre(Minion):
    def __init__(self,name="Mogor the Ogre",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="attack"
        
    def trigger_effect(self,triggering_entity):
        if triggering_entity.isMinion():
            triggering_entity.attack_wrong_enemy(0.5)
        
class Toshley(Minion):
    def __init__(self,name="Toshley",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
    
    def battlecry(self,target=None):
        self.give_random_spare_part(self.owner)
            
    def deathrattle(self):
        self.give_random_spare_part(self.owner)

class Dr_Boom(Minion):
    def __init__(self,name="Dr. Boom",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
    
    def battlecry(self,target=None):
        for i in range(2):
            bomb=Boom_Bot(owner=self.owner)
            self.summon(bomb, left=(-1)**i,speed=60)

class Boom_Bot(Minion):
    def __init__(self,name="Boom Bot",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
            
    def deathrattle(self):
        targets=self.enemy_characters()
        target = random.choice(targets)
        boom_bot_animation(self,target)
        self.deal_damage([target], [random.randint(1,4)])
                                       
class Troggzor_the_Earthinator(Minion):
    def __init__(self,name="Troggzor the Earthinator",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="cast a spell"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.side==-self.side:
            super(self.__class__,self).trigger_effect(triggering_card)
            minion=Burly_Rockjaw_Trogg(owner=self.owner)
            self.summon(minion)

class Foe_Reaper_4000(Minion):
    def __init__(self,name="Foe Reaper 4000",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="during attack"
        
    def trigger_effect(self,triggering_minion):
        if triggering_minion is self and self.target.isMinion():
            self.attack_adjacent_minions(self.target)
                                                                                                                                                         
class Sneeds_Old_Shredder(Minion):
    def __init__(self,name="Sneed's Old Shredder",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        minion = database.get_random_cards("[type]='Minion' AND [rarity]='Legendary'", self.owner, 1)[0]
        self.summon(minion)

class Mekgineer_Thermaplugg(Minion):
    def __init__(self,name="Mekgineer Thermaplugg",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="minion dies"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.side==-self.side:
            super(self.__class__,self).trigger_effect(triggering_card)
            minion=Leper_Gnome(owner=self.owner)
            self.summon(minion)

class Emperor_Thaurissan(Minion):
    def __init__(self,name="Emperor Thaurissan",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="end of turn"
        
    def trigger_effect(self,triggering_player):
        if triggering_player is self.owner:
            super(self.__class__,self).trigger_effect(triggering_player)
            mage_minion_animation(self)
            for card in self.owner.hand:
                card.current_cost-=1
                                                                                                                                                    
class Sir_Finley_Mrrgglton(Minion):
    def __init__(self,name="Sir Finley Mrrgglton",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        card=self.discover(filter_str="[type]='Hero Power' AND [cardset]='Basic' AND [card_name]!='"+self.owner.hero_power.name+"'",own_class=False,standard=False)
        hero_power=getattr(card_collection,database.cleaned(card.name))(owner=self.owner)
        self.owner.gain_hero_power(hero_power)

class Brann_Bronzebeard(Minion):
    def __init__(self,name="Brann Bronzebeard",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def ongoing_effect(self,target):
        if target.side==self.side:
            return {'battlecry twice':True}
        else:
            return {}      
                      
class Elise_Starseeker(Minion):
    def __init__(self,name="Elise Starseeker",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        card=Map_to_the_Golden_Monkey(owner=self.owner)
        card.initialize_location(self.location)
        deck_in_animation(card,self.owner.deck)
        self.owner.deck.add_card(card) 

class Map_to_the_Golden_Monkey(Spell):
    def __init__(self,name="Map to the Golden Monkey",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        card=Golden_Monkey(owner=self.owner,source=self.owner.location)
        deck_in_animation(card,self.owner.deck)
        self.owner.deck.add_card(card) 

class Golden_Monkey(Minion):
    def __init__(self,name="Golden Monkey",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        
    def battlecry(self,target=None):
        golden_monkey_animation(self)
        for card in self.owner.hand+self.owner.deck.cards:
            minion = database.get_random_cards("[type]='Minion' AND [rarity]='Legendary'", self.owner, 1)[0]
            card.replace_by(minion)

class Reno_Jackson(Minion):
    def __init__(self,name="Reno Jackson",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        if self.owner.deck.has_no_duplicates():
            reno_jackson_animation(self)
            self.heal([self.owner],[self.owner.temp_hp])

class Arch_Thief_Rafaam(Minion):
    def __init__(self,name="Arch-Thief Rafaam",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        option1         = Lantern_of_Power(owner=self.owner)
        option2         = Mirror_of_Doom(owner=self.owner)
        option3         = Timepiece_of_Horror(owner=self.owner)
        selected_card   = choose_one([option1,option2,option3])

        if selected_card is not None:
            selected_card.appear_in_hand()

class Lantern_of_Power(Spell):
    def __init__(self,name="Lantern of Power",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion()
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        if target is not None and target.isMinion() and target.is_targetable():
            lantern_of_power_animation(self,target)
            target.buff_stats(10,10)

class Mirror_of_Doom(Spell):
    def __init__(self,name="Mirror of Doom",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        self.owner.board.background = pygame.transform.scale(pygame.image.load('images/catacomb.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
        show_board(self.owner.board)
        time.sleep(1)
        while not self.owner.board.isFull(self.owner):
            minion=Mummy_Zombie(owner=self.owner,source="board")
            self.owner.recruit(minion)
        self.owner.board.background = pygame.transform.scale(pygame.image.load('images/background.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
   
class Mummy_Zombie(Minion):
    def __init__(self,name="Mummy Zombie",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
                    
class Timepiece_of_Horror(Spell):
    def __init__(self,name="Timepiece of Horror",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        self.owner.board.background=background_dark
        show_board(self.owner.board)
        time.sleep(0.6)
        self.deal_split_damage(self.enemy_characters(),shots=10,damage=1,effect=get_image("images/magic_bolt.png",(80,80)),speed=30)
        time.sleep(0.4)
        self.owner.board.background=background  

class CThun(Minion):
    def __init__(self,name="C'Thun",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.has_special_summon_effect=True
        
    def special_summoning_effect(self):
        cthun_animation(self)
                
    def battlecry(self,target=None):
        self.deal_split_damage(self.enemy_characters(),shots=self.temp_atk,damage=1,effect=get_image("images/magic_bolt.png",(80,80)),speed=50)
        
class Shifter_Zerus(Minion):
    def __init__(self,name="Shifter Zerus",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source) 
        self.trigger_event_type="start of turn"
        
    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner and self.board_area=="Hand":
            minion = database.get_random_cards("[type]='Minion'", self.owner, 1)[0]
            minion.transform_in_hand=True
            minion.trigger_events.append(["start of turn",MethodType(Shifter_Zerus.trigger_effect,minion)])
            minion.copy_target=self
            self.shapeshift(minion)
            
class Nat_the_Darkfisher(Minion):
    def __init__(self,name="Nat, the Darkfisher",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="start of turn"
                
    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner.opponent:
            if random.uniform(0,1)>=0.5:
                super(self.__class__,self).trigger_effect(triggering_player)
                nat_the_darkfisher_animation(self)
                self.owner.opponent.draw()

class Mukla_Tyrant_of_the_Vale(Minion):
    def __init__(self,name="Mukla, Tyrant of the Vale",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        king_mukla_animation(self)
        for k in range(2):
            banana=Bananas(owner=self.owner)
            banana.initialize_location(self.location)
            banana.hand_in()

class Hogger_Doom_of_Elwynn(Minion):
    def __init__(self,name="Hogger, Doom of Elwynn",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="minion damage"
        
    def trigger_effect(self,triggering_entity):
        if triggering_entity[0] is self:
            super(self.__class__,self).trigger_effect(self)
            minion=Gnoll_Hogger_Doom_of_Elwynn(owner=self.owner)
            self.summon(minion)

class Gnoll_Hogger_Doom_of_Elwynn(Minion):
    def __init__(self,name="Gnoll (Hogger, Doom of Elwynn)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True

class Twin_Emperor_Veklor(Minion):
    def __init__(self,name="Twin Emperor Vek'lor",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        
    def battlecry(self,target=None):
        if self.eval_cthun(atk=10):
            minion=Twin_Emperor_Veknilash(owner=self.owner)
            self.summon(minion)
            
class Twin_Emperor_Veknilash(Minion):
    def __init__(self,name="Twin Emperor Vek'nilash",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True            
            
class The_Boogeymonster(Minion):
    def __init__(self,name="The Boogeymonster",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="after attack"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card is self and self.target.destroyed_by is self:
            super(self.__class__,self).trigger_effect(triggering_card)
            buff_animation(self)
            self.buff_stats(2, 2)

class Soggoth_the_Slitherer(Minion):
    def __init__(self,name="Soggoth the Slitherer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        self.elusive=True

class Deathwing_Dragonlord(Minion):
    def __init__(self,name="Deathwing, Dragonlord",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.has_special_summon_effect=True
        
    def special_summoning_effect(self):
        deathwing_animation(self)
                
    def deathrattle(self):
        for minion in self.owner.hand:
            if minion.has_race("Dragon"):
                self.owner.put_into_battlefield(minion)

class NZoth_the_Corruptor(Minion):
    def __init__(self,name="N'Zoth, the Corruptor",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.has_special_summon_effect=True
        
    def special_summoning_effect(self):
        nzoth_the_corruptor_animation(self)
                
    def battlecry(self,target=None):
        target_pool = []
        for minion in self.owner.grave:
            if "Deathrattle" in minion.abilities:
                target_pool.append(minion)
                
        if len(target_pool)>0:
            minions=random.sample(target_pool,k=min(6,len(target_pool)))
            for minion in minions:
                minion_copy=getattr(card_collection,database.cleaned(minion.name))(owner=self.owner)
                self.summon(minion_copy)

class YShaarj_Rage_Unbound(Minion):
    def __init__(self,name="Y'Shaarj, Rage Unbound",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="end of turn"
        self.has_special_summon_effect=True
        
    def special_summoning_effect(self):
        yshaarj_rage_unbound_animation(self)
                        
    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner:
            minion = self.owner.search_card(self.owner.deck.cards,"Minion")
            if minion is not None:
                super(self.__class__,self).trigger_effect(self)
                self.recruit(minion)
            
class Yogg_Saron_Hopes_End(Minion):
    def __init__(self,name="Yogg-Saron, Hope's End",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
                
    def battlecry(self,target=None):
        self.owner.board.background = pygame.transform.scale(pygame.image.load('images/background_dark.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
        count=0
        for i in range(self.owner.turn):
            for card in self.owner.played_cards[i+1]:
                if card.isSpell and self.board_area=="Board":
                    spell = database.get_random_cards("[type]='Spell'", self.owner, 1)[0]
                    yogg_saron_spell_animation(spell)
                    spell.cast_on_random_target()   
                    count+=1
            if count>=30:
                break
        self.owner.board.background = pygame.transform.scale(pygame.image.load('images/background.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

class Moroes(Minion):
    def __init__(self,name="Moroes",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.stealth=True
        self.trigger_event_type="end of turn"
        
    def trigger_effect(self,triggering_player):
        if triggering_player is self.owner:
            super(self.__class__,self).trigger_effect(triggering_player)
            minion=Steward(owner=self.owner)
            self.summon(minion)

class Steward(Minion):
    def __init__(self,name="Steward",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Barnes(Minion):
    def __init__(self,name="Barnes",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
                
    def battlecry(self,target=None):
        target=self.owner.search_card(self.owner.deck.cards,"Minion")
        if target is not None:
            minion_copy = getattr(card_collection,database.cleaned(target.name))(owner=target.owner)
            minion_copy.set_stats(1,1)
            self.summon(minion_copy)
                                                                                                                                                                                                                                                                                  
class Prince_Malchezaar(Minion):
    def __init__(self,name="Prince Malchezaar",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
    
    def start_of_game(self):
        cards=[]
        for i in range(5):
            card=database.get_random_cards("[rarity]='Legendary' AND [type]='Minion' AND ([class]='Neutral' or [class] LIKE '%"+self.owner.class_name+"%')", owner=self.owner, k=1)[0]
            cards.append(card)
            self.owner.deck.add_card(card)
        
        prince_malchezaar_animation(self,cards)

class The_Curator(Minion):
    def __init__(self,name="The Curator",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
                
    def battlecry(self,target=None):
        targets=[]
        for race in ["Beast","Dragon","Murloc"]:
            target=self.owner.search_card(self.owner.deck.cards,card_type=race)
            if target is not None:
                self.owner.draw(target=target)

class Medivh_the_Guardian(Minion):
    def __init__(self,name="Medivh, the Guardian",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        weapon=Atiesh(owner=self.owner)
        self.owner.equip_weapon(weapon)

class Patches_the_Pirate(Minion):
    def __init__(self,name="Patches the Pirate",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="play a card"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.side==self.side and triggering_card.has_race("Pirate") and self in triggering_card.owner.deck.cards:
            patches_the_pirate_animation(self)
            self.owner.recruit(self)

class Auctionmaster_Beardo(Minion):
    def __init__(self,name="Auctionmaster Beardo",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="play a card"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.isSpell and triggering_card.owner is self.owner:
            super(self.__class__,self).trigger_effect(triggering_card)
            gadgetzan_auctioneer_animation(self)
            self.owner.hero_power.refresh()

class Sergeant_Sally(Minion):
    def __init__(self,name="Sergeant Sally",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        unstable_ghoul_animation(self)
        targets=self.enemy_minions()
        self.deal_damage(targets, [self.get_current_atk()]*len(targets))
        
class Genzo_the_Shark(Minion):
    def __init__(self,name="Genzo, the Shark",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="attack"
        
    def trigger_effect(self,triggering_minion):
        if triggering_minion is self:
            super(self.__class__,self).trigger_effect(triggering_minion)
            for player in [self.owner,self.owner.opponent]:
                while len(player.hand)<3:
                    player.draw()

class Finja_the_Flying_Star(Minion):
    def __init__(self,name="Finja, the Flying Star",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.stealth=True
        self.trigger_event_type="after attack"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card is self and self.target.destroyed_by is self:
            super(self.__class__,self).trigger_effect(triggering_card)
            for i in range(2):
                minion = self.owner.search_card(self.owner.deck.cards,"Murloc")
                if minion is not None:
                    self.recruit(minion)

class Madam_Goya(Minion):
    def __init__(self,name="Madam Goya",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def get_target(self):
        minion=choose_target(chooser=self,target="friendly minion",message="swap with a random minion in deck")
        return minion
    
    def battlecry(self,target):
        minion = self.owner.search_card(self.owner.deck.cards,"Minion")
        if minion is not None:
            location=target.location
            target.shuffle_into_deck()
            self.recruit(minion,location)

class Wrathion(Minion):
    def __init__(self,name="Wrathion",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True

    def battlecry(self,target):
        while True:
            card=self.owner.draw()
            if not card.has_race("Dragon"):
                break

class Mayor_Noggenfogger(Minion):
    def __init__(self,name="Mayor Noggenfogger",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    #Incomplete


class Spiritsinger_Umbra(Minion):
    def __init__(self,name="Spiritsinger Umbra",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="summon a minion"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.side==self.side and triggering_card.has_deathrattle and triggering_card is not self:
            super(self.__class__,self).trigger_effect(triggering_card)
            triggering_card.trigger_deathrattle()

class The_Voraxx(Minion):
    def __init__(self,name="The Voraxx",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="play a card"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.isSpell and triggering_card.side==self.side and triggering_card.target is self:
            super(self.__class__,self).trigger_effect(triggering_card)
            minion=Plant(owner=self.owner)
            spell_copy=getattr(card_collection,database.cleaned(triggering_card.name))(owner=self.owner)
            self.summon(minion)
            spell_copy.invoke(minion)

class Elise_the_Trailblazer(Minion):
    def __init__(self,name="Elise the Trailblazer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def battlecry(self,target=None):
        card=UnGoro_Pack(owner=self.owner)
        card.initialize_location(self.location)
        deck_in_animation(card,self.owner.deck)
        self.owner.deck.add_card(card) 

class UnGoro_Pack(Spell):
    def __init__(self,name="Un'Goro Pack",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        cards=[]
        for i in range(min(5,self.owner.hand_limit-len(self.owner.hand))):
            card = database.get_random_cards("[cardset] LIKE '%Journey to Un%'", self.owner, 1)[0]
            cards.append(card)
            self.owner.add_hand(card)
        ungoro_pack_animation(cards)

class Hemet_Jungle_Hunter(Minion):
    def __init__(self,name="Hemet, Jungle Hunter",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def battlecry(self,target=None):
        if len(self.owner.deck.cards)>0:
            big_game_hunter_animation(self, self.owner.deck.cards[0])
            card_pool=[]
            for card in self.owner.deck.cards:
                card_pool.append(card)
                
            for card in card_pool:
                if card.cost<=3:
                    move_animation(card,dest=(card.location[0]-80,card.location[1]-50),speed=80)
                    self.owner.deck.cards.remove(card)
                    card.burn(skip_animation=True)
                
class Ozruk(Minion):
    def __init__(self,name="Ozruk",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True

    def battlecry(self,target=None):
        if self.owner.turn>1:
            count=0
            for card in self.owner.played_cards[self.owner.turn-1]:
                if card.has_race("Elemental"):
                    count+=1
                    buff_animation(self,speed=25)
            self.buff_stats(0,5*count)

class Prince_Keleseth(Minion):
    def __init__(self,name="Prince Keleseth",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        if self.owner.deck.has_no_cost(2):
            prince_keleseth_animation(self)
            for target in self.owner.deck.cards:
                if target.isMinion():
                    target.buff_stats(1,1)

class Prince_Taldaram(Minion):
    def __init__(self,name="Prince Taldaram",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.tags.append("Targeted")

    def get_target(self):
        target=None
        if self.owner.deck.has_no_cost(3):
            target=choose_target(chooser=self,target="minion",message="become a copy of it")
        return target
        
    def battlecry(self,target):
        minion_copy=target.get_copy(owner=self.owner)
        minion_copy.copy_stats(target)
        minion_copy.set_stats(3,3)
        self.transform(minion_copy,come_onto_board=False)
        self.owner.board.queue.append(minion_copy)

class Prince_Valanar(Minion):
    def __init__(self,name="Prince Valanar",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target):
        if self.owner.deck.has_no_cost(4):
            self.gain_lifesteal()
            self.gain_taunt()

class Arfus(Minion):
    def __init__(self,name="Arfus",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        death_knight_cards=[Death_Coil,Death_Grip,Obliterate,Death_and_Decay,Anti_Magic_Shell,Doom_Pact,Army_of_the_Dead,Frostmourne]
        card=random.choice(death_knight_cards)(owner=self.owner)
        card.initialize_location(self.location)
        card.hand_in()

class The_Lich_King(Minion):
    def __init__(self,name="The Lich King",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source) 
        self.taunt=True
        self.trigger_event_type="end of turn"
       
    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner:
            super(self.__class__,self).trigger_effect(triggering_player)
            death_knight_cards=[Death_Coil,Death_Grip,Obliterate,Death_and_Decay,Anti_Magic_Shell,Doom_Pact,Army_of_the_Dead,Frostmourne]
            card=random.choice(death_knight_cards)(owner=self.owner)
            card.initialize_location(self.location)
            nether_portal_animation(self)
            card.hand_in()
            
class Death_Coil(Spell):
    def __init__(self,name="Death Coil",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        soulfire_animation(self,target)
        if target.side==self.side:
            self.heal([target],[5])
        else:
            self.deal_damage([target], [5])

class Death_Grip(Spell):
    def __init__(self,name="Death Grip",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        if len(self.owner.opponent.deck.cards)>0:
            card=random.choice(self.owner.opponent.deck.cards)
            self.owner.opponent.deck.cards.remove(card)
            card.owner=self.owner
            card.side=self.side
            card.appear_in_hand()

class Obliterate(Spell):
    def __init__(self,name="Obliterate",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return target is not None and target.isMinion()
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        damage=target.get_current_hp()
        charge_shot_animation(self, target)
        target.destroy()
        self.deal_damage([self.owner], [damage])

class Death_and_Decay(Spell):
    def __init__(self,name="Death and Decay",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        minions=self.enemy_minions()
        arcane_explosion_animation(self)
        self.deal_damage(minions, [3]*len(minions))

class Anti_Magic_Shell(Spell):
    def __init__(self,name="Anti-Magic Shell",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self, target):
        return len(self.friendly_minions())>0
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        minions=self.friendly_minions()
        light_buff_multiple_animation(self, minions)
        for minion in minions:
            minion.buff_stats(2,2)
            minion.gain_elusive()

class Doom_Pact(Spell):
    def __init__(self,name="Doom Pact",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
       
    def invoke(self,target):
        super(self.__class__,self).invoke()
        minions=self.all_minions()
        DOOM_animation(self,minions)
        destroy_multiple_animation(minions)
        for minion in minions:
            minion.destroy(skip_animation=True)
            card=self.owner.deck.top()
            if not card.isFatigue():
                card.burn()            

class Army_of_the_Dead(Spell):
    def __init__(self,name="Army of the Dead",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
       
    def invoke(self,target):
        super(self.__class__,self).invoke()
        for i in range(5):
            card=self.owner.deck.top()
            if not card.isFatigue():
                if card.isMinion():
                    card.initialize_location("board")
                    self.owner.recruit(card,speed=50)
                else:
                    card.burn(skip_animation=True)  
                                                                                                                                                                                                                                                        
class Frostmourne(Weapon):
    def __init__(self,name="Frostmourne",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.killed_minions=[]

    def trigger_after_effect(self, target=None):
        if target.destroyed_by is self:
            self.killed_minions.append(target)
        super(self.__class__,self).trigger_after_effect(target)

    def deathrattle(self):
        for minion in self.killed_minions:
            minion_copy=minion.get_copy(owner=self.owner)
            minion_copy.initialize_location("board")
            self.owner.recruit(minion_copy)

class Zola_the_Gorgon(Minion):
    def __init__(self,name="Zola the Gorgon",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.tags.append("Targeted")
        
    def get_target(self):
        minion=choose_target(chooser=self,target="friendly minion",message="get a Golden copy of it")
        return minion
    
    def battlecry(self,target):
        minion_copy=target.get_copy(owner=self.owner)
        minion_copy.initialize_location(target.location)
        minion_copy.big_image  = get_image("images/card_images/"+minion_copy.name.replace(":","").replace('"',"")+"_gold.png",(265,367)) 
        minion_copy.raw_image  = get_image("images/card_images/"+minion_copy.name.replace(":","").replace('"',"")+"_gold.png",(265,367)) 
        minion_copy.mini_image = get_image("images/card_images/"+minion_copy.name.replace(":","").replace('"',"")+"_gold.png",(103,141))
        minion_copy.image = minion_copy.mini_image
        minion_copy.hand_in()

class The_Darkness(Minion):
    def __init__(self,name="The Darkness",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.dormant=True
        self.dormant_cap=3
        #self.current_hp=1
    
    def battlecry(self,target):
        for i in range(3):
            card=Darkness_Candle(owner=self.owner.opponent)
            card.origin=self
            card.initialize_location(self.location)
            card.shuffle_into_deck(skip_zoom=(i>=1))

    def refresh_status(self):
        if not self.has_dormant:
            super(self.__class__,self).refresh_status()
        
class Darkness_Candle(Spell):
    def __init__(self,name="Darkness Candle",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        self.casts_when_drawn=True

    def invoke(self,target=None):
        super(self.__class__,self).invoke()
        self.origin.increment_dormant_counter()

class King_Togwaggle(Minion):
    def __init__(self,name="King Togwaggle",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def battlecry(self,target):
        self.owner.swap_deck()
        card=Kings_Ransom(owner=self.owner.opponent)
        card.appear_in_hand()

class Kings_Ransom(Spell):
    def __init__(self,name="King's Ransom",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)

    def invoke(self,target=None):
        super(self.__class__,self).invoke()
        self.owner.swap_deck()

class Marin_the_Fox(Minion):
    def __init__(self,name="Marin the Fox",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def battlecry(self,target):
        minion=Master_Chest(owner=self.owner.opponent)
        self.summon(minion)

class Master_Chest(Minion):
    def __init__(self,name="Master Chest",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        card=random.choice([Golden_Kobold,Tolins_Goblet,Wondrous_Wand,Zarogs_Crown])(owner=self.owner.opponent)
        card.initialize_location(self.location)
        card.hand_in()

class Golden_Kobold(Minion):
    def __init__(self,name="Golden Kobold",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        
    def battlecry(self,target=None):
        golden_monkey_animation(self)
        for card in self.owner.hand+self.owner.deck.cards:
            minion = database.get_random_cards("[type]='Minion' AND [rarity]='Legendary'", self.owner, 1)[0]
            card.replace_by(minion)

class Tolins_Goblet(Spell):
    def __init__(self,name="Tolin's Goblet",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        card=self.owner.draw()
        for i in range(self.owner.hand_limit):
            card_copy=card.get_copy(owner=self.owner)
            card_copy.initialize_location(self.owner.location)
            card_copy.hand_in(speed=40)

class Wondrous_Wand(Spell):
    def __init__(self,name="Wondrous Wand",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        for i in range(3):
            card=self.owner.draw()
            card.current_cost=0

class Zarogs_Crown(Spell):
    def __init__(self,name="Zarog's Crown",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        minion=self.discover(filter_str="[type]='Minion' and [rarity]='Legendary'")
        if minion is not None:
            for i in range(2):
                minion_copy=minion.get_copy(owner=self.owner)
                minion_copy.initialize_location("board")
                self.owner.recruit(minion_copy)

class Master_Oakheart(Minion):
    def __init__(self,name="Master Oakheart",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        for atk in [1,2,3]:
            pool=[]
            for card in self.owner.deck.cards:
                if card.isMinion() and card.temp_atk==atk:
                    pool.append(card)
            if len(pool)>0:
                minion = random.choice(pool)
                self.recruit(minion)

class Dollmaster_Dorian(Minion):
    def __init__(self,name="Dollmaster Dorian",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="draw a card"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.isMinion() and triggering_card.side==self.side:
            super(self.__class__,self).trigger_effect(triggering_card)
            minion=triggering_card.get_copy(owner=self.owner)
            minion.set_stats(1,1)
            self.summon(minion)

class Azalina_Soulthief(Minion): 
    def __init__(self,name="Azalina Soulthief",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def battlecry(self,target):
        hand_copy=[]
        for card in self.owner.hand:
            hand_copy.append(card)
            card.board_area="Burn"
        for card in hand_copy:
            self.owner.hand.remove(card)    
        self.hand=[]
        for card in self.owner.opponent.hand:
            card_copy=card.get_copy(owner=self.owner)
            card_copy.initialize_location(card.location)
            card_copy.hand_in(speed=30)

        
        
                                                                                                                                               
class Genn_Greymane(Minion):
    def __init__(self,name="Genn Greymane",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
    
    def start_of_game(self):
        if self.owner.deck.has_even_cards_only():
            upgrade_hero_power_animation(self)
            self.owner.hero_power.current_cost=1
            self.owner.hero_power.refresh()
                        
class Baku_the_Mooneater(Minion):
    def __init__(self,name="Baku the Mooneater",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
    
    def start_of_game(self):
        if self.owner.deck.has_odd_cards_only():
            upgrade_hero_power_animation(self)
            self.owner.hero_power.upgrade()

                                                                                                                                                                                                                                   
'''Demon Hunter Minions'''
        
class Shadowhoof_Slayer(Minion):
    def __init__(self,name="Shadowhoof Slayer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        zodiac_animation(self.owner, self.card_class)
        self.owner.current_atk+=1

class Battlefiend(Minion):
    def __init__(self,name="Battlefiend",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="after attack"
        
    def trigger_effect(self, triggering_player=None):
        if triggering_player is self.owner:
            super(self.__class__,self).trigger_effect(triggering_player)
            buff_animation(self)
            self.buff_stats(1, 0) 

class Urzul_Horror(Minion):
    def __init__(self,name="Ur'zul Horror",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        minion=Lost_Soul(owner=self.owner,source=self.location)
        minion.hand_in()
           
class Sightless_Watcher(Minion):
    def __init__(self,name="Sightless Watcher",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        cards=random.sample(self.owner.deck.cards,k=min(3,len(self.owner.deck.cards)))
        selected_card = choose_one(cards)
        self.owner.deck.cards.remove(selected_card)
        self.owner.deck.cards.insert(0,selected_card)

class Illidari_Initiate(Minion):
    def __init__(self,name="Illidari Initiate",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source) 
        self.rush=True

class Felwing(Minion):
    def __init__(self,name="Felwing",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source) 

class Lost_Soul(Minion):
    def __init__(self,name="Lost Soul",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source) 
                                            
class Satyr_Overseer(Minion):
    def __init__(self,name="Satyr Overseer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="after attack"
        
    def trigger_effect(self, triggering_player=None):
        if triggering_player is self.owner:
            super(self.__class__,self).trigger_effect(triggering_player)
            minion=Illidari_Satyr(owner=self.owner,source=self.location)
            self.summon(minion)                         

class Illidari_Satyr(Minion):
    def __init__(self,name="Illidari Satyr",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Glaivebound_Adept(Minion):
    def __init__(self,name="Glaivebound Adept",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=None
        if self.owner.attacked:
            target=choose_target(chooser=self,target="character",message="deal 4 damage")
        return target
    
    def battlecry(self,target):
        glaivebound_adept_animation(self, target)
        self.deal_damage([target], [4])
        
class Crimson_Sigil_Runner(Minion):
    def __init__(self,name="Crimson Sigil Runner",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def outcast(self):
        super(self.__class__,self).outcast()
        self.owner.draw()
        
class Illidari_Felblade(Minion):
    def __init__(self,name="Illidari Felblade",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.rush=True
        
    def outcast(self):
        super(self.__class__,self).outcast()
        self.temporary_effects['immune']=True

class Raging_Felscreamer(Minion):
    def __init__(self,name="Raging Felscreamer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def battlecry(self,target=None):
        mage_minion_animation(self)
        card=Raging_Felscreamer_Effect(owner=self.owner)
        
class Raging_Felscreamer_Effect(Enchantment):
    def __init__(self,name="Raging Felscreamer",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_events=[("play a card",self.trigger_effect)]

    def ongoing_effect(self,target):
        if target.side==self.side and target.board_area=="Hand" and target.has_race("Demon"):
            return {'cost':-2}
        else:
            return {}            
        
    def trigger_effect(self, triggering_card):
        if triggering_card.side==self.side and triggering_card.has_race("Demon"):
            self.destroy()

class Hulking_Overfiend(Minion):
    def __init__(self,name="Hulking Overfiend",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.rush=True
        self.trigger_event_type="after attack"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card is self and self.target.destroyed_by is self:
            super(self.__class__,self).trigger_effect(triggering_card)
            self.attacked=False

class Wrathscale_Naga(Minion):
    def __init__(self,name="Wrathscale Naga",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="minion dies"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.side==self.side and triggering_card is not self:
            super(self.__class__,self).trigger_effect(triggering_card)
            target_pool=self.enemy_characters()
            target=random.choice(target_pool)
            soul_cleave_animation(self, [target])
            self.deal_damage([target], [3])

class Wrathspike_Brute(Minion):
    def __init__(self,name="Wrathspike Brute",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        self.trigger_event_type="after attack"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.target is self:
            super(self.__class__,self).trigger_effect(triggering_card)
            targets=self.enemy_characters()
            dread_infernal_animation(self)
            self.deal_damage(targets, [1]*len(targets))

class Altruis_the_Outcast(Minion):
    def __init__(self,name="Altruis the Outcast",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="play a card"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.side==self.side and triggering_card.trigger_outcast and triggering_card is not self:
            super(self.__class__,self).trigger_effect(triggering_card)
            targets=self.enemy_characters()
            dread_infernal_animation(self)
            self.deal_damage(targets, [1]*len(targets))

class Nethrandamus(Minion):
    def __init__(self,name="Nethrandamus",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="minion dies"
        self.level=0
    
    def battlecry(self,target=None):
        for i in range(2):
            minion = database.get_random_cards("[type]='Minion' AND [cost]="+str(self.level), self.owner, 1)[0]
            self.summon(minion,left=(-1)**i,speed=60)
            
    def trigger_effect(self, triggering_card=None):
        if triggering_card.side==self.side and self.board_area=="Hand" and self.level<10:
            self.level+=1
                                                                                        
'''Druid Minions'''
class Panther_Power_of_the_Wild(Minion):
    def __init__(self,name="Panther (Power of the Wild)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
              
class Treant_Classic(Minion):
    def __init__(self,name="Treant (Classic)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Treant_Force_of_Nature(Minion):
    def __init__(self,name="Treant (Force of Nature)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Treant_Shandos_Lesson(Minion):
    def __init__(self,name="Treant (Shan'do's Lesson)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True

class Treant_Poison_Seeds(Minion):
    def __init__(self,name="Treant (Shan'do's Lesson)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
                       
class Ironbark_Protector(Minion):
    def __init__(self,name="Ironbark Protector",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True

class Druid_of_the_Claw(Minion):
    def __init__(self,name="Druid of the Claw",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.options=[Cat_Form,Bear_Form]
        
    def trigger_choose_one(self):
        selected_card = choose_one([option(owner=self.owner) for option in self.options])
        selected_form = getattr(card_collection,"Druid_of_the_Claw_"+selected_card.__class__.__name__)(owner=self.owner,source=(self.rect.x,self.rect.y))
        self.transform(selected_form)
    
    def trigger_choose_both(self):
        minion         = Druid_of_the_Claw_Combined(owner=self.owner,source=(self.rect.x,self.rect.y))
        self.transform(minion)

class Cat_Form(Spell):
    def __init__(self,name="Cat Form",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        
class Bear_Form(Spell):
    def __init__(self,name="Bear Form",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
                
class Druid_of_the_Claw_Cat_Form(Minion):
    def __init__(self,name="Druid of the Claw (Cat Form)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.charge=True
        
class Druid_of_the_Claw_Bear_Form(Minion):
    def __init__(self,name="Druid of the Claw (Bear Form)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source) 
        self.taunt=True

class Druid_of_the_Claw_Combined(Minion):
    def __init__(self,name="Druid of the Claw (Combined)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source) 
        self.charge=True
        self.taunt=True
        
class Keeper_of_the_Grove(Minion):
    def __init__(self,name="Keeper of the Grove",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.options=[Dispel,Moonfire_Choose_One]
        
    def trigger_choose_one(self):
        selected_card = choose_one([option(owner=self.owner) for option in self.options])
        selected_card.origin=self
        selected_card.invoke()    

            
class Moonfire_Choose_One(Spell):
    def __init__(self,name="Moonfire (Choose One)",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self,target):
        return target is not None
    
    def invoke(self,target=None):
        if target is None:
            target=choose_target(self.origin, target="character", message=self.card_text)
        if self.is_valid_on(target):
            moonfire_animation(self,target)
            self.origin.deal_damage([target],[2])

class Dispel(Spell):
    def __init__(self,name="Dispel",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)

    def is_valid_on(self,target):
        return target is not None and target.isMinion()
        
    def invoke(self,target=None):
        if target is None:
            target=choose_target(self.origin, target="minion", message=self.card_text)
        if self.is_valid_on(target):
            self.origin.silence(target)

class Ancient_of_Lore(Minion):
    def __init__(self,name="Ancient of Lore",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.options=[Ancient_Teachings,Ancient_Secrets]
        
    def trigger_choose_one(self):
        selected_card = choose_one([option(owner=self.owner) for option in self.options])
        selected_card.origin=self
        selected_card.invoke()    
     
class Ancient_Teachings(Spell):
    def __init__(self,name="Ancient Teachings",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target=None):
        self.owner.draw()

class Ancient_Secrets(Spell):
    def __init__(self,name="Ancient Secrets",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self,target):
        return target is not None
    
    def invoke(self,target=None):
        if target is None:
            target=choose_target(self, target="character", message=self.card_text)
        if self.is_valid_on(target):
            self.heal([target], [5])

class Ancient_of_War(Minion):
    def __init__(self,name="Ancient of War",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.options=[Uproot,Rooted]
        
    def trigger_choose_one(self):
        selected_card = choose_one([option(owner=self.owner) for option in self.options])
        selected_card.origin=self
        selected_card.invoke()    
     
class Uproot(Spell):
    def __init__(self,name="Uproot",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target=None):
        self.origin.buff_stats(5,0)

class Rooted(Spell):
    def __init__(self,name="Rooted",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target=None):
        self.origin.buff_stats(0,5)
        self.origin.gain_taunt()

class Anodized_Robo_Cub(Minion):
    def __init__(self,name="Anodized Robo Cub",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        self.options=[Attack_Mode,Tank_Mode]
        
    def trigger_choose_one(self):
        selected_card = choose_one([option(owner=self.owner) for option in self.options])
        selected_card.origin=self
        selected_card.invoke()    
     
class Attack_Mode(Spell):
    def __init__(self,name="Attack Mode",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target=None):
        self.origin.buff_stats(1,0)

class Tank_Mode(Spell):
    def __init__(self,name="Tank Mode",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target=None):
        self.origin.buff_stats(0,1)

class Druid_of_the_Fang(Minion):
    def __init__(self,name="Druid of the Fang",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        if self.owner.control("Beast"):
            minion=Druid_of_the_Fang_Beast(owner=self.owner)
            self.transform(minion)

class Druid_of_the_Fang_Beast(Minion):
    def __init__(self,name="Druid of the Fang (Beast)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Grove_Tender(Minion):
    def __init__(self,name="Grove Tender",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.options=[Gift_of_Mana,Gift_of_Cards]
        
    def trigger_choose_one(self):
        selected_card = choose_one([option(owner=self.owner) for option in self.options])
        selected_card.origin=self
        selected_card.invoke()    
     
class Gift_of_Mana(Spell):
    def __init__(self,name="Gift of Mana",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target=None):
        self.owner.gain_mana()
        self.owner.opponent.gain_mana()

class Gift_of_Cards(Spell):
    def __init__(self,name="Gift of Cards",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target=None):
        self.owner.draw()
        self.owner.opponent.draw()
              
class Mech_Bear_Cat(Minion):
    def __init__(self,name="Mech Bear Cat",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="minion damage"
        
    def trigger_effect(self,triggering_entity):
        if triggering_entity[0] is self:
            super(self.__class__,self).trigger_effect(self)
            self.give_random_spare_part(self.owner)

class Druid_of_the_Flame(Minion):
    def __init__(self,name="Druid of the Flame",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.options=[Firecat_Form,Fire_Hawk_Form]
        
    def trigger_choose_one(self):
        selected_card = choose_one([option(owner=self.owner) for option in self.options])
        selected_form=getattr(card_collection,"Druid_of_the_Flame_"+selected_card.__class__.__name__)(owner=self.owner,source=(self.rect.x,self.rect.y))
        self.transform(selected_form)
    
    def trigger_choose_both(self):
        minion         = Druid_of_the_Flame_Combined(owner=self.owner,source=(self.rect.x,self.rect.y))
        self.transform(minion)
        
class Firecat_Form(Spell):
    def __init__(self,name="Firecat Form",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        
class Fire_Hawk_Form(Spell):
    def __init__(self,name="Fire Hawk Form",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)

class Druid_of_the_Flame_Firecat_Form(Minion):
    def __init__(self,name="Druid of the Flame (Firecat Form)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        
class Druid_of_the_Flame_Fire_Hawk_Form(Minion):
    def __init__(self,name="Druid of the Flame (Fire Hawk Form)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source) 
        
class Druid_of_the_Flame_Combined(Minion):
    def __init__(self,name="Druid of the Flame (Combined)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source) 
        
class Volcanic_Lumberer(Minion):
    def __init__(self,name="Volcanic Lumberer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        
    def ongoing_effect(self,target):
        if target is self and target.board_area=="Hand":
            n=self.owner.get_num_minions_died()
            return {'cost':-n}
        else:
            return {} 

class Sapling(Minion):
    def __init__(self,name="Sapling",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Druid_of_the_Saber(Minion):
    def __init__(self,name="Druid of the Saber",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.options=[Lion_Form,Panther_Form]
        
    def trigger_choose_one(self):
        selected_card = choose_one([option(owner=self.owner) for option in self.options])
        selected_form=getattr(card_collection,"Sabertooth_"+selected_card.__class__.__name__.replace("_Form",""))(owner=self.owner,source=(self.rect.x,self.rect.y))
        self.transform(selected_form)
    
    def trigger_choose_both(self):
        minion         = Tiger_Form(owner=self.owner,source=(self.rect.x,self.rect.y))
        self.transform(minion)
        
class Lion_Form(Spell):
    def __init__(self,name="Lion Form",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        
class Sabertooth_Lion(Minion):
    def __init__(self,name="Sabertooth Lion",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.charge=True 

class Panther_Form(Spell):
    def __init__(self,name="Panther Form",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        
class Sabertooth_Panther(Minion):
    def __init__(self,name="Sabertooth Panther",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.stealth=True
                        
class Tiger_Form(Minion):
    def __init__(self,name="Tiger Form",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.charge=True
        self.stealth=True 

class Wildwalker(Minion):
    def __init__(self,name="Wildwalker",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(chooser=self,target="friendly minion",target_type="Beast",message="give +3 Health")
        return target
    
    def battlecry(self,target):
        rage_buff_animation(target)
        target.buff_stats(0,3)
        
class Darnassus_Aspirant(Minion):
    def __init__(self,name="Darnassus Aspirant",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        self.owner.gain_mana()

    def deathrattle(self):
        self.owner.gain_mana(-1)

class Savage_Combatant(Minion):
    def __init__(self,name="Savage Combatant",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.inspire=True
        
    def trigger_inspire(self, hero_power=None):
        if hero_power.owner is self.owner:
            super(self.__class__,self).trigger_inspire()
            savage_roar_animation(self, [])
            self.owner.current_atk+=2

class Knight_of_the_Wild(Minion):
    def __init__(self,name="Knight of the Wild",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="summon a minion"
        
    def trigger_effect(self,triggering_minion):
        if self.board_area=="Hand" and triggering_minion.side==self.side and triggering_minion.has_race("Beast"):
            self.modify_cost(-1)

class Mounted_Raptor(Minion):
    def __init__(self,name="Mounted Raptor",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        minion = database.get_random_cards("[type]='Minion' AND [cost]=1", self.owner, 1)[0]
        self.summon(minion)

class Jungle_Moonkin(Minion):
    def __init__(self,name="Jungle Moonkin",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.spell_damage_boost=2
        self.opponent_spell_damage_boost=2

class Dark_Arakkoa(Minion):
    def __init__(self,name="Dark Arakkoa",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        self.buff_cthun(3,3)

class Addled_Grizzly(Minion):
    def __init__(self,name="Addled Grizzly",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="summon a minion"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.owner is self.owner and triggering_card is not self:
            super(self.__class__,self).trigger_effect(triggering_card)
            rage_buff_animation(triggering_card)
            triggering_card.buff_stats(1,1)

class Klaxxi_Amber_Weaver(Minion):
    def __init__(self,name="Klaxxi Amber Weaver",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        if self.eval_cthun(atk=10):
            buff_animation(self)
            self.buff_stats(0, 5)

class Mire_Keeper(Minion):
    def __init__(self,name="Mire Keeper",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.options=[YShaarjs_Strength,Yogg_Sarons_Magic]
        
    def trigger_choose_one(self):
        selected_card = choose_one([option(owner=self.owner) for option in self.options])
        selected_card.origin=self
        selected_card.invoke()    

class YShaarjs_Strength(Spell):
    def __init__(self,name="Y'Shaarj's Strength",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target=None):
        minion=Slime_Mire_Keeper(owner=self.owner)
        self.origin.summon(minion)

class Slime_Mire_Keeper(Minion):
    def __init__(self,name="Slime (Mire Keeper)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        
class Yogg_Sarons_Magic(Spell):
    def __init__(self,name="Yogg-Saron's Magic",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target=None):
        wild_growth_animation(self)
        self.owner.gain_mana(empty=True)

class Forbidden_Ancient(Minion):
    def __init__(self,name="Forbidden Ancient",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        buff_animation(self)
        self.buff_stats(self.owner.current_mana,self.owner.current_mana)
        self.owner.current_mana=0

class Enchanted_Raven(Minion):
    def __init__(self,name="Enchanted Raven",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

class Menagerie_Warden(Minion):
    def __init__(self,name="Menagerie Warden",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(chooser=self,target="friendly minion",target_type="Beast", message="summon a copy of it")
        return target
    
    def battlecry(self,target):
        minion_copy=getattr(card_collection,database.cleaned(target.name))(owner=self.owner)
        self.summon(minion_copy)

class Jade_Behemoth(Minion):
    def __init__(self,name="Jade Behemoth",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        
    def battlecry(self,target=None):
        minion = Jade_Golem(owner=self.owner)
        self.summon(minion)

class Virmen_Sensei(Minion):
    def __init__(self,name="Virmen Sensei",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(chooser=self,target="friendly minion",target_type="Beast",message="+2/+2 and Taunt")
        return target
    
    def battlecry(self,target):
        target.buff_stats(2,2)

class Celestial_Dreamer(Minion):
    def __init__(self,name="Celestial Dreamer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
    
    def battlecry(self,target):
        for minion in self.friendly_minions():
            if minion.get_current_atk()>=5:
                buff_animation(self)
                self.buff_stats(2,2)
                break

class Tortollan_Forager(Minion):
    def __init__(self,name="Tortollan Forager",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        minion = database.get_random_cards("[type]='Minion' AND [attack]>=5", self.owner, 1)[0]
        minion.initialize_location(self.location)
        minion.hand_in()

class Elder_Longneck(Minion):
    def __init__(self,name="Elder Longneck",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        for card in self.owner.hand:
            if card.isMinion() and card.temp_atk>=5:
                self.adapt()
                break

class Shellshifter(Minion):
    def __init__(self,name="Shellshifter",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.options=[Raptor_Form,Direhorn_Form]
        
    def trigger_choose_one(self):
        selected_card = choose_one([option(owner=self.owner) for option in self.options])
        selected_form=getattr(card_collection,"Shellshifter_"+selected_card.__class__.__name__)(owner=self.owner,source=(self.rect.x,self.rect.y))
        self.transform(selected_form)
    
    def trigger_choose_both(self):
        minion         = Shellshifter_Combined(owner=self.owner,source=(self.rect.x,self.rect.y))
        self.transform(minion)
        
class Raptor_Form(Spell):
    def __init__(self,name="Raptor Form",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        
class Direhorn_Form(Spell):
    def __init__(self,name="Direhorn Form",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)

class Shellshifter_Raptor_Form(Minion):
    def __init__(self,name="Shellshifter (Raptor Form)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.stealth=True
        
class Shellshifter_Direhorn_Form(Minion):
    def __init__(self,name="Shellshifter (Direhorn Form)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source) 
        self.taunt=True
        
class Shellshifter_Combined(Minion):
    def __init__(self,name="Shellshifter (Combined)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source) 
        self.stealth=True
        self.taunt=True

class Mana_Treant(Minion):
    def __init__(self,name="Mana Treant",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

    def deathrattle(self):
        self.owner.gain_mana(empty=True)

class Giant_Anaconda(Minion):
    def __init__(self,name="Giant Anaconda",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        target_pool=[]
        for card in self.owner.hand:
            if card.isMinion() and card.temp_atk>=5:
                target_pool.append(card)
        if len(target_pool)>0:
            minion=random.choice(target_pool)
            self.owner.put_into_battlefield(minion)

class Crypt_Lord(Minion):
    def __init__(self,name="Crypt Lord",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        self.trigger_event_type="summon a minion"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.side==self.side and triggering_card is not self:
            super(self.__class__,self).trigger_effect(triggering_card)
            buff_animation(self)
            self.buff_stats(0,1)

class Druid_of_the_Swarm(Minion):
    def __init__(self,name="Druid of the Swarm",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.options=[Spider_Form,Scarab_Form]
        
    def trigger_choose_one(self):
        selected_card = choose_one([option(owner=self.owner) for option in self.options])
        selected_form=getattr(card_collection,"Druid_of_the_Swarm_"+selected_card.__class__.__name__)(owner=self.owner,source=(self.rect.x,self.rect.y))
        self.transform(selected_form)
    
    def trigger_choose_both(self):
        minion         = Druid_of_the_Swarm_Combined(owner=self.owner,source=(self.rect.x,self.rect.y))
        self.transform(minion)
        
class Spider_Form(Spell):
    def __init__(self,name="Spider Form",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        
class Scarab_Form(Spell):
    def __init__(self,name="Scarab Form",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)

class Druid_of_the_Swarm_Spider_Form(Minion):
    def __init__(self,name="Druid of the Swarm (Spider Form)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.poisonous=True
        
class Druid_of_the_Swarm_Scarab_Form(Minion):
    def __init__(self,name="Druid of the Swarm (Scarab Form)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        
class Druid_of_the_Swarm_Combined(Minion):
    def __init__(self,name="Druid of the Swarm (Combined)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.poisonous=True
        self.taunt=True

class Strongshell_Scavenger(Minion):
    def __init__(self,name="Strongshell Scavenger",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        target_pool=self.friendly_minions()
        targets=[]
        for minion in target_pool:
            if minion.has_taunt:
                targets.append(minion)
                minion.buff_stats(2,2)
                
        buff_multiple_animation(self, targets)

class Fatespinner(Minion):
    def __init__(self,name="Fatespinner",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.options=[Decay,Growth_Fatespinner]
        
    def trigger_choose_one(self):
        selected_card = choose_one([option(owner=self.owner) for option in self.options])
        selected_card.origin=self
        selected_card.invoke()    
     
class Decay(Spell):
    def __init__(self,name="Decay",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target=None):
        self.origin.deathrattles.append([MethodType(self.deathrattle.__func__,self.origin),"???"])
        self.origin.has_deathrattle=True
        
    def deathrattle(self):
        unstable_ghoul_animation(self)
        targets=self.all_minions()
        self.deal_damage(targets, [3]*len(targets))

class Growth_Fatespinner(Spell):
    def __init__(self,name="Growth (Fatespinner)",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target=None):
        self.origin.deathrattles.append([MethodType(self.deathrattle.__func__,self.origin),"???"])
        self.origin.has_deathrattle=True
        
    def deathrattle(self):
        minions=self.all_minions()
        gift_of_the_wild_animation(self,minions) 
        for minion in minions:
            minion.buff_stats(2,2)

class Ghoul_Infestor(Minion):
    def __init__(self,name="Ghoul Infestor",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Ironwood_Golem(Minion):
    def __init__(self,name="Ironwood Golem",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        self.cannot_attack=True

    def ongoing_effect(self,target):
        if target is self and self.owner.shield>=3:
            return {'can attack':True}
        else:
            return {}      

class Greedy_Sprite(Minion):
    def __init__(self,name="Greedy Sprite",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        self.owner.gain_mana()

class Grizzled_Guardian(Minion):
    def __init__(self,name="Grizzled Guardian",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        for i in range(2):
            minion=self.owner.search_card_based_cost(self.owner.deck.cards,card_type="Minion",cost=4,compare="__le__")
            if minion is not None:
                self.recruit(minion)

class Astral_Tiger(Minion):
    def __init__(self,name="Astral Tiger",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        minion_copy=self.get_copy(owner=self.owner)
        minion_copy.initialize_location(self.location)
        minion_copy.shuffle_into_deck(self.owner.deck)

class Treant_Witchwood_Apple(Minion):
    def __init__(self,name="Treant Witchwood Apple",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Druid_of_the_Scythe(Minion):
    def __init__(self,name="Druid of the Scythe",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.options=[Dire_Panther_Form,Dire_Wolf_Form]
        
    def trigger_choose_one(self):
        selected_card = choose_one([option(owner=self.owner) for option in self.options])
        selected_form=getattr(card_collection,"Druid_of_the_Scythe_"+selected_card.__class__.__name__)(owner=self.owner,source=(self.rect.x,self.rect.y))
        self.transform(selected_form)
    
    def trigger_choose_both(self):
        minion         = Druid_of_the_Swarm_Combined(owner=self.owner,source=(self.rect.x,self.rect.y))
        self.transform(minion)
        
class Dire_Panther_Form(Spell):
    def __init__(self,name="Dire Panther Form",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        
class Dire_Wolf_Form(Spell):
    def __init__(self,name="Dire Wolf Form",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)

class Druid_of_the_Scythe_Dire_Panther_Form(Minion):
    def __init__(self,name="Druid of the Scythe (Dire Panther Form)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.rush=True
        
class Druid_of_the_Scythe_Dire_Wolf_Form(Minion):
    def __init__(self,name="Druid of the Scythe (Dire Wolf Form)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        
class Druid_of_the_Scythe_Combined(Minion):
    def __init__(self,name="Druid of the Scythe (Combined)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.rush=True
        self.taunt=True

class Forest_Guide(Minion):
    def __init__(self,name="Forest Guide",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="end of turn"
        
    def trigger_effect(self,triggering_player):
        if triggering_player is self.owner:
            self.owner.draw()
            self.owner.opponent.draw()

class Bewitched_Guardian(Minion):
    def __init__(self,name="Bewitched Guardian",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        
    def battlecry(self,target=None):
        handsize=len(self.owner.hand)
        self.buff_stats(0, handsize)

class Wisp_Wispering_Woods(Minion):
    def __init__(self,name="Wisp (Wispering Woods)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
                                                                                                                                                                                                                                                                                                                                                                       
class Gloom_Stag(Minion):
    def __init__(self,name="Gloom Stag",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        
    def battlecry(self,target=None):
        if self.owner.deck.has_odd_cards_only():
            self.buff_stats(2, 2)
                            
class Cenarius(Minion):
    def __init__(self,name="Cenarius",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.options=[Shandos_Lesson,Demigods_Favor]
           
    def trigger_choose_one(self):
        selected_card = choose_one([option(owner=self.owner) for option in self.options])
        selected_card.origin=self
        cenarius_animation(self)
        selected_card.invoke()    

class Demigods_Favor(Spell):
    def __init__(self,name="Demigod's Favor",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target=None):
        minions=self.friendly_minions()
        minions.remove(self.origin)
        if len(minions)>0:
            gift_of_the_wild_animation(self,minions) 
            for minion in minions:
                minion.buff_stats(2,2)

class Shandos_Lesson(Spell):
    def __init__(self,name="Shan'do's Lesson",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target=None):
        for i in range(2):
            minion=Treant_Shandos_Lesson(owner=self.owner)
            self.origin.summon(minion,left=(-1)**i,speed=60)
                                   
class Malorne(Minion):
    def __init__(self,name="Malorne",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def destroy(self,skip_animation=False,skip_deathrattle=False):

        for deathrattle in self.deathrattles:
            deathrattle[0]()

        if self.board_area!="Deck":
            super(self.__class__,self).destroy(skip_animation=skip_animation,skip_deathrattle=True)
     
    def deathrattle(self):
        if self.board_area=="Board":
            self.shuffle_into_deck(self.owner.deck)

class Aviana(Minion):
    def __init__(self,name="Aviana",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.has_special_summon_effect=True
    
    def special_summoning_effect(self):
        aviana_animation(self) 
                
    def overriding_ongoing_effect(self,target):
        if isinstance(target, Minion) and target.board_area=="Hand" and target.side==self.side:
            return {'cost':1}
        else:
            return {}   
        
class Fandral_Staghelm(Minion):
    def __init__(self,name="Fandral Staghelm",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def ongoing_effect(self,target):
        if not target.isHero() and target.side==self.side and "Choose One" in target.abilities:
            return {'choose both':True}
        else:
            return {}  

class Kun_the_Forgotten_King(Minion):
    def __init__(self,name="Kun the Forgotten King",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.options=[Forgotten_Armor,Forgotten_Mana]
           
    def trigger_choose_one(self):
        selected_card = choose_one([option(owner=self.owner) for option in self.options])
        selected_card.origin=self
        kun_the_forgotten_king_animation(self)
        selected_card.invoke()    

class Forgotten_Armor(Spell):
    def __init__(self,name="Forgotten Armor",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target=None):
        self.owner.increse_shield(10)

class Forgotten_Mana(Spell):
    def __init__(self,name="Forgotten Mana",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target=None):
        self.owner.gain_mana(10)
              
class Barnabus_the_Stomper(Minion):
    def __init__(self,name="Barnabus the Stomper",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        zodiac_animation(self.owner, zodiac=self.card_class)
        for card in self.owner.deck.cards:
            if card.isMinion():
                card.current_cost=0

class Tyrantus(Minion):
    def __init__(self,name="Tyrantus",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.elusive=True

class Hadronox(Minion):
    def __init__(self,name="Hadronox",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        for minion in self.owner.grave[::-1]:
            if minion.taunt:
                minion_copy=minion.get_copy(owner=self.owner)
                self.summon(minion_copy)

class Ixlid_Fungal_Lord(Minion):
    def __init__(self,name="Ixlid, Fungal Lord",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="play a card"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.isMinion() and triggering_card.side==self.side and triggering_card is not self:
            super(self.__class__,self).trigger_effect(self)
            minion_copy=triggering_card.get_copy(owner=self.owner)
            minion_copy.copy_stats(triggering_card)
            self.summon(minion_copy)

class Duskfallen_Aviana(Minion):
    def __init__(self,name="Duskfallen Aviana",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def overriding_ongoing_effect(self,target):
        if target.board_area=="Hand" and target.first_played():
            return {'cost':0}
        else:
            return {}    

class Splintergraft(Minion):
    def __init__(self,name="Splintergraft",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def get_target(self):
        minion=choose_target(chooser=self,target="friendly minion",message="get a 10/10 copy of it")
        return minion
    
    def battlecry(self,target):
        minion_copy=target.get_copy(owner=self.owner)
        minion_copy.initialize_location(target.location)
        minion_copy.set_stats(10,10)
        minion_copy.current_cost=10
        minion_copy.hand_in()
                                                                               
'''Hunter Minions'''
class Timber_Wolf(Minion):
    def __init__(self,name="Timber Wolf",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def ongoing_effect(self,target):
        if target.isMinion() and target.board_area=="Board" and target.side==self.side and target is not self and target.has_race("Beast"):
            return {'atk':1}
        else:
            return {}        

class Huffer(Minion):
    def __init__(self,name="Huffer",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.charge=True
 
        
class Leokk(Minion):
    def __init__(self,name="Leokk",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

    def ongoing_effect(self,target):
        if target.isMinion() and target.board_area=="Board" and target.side==self.side and target is not self:
            return {'atk':1}
        else:
            return {}  

class Misha(Minion):
    def __init__(self,name="Misha",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True

class Houndmaster(Minion):
    def __init__(self,name="Houndmaster",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(chooser=self,target="friendly minion",target_type="Beast",message="+2/+2 and Taunt")
        return target
    
    def battlecry(self,target):
        target.buff_stats(2,2)
        target.gain_taunt()
        
class Starving_Buzzard(Minion):
    def __init__(self,name="Starving Buzzard",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="summon a minion"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.side==self.side and triggering_card is not self and triggering_card.has_race("Beast"):
            super(self.__class__,self).trigger_effect(triggering_card)
            self.owner.draw()

class Tundra_Rhino(Minion):
    def __init__(self,name="Tundra Rhino",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def ongoing_effect(self,target):
        if target.isMinion() and target.side==self.side and target.has_race("Beast"):
            return {'charge':True}
        else:
            return {}

class Hound(Minion):
    def __init__(self,name="Hound",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.charge=True

class Mastiff(Minion):
    def __init__(self,name="Mastiff",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        
class Scavenging_Hyena(Minion):
    def __init__(self,name="Scavenging Hyena",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="minion dies"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.side==self.side and triggering_card.has_race("Beast") and triggering_card is not self:
            super(self.__class__,self).trigger_effect(triggering_card)
            self.buff_stats(2, 1)

class Savannah_Highmane(Minion):
    def __init__(self,name="Savannah Highmane",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        for i in range(2):
            minion=Hyena(owner=self.owner)
            self.summon(minion)

class Hyena(Minion):
    def __init__(self,name="Hyena",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Snake(Minion):
    def __init__(self,name="Snake",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Webspinner(Minion):
    def __init__(self,name="Webspinner",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        card = database.get_random_cards("[race]='Beast'", self.owner, 1)[0]
        card.initialize_location(self.location)
        card.hand_in()

class Metaltooth_Leaper(Minion):
    def __init__(self,name="Metaltooth Leaper",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        self.buff_multiple(race="Mech",atk=2,hp=0)

class King_of_Beasts(Minion):
    def __init__(self,name="King of Beasts",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        n=0
        for target in self.friendly_minions():
            if target.has_race("Beast"):
                n+=1
        self.buff_stats(n, 0)

class Steamwheedle_Sniper(Minion):
    def __init__(self,name="Steamwheedle Sniper",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def ongoing_effect(self,target):
        if target.isHero() and target.side==self.side:
            return {'target minion':True}
        else:
            return {} 

class Core_Rager(Minion):
    def __init__(self,name="Core Rager",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        if self.owner.empty_handed():
            rage_buff_animation(self)
            self.buff_stats(3, 3)
                                            
class Brave_Archer(Minion):
    def __init__(self,name="Brave Archer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.inspire=True
        
    def trigger_inspire(self, hero_power=None):
        if hero_power.owner is self.owner:
            super(self.__class__,self).trigger_inspire()
            if self.owner.empty_handed():
                elven_archer_animation(self, self.owner.opponent)
                self.deal_damage([self.owner.opponent], [2])
                                                                                              
class Kings_Elekk(Minion):
    def __init__(self,name="King's Elekk",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        winner = self.joust("Minion")
        if winner is not None and winner.owner is self.owner:
            self.owner.draw(target=winner)

class Ram_Wrangler(Minion):
    def __init__(self,name="Ram Wrangler",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        if self.owner.control("Beast"):
            minion = database.get_random_cards("[type]='Minion' AND [race]='Beast'", self.owner, 1)[0]
            self.summon(minion)

class Stablemaster(Minion):
    def __init__(self,name="Stablemaster",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(chooser=self,target="friendly minion",target_type="Beast",message="give +3 Health")
        return target
    
    def battlecry(self,target):
        target.temporary_effects['immune']=True

class Desert_Camel(Minion):
    def __init__(self,name="Desert Camel",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        for player in [self.owner,self.owner.opponent]:
            minion=player.search_card_based_cost(player.deck.cards,card_type="Minion",cost=1)
            if minion is not None:
                player.recruit(minion)

class Fiery_Bat(Minion):
    def __init__(self,name="Fiery Bat",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self,target=None):
        target_pool=self.enemy_characters()
        target=random.choice(target_pool)
        flame_juggler_animation(self,target)
        self.deal_damage([target], [1]) 

class Carrion_Grub(Minion):
    def __init__(self,name="Carrion_Grub",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
 
class Forlorn_Stalker(Minion):
    def __init__(self,name="Forlorn Stalker",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        targets=[] 
        for card in self.owner.hand:
            if card.isMinion() and "Deathrattle" in card.abilities:
                targets.append(card)
                card.buff_stats(1,1)
        buff_hand_animation(self.owner,targets)

class Infested_Wolf(Minion):
    def __init__(self,name="Infested Wolf",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        for i in range(2):
            minion=Spider_Infested_Wolf(owner=self.owner)
            self.summon(minion)
            
class Spider_Infested_Wolf(Minion):
    def __init__(self,name="Spider (Infested Wolf)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Giant_Sand_Worm(Minion):
    def __init__(self,name="Giant Sand Worm",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="after attack"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card is self and self.target.destroyed_by is self:
            super(self.__class__,self).trigger_effect(triggering_card)
            self.attacked=False

class Kindly_Grandmother(Minion):
    def __init__(self,name="Kindly Grandmother",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        minion=Big_Bad_Wolf(owner=self.owner)
        self.summon(minion)
            
class Big_Bad_Wolf(Minion):
    def __init__(self,name="Big Bad Wolf",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Cloaked_Huntress(Minion):
    def __init__(self,name="Cloaked Huntress",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def overriding_ongoing_effect(self,target):
        if target.side==self.side and isinstance(target,Secret):
            return {'cost':0}
        else:
            return {}

class Cat_in_a_Hat(Minion):
    def __init__(self,name="Cat in a Hat",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.stealth=True

class Alleycat(Minion):
    def __init__(self,name="Alleycat",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        minion = Tabbycat(owner=self.owner)
        self.summon(minion)

class Tabbycat(Minion):
    def __init__(self,name="Tabbycat",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Shaky_Zipgunner(Minion):
    def __init__(self,name="Shaky Zipgunner",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        self.owner.buff_hand("Minion",atk=2,hp=2)
        
class Trogg_Beastrager(Minion):
    def __init__(self,name="Trogg Beastrager",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        self.owner.buff_hand("Beast")
                                                                                                                                           
class Dwarven_Sharpshooter(Minion):
    def __init__(self,name="Dwarven Sharpshooter",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def ongoing_effect(self,target):
        if target.isHero() and target.side==self.side:
            return {'target minion':True}
        else:
            return {} 

class Dispatch_Kodo(Minion):
    def __init__(self,name="Dispatch Kodo",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(chooser=self,target="character",message="deal damage")
        return target
    
    def battlecry(self,target):
        charge_shot_animation(self, target)
        self.deal_damage([target], [self.current_atk])

class Rat_Pack(Minion):
    def __init__(self,name="Rat Pack",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        for i in range(self.get_current_atk()):
            minion=Rat(owner=self.owner)
            self.summon(minion)

class Rat(Minion):
    def __init__(self,name="Rat",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Piranha(Minion):
    def __init__(self,name="Piranha",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Jeweled_Macaw(Minion):
    def __init__(self,name="Jeweled Macaw",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
    
    def battlecry(self,target):
        minion = database.get_random_cards("[type]='Minion' AND [race]='Beast'", self.owner, 1)[0]
        minion.initialize_location(self.location)
        minion.hand_in()

class Crackling_Razormaw(Minion):
    def __init__(self,name="Crackling Razormaw",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(chooser=self,target="friendly minion",target_type="Beast",message="+2/+2 and Taunt")
        return target
    
    def battlecry(self,target):
        target.adapt()

class Raptor_Hatchling(Minion):
    def __init__(self,name="Raptor Hatchling",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        minion=Raptor_Patriarch(owner=self.owner,source=self.location)
        minion.shuffle_into_deck(self.owner.deck)
                    
class Raptor_Patriarch(Minion):
    def __init__(self,name="Raptor Patriarch",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Terrorscale_Stalker(Minion):
    def __init__(self,name="Terrorscale Stalker",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(chooser=self,target="minion",target_type="has_deathrattle attr",message="silence")
        return target
    
    def battlecry(self,target):
        target.trigger_deathrattle()

class Tolvir_Warden(Minion):
    def __init__(self,name="Tol'vir_Warden",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target):
        for i in range(2):
            minion=self.owner.search_card_based_cost(self.owner.deck.cards,card_type="Minion",cost=1)
            if minion is not None:
                self.owner.draw(target=minion)

class Bearshark(Minion):
    def __init__(self,name="Bearshark",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.elusive=True 

class Stitched_Tracker(Minion):
    def __init__(self,name="Stitched Tracker",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        cards=self.owner.search_card(self.owner.deck.cards,card_type="Minion",k=3)
        if cards is not None:
            card=self.discover(card_pool=cards)
            if card is not None:
                card_copy=card.get_copy(owner=self.owner)
                card_copy.initialize_location(self.location)
                card_copy.hand_in()

class Exploding_Bloatbat(Minion):
    def __init__(self,name="Exploding Bloatbat",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        unstable_ghoul_animation(self)
        targets=self.enemy_minions()
        self.deal_damage(targets, [2]*len(targets))

class Corpse_Widow(Minion):
    def __init__(self,name="Corpse Widow",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def ongoing_effect(self,target):
        if (target.isMinion() or target.isWeapon()) and "Deathrattle" in target.abilities and target.side==self.side:
            return {'cost':-2}
        else:
            return {}

class Abominable_Bowman(Minion):
    def __init__(self,name="Abominable Bowman",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        minion=self.owner.search_card(self.owner.grave,card_type="Beast")
        if minion is not None:
            self.summon(minion)

class Cave_Hydra(Minion):
    def __init__(self,name="Cave Hydra",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="during attack"
        
    def trigger_effect(self,triggering_minion):
        if triggering_minion is self and self.target.isMinion():
            self.attack_adjacent_minions(self.target)

class Wolf(Minion):
    def __init__(self,name="Wolf",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Seeping_Oozeling(Minion):
    def __init__(self,name="Seeping Oozeling",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        minion=self.owner.search_card_based_keyword(self.owner.deck.cards,card_type="Minion",keyword="Deathrattle",k=1)
        if minion is not None:
            self.deathrattles.append([MethodType(minion.deathrattle.__func__,self),minion.deathrattle_msg])
            self.has_deathrattle=True

class Hunting_Mastiff(Minion):
    def __init__(self,name="Hunting Mastiff",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.rush=True

class Duskhaven_Hunter(Minion):
    def __init__(self,name="Duskhaven Hunter",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.stealth=True
        self.trigger_event_type="start of turn"
        
    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner and self.board_area=="Hand":
            minion = Duskhaven_Hunter_5_2(owner=self.owner)
            minion.initialize_location(self.location)
            minion.board_area="Hand"
            self.owner.hand[self.get_index()]=minion

class Duskhaven_Hunter_5_2(Minion):
    def __init__(self,name="Duskhaven Hunter(5-2)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.stealth=True
        self.trigger_event_type="start of turn"
        
    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner and self.board_area=="Hand":
            minion = Duskhaven_Hunter(owner=self.owner)
            minion.initialize_location(self.location)
            minion.board_area="Hand"
            self.owner.hand[self.get_index()]=minion

class Vilebrood_Skitterer(Minion):
    def __init__(self,name="Vilebrood Skitterer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.poisonous=True
        self.rush=True

class Carrion_Drake(Minion):
    def __init__(self,name="Carrion Drake",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def battlecry(self,target):
        if self.owner.get_num_minions_died()>0:
            self.gain_poisonous()

class Doom_Rat(Minion):
    def __init__(self,name="Doom Rat",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
                    
class Toxmonger(Minion):
    def __init__(self,name="Toxmonger",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="play a card"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.isMinion() and triggering_card.side==self.side and triggering_card.get_current_cost()==1 and triggering_card is not self:
            super(self.__class__,self).trigger_effect(self)
            acidic_swamp_ooze_animation(self, triggering_card)
            triggering_card.gain_poisonous()
                                                                                                                                                                                                                                
class King_Krush(Minion):
    def __init__(self,name="King Krush",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.charge=True
        self.has_special_summon_effect=True
        
    def special_summoning_effect(self):
        king_crush_animation(self)
          
class Gahzrilla(Minion):
    def __init__(self,name="Gahz'rilla",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="minion damage"
        
    def trigger_effect(self,triggering_entity):
        if triggering_entity[0] is self:
            super(self.__class__,self).trigger_effect(self)
            self.current_atk*=2
            self.temp_atk*=2

class Dreadscale(Minion):
    def __init__(self,name="Dreadscale",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="end of turn"
        
    def trigger_effect(self,triggering_player):
        if triggering_player is self.owner:
            super(self.__class__,self).trigger_effect(triggering_player)
            dreadscale_animation(self)
            targets=self.all_minions()
            if self in targets:
                targets.remove(self)
            self.deal_damage(targets, [1]*len(targets))

class Acidmaw(Minion):
    def __init__(self,name="Acidmaw",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="minion damage"
        
    def trigger_effect(self,triggering_entity):
        if triggering_entity[0] is not self:
            super(self.__class__,self).trigger_effect(triggering_entity[0])
            acidmaw_animation(self,triggering_entity[0])
            triggering_entity[0].destroy()

class Princess_Huhuran(Minion):
    def __init__(self,name="Princess Huhuran",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def get_target(self):
        target=choose_target(self, target="friendly minion", target_type="has_deathrattle attr", message="trigger its deathrattle")
        return target
    
    def battlecry(self,target):
        target.trigger_deathrattle()

class Knuckles(Minion):
    def __init__(self,name="Knuckles",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="after attack"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card is self and self.target.isMinion():
            super(self.__class__,self).trigger_effect(triggering_card)
            charge_shot_animation(self, self.owner.opponent)
            self.deal_damage([self.owner.opponent], [self.get_current_atk()])
 
class Queen_Carnassa(Minion):
    def __init__(self,name="Queen Carnassa",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        for i in range(15):
            card=Carnassas_Brood(owner=self.owner,source=self.location)
            deck_in_animation(card,self.owner.deck,skip_zoom=True)
            self.owner.deck.add_card(card) 
        
class Carnassas_Brood(Minion):
    def __init__(self,name="Carnassa's Brood",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

    def battlecry(self,target=None):
        self.owner.draw()
                                    
class Swamp_King_Dred(Minion):
    def __init__(self,name="Swamp King Dred",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="summon from hand"
        
    def trigger_effect(self, triggering_minion=None):
        if triggering_minion.side==-self.side and (not self.frozen or self.owner.board.get_buff(self)['defrozen']) and triggering_minion.board_area=="Board" and triggering_minion.get_current_hp()>0:
                super(self.__class__,self).trigger_effect(triggering_minion)
                self.attack(triggering_minion)

class Professor_Putricide(Minion):
    def __init__(self,name="Professor Putricide",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="play a card"
        
    def trigger_effect(self, triggering_card=None):
        if isinstance(triggering_card,Secret) and triggering_card.owner is self.owner:
            super(self.__class__,self).trigger_effect(triggering_card)
            secret = database.get_random_cards(filter_str="[class] LIKE '%Hunter%'",owner=self.owner,k=1,by_ability="Secret")[0]
            secret.invoke()

class Kathrena_Winterwisp(Minion):
    def __init__(self,name="Kathrena Winterwisp",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        minion=self.owner.search_card(self.owner.deck.cards,card_type="Beast")
        if minion is not None:
            self.recruit(minion)
    
    def deathrattle(self,target=None):
        minion=self.owner.search_card(self.owner.deck.cards,card_type="Beast")
        if minion is not None:
            self.recruit(minion)

class Houndmaster_Shaw(Minion):
    def __init__(self,name="Houndmaster Shaw",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def ongoing_effect(self,target):
        if target.isMinion() and target.side==self.side:
            return {'rush':True}
        else:
            return {}

class Emeriss(Minion):
    def __init__(self,name="Emeriss",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        targets=[]
        for card in self.owner.hand:
            if card.isMinion():
                card.buff_stats(card.temp_atk,card.temp_hp)
                targets.append(card)
        buff_hand_animation(self.owner, targets)
                                                                                                                                       
'''Mage Minions'''
class Mirror_Image_minion(Minion):
    def __init__(self,name="Mirror Image (minion)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
                 
class Water_Elemental(Minion):
    def __init__(self,name="Water Elemental",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def on_hit_effect(self, target):
        target.get_frozen()

class Mana_Wyrm(Minion):
    def __init__(self,name="Mana Wyrm",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="cast a spell"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.owner is self.owner:
            super(self.__class__,self).trigger_effect(triggering_card)
            buff_animation(self)
            self.buff_stats(1, 0)

class Sorcerers_Apprentice(Minion):
    def __init__(self,name="Sorcerer's Apprentice",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def ongoing_effect(self,target):
        if target.isSpell and target.side==self.side:
            return {'cost':-1}
        else:
            return {}

class Kirin_Tor_Mage(Minion):
    def __init__(self,name="Kirin Tor Mage",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def battlecry(self,target=None):
        mage_minion_animation(self)
        card=Kirin_Tor_Mage_Effect(owner=self.owner)
                                       
class Kirin_Tor_Mage_Effect(Enchantment):
    def __init__(self,name="Kirin Tor Mage",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_events.append(("play a card",self.trigger_effect))

    def overriding_ongoing_effect(self,target):
        if target.side==self.side and target.board_area=="Hand" and isinstance(target, Secret):
            return {'cost':0}
        else:
            return {}            
        
    def trigger_effect(self, triggering_card):
        if triggering_card.side==self.side and isinstance(triggering_card, Secret):
            self.destroy()

class Spellbender_minion(Minion):
    def __init__(self,name="Spellbender (minion)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Ethereal_Arcanist(Minion):
    def __init__(self,name="Ethereal Arcanist",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="end of turn"
        
    def trigger_effect(self,triggering_player):
        if triggering_player is self.owner and len(self.owner.secrets)>0:
            super(self.__class__,self).trigger_effect(triggering_player)
            buff_animation(self,speed=8)
            self.buff_stats(2,2)

class Snowchugger(Minion):
    def __init__(self,name="Snowchugger",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def on_hit_effect(self, target):
        target.get_frozen()
        
class Soot_Spewer(Minion):
    def __init__(self,name="Soot Spewer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.spell_damage_boost=1

class Goblin_Blastmage(Minion):
    def __init__(self,name="Goblin Blastmage",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def battlecry(self,target=None):
        if self.owner.control("Mech"):
            self.deal_split_damage(self.enemy_characters(), shots=4, damage=1, effect=get_image("images/fireball.png",(60,65)), speed=50, curve=False)

class Wee_Spellstopper(Minion):
    def __init__(self,name="Wee Spellstopper",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def ongoing_effect(self,target):
        if target.isMinion() and target.board_area=="Board" and target.side==self.side and abs(target.get_index()-self.get_index())==1:
            return {'elusive':True}
        else:
            return {} 

class Flamewaker(Minion):
    def __init__(self,name="Flamewaker",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="cast a spell"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.owner is self.owner:
            super(self.__class__,self).trigger_effect(triggering_card)
            self.deal_split_damage(self.enemy_minions(), shots=2, damage=1, effect=get_image("images/fireball2.png",(50,50)), speed=80, curve=False)
                                         
class Black_Cat(Minion):
    def __init__(self,name="Black Cat",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.spell_damage_boost=1

    def battlecry(self,target=None):
        if self.owner.deck.has_odd_cards_only():
            self.owner.draw()

class Spellslinger(Minion):
    def __init__(self,name="Spellslinger",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        for player in [self.owner,self.owner.opponent]:
            card = database.get_random_cards("[type]='Spell'", owner=player, k=1)[0]
            card.initialize_location(self.location)
            card.hand_in()

class Dalaran_Aspirant(Minion):
    def __init__(self,name="Dalaran Aspirant",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.inspire=True
         
    def trigger_inspire(self, hero_power=None):
        if hero_power.owner is self.owner:
            super(self.__class__,self).trigger_inspire()
            self.gain_spell_damage_boost(self.spell_damage_boost+1)

class Fallen_Hero(Minion):
    def __init__(self,name="Fallen Hero",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def ongoing_effect(self,target):
        if target.isHero() and target.side==self.side:
            return {'hero power damage':1}
        else:
            return {}  

class Coldarra_Drake(Minion):
    def __init__(self,name="Coldarra Drake",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def overriding_ongoing_effect(self,target):
        if isinstance(target, Hero_Power) and target.side==self.side:
            if target.use_count>0:
                target.refresh()
            return {'usage cap':1}
        else:
            return {}
                                                                                                    
class Ethereal_Conjurer(Minion):
    def __init__(self,name="Ethereal Conjurer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        card=self.discover(filter_str="[type]='Spell'")
        if card is not None:
            card.hand_in()

class Animated_Armor(Minion): 
    def __init__(self,name="Animated Armor",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="modify damage"
        
    def trigger_effect(self, triggering_entity):
        amount=triggering_entity[1]
        player=triggering_entity[2]
        if player is self.owner and amount>0:
            super(self.__class__,self).trigger_effect(self)
            bolf_ramshield_animation(self)
            self.owner.modified_damage=1

class Twilight_Flamecaller(Minion):
    def __init__(self,name="Twilight Flamecaller",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        unstable_ghoul_animation(self)
        targets=self.enemy_minions()
        self.deal_damage(targets, [1]*len(targets))

class Faceless_Summoner(Minion):
    def __init__(self,name="Faceless Summoner",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        minion = database.get_random_cards("[type]='Minion' AND [cost]=3", self.owner, 1)[0]
        self.summon(minion)

class Cult_Sorcerer(Minion):
    def __init__(self,name="Cult Sorcerer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.spell_damage_boost=1
        self.trigger_event_type="cast a spell"

    def trigger_effect(self, triggering_card=None):
        if triggering_card.owner is self.owner:
            super(self.__class__,self).trigger_effect(triggering_card)
            self.buff_cthun(1, 1)

class Demented_Frostcaller(Minion):
    def __init__(self,name="Demented Frostcaller",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="cast a spell"

    def trigger_effect(self, triggering_card=None):
        if triggering_card.owner is self.owner:
            super(self.__class__,self).trigger_effect(triggering_card)
            target=random.choice(self.enemy_characters())
            demented_frostcaller_animation(self, target)
            target.get_frozen()
            
class Servant_of_Yogg_Saron(Minion):
    def __init__(self,name="Servant of Yogg-Saron",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        spell = database.get_random_cards("[type]='Spell' and [cost]<=5", self.owner, 1)[0]
        yogg_saron_spell_animation(spell)
        spell.cast_on_random_target()  

class Medivhs_Valet(Minion):
    def __init__(self,name="Medivh's Valet",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def get_target(self):
        target=choose_target(chooser=self,target="character",message="deal 3 damage")
        return target
    
    def battlecry(self,target):
        if len(self.owner.secrets)>0:
            mini_fireball_animation(self, target)
            self.deal_damage([target], [3])

class Babbling_Book(Minion):
    def __init__(self,name="Babbling Book",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        card = database.get_random_cards("[class] LIKE '%Mage%' AND [type]='Spell'", self.owner, 1)[0]
        card.initialize_location(self.location)
        card.hand_in()

class Kabal_Lackey(Minion):
    def __init__(self,name="Kabal Lackey",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def battlecry(self,target=None):
        mage_minion_animation(self)
        card=Kirin_Tor_Mage_Effect(owner=self.owner)
                                        
class Cryomancer(Minion):
    def __init__(self,name="Cryomancer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
    
    def battlecry(self,target):
        for minion in self.enemy_minions():
            if minion.frozen:
                buff_animation(self)
                self.buff_stats(2,2)
                break

class Kabal_Crystal_Runner(Minion):
    def __init__(self,name="Kabal Crystal Runner",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def ongoing_effect(self,target):
        if target is self and target.board_area=="Hand":
            count=0
            for i in range(self.owner.turn):
                for card in self.owner.played_cards[i+1]:
                    if isinstance(card,Secret):
                        count+=1
            return {'cost':-2*count}
        else:
            return {} 

class Manic_Soulcaster(Minion):
    def __init__(self,name="Manic Soulcaster",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def get_target(self):
        minion=choose_target(chooser=self,target="friendly minion",message="shuffle into deck")
        return minion
    
    def battlecry(self,target):
        minion_copy=getattr(card_collection,database.cleaned(target.name))(owner=self.owner,source=target.location)
        minion_copy.shuffle_into_deck()

class Arcanologist(Minion):
    def __init__(self,name="Arcanologist",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        secret=self.search_card_by_type(Secret)
        if secret is not None:
            self.owner.draw(target=secret)
        
class Shimmering_Tempest(Minion): 
    def __init__(self,name="Shimmering Tempest",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.has_special_summon_effect=True
        
    def deathrattle(self):
        spell = database.get_random_cards("[type]='Spell' AND [class] LIKE '%Mage%'", self.owner, 1)[0]
        spell.initialize_location(self.owner.location)
        spell.hand_in()

class Steam_Surger(Minion):
    def __init__(self,name="Steam Surger",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        if self.owner.played_before("Elemental"):
            card=Flame_Geyser(owner=self.owner)
            card.initialize_location(self.location)
            card.hand_in()

class Coldwraith(Minion):
    def __init__(self,name="Coldwraith",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        for target in self.enemy_minions()+[self.owner.opponent]:
            if target.frozen:
                self.owner.draw()
                break

class Ice_Walker(Minion):
    def __init__(self,name="Ice Walker",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def ongoing_effect(self,target):
        if isinstance(target,Hero_Power) and target.is_targeted() and target.side==self.side:
            return {'freeze target':True}
        else:
            return {} 

class Doomed_Apprentice(Minion):
    def __init__(self,name="Doomed Apprentice",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def ongoing_effect(self,target):
        if target.isSpell and target.side==-self.side:
            return {'cost':1}
        else:
            return {}

class Ghastly_Conjurer(Minion):
    def __init__(self,name="Ghastly Conjurer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        card=Mirror_Image(owner=self.owner)
        card.initialize_location(self.location)
        card.hand_in()

class Arcane_Artificer(Minion):
    def __init__(self,name="Arcane Artificer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="cast a spell"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.owner is self.owner:
            super(self.__class__,self).trigger_effect(triggering_card)
            self.owner.increase_shield(triggering_card.get_current_cost())
                                                                                                                                                                                                                   
class Arcane_Amplifier(Minion):
    def __init__(self,name="Arcane Amplifier",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def ongoing_effect(self,target):
        if target.isHero() and target.side==self.side:
            return {'hero power damage':2}
        else:
            return {}   

class Raven_Familiar(Minion):
    def __init__(self,name="Raven Familiar",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        winner = self.joust("Spell")
        if winner is not None and winner.owner is self.owner:
            self.owner.draw(target=winner)

class Leyline_Manipulator(Minion):
    def __init__(self,name="Leyline Manipulator",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        silence_animation(self)
        for card in self.owner.hand:
            if not card.started_in_deck:
                card.modify_cost(-2)

class Vex_Crow(Minion):
    def __init__(self,name="Vex Crow",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="cast a spell"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.owner is self.owner:
            super(self.__class__,self).trigger_effect(triggering_card)
            minion = database.get_random_cards("[type]='Minion' AND [cost]=2", self.owner, 1)[0]
            self.summon(minion)

class Bonfire_Elemental(Minion):
    def __init__(self,name="Bonfire Elemental",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        if self.owner.played_before("Elemental"):
            self.owner.draw()

class Curio_Collector(Minion):
    def __init__(self,name="Curio Collector",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="draw a card"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.side==self.side:
            super(self.__class__,self).trigger_effect(triggering_card)
            light_buff_animation(self)
            self.buff_stats(1, 1)

class Arcane_Keysmith(Minion):
    def __init__(self,name="Arcane Keysmith",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        secret=self.discover(by_ability="Secret")
        if secret is not None:
            secret.invoke()
                                                                        
class Archmage_Antonidas(Minion):
    def __init__(self,name="Archmage Antonidas",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="cast a spell"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.owner is self.owner:
            super(self.__class__,self).trigger_effect(triggering_card)
            spell=Fireball(owner=self.owner)
            spell.initialize_location(self.location)
            spell.hand_in()  
            
class Flame_Leviathan(Minion):
    def __init__(self,name="Flame Leviathan",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.casts_when_drawn=True
        
    def on_drawn(self):
        on_drawn_animation(self)
        targets=self.all_characters()
        flame_leviathan_animation(self)
        self.deal_damage(targets, [2]*len(targets))
    
class Rhonin(Minion): 
    def __init__(self,name="Rhonin",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.has_special_summon_effect=True
    
    def special_summoning_effect(self):
        rhonin_animation(self)
        
    def deathrattle(self):
        for i in range(3):
            card=Arcane_Missiles(owner=self.owner)
            card.appear_in_hand()

class Anomalus(Minion):
    def __init__(self,name="Anomalus",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        anomalus_animation(self) 
        targets=self.all_minions()
        self.deal_damage(targets, [8]*len(targets))

class Inkmaster_Solia(Minion):
    def __init__(self,name="Inkmaster Solia",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        if self.owner.deck.has_no_duplicates():
            rhonin_animation(self)
            card=Inkmaster_Solia_Effect(owner=self.owner)
                                       
class Inkmaster_Solia_Effect(Enchantment):
    def __init__(self,name="Inkmaster Solia",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_events.append(("play a card",self.trigger_effect))

    def overriding_ongoing_effect(self,target):
        if target.side==self.side and target.board_area=="Hand" and isinstance(target, Spell):
            return {'cost':0}
        else:
            return {}            
        
    def trigger_effect(self, triggering_card):
        if triggering_card.side==self.side and isinstance(triggering_card, Spell):
            self.destroy()

class Pyros(Minion):
    def __init__(self,name="Pyros",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
                
    def destroy(self,skip_animation=False,skip_deathrattle=False):
        for deathrattle in self.deathrattles:
            deathrattle[0]()

        if self.board_area!="Burn":
            super(self.__class__,self).destroy(skip_animation=skip_animation,skip_deathrattle=True)

    def deathrattle(self):
        if self.board_area=="Board":
            pyros_animation(self)
            minion=Pyros_6_6(owner=self.owner)
            self.transform(minion)
            minion.return_hand()

class Pyros_6_6(Minion):
    def __init__(self,name="Pyros (6-6)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
                
    def destroy(self,skip_animation=False,skip_deathrattle=False):
        for deathrattle in self.deathrattles:
            deathrattle[0]()

        if self.board_area!="Burn":
            super(self.__class__,self).destroy(skip_animation=skip_animation,skip_deathrattle=True)

    def deathrattle(self):
        if self.board_area=="Board":
            pyros_animation(self)
            minion=Pyros_10_10(owner=self.owner)
            self.transform(minion)
            minion.return_hand()          

class Pyros_10_10(Minion):
    def __init__(self,name="Pyros (10-10)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Sindragosa(Minion):
    def __init__(self,name="Sindragosa",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def battlecry(self,target):
        for i in range(2):
            minion=Frozen_Champion(owner=self.owner)
            self.summon(minion,left=(-1)**i,speed=40)

class Frozen_Champion(Minion):
    def __init__(self,name="Frozen Champion",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
    
    def deathrattle(self):
        minion=self.owner.search_card_based_cost(self.owner.deck.cards,card_type="Minion",cost=8)
        if minion is not None:
            self.recruit(minion) 

class Dragoncaller_Alanna(Minion):
    def __init__(self,name="Dragoncaller Alanna",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
                
    def battlecry(self,target=None):
        for i in range(self.owner.turn):
            for card in self.owner.played_cards[i+1]:
                if card.isSpell and card.cost>=5:
                    minion=Fire_Dragon(owner=self.owner)
                    self.summon(minion)

class Fire_Dragon(Minion):
    def __init__(self,name="Fire Dragon",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Archmage_Arugal(Minion):
    def __init__(self,name="Archmage Arugal",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="draw a card"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.isMinion() and triggering_card.side==self.side:
            super(self.__class__,self).trigger_effect(triggering_card)
            card=triggering_card.get_copy(owner=self.owner)
            card.appear_in_hand()

class Toki_Time_Tinker(Minion):
    def __init__(self,name="Toki, Time-Tinker",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        minion = database.get_random_cards("[type]='Minion' AND [rarity]='Legendary'", owner=self.owner, k=1,standard=False)[0]
        time_warp_animation(self)
        minion.initialize_location(self.location)
        minion.hand_in()
                                                                                                   
'''Paladin Minions'''
class Silver_Hand_Recruit(Minion):
    def __init__(self,name="Silver Hand Recruit",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
                                
class Defender(Minion):
    def __init__(self,name="Defender",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Annoy_o_Module(Minion):
    def __init__(self,name="Annoy-o-Module",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source) 
        self.magnetic=True
        self.divine_shield=True
        self.taunt=True
                                    
class Guardian_of_Kings(Minion):
    def __init__(self,name="Guardian of Kings",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        self.heal([self.owner],[6])

class Argent_Protector(Minion):
    def __init__(self,name="Argent Protector",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(chooser=self,target="friendly minion",message="give Divine Shield")
        return target
    
    def battlecry(self,target):
        target.gain_divine_shield()
        
class Aldor_Peacekeeper(Minion):
    def __init__(self,name="Aldor Peacekeeper",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(chooser=self,target="enemy minion",message="change attack to 1")
        return target
    
    def battlecry(self,target):
        paladin_debuff_animation(self,target)
        target.set_stats(atk=1)
        
class Shielded_Minibot(Minion):
    def __init__(self,name="Shielded Minibot",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.divine_shield=True

class Scarlet_Purifier(Minion):
    def __init__(self,name="Scarlet Purifier",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
                
    def battlecry(self,target=None):
        targets=[]
        for minion in self.all_minions():
            if minion.has_deathrattle:
                targets.append(minion)
        if len(targets)>0:
            scarlet_purifier_animation(self,targets)  
            self.deal_damage(targets, [2]*len(targets))

class Cobalt_Guardian(Minion):
    def __init__(self,name="Cobalt Guardian",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="summon a minion"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.owner is self.owner and triggering_card.has_race("Mech") and triggering_card is not self:
            super(self.__class__,self).trigger_effect(triggering_card)
            self.gain_divine_shield()

class Quartermaster(Minion):
    def __init__(self,name="Quartermaster",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
                
    def battlecry(self,target=None):
        targets=[]
        for minion in self.friendly_minions():
            if isinstance(minion, Silver_Hand_Recruit):
                targets.append(minion)
        if len(targets)>0:
            quartermaster_animation(self,targets)  
            for target in targets:
                target.buff_stats(2,2)

class Dragon_Consort(Minion):
    def __init__(self,name="Dragon Consort",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def battlecry(self,target=None):
        mage_minion_animation(self)
        card=Dragon_Consort_Effect(owner=self.owner)
        
class Dragon_Consort_Effect(Enchantment):
    def __init__(self,name="Dragon Consort",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_events=[("play a card",self.trigger_effect)]

    def ongoing_effect(self,target):
        if target.side==self.side and target.board_area=="Hand" and target.has_race("Dragon"):
            return {'cost':-2}
        else:
            return {}            
        
    def trigger_effect(self, triggering_card):
        if triggering_card.side==self.side and triggering_card.has_race("Dragon"):
            self.destroy()

class Warhorse_Trainer(Minion):
    def __init__(self,name="Warhorse Trainer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def ongoing_effect(self,target):
        if isinstance(target, Silver_Hand_Recruit) and target.board_area=="Board" and target.side==self.side:
            return {'atk':1}
        else:
            return {}
                                                    
class Murloc_Knight(Minion):
    def __init__(self,name="Murloc Knight",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.inspire=True
        
    def trigger_inspire(self, hero_power=None):
        if hero_power.owner is self.owner:
            super(self.__class__,self).trigger_inspire()
            minion = database.get_random_cards("[race]='Murloc'", owner=self.owner, k=1)[0]
            if minion is not None:
                self.summon(minion)

class Tuskarr_Jouster(Minion):
    def __init__(self,name="Tuskarr Jouster",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        winner = self.joust("Minion")
        if winner is not None and winner.owner is self.owner:
            priest_heal_animation(self, self.owner)
            self.heal([self.owner],[7]) 

class Mysterious_Challenger(Minion):
    def __init__(self,name="Mysterious Challenger",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        secret_pool=[]
        secret_names=[]
        for card in self.owner.deck.cards:
            if isinstance(card, Secret) and card.is_valid_on():
                if card.name not in secret_names:
                    secret_names.append(card.name)
                    secret_pool.append(card)
                
        secrets=random.sample(secret_pool,k=min(5,len(secret_pool)))
        for secret in secrets:
            secret.invoke()
            self.owner.deck.cards.remove(secret)

class Keeper_of_Uldaman(Minion):
    def __init__(self,name="Keeper of Uldaman",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(chooser=self,target="minion",message="set Attack and Health to 3")
        return target
    
    def battlecry(self,target):
        light_buff_animation(target)
        target.set_stats(3,3)

class Selfless_Hero(Minion):
    def __init__(self,name="Selfless Hero",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source) 
       
    def deathrattle(self):
        minion=self.get_another_friendly_minion()
        if minion is not None:
            minion.gain_divine_shield()

class Steward_of_Darkshire(Minion):
    def __init__(self,name="Steward of Darkshire",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="summon a minion"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.side==self.side and triggering_card.temp_hp==1:
            super(self.__class__,self).trigger_effect(triggering_card)
            triggering_card.gain_divine_shield()

class Vilefin_Inquisitor(Minion):
    def __init__(self,name="Vilefin Inquisitor",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def battlecry(self,target):
        new_hero_power=The_Tidal_Hand(owner=self.owner)
        self.owner.gain_hero_power(new_hero_power)
        
class Silver_Hand_Murloc(Minion):
    def __init__(self,name="Silver Hand Murloc",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Nightbane_Templar(Minion):
    def __init__(self,name="Nightbane_Templar",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        if self.owner.holding("Dragon"):
            for i in range(2):
                minion=Whelp_Nightbane_Templar(owner=self.owner)
                self.summon(minion,left=(-1)**i,speed=60)

class Whelp_Nightbane_Templar(Minion):
    def __init__(self,name="Whelp (Nightbane Templar)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Ivory_Knight(Minion):
    def __init__(self,name="Ivory Knight",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        card=self.discover(filter_str="[type]='Spell'")
        if card is not None:
            self.heal([self.owner],[card.cost])
            card.hand_in()
            
class Grimscale_Chum(Minion):
    def __init__(self,name="Grimscale Chum",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        self.owner.buff_hand("Murloc",atk=1,hp=1)

class Grimestreet_Outfitter(Minion):
    def __init__(self,name="Grimestreet Outfitter",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        self.owner.buff_hand(card_type="Minion",multiple=True)

class Grimestreet_Enforcer(Minion):
    def __init__(self,name="Grimestreet Enforcer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source) 
        self.trigger_event_type="end of turn"
       
    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner:
            super(self.__class__,self).trigger_effect(triggering_player)
            self.owner.buff_hand(card_type="Minion",multiple=True)

class Grimestreet_Protector(Minion):
    def __init__(self,name="Grimestreet Protector",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        
    def battlecry(self,target=None):
        targets=self.adjacent_minions()
        for target in targets:
            target.gain_divine_shield()

class Meanstreet_Marshal(Minion):
    def __init__(self,name="Meanstreet Marshal",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        if self.get_current_atk()>=2:
            self.owner.draw()

class Hydrologist(Minion):
    def __init__(self,name="Hydrologist",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        if self.owner.class_name in ["Mage","Hunter","Rogue"]:
            card=self.discover(by_ability="Secret")
        else:
            card=self.discover(filter_str="[class] LIKE '%Paladin%'",own_class=False, by_ability="Secret")
        
        if card is not None:
            card.appear_in_hand()

class Lightfused_Stegodon(Minion):
    def __init__(self,name="Lightfused Stegodon",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        minions=[]
        for minion in self.friendly_minions():
            if isinstance(minion,Silver_Hand_Recruit):
                minions.append(minion)
        if len(minions)>0:
            choice=minions[0].adapt()
            minions.remove(minions[0])
            for minion in minions:
                minion.adapt(choice=choice)

class Primalfin_Champion(Minion):
    def __init__(self,name="Primalfin Champion",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="play a card"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.isSpell and triggering_card.target is self:
            self.attachments["Spell History"].append(triggering_card)

    def deathrattle(self):
        for spell in self.attachments["Spell History"]:
            if spell.owner is self.owner:
                card=spell.get_copy()
                card.appear_in_hand()

class Righteous_Protector(Minion):
    def __init__(self,name="Righteous Protector",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        self.divine_shield=True

class Chillblade_Champion(Minion):
    def __init__(self,name="Chillblade Champion",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.charge=True
        self.lifesteal=True

class Howling_Commander(Minion):
    def __init__(self,name="Howling Commander",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target):
        minion=self.owner.search_card_based_keyword(self.owner.deck.cards,card_type="Minion",keyword="divine_shield")
        if minion is not None:
            self.owner.draw(target=minion)

class Arrogant_Crusader(Minion):
    def __init__(self,name="Arrogant Crusader",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        if self.owner.board.control==-self.side:
            minion=Ghoul(owner=self.owner)
            self.summon(minion)

class Blackguard(Minion):
    def __init__(self,name="Blackguard",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="character healed"
        
    def trigger_effect(self,triggering_entity):
        if triggering_entity[0].isHero():
            super(self.__class__,self).trigger_effect(triggering_entity[0])
            target_pool=self.enemy_minions()
            if len(target_pool)>0:
                target=random.choice(target_pool)
                charge_shot_animation(self, target)
                self.deal_damage([target], [triggering_entity[1]])

class Drygulch_Jailor(Minion):
    def __init__(self,name="Drygulc Jailor",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        for i in range(3):
            minion=Silver_Hand_Recruit(owner=self.owner,source=self.location)
            minion.hand_in(speed=35)

class Benevolent_Djinn(Minion):
    def __init__(self,name="Benevolent Djinn",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source) 
        self.trigger_event_type="end of turn"
       
    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner:
            self.heal([self.owner],[3])

class Guardian_Spirit_2_2(Minion):
    def __init__(self,name="Guardian Spirit (2-2)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source) 
        self.taunt=True

class Guardian_Spirit_4_4(Minion):
    def __init__(self,name="Guardian Spirit (4-4)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source) 
        self.taunt=True

class Guardian_Spirit_6_6(Minion):
    def __init__(self,name="Guardian Spirit (6-6)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source) 
        self.taunt=True

class Crystal_Lion(Minion):
    def __init__(self,name="Crystal Lion",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def ongoing_effect(self,target):
        if target is self and target.board_area=="Hand":
            targets=self.friendly_minions()
            n=0
            for minion in targets:
                if isinstance(minion, Silver_Hand_Recruit):
                    n+=1
            return {'cost':-n}
        else:
            return {} 
                                                                                                                                                                                                                                                                                                          
class Micro_Mummy(Minion):
    def __init__(self,name="Micro Mummy",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.reborn=True
        self.trigger_event_type="end of turn"
        
    def trigger_effect(self,triggering_player):
        if triggering_player is self.owner:
            minion = self.get_another_friendly_minion()
            if minion is not None:
                super(self.__class__,self).trigger_effect(triggering_player)
                minion.buff_stats(1,0)
                                                    
class Tirion_Fordring(Minion):
    def __init__(self,name="Tirion Fordring",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        
    def deathrattle(self):
        weapon=Ashbringer(owner=self.owner)
        weapon.initialize_location(self.location)
        self.owner.equip_weapon(weapon)

class Bolvar_Fordragon(Minion):
    def __init__(self,name="Bolvar Fordragon",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="minion dies"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.owner is self.owner and self.board_area=="Hand":
            bolvar_fordragon_animation(self,triggering_card)
            self.buff_stats(1, 0)

class Ragnaros_Lightlord(Minion):
    def __init__(self,name="Ragnaros, Lightlord",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source) 
        self.trigger_event_type="end of turn"
       
    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner:
            heal_targets=[]
            for target in self.friendly_characters():
                if target.damaged() and target.current_hp>0:
                    heal_targets.append(target)
            
            if len(heal_targets)>0:
                super(self.__class__,self).trigger_effect(triggering_player)  
                target = random.choice(heal_targets)
                ragnaros_lightlord_animation(self,target)
                self.heal([target],[8])

class Wickerflame_Burnbristle(Minion):
    def __init__(self,name="Wickerflame Burnbristle",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source) 
        self.divine_shield=True
        self.taunt=True
        self.lifesteal=True

class Galvadon(Minion):
    def __init__(self,name="Galvadon",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        self.adapt(5)
                                                                                                      
class Eadric_the_Pure(Minion):
    def __init__(self,name="Eadric the Pure",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None): 
        targets=self.enemy_minions()
        debuff_multiple_animation(self,targets)
        for minion in targets:
            minion.temp_atk=1
            minion.current_atk=1
                        
class Sunkeeper_Tarim(Minion):
    def __init__(self,name="Sunkeeper Tarim",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        circle_of_healing_animation(self)
        for minion in self.all_minions():
            minion.set_stats(atk=3,hp=3)

class Bolvar_Fireblood(Minion):
    def __init__(self,name="Bolvar, Fireblood",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source) 
        self.trigger_event_type="lose divine shield"
        
    def trigger_effect(self,triggering_entity):
        if triggering_entity.side==self.side:
            super(self.__class__,self).trigger_effect(self)
            self.buff_stats(2, 0)

class Lynessa_Sunsorrow(Minion):
    def __init__(self,name="Lynessa Sunsorrow",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
                
    def battlecry(self,target=None):
        self.owner.board.random_select=True
        count=0
        for i in range(self.owner.turn):
            for card in self.owner.played_cards[i+1]:
                if card.isSpell and "Targeted" in card.tags and card.target is not None and card.target.side==self.side and self.board_area=="Board":
                    spell = card.get_copy(owner=self.owner)
                    yogg_saron_spell_animation(spell)
                    spell.invoke(self)
                    count+=1
            if count>=30:
                break
        self.owner.board.random_select=False
                                                  
'''Priest Minions'''
class Psychic_Conjurer(Minion):
    def __init__(self,name="Psychic Conjurer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        if len(self.owner.opponent.deck.cards)>0:
            opponent_card=random.choice(self.owner.opponent.deck.cards)
            mind_vision_animation(self)
            card_copy=opponent_card.get_copy(owner=self.owner)
            card_copy.appear_in_hand() 
            
class Northshire_Cleric(Minion):
    def __init__(self,name="Northshire Cleric",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="character healed"
        
    def trigger_effect(self,triggering_entity):
        if triggering_entity[0].isMinion():
            super(self.__class__,self).trigger_effect(triggering_entity[0])
            self.owner.draw()
        
class Lightspawn(Minion):
    def __init__(self,name="Lightspawn",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def ongoing_effect(self,target):
        if target is self:
            return {'atk':self.current_hp-self.current_atk}
        else:
            return {} 

class Auchenai_Soulpriest(Minion):
    def __init__(self,name="Auchenai Soulpriest",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def ongoing_effect(self,target):
        if target.side==self.side:
            return {'heal reverse':True}
        else:
            return {} 
        
class Temple_Enforcer(Minion):
    def __init__(self,name="Temple Enforcer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(self, target="friendly minion",message="+3 Health")
        return target
    
    def battlecry(self,target):
        target.buff_stats(0,3)
        buff_animation(target)
        
class Scarlet_Subjugator(Minion):
    def __init__(self,name="Scarlet Subjugator",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(chooser=self,target="enemy minion",message="give -2 attack until your next turn")
        return target
    
    def battlecry(self,target):
        target.current_atk-=2
        
class Kul_Tiran_Chaplain(Minion):
    def __init__(self,name="Kul Tiran Chaplain",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(self, target="friendly minion",message="+2 Health")
        return target
    
    def battlecry(self,target):
        target.buff_stats(0,2)
        buff_animation(target)
        
class Lightwell(Minion):
    def __init__(self,name="Lightwell",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source) 
        self.trigger_event_type="start of turn"
       
    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner:
            heal_targets=[]
            for target in self.friendly_characters():
                if target.damaged() and target.current_hp>0:
                    heal_targets.append(target)
            
            if len(heal_targets)>0:
                super(self.__class__,self).trigger_effect(triggering_player)  
                target = random.choice(heal_targets)
                self.heal([target],[5])
                
class Shadow_of_Nothing(Minion):
    def __init__(self,name="Shadow of Nothing",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)


class Cabal_Shadow_Priest(Minion):
    def __init__(self,name="Cabal Shadow Priest",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(chooser=self,target="enemy minion",target_type="get_current_atk __le__ 2", message="take control")
        return target
    
    def battlecry(self,target):
        self.owner.take_control(target)
        
class Glitter_Moth(Minion):
    def __init__(self,name="Glitter Moth",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        if self.owner.deck.has_odd_cards_only():
            targets=self.friendly_minions()
            glitter_moth_animation(self,targets)
            for minion in targets:
                minion.current_hp*=2
                minion.temp_hp+=minion.current_hp

class Shrinkmeister(Minion):
    def __init__(self,name="Shrinkmeister",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
             
    def get_target(self):
        target=choose_target(chooser=self,target="enemy minion",message="give -2 attack until your next turn")
        return target
    
    def battlecry(self,target):
        target.current_atk-=2 
        
class Shadowboxer(Minion):
    def __init__(self,name="Shadowboxer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="character healed"
        
    def trigger_effect(self,triggering_entity):
        if triggering_entity[0].isMinion():
            super(self.__class__,self).trigger_effect(triggering_entity[0])
            target=random.choice(self.enemy_characters())
            shadowboxer_animation(self,target) 
            self.deal_damage([target], [1])

class Upgraded_Repair_Bot(Minion):
    def __init__(self,name="Upgraded Repair Bot",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(chooser=self,target="friendly minion",target_type="Mech",message="give +4 Health")
        return target
    
    def battlecry(self,target):
        mech_buff_animation(target)
        target.buff_stats(0,4) 
        
class Shadowbomber(Minion): 
    def __init__(self,name="Shadowbomber",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        shadowbomber_animation(self)
        self.deal_damage([self.owner.opponent,self.owner], [3,3])

class Twilight_Whelp(Minion):
    def __init__(self,name="Twilight Whelp",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        if self.owner.holding("Dragon"):
            buff_animation(self)
            self.buff_stats(2, 2)
            
class Holy_Champion(Minion):
    def __init__(self,name="Holy Champion",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="character healed"
        
    def trigger_effect(self,triggering_entity):
        super(self.__class__,self).trigger_effect(triggering_entity[0])
        self.buff_stats(2, 0)

class Wyrmrest_Agent(Minion):
    def __init__(self,name="Wyrmrest Agent",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        if self.owner.holding("Dragon"):
            light_buff_animation(self)
            self.buff_stats(1, 0)
            self.gain_taunt()

class Spawn_of_Shadows(Minion): 
    def __init__(self,name="Spawn of Shadows",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.inspire=True
        
    def trigger_inspire(self, hero_power=None):
        if hero_power.owner is self.owner:
            super(self.__class__,self).trigger_inspire()
            shadowbomber_animation(self)
            self.deal_damage([self.owner.opponent,self.owner], [4,4])

class Shadowfiend(Minion):
    def __init__(self,name="Shadowfiend",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="draw a card"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.side==self.side:
            super(self.__class__,self).trigger_effect(triggering_card)
            triggering_card.modify_cost(-1)

class Museum_Curator(Minion):
    def __init__(self,name="Museum Curator",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        card=self.discover(by_ability="Deathrattle")
        if card is not None:
            card.hand_in()

class Hooded_Acolyte(Minion):
    def __init__(self,name="Hooded Acolyte",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="character healed"
        
    def trigger_effect(self,triggering_entity):
        super(self.__class__,self).trigger_effect(triggering_entity[0])
        self.buff_cthun(1, 1)

class Darkshire_Alchemist(Minion):
    def __init__(self,name="Darkshire Alchemist",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(chooser=self,target="character",message="restore 5 health")
        return target
    
    def battlecry(self,target):
        lesser_heal_animation(self, target)
        target.restore_health(5,self)

class Shifting_Shade(Minion):
    def __init__(self,name="Shifting Shade",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        if len(self.owner.opponent.deck.cards)>0:
            opponent_card=random.choice(self.owner.opponent.deck.cards)
            mind_vision_animation(self)
            card_copy=getattr(card_collection,database.cleaned(opponent_card.name))(owner=self.owner)
            card_copy.initialize_location(self.location)
            card_copy.appear_in_hand() 

class Twilight_Darkmender(Minion):
    def __init__(self,name="Twilight Darkmender",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        if self.eval_cthun(atk=10):
            self.heal([self.owner],[10])

class Priest_of_the_Feast(Minion):
    def __init__(self,name="Priest of the Feast",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="cast a spell"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.owner is self.owner:
            super(self.__class__,self).trigger_effect(triggering_card)
            priest_of_the_feast_animation(self)
            self.heal([self.owner],[3])

class Onyx_Bishop(Minion):
    def __init__(self,name="Onyx Bishop",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        minion = self.owner.search_card(self.owner.grave,"Minion")
        if minion is not None:
            minion_copy = getattr(card_collection,database.cleaned(minion.name))(owner=self.owner)
            self.summon(minion_copy)
            resurrect_animation(minion)

class Kabal_Taronpriest(Minion):
    def __init__(self,name="Kabal Taronpriest",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(self, target="friendly minion",message="+3 Health")
        return target
    
    def battlecry(self,target):
        target.buff_stats(0,3)
        light_buff_animation(target)

class Kabal_Songstealer(Minion):
    def __init__(self,name="Kabal Songstealer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
      
    def get_target(self):
        target=choose_target(chooser=self,target="minion",message="silence")
        return target
    
    def battlecry(self,target):
        self.silence(target)

class Drakonid_Operative(Minion):
    def __init__(self,name="Drakonid Operative",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        if self.owner.holding("Dragon"):
            opponent_cards=random.sample(self.owner.opponent.deck.cards,k=min(3,len(self.owner.opponent.deck.cards)))
            if len(opponent_cards)>0:
                selection_pool=[]
                for card in opponent_cards:
                    selection_pool.append(getattr(card_collection,database.cleaned(card.name))(owner=self.owner))
                card=self.discover(card_pool=selection_pool)
                if card is not None:
                    card.hand_in()

class Mana_Geode(Minion):
    def __init__(self,name="Mana Geode",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="character healed"
        
    def trigger_effect(self,triggering_entity):
        if triggering_entity[0] is self:
            super(self.__class__,self).trigger_effect(triggering_entity[0])
            minion=Crystal(owner=self.owner)
            self.summon(minion)

class Crystal(Minion):
    def __init__(self,name="Crystal",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Radiant_Elemental(Minion):
    def __init__(self,name="Radiant Elemental",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def ongoing_effect(self,target):
        if target.isSpell and target.side==self.side:
            return {'cost':-1}
        else:
            return {}

class Tortollan_Shellraiser(Minion):
    def __init__(self,name="Tortollan Shellraiser",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        
    def deathrattle(self):
        minion=self.get_another_friendly_minion()
        if minion is not None:
            priest_buff_animation(self, minion)
            minion.buff_stats(1,1)

class Crystalline_Oracle(Minion):
    def __init__(self,name="Crystalline Oracle",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        if len(self.owner.opponent.deck.cards)>0:
            opponent_card=random.choice(self.owner.opponent.deck.cards)
            card_copy=opponent_card.get_copy(owner=self.owner)
            card_copy.initialize_location(self.location)
            card_copy.hand_in()

class Mirage_Caller(Minion):
    def __init__(self,name="Mirage Caller",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def get_target(self):
        minion=choose_target(chooser=self,target="friendly minion",message="summon a 1/1 copy")
        return minion
    
    def battlecry(self,target):
        minion_copy=target.get_copy()
        minion_copy.copy_stats(target)
        minion_copy.set_stats(1,1)
        self.summon(minion_copy)

class Curious_Glimmerroot(Minion):
    def __init__(self,name="Curious Glimmerroot",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        choices=[]
        correct_card=self.owner.search_card(self.owner.opponent.initial_deck,card_type=self.owner.opponent.class_name)
        if correct_card is None:
            correct_card=random.choice(self.owner.opponent.initial_deck)
            class_name="Neutral"
        else:
            class_name=correct_card.card_class
        
        card=correct_card
        while card.name not in choices and len(choices)<3:
            choices.append(card.name)
            card=database.get_random_cards(filter_str="[class] LIKE '%"+class_name+"%'", owner=self.owner, k=1)[0]
        
        selection=[]
        for card_name in choices:
            card_copy=getattr(card_collection,database.cleaned(card_name))(owner=self.owner)
            selection.insert(random.randint(0,len(selection)),card_copy)
        card=self.discover(own_class=False, card_pool=selection)
        if isinstance(card,correct_card.__class__):
            card.hand_in()
        else:
            curious_glimmerroot_animation(self,correct_card,selection)

class Shadow_Ascendant(Minion):
    def __init__(self,name="Shadow Ascendant",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="end of turn"
        
    def trigger_effect(self,triggering_player):
        if triggering_player is self.owner:
            minion = self.get_another_friendly_minion()
            if minion is not None:
                super(self.__class__,self).trigger_effect(triggering_player)
                minion.buff_stats(1,1)

class Acolyte_of_Agony(Minion):
    def __init__(self,name="Acolyte of Agony",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.lifesteal=True

class Obsidian_Statue(Minion):
    def __init__(self,name="Obsidian Statue",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        self.lifesteal=True
       
    def deathrattle(self):
        target_pool=[]
        for minion in self.enemy_minions():
            if minion.get_current_hp()>0:
                target_pool.append(minion)
        if len(target_pool)>0:
            target=random.choice(target_pool)
            sylvanas_windrunner_animation(self,target)
            target.destroy()

class Gilded_Gargoyle(Minion): 
    def __init__(self,name="Gilded Gargoyle",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        card=The_Coin(owner=self.owner)
        card.appear_in_hand()

class Duskbreaker(Minion):
    def __init__(self,name="Duskbreaker",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        if self.owner.holding("Dragon"):
            targets=self.all_minions()
            chillmaw_animation(self)
            self.deal_damage(targets, [3]*len(targets))

class Twilight_Acolyte(Minion):
    def __init__(self,name="Twilight Acolyte",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(chooser=self,target="minion",message="swap attack with")
        return target
    
    def battlecry(self,target):
        if self.owner.holding("Dragon"):
            natalie_seline_animation(self, target)
            target.temp_atk,self.temp_atk=self.temp_atk,target.temp_atk
            target.current_atk,self.current_atk=self.current_atk,target.current_atk

class Dragon_Spirit(Minion):
    def __init__(self,name="Dragon Spirit",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
                                                                                                                                                                                                                                                                                                                                      
class Prophet_Velen(Minion):
    def __init__(self,name="Prophet Velen",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.has_special_summon_effect=True
    
    def special_summoning_effect(self):
        prophet_velen_animation(self)
                
    def ongoing_effect(self,target):
        if target.side==self.side and (target.isSpell or isinstance(target, Hero_Power)):
            return {'double effect':1}
        else:
            return {}
                    
class Natalie_Seline(Minion):
    def __init__(self,name="Natalie Seline",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(chooser=self,target="minion",message="destroy and gain its Health")
        return target
    
    def battlecry(self,target):
        natalie_seline_animation(self,target)
        hp=target.get_current_hp()
        target.destroy()
        self.buff_stats(0,hp)
                    
class Voljin(Minion): 
    def __init__(self,name="Vol'jin",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(chooser=self, target="enemy minion", message="swap health")
        return target
    
    def battlecry(self,target):
        natalie_seline_animation(self,target)
        self.current_hp,target.current_hp=target.current_hp,self.current_hp
        
class Confessor_Paletress(Minion): 
    def __init__(self,name="Confessor Paletress",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.inspire=True
        
    def trigger_inspire(self, hero_power=None):
        if hero_power.owner is self.owner:
            super(self.__class__,self).trigger_inspire()
            confessor_paletress_animation(self)
            minion = database.get_random_cards("[type]='Minion' AND [rarity]='Legendary'", self.owner, 1)[0]
            self.summon(minion)

class Herald_Volazj(Minion):
    def __init__(self,name="Herald Volazj",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
    
    def battlecry(self,target):
        for minion in self.friendly_minions():
            minion_copy = getattr(card_collection,database.cleaned(minion.name))(owner=minion.owner,source="board")
            minion_copy.copy_stats(minion)
            minion_copy.set_stats(1,1)
            self.summon(minion_copy)

class Raza_the_Chained(Minion):
    def __init__(self,name="Raza the Chained",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def battlecry(self,target=None):
        if self.owner.deck.has_no_duplicates():
            rhonin_animation(self)
            card=Raza_the_Chained_Effect(owner=self.owner)
                                       
class Raza_the_Chained_Effect(Enchantment):
    def __init__(self,name="Raza the Chained",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_events.remove(("end of turn",self.trigger_remove))

    def overriding_ongoing_effect(self,target):
        if isinstance(target, Hero_Power) and target.side==self.side:
            return {'cost':0}
        else:
            return {}        

class Amara_Warden_of_Hope(Minion):
    def __init__(self,name="Amara, Warden of Hope",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True

    def battlecry(self,target=None):
        amara_warden_of_hope_animation(self)
        self.owner.temp_hp=40
        self.owner.current_hp=40
            
class Lyra_the_Sunshard(Minion):
    def __init__(self,name="Lyra the Sunshard",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="cast a spell"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.side==self.side:
            super(self.__class__,self).trigger_effect(triggering_card)
            card = database.get_random_cards(filter_str="[class] LIKE '%Priest%' AND [type]='Spell'", owner=self.owner, k=1)[0]
            card.initialize_location(self.location)
            card.hand_in()

class Archbishop_Benedictus(Minion): 
    def __init__(self,name="Archbishop Benedictus",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def battlecry(self,target):
        card_copies=[]
        for card in self.owner.opponent.deck.cards:
            card_copy=card.get_copy(owner=self.owner)
            card_copy.initialize_location(self.owner.opponent.deck.location)
            card_copies.append(card_copy)
        self.shuffle_cards(card_copies,self.owner.deck)

class Temporus(Minion): 
    def __init__(self,name="Temporus",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def battlecry(self,target):
        time_warp_animation(self)
        self.owner.opponent.take_extra_turn+=1
        card=Temporus_Effect(owner=self.owner.opponent)
                    
class Temporus_Effect(Enchantment):
    def __init__(self,name="Temporus",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_events.append(("start of turn",self.trigger_effect))

    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner:
            self.owner.opponent.take_extra_turn+=1
                                                                                                                                                           
'''Rogue Minions'''
class Plaguebringer(Minion):
    def __init__(self,name="Plaguebringer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(chooser=self,target="friendly minion",message="give Poisonous")
        return target
    
    def battlecry(self,target):
        target.gain_poisonous()
        
class Defias_Ringleader(Minion):
    def __init__(self,name="Defias Ringleader",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def combo(self):
        minion=Defias_Bandit(owner=self.owner)
        self.summon(minion)

class Defias_Bandit(Minion):
    def __init__(self,name="Defias Bandit",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class SI7_Agent(Minion):
    def __init__(self,name="SI:7 Agent",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def combo(self):
        target=choose_target(chooser=self,target="character",message="deal 2 damage")
        if target is not None:
            si7_agent_animation(self,target)
            self.deal_damage([target], [2])

class Master_of_Disguise(Minion):
    def __init__(self,name="Master of Disguise",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(chooser=self,target="friendly minion",message="give stealth until your next turn")
        return target
    
    def battlecry(self,target):
        target.temporary_effects['stealth']=2
                                        
class Patient_Assassin(Minion):
    def __init__(self,name="Patient Assassin",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.poisonous=True
        self.stealth=True
        
class Kidnapper(Minion):
    def __init__(self,name="Kidnapper",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def combo(self):
        target=choose_target(chooser=self,target="minion",message="return to its owner's hand")
        if target is not None:
            target.return_hand(reset=True)
            
class Anubar_Ambusher(Minion):
    def __init__(self,name="Anub'ar_Ambusher",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        targets=self.friendly_minions()
        if len(targets>0):
            minion=random.choice(targets)
            minion.return_hand(reset=True)

class Goblin_Auto_Barber(Minion):
    def __init__(self,name="Goblin Auto-Barber",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        if self.owner.has_weapon():
            self.owner.weapon.buff_stats(1,0)

class One_Eyed_Cheat(Minion):
    def __init__(self,name="One-Eyed Cheat",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="summon a minion"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.owner is self.owner and triggering_card.has_race("Pirate") and triggering_card is not self:
            super(self.__class__,self).trigger_effect(triggering_card)
            self.gain_stealth()
                  
class Iron_Sensei(Minion):
    def __init__(self,name="Iron Sensei",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source) 
        self.trigger_event_type="end of turn"
       
    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner:
            super(self.__class__,self).trigger_effect(triggering_player)
            minion=self.get_another_friendly_minion("Mech")
            if minion is not None:
                mech_buff_animation(minion)
                minion.buff_stats(2,2)
            
class Ogre_Ninja(Minion):
    def __init__(self,name="Ogre Ninja",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.stealth=True
        self.trigger_event_type="attack"
        
    def trigger_effect(self,triggering_minion):
        if triggering_minion is self:
            self.attack_wrong_enemy(0.5)    

class Dark_Iron_Skulker(Minion):
    def __init__(self,name="Dark Iron Skulker",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        targets=[]
        for minion in self.enemy_minions():
            if not minion.damaged():
                targets.append(minion)
        if len(targets)>0:
            dark_iron_skulker_animation(self,targets)
            self.deal_damage(targets, [2]*len(targets))

class Buccaneer(Minion):
    def __init__(self,name="Buccaneer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="equip weapon"
        
    def trigger_effect(self,triggering_weapon):
        if triggering_weapon.side==self.side:
            super(self.__class__,self).trigger_effect(triggering_weapon)
            weapon_buff_animation(self)
            triggering_weapon.buff_stats(1,0)

class Undercity_Valiant(Minion):
    def __init__(self,name="Undercity Valiant",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def combo(self):
        target=choose_target(chooser=self,target="character",message="deal 1 damage")
        if target is not None:
            flame_juggler_animation(self, target)
            self.deal_damage([target], [1])

class Shado_Pan_Rider(Minion):
    def __init__(self,name="Shado-Pan Rider",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def combo(self):
        rage_buff_animation(self)
        self.buff_stats(3, 0)

class Cutpurse(Minion):
    def __init__(self,name="Cutpurse",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="attack"
        
    def trigger_effect(self,triggering_minion):
        if triggering_minion is self and self.target is self.owner.opponent:
            super(self.__class__,self).trigger_effect(triggering_minion)
            self.owner.get_coin() 

class Shade_Dealer(Minion):
    def __init__(self,name="Shade Dealer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        if self.owner.holding("Pirate"):
            buff_animation(self)
            self.buff_stats(1, 1)

class Pit_Snake(Minion):
    def __init__(self,name="Pit Snake",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.poisonous=True

class Tomb_Pillager(Minion): 
    def __init__(self,name="Tomb Pillager",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        card=The_Coin(owner=self.owner)
        card.appear_in_hand()

class Unearthed_Raptor(Minion):
    def __init__(self,name="Unearthed Raptor",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def get_target(self):
        target=choose_target(chooser=self,target="friendly minion",target_type="has_deathrattle attr", message="gain a copy of its Deatrhrattle")
        return target
    
    def battlecry(self,target):
        for deathrattle in target.deathrattles:
            self.deathrattles.append([MethodType(deathrattle[0].__func__,self),deathrattle[1]])
        self.has_deathrattle=True
        self.destroy=MethodType(target.destroy.__func__,self)
            
class Bladed_Cultist(Minion):
    def __init__(self,name="Bladed Cultist",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def combo(self):
        self.buff_stats(1, 1)
        buff_animation(self)

class Southsea_Squidface(Minion): 
    def __init__(self,name="Southsea Squidface",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        if self.owner.has_weapon():
            weapon_buff_animation(self)
            self.owner.weapon.buff_stats(2,0)

class Undercity_Huckster(Minion): 
    def __init__(self,name="Undercity Huckster",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        card = database.get_random_cards("[class] LIKE '%"+self.owner.opponent.class_name+"%'", self.owner, 1)[0]
        card.initialize_location(self.location)
        card.hand_in(speed=30)

class Shadowcaster(Minion):
    def __init__(self,name="Shadowcaster",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def get_target(self):
        minion=choose_target(chooser=self,target="friendly minion",message="add a 1/1 copy")
        return minion
    
    def battlecry(self,target):
        minion_copy = getattr(card_collection,database.cleaned(target.name))(owner=target.owner,source=self.location)
        minion_copy.set_stats(1,1) 
        minion_copy.current_cost=1
        minion_copy.hand_in()

class Blade_of_CThun(Minion):
    def __init__(self,name="Blade of C'Thun",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def get_target(self):
        minion=choose_target(chooser=self,target="minion",message="destroy")
        return minion
    
    def battlecry(self,target):
        the_black_knight_animation(self, target)
        self.buff_cthun(target.get_current_atk(), target.get_current_hp())
        target.destroy()

class Swashburglar(Minion): 
    def __init__(self,name="Swashburglar",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target):
        card = database.get_random_cards("[class] LIKE '%"+self.owner.opponent.class_name+"%'", self.owner, 1)[0]
        card.initialize_location(self.location)
        card.hand_in(speed=30)

class Deadly_Fork(Minion): 
    def __init__(self,name="Deadly Fork",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        weapon=Sharp_Fork(owner=self.owner)
        weapon.initialize_location(self.location)
        weapon.hand_in()

class Ethereal_Peddler(Minion): 
    def __init__(self,name="Ethereal Peddler",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target):
        for card in self.owner.hand:
            if card.card_class not in [self.owner.class_name,"Neutral"]:
                card.modify_cost(-2)

class Jade_Swarmer(Minion):
    def __init__(self,name="Jade Swarmer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.stealth=True
        
    def deathrattle(self):
        minion=Jade_Golem(owner=self.owner)
        self.summon(minion)

class Shadow_Rager(Minion):
    def __init__(self,name="Shadow Rager",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.stealth=True

class Gadgetzan_Ferryman(Minion):
    def __init__(self,name="Gadgetzan Ferryman",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def combo(self):
        target=choose_target(chooser=self,target="friendly minion",message="return to hand")
        if target is not None:
            youthful_brewmaster_animation(self, target)
            target.return_hand()

class Shadow_Sensei(Minion):
    def __init__(self,name="Shadow Sensei",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
  
    def get_target(self):
        target=choose_target(self, target="friendly minion", target_type="has_stealth attr", message="give +2/+2")
        return target
    
    def battlecry(self,target):
        rogue_buff_animation(self, target)
        target.buff_stats(2,2)

class Lotus_Assassin(Minion):
    def __init__(self,name="Lotus Assassin",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="after attack"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card is self and self.target.destroyed_by is self:
            super(self.__class__,self).trigger_effect(triggering_card)
            self.gain_stealth()

class Luckydo_Buccaneer(Minion): 
    def __init__(self,name="Luckydo Buccaneer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target):
        if self.owner.has_weapon() and self.owner.weapon.get_current_atk()>=3:
            rogue_buff_animation(self, self)
            self.buff_stats(4,4)

class Razorpetal_Lasher(Minion):
    def __init__(self,name="Razorpetal Lasher",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
    
    def battlecry(self,target):
        card=Razorpetal(owner=self.owner)
        card.initialize_location(self.location)
        card.hand_in()

class Biteweed(Minion):
    def __init__(self,name="Biteweed",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def combo(self):
        n=len(self.owner.played_cards[self.owner.turn])
        self.buff_stats(n, n)
        buff_animation(self)

class Vilespine_Slayer(Minion):
    def __init__(self,name="Vilespine Slayer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def combo(self):
        target=choose_target(chooser=self,target="minion",message="destroy")
        if target is not None:
            assassinate_animation(self, target)
            target.destroy()

class Plague_Scientist(Minion):
    def __init__(self,name="Plague Scientist",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def combo(self):
        target=choose_target(chooser=self,target="friendly minion",message="give Poisonous")
        if target is not None:
            weapon_enchantment_animation(self, target)
            target.gain_poisonous()

class Bone_Baron(Minion):
    def __init__(self,name="Bone Baron",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        for i in range(2):
            minion=Skeleton_1_1(owner=self.owner,source=self.location)
            minion.hand_in(speed=35)

class Spectral_Pillager(Minion):
    def __init__(self,name="Spectral Pillager",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def combo(self):
        n=len(self.owner.played_cards[self.owner.turn])
        target=choose_target(chooser=self,target="character",message="deal "+str(n)+" damage")
        if target is not None:
            charge_shot_animation(self, target)
            self.deal_damage([target], [n])

class Cavern_Shinyfinder(Minion):
    def __init__(self,name="Cavern Shinyfinder",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
    
    def battlecry(self,target):
        weapon=self.owner.search_card(self.owner.deck.cards,"Weapon")
        if weapon is not None:
            self.owner.draw(target=weapon)

class Elven_Minstrel(Minion):
    def __init__(self,name="Elven Minstrel",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def combo(self):
        self.owner.draw(2)

class Kobold_Illusionist(Minion):
    def __init__(self,name="Kobold Illusionist",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        minion=self.owner.search_card(self.owner.hand,"Minion")
        minion_copy=minion.get_1_1_copy(owner=self.owner)
        self.summon(minion_copy)
     
class Faldorei_Strider(Minion):
    def __init__(self,name="Fal'dorei Strider",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
    
    def battlecry(self,target):
        for i in range(3):
            card=Spider_Ambush(owner=self.owner)
            card.initialize_location(self.owner.location)
            card.shuffle_into_deck(skip_zoom=(i>=1))

class Spider_Ambush(Spell):
    def __init__(self,name="Spider Ambush!",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        self.casts_when_drawn=True

    def invoke(self,target=None):
        super(self.__class__,self).invoke()
        minion=Leyline_Spider(owner=self.owner,source="board")
        self.owner.recruit(minion)

class Leyline_Spider(Minion):
    def __init__(self,name="Leyline Spider",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
                                                                                                                                                                                                                                                                                                                                                                                                          
class Edwin_VanCleef(Minion):
    def __init__(self,name="Edwin VanCleef",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def combo(self):
        n=len(self.owner.played_cards[self.owner.turn])
        self.buff_stats(n*2, n*2)
        buff_animation(self)

class Trade_Prince_Gallywix(Minion):
    def __init__(self,name="Trade Prince Gallywix",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="cast a spell"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.side==-self.side and not isinstance(triggering_card, Gallywixs_Coin):
            super(self.__class__,self).trigger_effect(triggering_card)
            gadgetzan_auctioneer_animation(self)
            card_copy = getattr(card_collection,database.cleaned(triggering_card.name))(owner=triggering_card.owner.opponent)
            card_copy.appear_in_hand()
            
            coin=Gallywixs_Coin(owner=self.owner.opponent)
            coin.appear_in_hand()

class Gallywixs_Coin(Spell):
    def __init__(self,name="Gallywix's Coin",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        self.owner.current_mana+=1

class Anubarak(Minion):
    def __init__(self,name="Anub'arak",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
                
    def destroy(self,skip_animation=False,skip_deathrattle=False):
        for deathrattle in self.deathrattles:
            deathrattle[0]()

        if self.board_area!="Hand":
            super(self.__class__,self).destroy(skip_animation=skip_animation,skip_deathrattle=True)

    def deathrattle(self):
        anubarak_animation(self)
        minion=Nerubian_Beneath_the_Grounds(owner=self.owner)
        self.summon(minion)
        if self.board_area=="Board":
            self.return_hand(reset=True)

class Xaril_Poisoned_Mind(Minion):
    def __init__(self,name="Xaril, Poisoned Mind",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def battlecry(self,target):
        toxin=random.choice([Bloodthistle_Toxin,Briarthorn_Toxin,Fadeleaf_Toxin,Firebloom_Toxin,Kingsblood_Toxin])
        card=toxin(owner=self.owner)
        card.initialize_location(self.location)
        card.hand_in()
     
    def deathrattle(self):
        toxin=random.choice([Bloodthistle_Toxin,Briarthorn_Toxin,Fadeleaf_Toxin,Firebloom_Toxin,Kingsblood_Toxin])
        card=toxin(owner=self.owner)
        card.initialize_location(self.location)
        card.hand_in()
           
class Bloodthistle_Toxin(Spell):
    def __init__(self,name="Bloodthistle Toxin",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None and target.isMinion() and target.side==self.side
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        rogue_buff_animation(self,target)
        target.return_hand(reset=True)
        target.current_cost=target.cost-2

class Briarthorn_Toxin(Spell):
    def __init__(self,name="Briarthorn Toxin",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None and target.isMinion()
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        buff_animation(self,target)
        target.buff_stats(3,0)
        
class Fadeleaf_Toxin(Spell):
    def __init__(self,name="Fadeleaf Toxin",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None and target.isMinion() and target.side==self.side

    def invoke(self,target):
        super(self.__class__,self).invoke()
        mech_buff_animation(target)
        target.temporary_effects['stealth']=2

class Firebloom_Toxin(Spell):
    def __init__(self,name="Firebloom Toxin",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        backstab_animation(self,target)
        self.deal_damage([target],[2])
            
class Kingsblood_Toxin(Spell):
    def __init__(self,name="Kingsblood Toxin",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        
    def invoke(self,target):
        super(self.__class__,self).invoke()
        self.owner.draw()
        
class Shaku_the_Collector(Minion):
    def __init__(self,name="Shaku, the Collector",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.stealth=True
        self.trigger_event_type="attack"
        
    def trigger_effect(self,triggering_minion):
        if triggering_minion is self:
            super(self.__class__,self).trigger_effect(triggering_minion)
            card = database.get_random_cards("[class] LIKE '%"+self.owner.opponent.class_name+"%'", self.owner, 1)[0]
            card.initialize_location(self.owner.opponent.location)
            card.hand_in(speed=50)

class Sherazin_Corpse_Flower(Minion):
    def __init__(self,name="Sherazin, Corpse Flower",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
     
    def deathrattle(self):
        if self.board_area=="Board":
            self.destroy()
        else:
            minion=Sherazin_Seed(owner=self.owner)
            self.summon(minion)
            self.owner.enchantments.append(minion)
        
class Sherazin_Seed(Minion):
    def __init__(self,name="Sherazin, Seed",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.dormant=True
        self.dormant_cap=4
        self.current_hp=1
        self.trigger_event_type="play a card"
        self.trigger_events.append([self.trigger_event_type,self.trigger_effect])
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.owner is self.owner:
            self.increment_dormant_counter()
                    
    def refresh_status(self):
        self.dormant_counter=0
    
    def awake(self):
        self.has_dormant=False
        awake_animation(self)
        minion=Sherazin_Corpse_Flower(owner=self.owner)
        self.transform(minion)
        if self in self.owner.enchantments:
            self.owner.enchantments.remove(self)

class Lilian_Voss(Minion):
    def __init__(self,name="Lilian Voss",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def battlecry(self,target):
        replace_hand_animation(self)
        for card in self.owner.hand:
            if card.isSpell:
                new_spell=database.get_random_cards("[type]='Spell' AND [class] LIKE '%"+self.owner.opponent.class_name+"%'", self.owner, 1)[0]
                card.replace_by(new_spell)

class Sonya_Shadowdancer(Minion):
    def __init__(self,name="Sonya Shadowdancer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="minion dies"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.side==self.side and triggering_card is not self:
            super(self.__class__,self).trigger_effect(triggering_card)
            card_copy=triggering_card.get_1_1_copy(owner=self.owner)
            card_copy.initialize_location(self.location)
            card_copy.current_cost=1
            card_copy.hand_in()
                                                                                                                                                
'''Shaman Minions'''
class Healing_Totem(Minion):
    def __init__(self,name="Healing Totem",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="end of turn"
        
    def trigger_effect(self,triggering_player):
        if triggering_player is self.owner:
            self.heal(self.friendly_minions(),[1]*len(self.friendly_minions()))
        
class Searing_Totem(Minion):
    def __init__(self,name="Searing Totem",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        
class Stoneclaw_Totem(Minion):
    def __init__(self,name="Stoneclaw Totem",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        
class Wrath_of_Air_Totem(Minion):
    def __init__(self,name="Wrath of Air Totem",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.spell_damage_boost=1
        
class Flametongue_Totem(Minion):
    def __init__(self,name="Flametongue Totem",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def ongoing_effect(self,target):
        if target.isMinion() and target.board_area=="Board" and target.side==self.side and abs(target.get_index()-self.get_index())==1:
            return {'atk':2}
        else:
            return {} 

class Frog(Minion):
    def __init__(self,name="Frog",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True

class Windspeaker(Minion):
    def __init__(self,name="Windspeaker",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(chooser=self,target="friendly minion",message="give Windfury")
        return target
    
    def battlecry(self,target):
        target.gain_windfury()
        
class Fire_Elemental(Minion):
    def __init__(self,name="Fire Elemental",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(chooser=self,target="character",message="deal 3 damage")
        return target
    
    def battlecry(self,target):
        fire_bolt_animation(self, target)
        self.deal_damage([target], [3])
        
class Dust_Devil(Minion):
    def __init__(self,name="Dust Devil",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.windfury=True
        self.overload=2
        
class Unbound_Elemental(Minion):
    def __init__(self,name="Unbound Elemental",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="play a card"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.owner is self.owner and triggering_card.overload:
            super(self.__class__,self).trigger_effect(triggering_card)
            buff_animation(self,speed=8)
            self.buff_stats(1, 1)

class Spirit_Wolf(Minion):
    def __init__(self,name="Spirit Wolf",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True

class Mana_Tide_Totem(Minion):
    def __init__(self,name="Mana Tide Totem",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="end of turn"
        
    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner:
            super(self.__class__,self).trigger_effect(triggering_player)
            self.owner.draw()
            
class Earth_Elemental(Minion):
    def __init__(self,name="Earth Elemental",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        self.overload=3

class Whirling_Zap_o_matic(Minion):
    def __init__(self,name="Whirling Zap-o-matic",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source) 
        self.windfury=True
        
class Vitality_Totem(Minion):
    def __init__(self,name="Vitality Totem",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source) 
        self.trigger_event_type="end of turn"
       
    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner:
            super(self.__class__,self).trigger_effect(triggering_player)
            self.heal([self.owner], [4])

class Dunemaul_Shaman(Minion):
    def __init__(self,name="Dunemaul Shaman",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.windfury=True
        self.overload=1
        self.trigger_event_type="attack"
        
    def trigger_effect(self,triggering_minion):
        if triggering_minion is self:
            self.attack_wrong_enemy(0.5)    

class Siltfin_Spiritwalker(Minion):
    def __init__(self,name="Siltfin Spiritwalker",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="minion dies"
        self.overload=1
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.side==self.side and triggering_card.has_race("Murloc") and triggering_card is not self:
            super(self.__class__,self).trigger_effect(triggering_card)
            self.owner.draw()

class Fireguard_Destroyer(Minion):
    def __init__(self,name="Fireguard Destroyer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.overload=1
        
    def battlecry(self,target=None):
        rage_buff_animation(self)
        self.buff_stats(random.randint(1,4), 0)

class Totem_Golem(Minion):
    def __init__(self,name="Totem Golem",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.overload=1

class Tuskarr_Totemic(Minion):
    def __init__(self,name="Tuskarr Totemic",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        totemic_call_animation(self.owner)
        totem_name = random.choice(["Healing Totem","Searing Totem","Stoneclaw Totem","Wrath of Air Totem"])
        minion=getattr(card_collection, database.cleaned(totem_name))(owner=self.owner)
        self.summon(minion)

class Draenei_Totemcarver(Minion):
    def __init__(self,name="Draenei Totemcarver",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        n=len(self.friendly_minions("Totem"))
        self.buff_stats(n, n)

class Thunder_Bluff_Valiant(Minion):
    def __init__(self,name="Thunder Bluff Valiant",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.inspire=True
        
    def trigger_inspire(self, hero_power=None):
        if hero_power.owner is self.owner:
            super(self.__class__,self).trigger_inspire()
            targets=self.friendly_minions("Totem")
            buff_multiple_animation(self, targets)
            for minion in targets:
                minion.buff_stats(2,0)

class Tunnel_Trogg(Minion):
    def __init__(self,name="Tunnel Trogg",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="play a card"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.owner is self.owner and triggering_card.overload:
            super(self.__class__,self).trigger_effect(triggering_card)
            buff_animation(self,speed=8)
            self.buff_stats(triggering_card.overload, 0)

class Rumbling_Elemental(Minion):
    def __init__(self,name="Rumbling Elemental",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="summon a minion"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.side==self.side and 'Battlecry' in triggering_card.abilities:
            super(self.__class__,self).trigger_effect(triggering_card)
            target=random.choice(self.enemy_characters())
            charge_shot_animation(self,target)
            self.deal_damage([target], [2])

class Flamewreathed_Faceless(Minion):
    def __init__(self,name="Flamewreathed Faceless",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.overload=2

class Master_of_Evolution(Minion):
    def __init__(self,name="Master of Evolution",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(self, target="friendly minion", message="evolve")
        return target
    
    def battlecry(self,target):
        target.evolve(1)

class Thing_from_Below(Minion):
    def __init__(self,name="Thing from Below",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
                
    def ongoing_effect(self,target):
        if target is self and target.board_area=="Hand" and "Totem" in self.owner.summoned_minions:
            return {'cost':-len(self.owner.summoned_minions["Totem"])}
        else:
            return {} 

class Eternal_Sentinel(Minion):
    def __init__(self,name="Eternal Sentinel",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
    
    def battlecry(self,target):
        self.owner.overloaded_mana=0

class Twilight_Elemental(Minion):
    def __init__(self,name="Twilight Elemental",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Wicked_Witchdoctor(Minion):
    def __init__(self,name="Wicked Witchdoctor",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="cast a spell"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.owner is self.owner:
            super(self.__class__,self).trigger_effect(triggering_card)
            totemic_call_animation(self.owner)
            totem_name = random.choice(["Healing Totem","Searing Totem","Stoneclaw Totem","Wrath of Air Totem"])
            minion=getattr(card_collection, database.cleaned(totem_name))(owner=self.owner)
            self.summon(minion)

class Murloc_Razorgill(Minion):
    def __init__(self,name="Murloc Razorgill",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Jade_Chieftain(Minion):
    def __init__(self,name="Jade Chieftain",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        minion = Jade_Golem(owner=self.owner)
        self.summon(minion)
        minion.gain_taunt()

class Jinyu_Waterspeaker(Minion):
    def __init__(self,name="Jinyu Waterspeaker",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.overload=1
        
    def get_target(self):
        target=choose_target(chooser=self,target="character",message="restore 6 health")
        return target
    
    def battlecry(self,target):
        lesser_heal_animation(self, target)
        self.heal([target],[6])

class Lotus_Illusionist(Minion):
    def __init__(self,name="Lotus Illusionist",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="after attack"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card is self and self.target.isHero():
            super(self.__class__,self).trigger_effect(triggering_card)
            minion = database.get_random_cards("[type]='Minion' AND [cost]=6", self.owner, 1)[0]
            self.transform(minion)

class Air_Elemental(Minion):
    def __init__(self,name="Air Elemental",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.elusive=True 

class Hot_Spring_Guardian(Minion):
    def __init__(self,name="Hot Spring Guardian",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(chooser=self,target="character",message="restore 3 health")
        return target
    
    def battlecry(self,target):
        lesser_heal_animation(self, target)
        target.restore_health(3,self)

class Fire_Plume_Harbinger(Minion):
    def __init__(self,name="Fire Plume Harbinger",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
 
    def battlecry(self,target):
        for card in self.owner.hand:
            if card.has_race("Elemental"):
                card.modify_cost(-1)

class Primalfin_Totem(Minion):
    def __init__(self,name="Primalfin Totem",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="end of turn"
        
    def trigger_effect(self,triggering_player):
        if triggering_player is self.owner:
            super(self.__class__,self).trigger_effect(triggering_player)
            minion=Primalfin(owner=self.owner)
            self.summon(minion)

class Stone_Sentinel(Minion):
    def __init__(self,name="Stone Sentinel",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        if self.owner.played_before("Elemental"):
            for i in range(2):
                minion=Rock_Elemental(owner=self.owner)
                self.summon(minion,left=(-1)**i)
                
class Rock_Elemental(Minion):
    def __init__(self,name="Rock Elemental",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Brrrloc(Minion):
    def __init__(self,name="Brrrloc",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(chooser=self,target="enemy character",message="freeze")
        return target
    
    def battlecry(self,target):
        glacial_shard_animation(self, target)
        target.get_frozen()

class Drakkari_Defender(Minion):
    def __init__(self,name="Drakkari Defender",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        self.overload=3

class Voodoo_Hexxer(Minion):
    def __init__(self,name="Voodoo Hexxer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        self.trigger_event_type="deal damage"
        
    def trigger_effect(self,triggering_entity):
        if triggering_entity[0] is self:
            super(self.__class__,self).trigger_effect(triggering_entity[0])
            for target in triggering_entity[2]:
                target.get_frozen()
                                                                                                                                                           
class Snowfury_Giant(Minion):
    def __init__(self,name="Snowfury Giant",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def ongoing_effect(self,target):
        if target is self and target.board_area=="Hand":
            return {'cost':-self.owner.total_overloaded_mana}
        else:
            return {} 

class Kobold_Hermit(Minion):
    def __init__(self,name="Kobold Hermit",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def battlecry(self,target):
        if not self.owner.board.isFull(self.owner):  
            # Get a list of unsummoned totems
            totem1         = Healing_Totem(owner=self.owner,source="board")
            totem2         = Searing_Totem(owner=self.owner,source="board")
            totem3         = Wrath_of_Air_Totem(owner=self.owner,source="board")
            totem4         = Stoneclaw_Totem(owner=self.owner,source="board")
            selected_totem = choose_one([totem1,totem2,totem3,totem4])
            self.summon(selected_totem)

class Murmuring_Elemental(Minion):
    def __init__(self,name="Murmuring Elemental",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target):
        card=Murmuring_Elemental_Effect(owner=self.owner)
        card.origin=self
                                               
class Murmuring_Elemental_Effect(Enchantment):
    def __init__(self,name="Murmuring Elemental",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_events.append(("play a card",self.trigger_effect))

    def ongoing_effect(self,target):
        if target.side==self.side:
            return {'battlecry twice':True}
        else:
            return {}            
        
    def trigger_effect(self, triggering_card):
        if triggering_card.side==self.side and 'Battlecry' in triggering_card.abilities and triggering_card is not self.origin:
            self.destroy()

class Windshear_Stormcaller(Minion):
    def __init__(self,name="Windshear Stormcaller",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target):
        if self.owner.control_all([Healing_Totem,Searing_Totem,Stoneclaw_Totem,Wrath_of_Air_Totem]):
            minion=AlAkir_the_Windlord(owner=self.owner)
            malygos_animation(minion)
            self.summon(minion)
                                                                                                                                                            
class Murkspark_Eel(Minion):
    def __init__(self,name="Murkspark Eel",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=None
        if self.owner.deck.has_even_cards_only():
            target=choose_target(chooser=self,target="character",message="deal 2 damage")
        return target
    
    def battlecry(self,target):
        murkspark_eel_animation(self, target)
        self.deal_damage([target], [2])
                                               
class Ghost_Light_Angler(Minion):
    def __init__(self,name="Ghost Light Angler",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

class AlAkir_the_Windlord(Minion):
    def __init__(self,name="Al'Akir the Windlord",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.windfury=True
        self.charge=True
        self.divine_shield=True
        self.taunt=True

class Neptulon(Minion):
    def __init__(self,name="Neptulon",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.overload=3
        
    def battlecry(self,target=None):
        minions = database.get_random_cards("[race]='Murloc'", self.owner, 4)
        for minion in minions:
            minion.location=self.location
            minion.hand_in(speed=60)
        
class The_Mistcaller(Minion):
    def __init__(self,name="The Mistcaller",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        the_mistcaller_animation(self)
        for target in self.owner.hand+self.owner.deck.cards:
            if target.isMinion():
                target.buff_stats(1,1)

class Hallazeal_the_Ascended(Minion):
    def __init__(self,name="Hallazeal the Ascended",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="minion damage"
        
    def trigger_effect(self,triggering_entity):
        if triggering_entity[0].last_damage_source.isSpell:
            super(self.__class__,self).trigger_effect(self)
            ragnaros_lightlord_animation(self, self.owner)
            self.heal([self.owner],[triggering_entity[1]])
                        
class White_Eyes(Minion):
    def __init__(self,name="White Eyes",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        
    def deathrattle(self):
        minion=The_Storm_Guardian(owner=self.owner,source=self.location)
        minion.shuffle_into_deck(self.owner.deck)
            
class The_Storm_Guardian(Minion):
    def __init__(self,name="The Storm Guardian",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True

class Megafin(Minion):
    def __init__(self,name="Megafin",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
    
    def battlecry(self,target):
        while len(self.owner.hand)<self.owner.hand_limit:
            minion = database.get_random_cards("[type]='Minion' AND [race]='Murloc'", self.owner, 1)[0]
            minion.initialize_location(self.location)
            minion.hand_in(speed=60)

class Kalimos_Primal_Lord(Minion):
    def __init__(self,name="Kalimos, Primal Lord",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        if self.owner.played_before("Elemental"):
            selected_card = choose_one([option(owner=self.owner) for option in [Invocation_of_Air,Invocation_of_Earth,Invocation_of_Fire,Invocation_of_Water]])
            if selected_card is not None:
                selected_card.origin=self
                selected_card.invoke()
 
class Invocation_of_Air(Spell):
    def __init__(self,name="Invocation of Air",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target=None):
        targets=self.enemy_minions()
        lightning_storm_animation(self)
        self.deal_damage(targets,[3]*len(targets))

class Invocation_of_Earth(Spell):
    def __init__(self,name="Invocation of Earth",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target=None):
        while not self.owner.board.isFull(self.owner):
            minion=Stone_Elemental(owner=self.owner,source="board")
            self.owner.recruit(minion)

class Stone_Elemental(Minion):
    def __init__(self,name="Stone Elemental",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Invocation_of_Fire(Spell):
    def __init__(self,name="Invocation of Fire",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target=None):
        fire_spell_animation(self, self.owner.opponent)
        self.deal_damage([self.owner.opponent],[6])

class Invocation_of_Water(Spell):
    def __init__(self,name="Invocation of Water",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target=None):
        healing_touch_animation(self, self.owner)
        self.heal([self.owner],[12])

class Moorabi(Minion):
    def __init__(self,name="Moorabi",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="frozen"
        self.tags.append("Triggered effect")
        
    def trigger_effect(self, triggering_entity=None):
        if triggering_entity.isMinion() and triggering_entity is not self:
            super(self.__class__,self).trigger_effect(self)
            card_copy=triggering_entity.get_copy(owner=self.owner)
            card_copy.appear_in_hand()

class Grumble_Worldshaker(Minion):
    def __init__(self,name="Grumble, Worldshaker",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target):
        vanish_animation(self, self.friendly_minions())
        for minion in self.friendly_minions():
            minion.return_hand(skip_animation=True)
            minion.current_cost=1
            
                                                                                                                     
'''Warlock Minions'''                                                 
class Voidwalker(Minion):
    def __init__(self,name="Voidwalker",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True

            
class Felstalker(Minion):
    def __init__(self,name="Felstalker",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        self.owner.discard(1)

class Doomguard(Minion):
    def __init__(self,name="Doomguard",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.charge=True
        
    def battlecry(self,target=None):
        self.owner.discard(2)
                
class Dread_Infernal(Minion):
    def __init__(self,name="Dread Infernal",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        targets=self.all_characters()
        dread_infernal_animation(self)
        self.deal_damage(targets, [1]*len(targets))

class Blood_Imp(Minion):
    def __init__(self,name="Blood Imp",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.stealth=True
        self.trigger_event_type="end of turn"
       
    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner:
            super(self.__class__,self).trigger_effect(triggering_player)
            minion=self.get_another_friendly_minion()
            if minion is not None:
                minion.buff_stats(0,1)

class Flame_Imp(Minion):
    def __init__(self,name="Flame Imp",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        fire_bolt_animation(self, self.owner)
        self.deal_damage([self.owner], [3])
                                    
class Voidcaller(Minion):
    def __init__(self,name="Voidcaller",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        demon=self.owner.search_card(self.owner.hand,"Demon")
        if demon is not None:
            self.owner.put_into_battlefield(demon,location="board")

class Worthless_Imp(Minion):
    def __init__(self,name="Worthless Imp",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

        
class Glinda_Crowskin(Minion):
    def __init__(self,name="Glinda Crowskin",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def ongoing_effect(self,target):
        if target.isMinion() and target.side==self.side and target is not self :
            return {'echo':True}
        else:
            return {}

class Summoning_Portal(Minion):
    def __init__(self,name="Summoning Portal",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def ongoing_effect(self,target,pool):
        if target.isMinion() and target.side==self.side and target.board_area=="Hand" and target is not self:
            i=pool.index(self)
            if i==0:
                if target.current_cost<=1:
                    reduction=0
                elif 1<target.current_cost==2:
                    reduction=1
                else:
                    reduction=2
                return {'cost':-reduction}
            else:
                target_current_cost=target.current_cost
                for k in range(i):
                    target_current_cost+=pool[k].ongoing_effect(target,pool[:k+1])['cost']
                    
                if target_current_cost<=1:
                    reduction=0
                elif 1<target_current_cost==2:
                    reduction=1
                else:
                    reduction=2
                return {'cost':-reduction}
        else:
            return {'cost':0}
                  
class Felguard(Minion):
    def __init__(self,name="Felguard",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        
    def battlecry(self,target=None):
        self.owner.gain_mana(-1,empty=(self.owner.mana>self.owner.current_mana))

class Siegebreaker(Minion):
    def __init__(self,name="Siegebreaker",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        
    def ongoing_effect(self,target):
        if target.isMinion() and target.board_area=="Board" and target.side==self.side and target.has_race("Demon"):
            return {'atk':1}
        else:
            return {} 

class Pit_Lord(Minion):
    def __init__(self,name="Pit Lord",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        fire_bolt_animation(self, self.owner)
        self.deal_damage([self.owner], [5])

class Floating_Watcher(Minion):
    def __init__(self,name="Floating Watcher",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="hero damage"
        
    def trigger_effect(self,triggering_entity):
        if self.owner.board.control==self.owner.side:
            super(self.__class__,self).trigger_effect(self)
            rage_buff_animation(self) 
            self.buff_stats(2, 2)

class Fel_Cannon(Minion):
    def __init__(self,name="Fel Cannon",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source) 
        self.trigger_event_type="end of turn"
       
    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner:
            super(self.__class__,self).trigger_effect(triggering_player)
            target_pool=self.all_minions_except("Mech")
            if len(target_pool)>0:
                target = random.choice(target_pool)
                fel_cannon_animation(self,target)
                self.deal_damage([target], [2])
            
class Queen_of_Pain(Minion):
    def __init__(self,name="Queen of Pain",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.lifesteal=True

class Anima_Golem(Minion):
    def __init__(self,name="Anima Golem",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="end of turn"
        
    def trigger_effect(self,triggering_player):
        if len(self.friendly_minions())==1:
            super(self.__class__,self).trigger_effect(triggering_player)
            self.destroy()
                
class Imp_Gang_Boss(Minion):
    def __init__(self,name="Imp Gang Boss",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="minion damage"
        
    def trigger_effect(self,triggering_entity):
        if triggering_entity[0] is self:
            super(self.__class__,self).trigger_effect(self)
            minion=Imp_Imp_Gang_Boss(owner=self.owner)
            self.summon(minion)

class Wrathguard(Minion):
    def __init__(self,name="Wrathguard",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="minion damage"
        
    def trigger_effect(self,triggering_entity):
        if triggering_entity[0] is self:
            super(self.__class__,self).trigger_effect(self)
            fire_bolt_animation(self, self.owner)
            self.deal_damage([self.owner], [triggering_entity[1]])

class Fearsome_Doomguard(Minion):
    def __init__(self,name="Fearsome Doomguard",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

class Tiny_Knight_of_Evil(Minion):
    def __init__(self,name="Tiny Knight of Evil",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="on discard"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.owner is self.owner:
            super(self.__class__,self).trigger_effect(triggering_card)
            buff_animation(self)
            self.buff_stats(1,1)

class Void_Crusher(Minion):
    def __init__(self,name="Void Crusher",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.inspire=True
        
    def trigger_inspire(self, hero_power=None):
        if hero_power.owner is self.owner:
            super(self.__class__,self).trigger_inspire()
            minions=[]
            minions.append(random.choice(self.friendly_minions()))
            if len(self.enemy_minions())>0:
                minions.append(random.choice(self.enemy_minions()))
            void_crusher_animation(self,minions) 
            for minion in minions:
                minion.destroy()

class Dreadsteed(Minion):
    def __init__(self,name="Dreadsteed",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        card=Dreadsteed_Effect(owner=self.owner)

class Dreadsteed_Effect(Enchantment):
    def __init__(self,name="Dreadsteed",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        
    def trigger_remove(self, triggering_player):
        self.destroy()
        minion=Dreadsteed(owner=self.owner,source="board")
        self.owner.recruit(minion)

class Dark_Peddler(Minion):
    def __init__(self,name="Dark Peddler",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        card=self.discover(filter_str="[cost]=1")
        if card is not None:
            card.hand_in()

class Reliquary_Seeker(Minion):
    def __init__(self,name="Reliquary Seeker",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        if len(self.owner.minions)>=7:
            demonheart_animation(self, self)
            self.buff_stats(4, 4)

class Possessed_Villager(Minion):
    def __init__(self,name="Possessed Villager",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        minion=Shadowbeast(owner=self.owner)
        self.summon(minion)
            
class Shadowbeast(Minion):
    def __init__(self,name="Shadowbeast",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Darkshire_Councilman(Minion):
    def __init__(self,name="Darkshire Councilman",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="summon a minion"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.side==self.side and triggering_card is not self:
            super(self.__class__,self).trigger_effect(triggering_card)
            self.buff_stats(1, 0)

class Usher_of_Souls(Minion):
    def __init__(self,name="Usher of Souls",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="minion dies"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.side==self.side and triggering_card is not self:
            super(self.__class__,self).trigger_effect(triggering_card)
            self.buff_cthun(1, 1)

class Icky_Tentacle(Minion):
    def __init__(self,name="Icky Tentacle",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Darkshire_Librarian(Minion):
    def __init__(self,name="Darkshire Librarian",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def battlecry(self,target):
        self.owner.discard()
     
    def deathrattle(self):
        self.owner.draw()
                                                                                                                                                                                                                                                               
class Malchezaars_Imp(Minion):
    def __init__(self,name="Malchezaar's Imp",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="on discard"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.owner is self.owner:
            super(self.__class__,self).trigger_effect(triggering_card)
            self.owner.draw()

class Candle(Minion):
    def __init__(self,name="Candle",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Broom(Minion):
    def __init__(self,name="Broom",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        
class Teapot(Minion):
    def __init__(self,name="Teapot",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Silverware_Golem(Minion):
    def __init__(self,name="Silverware Golem",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def on_discard(self):
        self.initialize_location("board")
        if self in self.owner.discards:
            self.owner.discards.remove(self)
        self.owner.recruit(self)     

class Crystal_Weaver(Minion):
    def __init__(self,name="Crystal Weaver",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        self.buff_multiple(race="Demon",atk=1,hp=1)

class Abyssal_Enforcer(Minion):
    def __init__(self,name="Abyssal Enforcer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        targets=self.all_characters()
        dread_infernal_animation(self)
        self.deal_damage(targets, [3]*len(targets))

class Seadevil_Stinger(Minion):
    def __init__(self,name="Seadevil Stinger",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def battlecry(self,target=None):
        card=Seadevil_Stinger_Effect(owner=self.owner)
        card.origin=self
                    
class Seadevil_Stinger_Effect(Enchantment):
    def __init__(self,name="Seadevil Stinger",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_events.append(("play a card",self.trigger_effect))

    def ongoing_effect(self,target):
        if target.isMinion() and target.has_race("Murloc") and target.side==self.side:
            return {'cost health':True}
        else:
            return {}            
        
    def trigger_effect(self, triggering_card):
        if triggering_card.isMinion() and triggering_card.has_race("Murloc") and triggering_card.side==self.side and triggering_card is not self.origin:
            self.destroy()

class Unlicensed_Apothecary(Minion):
    def __init__(self,name="Unlicensed Apothecary",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="summon a minion"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.side==self.side and triggering_card is not self:
            super(self.__class__,self).trigger_effect(triggering_card)
            fel_cannon_animation(self, self.owner)
            self.deal_damage([self.owner], [5])

class Kabal_Trafficker(Minion):
    def __init__(self,name="Kabal Trafficker",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source) 
        self.trigger_event_type="end of turn"
       
    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner:
            super(self.__class__,self).trigger_effect(triggering_player)
            minion = database.get_random_cards("[type]='Minion' AND [race]='Demon'", self.owner, 1)[0]
            minion.initialize_location(self.location)
            unstable_portal_animation(self, minion)
            minion.hand_in()

class Lakkari_Felhound(Minion):
    def __init__(self,name="Lakkari Felhound",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        
    def battlecry(self,target=None):
        self.owner.discard(2)

class Ravenous_Pterrordax(Minion):
    def __init__(self,name="Ravenous Pterrordax",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def combo(self):
        target=choose_target(chooser=self,target="friendly minion",message="destroy")
        if target is not None:
            target.destroy()
            self.adapt(2)

class Tar_Lurker(Minion):
    def __init__(self,name="Tar Lurker",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        
    def ongoing_effect(self,target):
        if target is self and self.owner.board.control==-self.side:
            return {'atk':3}
        else:
            return {}
        
class Pterrordax(Minion):
    def __init__(self,name="Pterrordax",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Cruel_Dinomancer(Minion):
    def __init__(self,name="Cruel Dinomancer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        minion=self.owner.search_card(self.owner.discards,card_type="Minion")
        if minion is not None:
            self.summon(minion)

class Chittering_Tunneler(Minion):
    def __init__(self,name="Chittering Tunneler",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        card=self.discover(filter_str="[type]='Spell'")
        if card is not None:
            self.deal_damage([self.owner], [card.cost])
            card.hand_in()

class Sanguine_Reveler(Minion):
    def __init__(self,name="Sanguine Reveler",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def get_target(self):
        minion=choose_target(chooser=self,target="friendly minion",message="destroy")
        return minion
    
    def battlecry(self,target):
        target.destroy()
        buff_animation(self)
        self.buff_stats(2,2)
                    
class Howlfiend(Minion):
    def __init__(self,name="Howlfiend",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="minion damage"
        
    def trigger_effect(self,triggering_entity):
        if triggering_entity[0] is self:
            super(self.__class__,self).trigger_effect(self)
            self.owner.discard()

class Despicable_Dreadlord(Minion):
    def __init__(self,name="Despicabl Dreadlord",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="end of turn"
        
    def trigger_effect(self,triggering_player):
        if triggering_player is self.owner:
            super(self.__class__,self).trigger_effect(triggering_player)
            dread_infernal_animation(self)
            targets=self.enemy_minions()
            self.deal_damage(targets, [1]*len(targets))

class Gnomeferatu(Minion):
    def __init__(self,name="Gnomeferatu",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def battlecry(self,target):
        card=self.owner.opponent.deck.top()
        if not card.isFatigue():
            card.burn()  

class Kobold_Librarian(Minion):
    def __init__(self,name="Kobold Librarian",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        fire_bolt_animation(self, self.owner)
        self.deal_damage([self.owner], [2])
        self.owner.draw()

class Vulgar_Homunculus(Minion):
    def __init__(self,name="Vulgar Homunculus",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        
    def battlecry(self,target=None):
        fel_cannon_animation(self, self.owner)
        self.deal_damage([self.owner], [2])

class Hooked_Reaver(Minion):
    def __init__(self,name="Hooked Reaver",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def battlecry(self,target=None):
        if self.owner.current_hp<=15:
            buff_animation(self)
            self.buff_stats(3,3)
            self.gain_taunt()

class Possessed_Lackey(Minion): 
    def __init__(self,name="Possessed Lackey",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        minion=self.owner.search_card(self.owner.deck.cards,card_type="Demon")
        if minion is not None:
            self.recruit(minion)

class Voidlord(Minion):
    def __init__(self,name="Voidlord",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        for i in range(3):
            minion=Voidwalker(owner=self.owner)
            self.summon(minion)
                                                                                                                                                                                                                                  
class Lord_Jaraxxus(Minion):
    def __init__(self,name="Lord Jaraxxus",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.health=15
             
    def battlecry(self,target=None):
        self.board_area="Burn"
        self.owner.minions.remove(self)
        #self.owner.board.queue.remove(self)
        self.image=self.mini_image
        self.owner.board.sort_minions(self.side)
        
        #Hero replacement
        replace_hero_animation(self)
        self.owner.hero_name=self.name
        self.owner.class_name=self.card_class
        self.owner.image=get_image("images/hero_images/"+self.name+".png",(170,236))
        self.owner.hp=self.health
        self.owner.current_hp=self.health
        
        #Get new hero power
        new_hero_power=INFERNO(owner=self.owner)
        self.owner.gain_hero_power(new_hero_power)
        
        #Get new weapon
        weapon=Blood_Fury(owner=self.owner)
        self.owner.equip_weapon(weapon)
                    
class Infernal(Minion):
    def __init__(self,name="Infernal",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        
class MalGanis(Minion):
    def __init__(self,name="Mal'Ganis",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.has_special_summon_effect=True

    def special_summoning_effect(self):
        malganis_animation(self)
                
    def ongoing_effect(self,target):
        if target.isMinion() and target.board_area=="Board" and target.side==self.side and target.has_race("Demon") and target is not self:
            return {'atk':2,'hp':2}
        elif target is self.owner:
            return {'immune':True}
        else:
            return {}
        
    def destroy(self,skip_animation=False,skip_deathrattle=False):
        super(self.__class__,self).destroy(skip_animation,skip_deathrattle)
        for minion in self.friendly_minions():
            if minion.current_hp<=0:
                minion.current_hp=1

class Wilfred_Fizzlebang(Minion):
    def __init__(self,name="Wilfred Fizzlebang",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def ongoing_effect(self,target):
        if (isinstance(target,Life_Tap) or isinstance(target,Soul_Tap)) and target.side==self.side:
            return {'Fizzlebang':True}
        else:
            return {}
            
class Chogall(Minion):
    def __init__(self,name="Cho'gall",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def battlecry(self,target=None):
        zodiac_animation(self.owner, self.card_class)
        card=Chogall_Effect(owner=self.owner)
        card.origin=self
                    
class Chogall_Effect(Enchantment):
    def __init__(self,name="Cho'gall",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_events.append(("play a card",self.trigger_effect))

    def ongoing_effect(self,target):
        if target.isSpell and target.side==self.side:
            return {'cost health':True}
        else:
            return {}            
        
    def trigger_effect(self, triggering_card):
        if triggering_card.isSpell and triggering_card.side==self.side and triggering_card is not self.origin:
            self.destroy()

class Krul_the_Unshackled(Minion):
    def __init__(self,name="Krul the Unshackled",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def battlecry(self,target=None):
        if self.owner.deck.has_no_duplicates():
            krul_the_unshackled_animation(self)
            for minion in self.owner.hand:
                if minion.has_race("Demon"):
                    self.owner.put_into_battlefield(minion)

class Nether_Portal_minion(Minion):
    def __init__(self,name="Nether Portal (minion)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.dormant=True
        self.dormant_cap=999
        self.current_hp=1
        self.trigger_event_type="end of turn"
        self.trigger_events.append([self.trigger_event_type,self.trigger_effect])
        
    def trigger_effect(self,triggering_player):
        if triggering_player is self.owner:
            nether_portal_animation(self)
            for i in range(2):
                minion=Nether_Imp(owner=self.owner)
                self.summon(minion,left=(-1)**i,speed=40)

    def refresh_status(self):
        self.dormant_counter=0
                        
class Nether_Imp(Minion):
    def __init__(self,name="Nether Imp",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
               
class Clutchmother_Zavas(Minion):
    def __init__(self,name="Clutchmother Zavas",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def on_discard(self):
        if self in self.owner.discards:
            self.owner.discards.remove(self)
        self.buff_stats(2,2)
        clutchmother_zavas_animation(self)
        self.hand_in()    

class Blood_Queen_Lanathel(Minion):
    def __init__(self,name="Blood-Queen Lana'thel",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.lifesteal=True
        
    def ongoing_effect(self,target):
        if target is self:
            return {'cost':-self.owner.total_discards}
        else:
            return {} 

class Rin_the_First_Disciple(Minion):
    def __init__(self,name="Rin, the First Disciple",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True

    def deathrattle(self):
        card=The_First_Seal(owner=self.owner)
        card.initialize_location(self.location)
        card.hand_in()

class Felhunter_2_2(Minion):
    def __init__(self,name="Felhunter (2-2)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Felhunter_3_3(Minion):
    def __init__(self,name="Felhunter (3-3)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Felhunter_4_4(Minion):
    def __init__(self,name="Felhunter (4-4)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Felhunter_5_5(Minion):
    def __init__(self,name="Felhunter (5-5)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Felhunter_6_6(Minion):
    def __init__(self,name="Felhunter (6-6)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
                        
class The_First_Seal(Spell):
    def __init__(self,name="The First Seal",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)

    def invoke(self,target):
        super(self.__class__,self).invoke()
        minion=Felhunter_2_2(owner=self.owner,source="board")
        self.owner.recruit(minion)
        
        card=The_Second_Seal(owner=self.owner)
        card.initialize_location(self.owner.location)
        card.hand_in()

class The_Second_Seal(Spell):
    def __init__(self,name="The Second Seal",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)

    def invoke(self,target):
        super(self.__class__,self).invoke()
        minion=Felhunter_3_3(owner=self.owner,source="board")
        self.owner.recruit(minion)
        
        card=The_Third_Seal(owner=self.owner)
        card.initialize_location(self.owner.location)
        card.hand_in()

class The_Third_Seal(Spell):
    def __init__(self,name="The Third Seal",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)

    def invoke(self,target):
        super(self.__class__,self).invoke()
        minion=Felhunter_4_4(owner=self.owner,source="board")
        self.owner.recruit(minion)
        
        card=The_Fourth_Seal(owner=self.owner)
        card.initialize_location(self.owner.location)
        card.hand_in()

class The_Fourth_Seal(Spell):
    def __init__(self,name="The Fourth Seal",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)

    def invoke(self,target):
        super(self.__class__,self).invoke()
        minion=Felhunter_5_5(owner=self.owner,source="board")
        self.owner.recruit(minion)
        
        card=The_Final_Seal(owner=self.owner)
        card.initialize_location(self.owner.location)
        card.hand_in()

class The_Final_Seal(Spell):
    def __init__(self,name="The Final Seal",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)

    def invoke(self,target):
        super(self.__class__,self).invoke()
        minion=Felhunter_6_6(owner=self.owner,source="board")
        self.owner.recruit(minion)
        
        minion=Azari_the_Devourer(owner=self.owner)
        unstable_portal_animation(self, minion)
        azari_animation(self.owner)
        minion.hand_in()

class Azari_the_Devourer(Minion):
    def __init__(self,name="Azari, the Devourer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def battlecry(self,target=None):
        if len(self.owner.deck.cards)>0:
            krul_the_unshackled_animation(self)
            azari_the_devourer_animation(self, self.owner.opponent.deck)
            targets=[]
            for card in self.owner.opponent.deck.cards:
                targets.append(card)        
            for card in targets:
                move_animation(card,dest=(card.location[0]-80,card.location[1]-50),speed=80)
                self.owner.opponent.deck.cards.remove(card)
                card.burn(skip_animation=True)

class Countess_Ashmore(Minion):
    def __init__(self,name="Countess Ashmore",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
                
    def battlecry(self,target=None):
        targets=[]
        for ability in ["rush","Lifesteal","Deathrattle"]:
            target=self.owner.search_card_based_keyword(self.owner.deck.cards,keyword=ability)
            if target is not None:
                self.owner.draw(target=target)
                                                                                                                                            
'''Warrior Minions'''     
class Warsong_Commander(Minion):
    def __init__(self,name="Warsong Commander",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def ongoing_effect(self,target):
        if target.isMinion() and target.board_area=="Board" and target.side==self.side and target.has_charge:
            return {'atk':1}
        else:
            return {}

class Korkron_Elite(Minion):
    def __init__(self,name="Kor'kron Elite",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.charge=True

class Cruel_Taskmaster(Minion):
    def __init__(self,name="Cruel Taskmaster",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(chooser=self,target="minion",message="deal 1 damage and give it +1 Attack")
        return target
    
    def battlecry(self,target):
        charge_shot_animation(self,target)
        self.deal_damage([target], [1])
        target.buff_stats(2,0)

class Arathi_Weaponsmith(Minion):
    def __init__(self,name="Arathi Weaponsmith",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        weapon=Battle_Axe(owner=self.owner)
        self.owner.equip_weapon(weapon)

class Armorsmith(Minion):
    def __init__(self,name="Armorsmith",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="minion damage"
        
    def trigger_effect(self,triggering_entity):
        if triggering_entity[0].side==self.side:
            super(self.__class__,self).trigger_effect(triggering_entity[0])
            self.owner.increase_shield(1)

class Frothing_Berserker(Minion):
    def __init__(self,name="Frothing Berserker",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="minion damage"
        
    def trigger_effect(self,triggering_entity):
        super(self.__class__,self).trigger_effect(triggering_entity[0])
        self.buff_stats(1, 0)

class Warbot(Minion):
    def __init__(self,name="Warbot",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.enrage=True
        
    def ongoing_effect(self,target):
        if target is self and target.damaged():
            return {'atk':1}
        else:
            return {}

class Screwjank_Clunker(Minion):
    def __init__(self,name="Screwjank Clunker",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(chooser=self,target="friendly minion",target_type="Mech",message="+2/+2")
        return target
    
    def battlecry(self,target):
        mech_buff_animation(target)
        target.buff_stats(2,2)
        
class Siege_Engine(Minion):
    def __init__(self,name="Siege Engine",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="gain armor"
        
    def trigger_effect(self,triggering_entity):
        if triggering_entity[0] is self.owner:
            super(self.__class__,self).trigger_effect(triggering_entity)
            self.buff_stats(1, 0)

class Shieldmaiden(Minion):
    def __init__(self,name="Shieldmaiden",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        self.owner.increase_shield(5)

class Axe_Flinger(Minion):
    def __init__(self,name="Axe Flinger",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="minion damage"
        
    def trigger_effect(self,triggering_entity):
        if triggering_entity[0] is self: 
            super(self.__class__,self).trigger_effect(self)
            axe_flinger_animation(self)
            self.deal_damage([self.owner.opponent], [2])

class Orgrimmar_Aspirant(Minion):
    def __init__(self,name="Orgrimmar Aspirant",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.inspire=True
        
    def trigger_inspire(self, hero_power=None):
        if hero_power.owner is self.owner and self.owner.has_weapon():
            super(self.__class__,self).trigger_inspire()
            weapon_buff_animation(self)
            self.owner.weapon.buff_stats(1,0)

class Alexstraszas_Champion(Minion):
    def __init__(self,name="Alexstrasza's Champion",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        if self.owner.holding("Dragon"):
            rage_buff_animation(self)
            self.buff_stats(1,0)
            self.gain_charge()
                            
class Sparring_Partner(Minion):
    def __init__(self,name="Sparring Partner",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)

    def get_target(self):
        target=choose_target(chooser=self,target="minion",message="give Taunt")
        return target
    
    def battlecry(self,target):
        mech_buff_animation(target)
        target.gain_taunt()
        
class Magnataur_Alpha(Minion):
    def __init__(self,name="Magnataur Alpha",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="during attack"
        
    def trigger_effect(self,triggering_minion):
        if triggering_minion is self and self.target.isMinion():
            self.attack_adjacent_minions(self.target)

class Sea_Reaver(Minion):
    def __init__(self,name="Sea Reaver",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.casts_when_drawn=True
        
    def on_drawn(self):
        on_drawn_animation(self)
        targets=self.friendly_minions()
        flame_leviathan_animation(self)
        self.deal_damage(targets, [1]*len(targets))

class Fierce_Monkey(Minion):
    def __init__(self,name="Fierce Monkey",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        
class Obsidian_Destroyer(Minion):
    def __init__(self,name="Obsidian Destroyer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="end of turn"
        
    def trigger_effect(self,triggering_player):
        if triggering_player is self.owner:
            super(self.__class__,self).trigger_effect(triggering_player)
            minion=Scarab(owner=self.owner)
            self.summon(minion)

class Scarab(Minion):
    def __init__(self,name="Scarab",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True

class NZoths_First_Mate(Minion):
    def __init__(self,name="N'Zoth's First Mate",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        weapon=Rusty_Hook(owner=self.owner)
        self.owner.equip_weapon(weapon)

class Ravaging_Ghoul(Minion):
    def __init__(self,name="Ravaging Ghoul",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        unstable_ghoul_animation(self)
        targets=self.all_minions()
        self.deal_damage(targets, [1]*len(targets))

class Bloodhoof_Brave(Minion):
    def __init__(self,name="Bloodhoof Brave",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        self.enrage=True
        
    def ongoing_effect(self,target):
        if target is self and target.damaged():
            return {'atk':3}
        else:
            return {}

class Slime_Blood_To_Ichor(Minion):
    def __init__(self,name="Slime (Blood To Ichor)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Bloodsail_Cultist(Minion):
    def __init__(self,name="Bloodsail Cultist",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        if self.owner.control("Pirate") and self.owner.has_weapon():
            self.owner.weapon.buff_stats(1,1)

class Ancient_Shieldbearer(Minion):
    def __init__(self,name="Ancient Shieldbearer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        if self.eval_cthun(atk=10):
            self.owner.increase_shield(10)

class Public_Defender(Minion):
    def __init__(self,name="Public Defender",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True

class Grimy_Gadgeteer(Minion):
    def __init__(self,name="Grimy Gadgeteer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source) 
        self.trigger_event_type="end of turn"
       
    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner:
            super(self.__class__,self).trigger_effect(triggering_player)
            self.owner.buff_hand(card_type="Minion",atk=2,hp=2)

class Grimestreet_Pawnbroker(Minion):
    def __init__(self,name="Grimestreet Pawnbroker",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        self.owner.buff_hand(card_type="Weapon")

class Alley_Armorsmith(Minion):
    def __init__(self,name="Alley Armorsmith",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        self.trigger_event_type="deal damage"
        
    def trigger_effect(self,triggering_entity):
        if triggering_entity[0] is self:
            super(self.__class__,self).trigger_effect(triggering_entity[0])
            self.owner.increase_shield(triggering_entity[1])

class Ornery_Direhorn(Minion):
    def __init__(self,name="Ornery Direhorn",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
    
    def battlecry(self,target=None):
        self.adapt() 

class Tar_Lord(Minion):
    def __init__(self,name="Tar Lord",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        
    def ongoing_effect(self,target):
        if target is self and self.owner.board.control==-self.side:
            return {'atk':4}
        else:
            return {}

class Cornered_Sentry(Minion):
    def __init__(self,name="Cornered Sentry",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        
    def battlecry(self,target=None):
        for i in range(3):
            minion = Raptor_1_1(owner=self.owner.opponent)
            self.summon(minion)

class Direhorn_Hatchling(Minion):
    def __init__(self,name="Direhorn Hatchling",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        
    def deathrattle(self):
        minion=Direhorn_Matriarch(owner=self.owner,source=self.location)
        minion.shuffle_into_deck(self.owner.deck)
            
class Direhorn_Matriarch(Minion):
    def __init__(self,name="Direhorn Matriarch",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True

class Animated_Berserker(Minion):
    def __init__(self,name="Animated Berserker",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="play a card"
        
    def trigger_effect(self, triggering_card=None):
        if triggering_card.isMinion() and triggering_card.side==self.side and triggering_card.board_area=="Board" and triggering_card.get_current_hp()>0 and triggering_card is not self:
                super(self.__class__,self).trigger_effect(triggering_card)
                acidic_swamp_ooze_animation(self, triggering_card)
                self.deal_damage([triggering_card], [1])
                
class Mountainfire_Armor(Minion):
    def __init__(self,name="Mountainfire Armor",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def deathrattle(self):
        if self.owner.board.control==-self.side:
            self.owner.increase_shield(6)
            
class Valkyr_Soulclaimer(Minion):
    def __init__(self,name="Val'kyr Soulclaimer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="minion damage"
        
    def trigger_effect(self,triggering_entity):
        if triggering_entity[0] is self and self.get_current_hp()>0:
            super(self.__class__,self).trigger_effect(self)
            minion=Ghoul(owner=self.owner)
            self.summon(minion)

class Death_Revenant(Minion):
    def __init__(self,name="Death Revenant",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        targets=[]
        for minion in self.all_minions():
            if minion.damaged():
                targets.append(minion)
        buff_animation(self)
        self.buff_stats(len(targets),len(targets))

class Drywhisker_Armorer(Minion):
    def __init__(self,name="Drywhisker Armorer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        self.owner.increase_shield(2*len(self.enemy_minions()))

class Gemstudded_Golem(Minion):
    def __init__(self,name="Gemstudded Golem",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        self.cannot_attack=True

    def ongoing_effect(self,target):
        if target is self and self.owner.shield>=5:
            return {'can attack':True}
        else:
            return {}  

class Kobold_Barbarian(Minion):
    def __init__(self,name="Kobold Barbarian",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source) 
        self.trigger_event_type="start of turn"
       
    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner:
            super(self.__class__,self).trigger_effect(triggering_player)
            targets=self.enemy_characters()
            target = random.choice(targets)
            self.attack(target)
            
class Iron_Golem(Minion):
    def __init__(self,name="Iron Golem",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Mithril_Golem(Minion):
    def __init__(self,name="Mithril Golem",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
                                                                                                                                                                                                                                                                                            
class Grommash_Hellscream(Minion):
    def __init__(self,name="Grommash Hellscream",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.charge=True
        self.enrage=True
        
    def ongoing_effect(self,target):
        if target is self and target.damaged():
            return {'atk':6}
        else:
            return {}
                                        
class Iron_Juggernaut(Minion):
    def __init__(self,name="Iron Juggernaut",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        '''Initialzie a bomb card'''
        bomb=Burrowing_Mine(owner=self.owner.opponent,source=self.location)
        #bomb.rect=get_rect(self.rect.x,self.rect.y-100,self.raw_image.get_width(),self.raw_image.get_height())
        #bomb.location=bomb.rect.x,bomb.rect.y
        
        '''Put bomb into opponent deck'''
        deck_in_animation(bomb,self.owner.opponent.deck)
        self.owner.opponent.deck.add_card(bomb) 

class Burrowing_Mine(Spell):
    def __init__(self,name="Burrowing Mine",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.casts_when_drawn=True

    def invoke(self,target=None):
        super(self.__class__,self).invoke()
        explode_animation(self)
        self.deal_damage([self.owner], [10])

class Bomb(Spell):
    def __init__(self,name="Bomb",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.casts_when_drawn=True
        
    def invoke(self,target=None):
        super(self.__class__,self).invoke()
        explode_animation(self)
        self.deal_damage([self.owner], [5])  

class Pawn(Minion):
    def __init__(self,name="Pawn",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True
        
class Varian_Wrynn(Minion):
    def __init__(self,name="Varian Wrynn",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        for i in range(3):
            card=self.owner.draw()
            if card.isMinion():
                self.owner.put_into_battlefield(card)

class Malkorok(Minion):
    def __init__(self,name="Malkorok",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        weapon=database.get_random_cards("[type]='Weapon'", owner=self.owner, k=1)[0]
        self.owner.equip_weapon(weapon)

class Hobart_Grapplehammer(Minion):
    def __init__(self,name="Hobart Grapplehammer",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        hobart_grapplehammer_animation(self)
        for card in self.owner.hand+self.owner.deck.cards:
            if isinstance(card,Weapon):
                card.buff_stats(1,0)

class King_Mosh(Minion):
    def __init__(self,name="King Mosh",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        targets=[]
        for minion in self.all_minions():
            if minion.damaged():
                targets.append(minion)
        if len(targets)>0:
            king_mosh_animation(self,targets)
            for minion in targets:
                minion.destroy(skip_animation=True)

class Rotface(Minion):
    def __init__(self,name="Rotface",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="minion damage"
        
    def trigger_effect(self,triggering_entity):
        if triggering_entity[0] is self and self.get_current_hp()>0:
            super(self.__class__,self).trigger_effect(self)
            minion = database.get_random_cards("[type]='Minion' AND [rarity]='Legendary'", self.owner, 1)[0]
            self.summon(minion)

class Geosculptor_Yip(Minion):
    def __init__(self,name="Geosculptor Yip",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_event_type="end of turn"
                        
    def trigger_effect(self, triggering_player):
        if triggering_player is self.owner:
            minion = database.get_random_cards("[type]='Minion' AND [cost]="+str(min(10,self.owner.shield)), self.owner, 1)[0]
            if minion is not None:
                super(self.__class__,self).trigger_effect(self)
                self.summon(minion)
                                            
'''Tri-class cards'''
class Grimestreet_Smuggler(Minion):
    def __init__(self,name="Grimestreet Smuggler",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        self.owner.buff_hand(card_type="Minion",atk=1,hp=1)

class Grimestreet_Informant(Minion):
    def __init__(self,name="Grimestreet Informant",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        card1=database.get_random_cards(filter_str="[class] LIKE '%Hunter%'", owner=self.owner, k=1)[0]
        card2=database.get_random_cards(filter_str="[class] LIKE '%Paladin%'", owner=self.owner, k=1)[0]
        card3=database.get_random_cards(filter_str="[class] LIKE '%Warrior%'", owner=self.owner, k=1)[0]
        
        card=self.discover(card_pool=[card1,card2,card3])
        if card is not None:
            card.hand_in()


class Jade_Golem(Minion):
    def __init__(self,name="Jade Golem",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.atk=self.owner.jade_counter
        self.hp=self.owner.jade_counter
        self.cost=self.owner.jade_counter
        self.current_cost=self.cost
        self.current_atk=self.atk
        self.temp_atk=self.current_atk
        self.current_hp=self.hp
        self.temp_hp=self.current_hp
        
        #Adjusting image based on jade counter
        self.big_image  = get_image("images/card_images/jade_golems/Jade Golem_"+str(self.owner.jade_counter)+".png",(265,367)) 
        self.raw_image  = get_image("images/card_images/jade_golems/Jade Golem_"+str(self.owner.jade_counter)+".png",(170,236)) 
        self.mini_image = get_image("images/card_images/jade_golems/Jade Golem_"+str(self.owner.jade_counter)+".png",(103,141))
        self.board_image=pygame.transform.scale(self.big_image.subsurface((60, 20, 140, 175)),(103,128))
        self.image = self.mini_image
        
    def come_on_board(self):
        super(self.__class__,self).come_on_board()
        if self.owner.jade_counter<30:
            self.owner.jade_counter+=1
            
class Jade_Spirit(Minion):
    def __init__(self,name="Jade Spirit",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        minion = Jade_Golem(owner=self.owner)
        self.summon(minion)

class Lotus_Agents(Minion):
    def __init__(self,name="Lotus Agents",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        card1=database.get_random_cards(filter_str="[class] LIKE '%Druid%'", owner=self.owner, k=1)[0]
        card2=database.get_random_cards(filter_str="[class] LIKE '%Rogue%'", owner=self.owner, k=1)[0]
        card3=database.get_random_cards(filter_str="[class] LIKE '%Shaman%'", owner=self.owner, k=1)[0]
        
        card=self.discover(card_pool=[card1,card2,card3])
        if card is not None:
            card.initialize_location(self.location)
            card.hand_in()

class Kabal_Chemist(Minion):
    def __init__(self,name="Kabal Chemist",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        potion=random.choice([Freezing_Potion,Potion_of_Polymorph,Volcanic_Potion,Potion_of_Madness,\
                              Pint_Size_Potion,Greater_Healing_Potion,Dragonfire_Potion,\
                              Bloodfury_Potion,Blastcrystal_Potion,Felfire_Potion])
        card=potion(owner=self.owner)
        card.initialize_location(self.location)
        card.hand_in()

class Kabal_Courier(Minion):
    def __init__(self,name="Kabal Courier",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        card1=database.get_random_cards(filter_str="[class] LIKE '%Mage%'", owner=self.owner, k=1)[0]
        card2=database.get_random_cards(filter_str="[class] LIKE '%Priest%'", owner=self.owner, k=1)[0]
        card3=database.get_random_cards(filter_str="[class] LIKE '%Warlock%'", owner=self.owner, k=1)[0]
        
        card=self.discover(card_pool=[card1,card2,card3])
        if card is not None:
            card.hand_in()

class Don_HanCho(Minion):
    def __init__(self,name="Don Han'Cho",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        shake_board(self)
        self.owner.buff_hand(card_type="Minion",atk=5,hp=5)

class Aya_Blackpaw(Minion):
    def __init__(self,name="Aya Blackpaw",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        minion = Jade_Golem(owner=self.owner)
        self.summon(minion)
        
    def deathrattle(self):
        minion = Jade_Golem(owner=self.owner)
        self.summon(minion)

class Kazakus(Minion):
    def __init__(self,name="Kazakus",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        
    def battlecry(self,target=None):
        if self.owner.deck.has_no_duplicates():
            self.owner.board.background=background_dark
            selected_potion_type = choose_one([option(owner=self.owner) for option in [Lesser_Potion,Greater_Potion,Superior_Potion]])
            
            options_1_mana=[Felbloom_1_mana,Goldthorn_1_mana,Heart_of_Fire_1_mana,Icecap_1_mana,Ichor_of_Undeath_1_mana,Kingsblood_1_mana,Netherbloom_1_mana,Shadow_Oil_1_mana,Stonescale_Oil_1_mana]
            options_5_mana=[Felbloom_5_mana,Goldthorn_5_mana,Heart_of_Fire_5_mana,Icecap_5_mana,Ichor_of_Undeath_5_mana,Mystic_Wool_5_mana,Kingsblood_5_mana,Netherbloom_5_mana,Shadow_Oil_5_mana,Stonescale_Oil_5_mana]
            options_10_mana=[Felbloom_10_mana,Goldthorn_10_mana,Heart_of_Fire_10_mana,Icecap_10_mana,Ichor_of_Undeath_10_mana,Mystic_Wool_10_mana,Kingsblood_10_mana,Netherbloom_10_mana,Shadow_Oil_10_mana,Stonescale_Oil_10_mana]
            
            if isinstance(selected_potion_type,Lesser_Potion):
                options_1=random.sample(options_1_mana,k=3)
            elif isinstance(selected_potion_type,Greater_Potion):
                options_1=random.sample(options_5_mana,k=3)
            elif isinstance(selected_potion_type,Superior_Potion):
                options_1=random.sample(options_10_mana,k=3)
            else:
                return None
            
            first_choice = choose_one([option(owner=self.owner) for option in options_1])
            if isinstance(selected_potion_type,Lesser_Potion):
                options_1_mana.remove(first_choice.__class__)
                options_2=random.sample(options_1_mana,k=3)
            elif isinstance(selected_potion_type,Greater_Potion):
                options_5_mana.remove(first_choice.__class__)
                options_2=random.sample(options_5_mana,k=3)
            elif isinstance(selected_potion_type,Superior_Potion):
                options_10_mana.remove(first_choice.__class__)
                options_2=random.sample(options_10_mana,k=3)
            
            second_choice = choose_one([option(owner=self.owner) for option in options_2])
            
            if isinstance(selected_potion_type,Lesser_Potion):
                potion=Kazakus_Potion_1_mana(owner=self.owner)
            elif isinstance(selected_potion_type,Greater_Potion):
                potion=Kazakus_Potion_5_mana(owner=self.owner)
            elif isinstance(selected_potion_type,Superior_Potion):
                potion=Kazakus_Potion_10_mana(owner=self.owner)

            potion.effects.extend([first_choice,second_choice])
            if "Heart of Fire" in first_choice.name or "Heart of Fire" in second_choice.name:
                potion.tags.append("Targeted")
            potion.appear_in_hand()
            self.owner.board.background=background
            
class Sheep_Mean_Streets_of_Gadgetzan(Minion):
    def __init__(self,name="Sheep (Mean Streets of Gadgetzan)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Kabal_Demon_2_2(Minion):
    def __init__(self,name="Kabal Demon (2-2)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Kabal_Demon_5_5(Minion):
    def __init__(self,name="Kabal Demon (5-5)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Kabal_Demon_8_8(Minion):
    def __init__(self,name="Kabal Demon (8-8)",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)     

class Lesser_Potion(Spell):
    def __init__(self,name="Lesser Potion",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)

class Greater_Potion(Spell):
    def __init__(self,name="Greater Potion",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)

class Superior_Potion(Spell):
    def __init__(self,name="Superior Potion",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)

class Felbloom_1_mana(Spell):
    def __init__(self,name="Felbloom (1 mana)",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target):
        targets=self.all_minions()
        chillmaw_animation(self)
        self.deal_damage(targets, [2]*len(targets))

class Felbloom_5_mana(Spell):
    def __init__(self,name="Felbloom (5 mana)",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target):
        targets=self.all_minions()
        chillmaw_animation(self)
        self.deal_damage(targets, [4]*len(targets))
        
class Felbloom_10_mana(Spell):
    def __init__(self,name="Felbloom (10 mana)",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target):
        targets=self.all_minions()
        chillmaw_animation(self)
        self.deal_damage(targets, [6]*len(targets))

class Goldthorn_1_mana(Spell):
    def __init__(self,name="Goldthorn (1 mana)",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target):
        targets=self.friendly_minions()
        light_buff_multiple_animation(self, targets)
        for minion in targets:
            minion.buff_stats(0,2)

class Goldthorn_5_mana(Spell):
    def __init__(self,name="Goldthorn (5 mana)",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target):
        targets=self.friendly_minions()
        light_buff_multiple_animation(self, targets)
        for minion in targets:
            minion.buff_stats(0,4)

class Goldthorn_10_mana(Spell):
    def __init__(self,name="Goldthorn (10 mana)",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target):
        targets=self.friendly_minions()
        light_buff_multiple_animation(self, targets)
        for minion in targets:
            minion.buff_stats(0,6)
                                                                        
class Heart_of_Fire_1_mana(Spell):
    def __init__(self,name="Heart of Fire (1 mana)",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None
    
    def invoke(self,target):
        fireball_animation(self, target)
        self.deal_damage([target],[3])

class Heart_of_Fire_5_mana(Spell):
    def __init__(self,name="Heart of Fire (5 mana)",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None
    
    def invoke(self,target):
        fireball_animation(self, target)
        self.deal_damage([target],[5])

class Heart_of_Fire_10_mana(Spell):
    def __init__(self,name="Heart of Fire (10 mana)",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def is_valid_on(self, target):
        return target is not None
    
    def invoke(self,target):
        fireball_animation(self, target)
        self.deal_damage([target],[8])

class Icecap_1_mana(Spell):
    def __init__(self,name="Icecap (1 mana)",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)

    def invoke(self,target):
        frost_nova_animation(self)
        target_pool=self.enemy_minions()
        if len(target_pool)>0:
            targets=random.sample(target_pool,k=min(1,len(target_pool)))
            for target in targets:
                target.get_frozen()

class Icecap_5_mana(Spell):
    def __init__(self,name="Icecap (5 mana)",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)

    def invoke(self,target):
        frost_nova_animation(self)
        target_pool=self.enemy_minions()
        if len(target_pool)>0:
            targets=random.sample(target_pool,k=min(2,len(target_pool)))
            for target in targets:
                target.get_frozen()
                                       
class Icecap_10_mana(Spell):
    def __init__(self,name="Icecap (10 mana)",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)

    def invoke(self,target):
        frost_nova_animation(self)
        target_pool=self.enemy_minions()
        if len(target_pool)>0:
            targets=random.sample(target_pool,k=min(3,len(target_pool)))
            for target in targets:
                target.get_frozen()

class Ichor_of_Undeath_1_mana(Spell):
    def __init__(self,name="Ichor of Undeath (1 mana)",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)

    def invoke(self,target):
        for i in range(1):
            target = self.owner.search_card(self.owner.grave,"Minion")
            minion = getattr(card_collection,database.cleaned(target.name))(owner=self.owner,source="board")
            self.owner.recruit(minion)
            resurrect_animation(minion)

class Ichor_of_Undeath_5_mana(Spell):
    def __init__(self,name="Ichor of Undeath (5 mana)",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)

    def invoke(self,target):
        for i in range(2):
            target = self.owner.search_card(self.owner.grave,"Minion")
            minion = getattr(card_collection,database.cleaned(target.name))(owner=self.owner,source="board")
            self.owner.recruit(minion)
            resurrect_animation(minion)

class Ichor_of_Undeath_10_mana(Spell):
    def __init__(self,name="Ichor of Undeath (10 mana)",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)

    def invoke(self,target):
        for i in range(3):
            target = self.owner.search_card(self.owner.grave,"Minion")
            minion = getattr(card_collection,database.cleaned(target.name))(owner=self.owner,source="board")
            self.owner.recruit(minion)
            resurrect_animation(minion)

class Kingsblood_1_mana(Spell):
    def __init__(self,name="Kingsblood (1 mana)",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)

    def invoke(self,target):
        self.owner.draw(1)
                        
class Kingsblood_5_mana(Spell):
    def __init__(self,name="Kingsblood (5 mana)",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)

    def invoke(self,target):
        self.owner.draw(2)
        
class Kingsblood_10_mana(Spell):
    def __init__(self,name="Kingsblood (10 mana)",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)

    def invoke(self,target):
        self.owner.draw(3)

class Mystic_Wool_5_mana(Spell):
    def __init__(self,name="Mystic Wool (5 mana)",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)

    def invoke(self,target):
        target_pool=self.enemy_minions()
        if len(target_pool)>0:
            minion=random.choice(target_pool)
            sheep=Sheep_Mean_Streets_of_Gadgetzan(owner=minion.owner,source=minion.location)
            minion.transform(sheep)

class Mystic_Wool_10_mana(Spell):
    def __init__(self,name="Mystic Wool (10 mana)",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)

    def invoke(self,target):
        target_pool=self.enemy_minions()
        for minion in target_pool:
            sheep=Sheep_Mean_Streets_of_Gadgetzan(owner=minion.owner,source=minion.location)
            minion.transform(sheep)

class Netherbloom_1_mana(Spell):
    def __init__(self,name="Netherbloom (1 mana)",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)

    def invoke(self,target):
        minion=Kabal_Demon_2_2(owner=self.owner,source="board")
        self.owner.recruit(minion)

class Netherbloom_5_mana(Spell):
    def __init__(self,name="Netherbloom (5 mana)",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)

    def invoke(self,target):
        minion=Kabal_Demon_5_5(owner=self.owner,source="board")
        self.owner.recruit(minion)
        
class Netherbloom_10_mana(Spell):
    def __init__(self,name="Netherbloom (10 mana)",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)

    def invoke(self,target):
        minion=Kabal_Demon_8_8(owner=self.owner,source="board")
        self.owner.recruit(minion)

class Shadow_Oil_1_mana(Spell):
    def __init__(self,name="Shadow Oil (1 mana)",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)

    def invoke(self,target):
        for i in range(1):
            minion = database.get_random_cards("[type]='Minion' AND [race]='Demon'", self.owner, 1)[0]
            minion.appear_in_hand()

class Shadow_Oil_5_mana(Spell):
    def __init__(self,name="Shadow Oil (5 mana)",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)

    def invoke(self,target):
        for i in range(2):
            minion = database.get_random_cards("[type]='Minion' AND [race]='Demon'", self.owner, 1)[0]
            minion.appear_in_hand()

class Shadow_Oil_10_mana(Spell):
    def __init__(self,name="Shadow Oil (10 mana)",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)

    def invoke(self,target):
        for i in range(3):
            minion = database.get_random_cards("[type]='Minion' AND [race]='Demon'", self.owner, 1)[0]
            minion.appear_in_hand()

class Stonescale_Oil_1_mana(Spell):
    def __init__(self,name="Stonescale Oil (1 mana)",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)

    def invoke(self,target):
        self.owner.increase_shield(4)

class Stonescale_Oil_5_mana(Spell):
    def __init__(self,name="Stonescale Oil (5 mana)",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)

    def invoke(self,target):
        self.owner.increase_shield(7)

class Stonescale_Oil_10_mana(Spell):
    def __init__(self,name="Stonescale Oil (10 mana)",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)

    def invoke(self,target):
        self.owner.increase_shield(10)

class Kazakus_Potion_1_mana(Spell):
    def __init__(self,name="Kazakus Potion (1 mana)",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        self.effects=[]

    def is_valid_on(self, target):
        return target is not None or not "Targeted" in self.tags
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        for effect in self.effects:
            effect.invoke(target)

class Kazakus_Potion_5_mana(Spell):
    def __init__(self,name="Kazakus Potion (5 mana)",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        self.effects=[]

    def is_valid_on(self, target):
        return target is not None or not "Targeted" in self.tags
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        for effect in self.effects:
            effect.invoke(target)

class Kazakus_Potion_10_mana(Spell):
    def __init__(self,name="Kazakus Potion (10 mana)",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
        self.effects=[]

    def is_valid_on(self, target):
        return target is not None or not "Targeted" in self.tags
    
    def invoke(self,target):
        super(self.__class__,self).invoke()
        for effect in self.effects:
            effect.invoke(target)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
'''Hero Cards'''                                                    
class Hero_Card(Card):
    def __init__(self,name="Default Hero",owner=None):
        super(Hero_Card,self).__init__(name,owner)
        self.shield=0   
        
    def replace_hero(self):
        self.owner.hand.remove(self)
        self.board_area="Board"
        
        replace_hero_animation(self)
        
        self.owner.hero_name=self.name
        self.owner.class_name=self.card_class
        self.owner.image=get_image("images/hero_images/"+self.name+".png",(170,236))
        self.owner.increase_shield(self.shield)
         
        #Get new hero power
        new_hero_power=self.hero_power(owner=self.owner)
        self.owner.gain_hero_power(new_hero_power)
        
        self.battlecry()

class Malfurion_the_Pestilent(Hero_Card):
    def __init__(self,name="Malfurion the Pestilent",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.shield=5
        self.hero_power=Plague_Lord
        self.options=[Spider_Plague,Scarab_Plague]
        
    def replace_hero(self):
        super(self.__class__,self).replace_hero()
        
        if self.owner.board.get_buff(self)["choose both"]:
            self.trigger_choose_both()
        else:
            self.trigger_choose_one()
        
    def trigger_choose_one(self):
        selected_card = choose_one([option(owner=self.owner) for option in self.options])
        selected_card.origin=self
        selected_card.invoke()    

class Spider_Plague(Spell):
    def __init__(self,name="Spider Plague",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)

    def invoke(self,target=None):
        for i in range(2):
            minion=Frost_Widow(owner=self.owner,source="board")
            self.owner.recruit(minion,speed=80)

class Frost_Widow(Minion):
    def __init__(self,name="Frost Widow",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.poisonous=True
                    
class Scarab_Plague(Spell):
    def __init__(self,name="Scarab Plague",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)
    
    def invoke(self,target=None):
        for i in range(2):
            minion=Scarab_Beetle(owner=self.owner,source="board")
            self.owner.recruit(minion,speed=80)          
                
class Scarab_Beetle(Minion):
    def __init__(self,name="Scarab Beetle",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.taunt=True

class Spider_Fangs(Spell):
    def __init__(self,name="Spider Fangs",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)

    def invoke(self,target=None):
        self.owner.current_atk+=3

class Scarab_Shell(Spell):
    def __init__(self,name="Scarab Shell",owner=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner)

    def invoke(self,target=None):
        self.owner.increase_shield(3)

class Deathstalker_Rexxar(Hero_Card):
    def __init__(self,name="Deathstalker Rexxar",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.shield=5
        self.hero_power=Build_A_Beast
        
    def battlecry(self,target=None):
        targets=self.enemy_minions()
        deathstalker_rexxar_animation(self,targets)
        self.deal_damage(targets, [2]*len(targets))

class Frost_Lich_Jaina(Hero_Card):
    def __init__(self,name="Frost Lich Jaina",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.shield=5
        self.hero_power=Icy_Touch

    def battlecry(self,target=None):    
        minion=Water_Elemental(owner=self.owner,source="board")
        self.owner.recruit(minion)        
        enchantment=Frost_Lich_Jaina_Effect(owner=self.owner)

class Frost_Lich_Jaina_Effect(Enchantment):
    def __init__(self,name="Frost Lich Jaina",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.trigger_events=[]

    def ongoing_effect(self,target):
        if target.side==self.side and target.isMinion() and target.has_race("Elemental"):
            return {'lifesteal':True}
        else:
            return {}       

class Uther_of_the_Ebon_Blade(Hero_Card):
    def __init__(self,name="Uther of the Ebon Blade",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.shield=5
        self.hero_power=The_Four_Horsemen_Hero_Power
        
    def battlecry(self,target=None):           
        weapon=Grave_Vengeance(owner=self.owner)
        self.owner.equip_weapon(weapon)

class Deathlord_Nazgrim(Minion):
    def __init__(self,name="Deathlord Nazgrim",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Darion_Mograine(Minion):
    def __init__(self,name="Darion Mograine",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        
class Inquisitor_Whitemane(Minion):
    def __init__(self,name="Inquisitor Whitemane",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        
class Thoras_Trollbane(Minion):
    def __init__(self,name="Thoras Trollbane",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)

class Shadowreaper_Anduin(Hero_Card):
    def __init__(self,name="Shadowreaper Anduin",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.shield=5
        self.hero_power=Voidform
        
    def battlecry(self,target=None):           
        targets=[]
        for minion in self.all_minions():
            if minion.get_current_atk()>=5:
                targets.append(minion)
         
        shadow_word_ruin_animation(self)
        destroy_multiple_animation(targets)       
        for minion in targets:
            minion.destroy(skip_animation=True)
                                                                                                       
class Valeera_the_Hollow(Hero_Card):
    def __init__(self,name="Valeera the Hollow",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.shield=5
        self.hero_power=Deaths_Shadow
        
    def replace_hero(self):
        super(self.__class__,self).replace_hero()
        #Activate hero power
        self.owner.hero_power.invoke()

    def battlecry(self,target=None):
        self.owner.temporary_effects['stealth']=True
                                    
class Shadow_Reflection(Spell):
    def __init__(self,name="Shadow Reflection",owner=None,source=None):#Uncollectible
        super(self.__class__,self).__init__(name,owner,source)
        self.ephemeral=True
        self.trigger_event_type="play a card"
        self.trigger_events=[[self.trigger_event_type,self.trigger_effect]]
    
    def trigger_effect(self,triggering_card):
        if triggering_card is not None and triggering_card.side==self.side and self.board_area=="Hand":
            self.image=triggering_card.mini_image
            self.mini_image=triggering_card.mini_image
            self.raw_image=triggering_card.raw_image
            card_copy=getattr(card_collection,database.cleaned(triggering_card.name))(owner=self.owner)
            if card_copy.isMinion():
                card_copy.copy_stats(triggering_card)
                self.current_atk=card_copy.current_atk
                self.current_hp=card_copy.current_hp
            self.cost=card_copy.cost
            self.current_cost=card_copy.current_cost
            card_copy.board_area="Hand"
            
            self.copy_target=card_copy
            
            '''
            card_copy=getattr(card_collection,database.cleaned(triggering_card.name))(owner=self.owner)
            if card_copy.isMinion():
                card_copy.copy_stats(triggering_card)
            card_copy.initialize_location(self.location)
            card_copy.trigger_events=[["play a card",MethodType(self.trigger_effect.__func__,card_copy)]]
            card_copy.board_area="Hand"
            card_copy.ephemeral=True
            self.owner.hand.insert(self.get_index(),card_copy)
            self.owner.hand.remove(self)'''
            
    def invoke(self,target=None):
        card=self.copy_target
        card.initialize_location((self.rect.x,self.rect.y))
        self.owner.play(card,target)
        if card.board_area!="Hand":#Successfully casted
            self.owner.hand.remove(self)

class Thrall_Deathseer(Hero_Card):
    def __init__(self,name="Thrall, Deathseer",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.shield=5
        self.hero_power=Transmute_Spirit   
        
    def battlecry(self,target=None):           
        for minion in self.friendly_minions():
            minion.evolve(2)

class Bloodreaver_Guldan(Hero_Card):
    def __init__(self,name="Bloodreaver Gul'dan",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.shield=5
        self.hero_power=Siphon_Life  
        
    def battlecry(self,target=None):   
        demons = self.owner.search_card(self.owner.grave,"Demon",k=7-len(self.owner.minions))    
        if demons is not None:
            for minion in demons:
                minion_copy=minion.get_copy(owner=self.owner)
                minion_copy.initialize_location("board")
                self.owner.recruit(minion_copy)

class Scourgelord_Garrosh(Hero_Card):
    def __init__(self,name="Scourgelord Garrosh",owner=None):
        super(self.__class__,self).__init__(name,owner)
        self.shield=5
        self.hero_power=Bladestorm_Hero_Power 
        
    def battlecry(self,target=None):   
        weapon=Shadowmourne(owner=self.owner)
        self.owner.equip_weapon(weapon)
                                                
class Fatigue(Card):
    def __init__(self,name="Fatigue",owner=None,source=None):
        super(self.__class__,self).__init__(name,owner,source)
        self.always_show_face=True

    def perish(self):
        self.owner.overdraw+=1
        fatigue_animation(self)
        self.owner.incur_damage(self.owner.overdraw,damage_source=self)
        self.board_area="Burned"
     