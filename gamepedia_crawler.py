'''
Created on Apr 16, 2020

@author: shan.jiang
'''
import requests,re,shutil,database,time,random



#Navigating start page to find expansion list
starting_URL        = "https://hearthstone.gamepedia.com/Expansion"
starting_HTML       = str(requests.get(starting_URL).content)
table_match         = re.compile(r"<th class=\"unsortable\">Year</th>(.*?)</table>",re.S|re.I).findall(starting_HTML)
table_HTML          = table_match[0]
expansion_matches   = re.compile(r"<a href=\"/(.*?)\" title",re.S|re.I).findall(table_HTML)

#Navigating expansion pages to find card list
for expansion in expansion_matches:
    if "format" in expansion or "redirect" in expansion:
        continue
    
    expansion_URL   = "https://hearthstone.gamepedia.com/"+expansion
    expansion_HTML  = str(requests.get(expansion_URL).content)
    card_matches    = re.compile(r"text-align: center;\"><a href=\"\/(.{1,100}?)\" title=\".{1,100}?\"><img alt",re.S|re.I).findall(expansion_HTML)
    
    #Navigating card pages to find card meta
    for card in card_matches:
        error_log=open("error_log.txt","a")
        
        card_URL    = "https://hearthstone.gamepedia.com/"+card
        card_HTML   = str(requests.get(card_URL).content)
        
        #Initializing Default values of card meta
        card_type=""
        card_class="Neutral"
        race=""
        cardset="Basic"
        rarity=""
        cost=0
        attack=0
        health=0
        durability=0
        abilities=[]
        tags=[]
        artist=""
        card_text=""
        back_text=""
        lore=""
        craft_cost=-1
        disenchant_cost=-1
        
        reg_image_url=""
        gold_image_url=""
        full_image_url=""
        
        #Update card meta if found any
        
        #card_name
        card_name   = card.replace("%27","'").replace("_"," ").replace("\\'","'").replace("/","-")
        
        #Card info Block
        block_match  = re.compile(r"Regular<\/div>(.*?)data page",re.S|re.I).findall(card_HTML)
        if len(block_match)>0:
            block_HTML = block_match[0]
            
            #Type
            type_match  = re.compile(r"<b>Type:(.*?)<\/td><\/tr>",re.S|re.I).findall(block_HTML)
            if len(type_match)>0:
                card_type = re.sub("<.*?>","",type_match[0]).replace("\\n","").strip()
            
            #Card Class
            class_match  = re.compile(r"<b>Class:(.*?)<\/td><\/tr>",re.S|re.I).findall(block_HTML)
            if len(class_match)>0:
                card_class = re.sub("<.*?>","",class_match[0]).replace("\\n","").strip()
                    
            #Race
            race_match  = re.compile(r"<b>Subtype:(.*?)<\/td><\/tr>",re.S|re.I).findall(block_HTML)
            if len(race_match)>0:
                race = re.sub("<.*?>","",race_match[0]).replace("\\n","").strip()
        
            #Cardset
            set_match  = re.compile(r"<b>Set:(.*?)<\/td><\/tr>",re.S|re.I).findall(block_HTML)
            if len(set_match)>0:
                cardset = re.sub("<.*?>","",set_match[0]).replace("\\n","").replace("\\'","'").strip()
                
            #Rarity
            rarity_match  = re.compile(r"<b>Rarity:(.*?)<\/td><\/tr>",re.S|re.I).findall(block_HTML)
            if len(rarity_match)>0:
                rarity = re.sub("<.*?>","",rarity_match[0]).replace("\\n","").strip()
                
            #Cost
            cost_match  = re.compile(r"<b>Cost:(.*?)<\/td><\/tr>",re.S|re.I).findall(block_HTML)
            if len(cost_match)>0:
                cost = re.sub("<.*?>","",cost_match[0]).replace("\\n","").strip()
                
            #Attack
            attack_match  = re.compile(r"<b>Attack:(.*?)<\/td><\/tr>",re.S|re.I).findall(block_HTML)
            if len(attack_match)>0:
                attack = re.sub("<.*?>","",attack_match[0]).replace("\\n","").strip()
                
            #Health
            health_match  = re.compile(r"<b>Health:(.*?)<\/td><\/tr>",re.S|re.I).findall(block_HTML)
            if len(health_match)>0:
                health = re.sub("<.*?>","",health_match[0]).replace("\\n","").strip()
                
            #Durability
            durability_match  = re.compile(r"<b>Durability:(.*?)<\/td><\/tr>",re.S|re.I).findall(block_HTML)
            if len(durability_match)>0:
                durability = re.sub("<.*?>","",durability_match[0]).replace("\\n","").strip()
                
            #Abilities
            abilities_match  = re.compile(r"<b>Abilities:(.*?)<\/td><\/tr>",re.S|re.I).findall(card_HTML)
            if len(abilities_match)>0:
                abilities = re.sub("<.*?>","",abilities_match[0]).replace("\\n","").replace("\\'","'").strip().split(",")

        
            #Tags
            tags_match  = re.compile(r"<b>Tags:(.*?)<\/td><\/tr>",re.S|re.I).findall(card_HTML)
            if len(tags_match)>0:
                tags = re.sub("<.*?>","",tags_match[0]).replace("\\n","").strip().replace("\\'","'").split(",")

                
            #Artist
            artist_match  = re.compile(r"<b>Artist:(.*?)<\/td><\/tr>",re.S|re.I).findall(block_HTML)
            if len(artist_match)>0:
                artist = re.sub("<.*?>","",artist_match[0]).replace("\\n","").strip()
            
            #Card Text
            card_text_match  = re.compile(r"<p style=\"font-weight: bold;\">(.*?)<\/p>",re.S|re.I).findall(block_HTML)
            if len(card_text_match)>0:
                card_text = re.sub("<.*?>","",card_text_match[0]).replace("\\n","").strip()
                
            #Back Text
            back_text_match  = re.compile(r"<i>(.*?)<\/i>",re.S|re.I).findall(block_HTML)
            if len(back_text_match)>0:
                back_text = re.sub("<.*?>","",back_text_match[0]).replace("\\n","").replace("\\'","'").strip()
                
            #Regular and Gold Images
            image_url_match  = re.compile(r"(https:\/\/gamepedia.cursecdn.com\/hearthstone_gamepedia\/thumb.*?)\" decoding=\"async\"",re.S|re.I).findall(block_HTML)
            if len(image_url_match)>0:
                reg_image_url = re.sub("<.*?>","",image_url_match[0]).strip()
                if len(image_url_match)>1:
                    gold_image_url = re.sub("<.*?>","",image_url_match[1]).strip()
                
                
        #Craft and Disenchant Cost
        craft_match  = re.compile(r"Disenchanting.*?(\d{1,4}).*?>(\d{1,4})",re.S|re.I).findall(card_HTML)
        if len(craft_match)>0:
            craft_cost=craft_match[0][0]
            disenchant_cost=craft_match[0][1]
        
        #Lore
        lore_match  = re.compile(r"id=\"Lore\">.*?<p>(.*?)<\/p>",re.S|re.I).findall(block_HTML)
        if len(lore_match)>0:
            lore = re.sub("<.*?>","",lore_match[0]).replace("\\n","").replace("\\'","'").strip()
        
        #Full Image
        full_image_url_match  = re.compile(r"<img alt=\"\"\s+src=\"(https:\/\/gamepedia.cursecdn.com\/hearthstone_gamepedia.*?)\" decoding=\"async\"",re.S|re.I).findall(card_HTML)
        if len(full_image_url_match)>0:
            full_image_url = re.sub("<.*?>","",full_image_url_match[0]).strip()
                    
        try:
            database.insert_card(card_name=card_name,\
                                 card_type=card_type,\
                                 card_class=card_class,\
                                 race=race,\
                                 cardset=cardset,\
                                 rarity=rarity,\
                                 cost=cost,\
                                 attack=attack,\
                                 health=health,\
                                 durability=durability,\
                                 craft_cost=craft_cost,\
                                 disenchant_cost=disenchant_cost,\
                                 artist=artist,\
                                 card_text=card_text,\
                                 back_text=back_text,
                                 lore=lore)  
            
            for ability in abilities:
                database.insert_ability(card_name,ability)
            
            for tag in tags:
                database.insert_tag(card_name,tag)
                
        except:
            print("Failed inserting card: "+card_name)
            print("Failed inserting card: "+card_name,file=error_log)
          
        #Download Images:  
        try:
            response = requests.get(reg_image_url, stream=True)
            reg_image_file = open('images/card_images/'+card_name.replace(":","")+'.png', 'wb')
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, reg_image_file)
        except:
            print("Download regular image failed for: "+card_name)
            print("Download regular image failed for: "+card_name,file=error_log)
           
        try: 
            response = requests.get(gold_image_url, stream=True)
            gold_image_file = open('images/card_images/'+card_name.replace(":","")+'_gold.png', 'wb')
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, gold_image_file)
        except:
            print("Download gold image failed for: "+card_name)
            print("Download gold image failed for: "+card_name,file=error_log)
            
        try:
            response = requests.get(full_image_url, stream=True)
            full_image_file = open('images/card_images/'+card_name.replace(":","")+'_full.png', 'wb')
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, full_image_file)
        except:
            print("Download full image failed for: "+card_name)
            print("Download full image failed for: "+card_name,file=error_log)
        
        error_log.close()
        time.sleep(random.uniform(1,5))
    
    
    