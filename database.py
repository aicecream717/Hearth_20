'''
Created on Nov 11, 2019

@author: Aice
'''

import pyodbc,importlib,random,time
from datetime import datetime

card_collection = importlib.import_module("card")

def get_player(entity):
    if hasattr(entity,'owner'):
        return entity.owner
    elif hasattr(entity,'hero_power'):
        return entity
    else:
        return None
    
def cleaned(name):
    return name.replace(" ","_").replace("-","_").replace("'","").replace(":","").replace("!","").replace("+","").replace(".","").replace(",","").replace("(","").replace(")","").replace('"',"")

def get_connection():
#Hide sensitive information in a configuration file, and read from it
    config_file=open("database.config","r")
    params=[]
    for line in config_file:
        params.append(line.split("=")[1].rstrip("\n"))
    driver,server,database,uid,pwd = params[0],params[1],params[2],params[3],params[4]
    
    #Create database connection with parameters read from the configuration file
    conn = pyodbc.connect(driver=driver,
                          server=server,
                          database=database,
                          uid=uid,
                          pwd=pwd)
    
    return conn



def create_tables():
    
    conn=get_connection()
    cursor = conn.cursor()
    
    # execute SQL query
    cursor.execute("IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='card_meta' and xtype='U')\
                CREATE TABLE card_meta (\
                card_name nvarchar (50) NOT NULL,\
                type nvarchar (20),\
                class nvarchar (20),\
                race  nvarchar (50),\
                cardset nvarchar (50),\
                rarity nvarchar (20),\
                cost int,\
                attack int,\
                health int,\
                durability int,\
                craft_cost int,\
                disenchant_cost int,\
                artist nvarchar(50) ,\
                card_text ntext,\
                back_text ntext,\
                lore ntext,\
                PRIMARY KEY (card_name))")
    
    cursor.execute("IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='card_abilities' and xtype='U')\
                CREATE TABLE card_abilities (\
                card_name nvarchar (50) NOT NULL,\
                ability nvarchar (50),\
                FOREIGN KEY (card_name) REFERENCES card_meta (card_name))")
    
    cursor.execute("IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='card_tags' and xtype='U')\
            CREATE TABLE card_tags (\
            card_name nvarchar (50) NOT NULL,\
            tag nvarchar (50),\
            FOREIGN KEY (card_name) REFERENCES card_meta (card_name))")
    
    cursor.execute("IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='players' and xtype='U')\
            CREATE TABLE players (\
            username varchar (20) NOT NULL,\
            password varchar (20) NOT NULL,\
            current_hero varchar (20),\
            deck text,\
            db_username varchar (20),\
            PRIMARY KEY (username))")
    
    cursor.execute("IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='events' and xtype='U')\
            CREATE TABLE [dbo].[events](\
            [eventID] int IDENTITY(100000,1) PRIMARY KEY,\
            [sessionID] int NULL,\
            [player] [nvarchar](50) NULL,\
            [event] [nvarchar](200) NULL,\
            [register_time] [datetime2](7) NULL,\
            [resolve_time] [datetime2](7) NULL,\
            [event_type] [nvarchar](50) NULL)")
    
    cursor.execute("IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='matches' and xtype='U')\
            CREATE TABLE [dbo].[matches](\
            [sessionID] int IDENTITY(100000,1) PRIMARY KEY,\
            [player1] [nvarchar](50) NULL,\
            [player2] [nvarchar](50) NULL,\
            [queue_in_time] [datetime2](7) NULL,\
            [match_time] [datetime2](7) NULL,\
            [random_seed] int NULL,\
            [player1_hand_str] text NULL,\
            [player2_hand_str] text NULL,\
            [player1_deck_str] text NULL,\
            [player2_deck_str] text NULL)")
                           
    # make the change persistent
    cursor.commit()
    
    #close connection after using it
    conn.close()

def insert_card(card_name="",card_type="",card_class="Neutral",race="",cardset="Basic",rarity="Common",\
                cost=0,attack=0,health=0,durability=0,\
                craft_cost=-1,disenchant_cost=-1,artist="",card_text="",back_text="",lore="",play_format=""):
    
    conn=get_connection()
    cursor = conn.cursor()
    
    SQL_TEMPLATE="INSERT INTO [Hearth].[dbo].[card_meta]\
                (card_name,type,class,race,cardset,rarity,cost,attack,health,durability,\
                craft_cost,disenchant_cost,artist,card_text,back_text,lore,format)\
                VALUES ('$card_name$','$type$','$class$','$race$','$cardset$','$rarity$',\
                $cost$,$attack$,$health$,$durability$,$craft_cost$,\
                $disenchant_cost$,'$artist$','$card_text$','$back_text$','$lore$','$format$')"
                
    SQL_TEMPLATE = SQL_TEMPLATE.replace("$card_name$", card_name.replace("'","''"))
    SQL_TEMPLATE = SQL_TEMPLATE.replace("$type$", card_type)
    SQL_TEMPLATE = SQL_TEMPLATE.replace("$class$", card_class)
    SQL_TEMPLATE = SQL_TEMPLATE.replace("$race$", race)
    SQL_TEMPLATE = SQL_TEMPLATE.replace("$cardset$", cardset.replace("'","''"))
    SQL_TEMPLATE = SQL_TEMPLATE.replace("$rarity$", rarity)
    SQL_TEMPLATE = SQL_TEMPLATE.replace("$cost$", str(cost))
    SQL_TEMPLATE = SQL_TEMPLATE.replace("$attack$", str(attack))
    SQL_TEMPLATE = SQL_TEMPLATE.replace("$health$", str(health))
    SQL_TEMPLATE = SQL_TEMPLATE.replace("$durability$", str(durability))
    SQL_TEMPLATE = SQL_TEMPLATE.replace("$craft_cost$", str(craft_cost))
    SQL_TEMPLATE = SQL_TEMPLATE.replace("$disenchant_cost$", str(disenchant_cost))
    SQL_TEMPLATE = SQL_TEMPLATE.replace("$artist$", artist.replace("'","''"))
    SQL_TEMPLATE = SQL_TEMPLATE.replace("$card_text$", card_text.replace("'","''"))
    SQL_TEMPLATE = SQL_TEMPLATE.replace("$back_text$", back_text.replace("'","''"))
    SQL_TEMPLATE = SQL_TEMPLATE.replace("$lore$", lore.replace("'","''"))
    SQL_TEMPLATE = SQL_TEMPLATE.replace("$format$", play_format)
    
    print(SQL_TEMPLATE)
    cursor.execute(SQL_TEMPLATE)
    
    cursor.commit()
    conn.close()

def insert_ability(card_name,ability):  
    
    conn=get_connection()
    cursor = conn.cursor()  
    
    SQL_TEMPLATE="INSERT INTO [Hearth].[dbo].[card_abilities] VALUES ('$card_name$','$ability$')"
    SQL_TEMPLATE = SQL_TEMPLATE.replace("$card_name$", card_name.replace("'","''"))
    SQL_TEMPLATE = SQL_TEMPLATE.replace("$ability$", ability.replace("'","''"))
    
    print(SQL_TEMPLATE)
    cursor.execute(SQL_TEMPLATE)
    
    cursor.commit()
    conn.close()

def insert_tag(card_name,tag):  
    
    conn=get_connection()
    cursor = conn.cursor()  
    
    SQL_TEMPLATE="INSERT INTO [Hearth].[dbo].[card_tags] VALUES ('$card_name$','$tag$')"
    SQL_TEMPLATE = SQL_TEMPLATE.replace("$card_name$", card_name.replace("'","''"))
    SQL_TEMPLATE = SQL_TEMPLATE.replace("$tag$", tag.replace("'","''"))
    
    print(SQL_TEMPLATE)
    cursor.execute(SQL_TEMPLATE)
    
    cursor.commit()
    conn.close()

def get_card_metadata(card_name):    
    metadata=[]
    
    conn=get_connection()
    cursor = conn.cursor()  
    
    SQL_TEMPLATE="SELECT [card_name],[type],[class],[race],[cardset],[rarity],[cost],[attack],[health],[durability],\
                [craft_cost],[disenchant_cost],[artist],[card_text],[back_text],[lore]\
                 FROM [Hearth].[dbo].[card_meta] WHERE [card_name]='$name$'"
    SQL_TEMPLATE = SQL_TEMPLATE.replace("$name$", card_name.replace("'","''"))
    cursor.execute(SQL_TEMPLATE)
    results=cursor.fetchall()
    
    if len(results)>0:
        metadata.extend(results[0])
        
        abilities=[]
        SQL_TEMPLATE="SELECT [ability] FROM [Hearth].[dbo].[card_abilities] WHERE [card_name]='$name$'"
        SQL_TEMPLATE = SQL_TEMPLATE.replace("$name$", card_name.replace("'","''"))
        cursor.execute(SQL_TEMPLATE)
        results=cursor.fetchall()
        for ability in results:
            abilities.append(ability[0].strip())
        metadata.append(abilities)
            
        tags=[]
        SQL_TEMPLATE="SELECT [tag] FROM [Hearth].[dbo].[card_tags] WHERE [card_name]='$name$'"
        SQL_TEMPLATE = SQL_TEMPLATE.replace("$name$", card_name.replace("'","''"))
        cursor.execute(SQL_TEMPLATE)
        results=cursor.fetchall()
        for tag in results:
            tags.append(tag[0].strip())
        metadata.append(tags)

    else:
        metadata = [card_name,"","Neutral","","Basic","Common",1,1,1,1,-1,-1,"","","","",[],[]]
        
    conn.close()
    
    return metadata

def check_username_in_database(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM [Hearth].[dbo].[players] WHERE [username]='"+username+"' AND [db_username]=CURRENT_USER")
    result1 = len(cursor.fetchall())>0
    
    cursor.execute("SELECT * FROM [Hearth].[dbo].[players] WHERE [username]='"+username+"' AND [db_username]!=CURRENT_USER")
    result2 = len(cursor.fetchall())>0
    
    conn.close()
    
    return result1,result2

def get_user_info(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT [username],[password],[current_hero],[deck] FROM [Hearth].[dbo].[players] WHERE [username]='"+username+"'")
    player_name, password, current_hero, deck= cursor.fetchone()
    conn.close()
    
    return player_name, password, current_hero, deck

def create_new_player(username,password):#Create game level logins
    conn = get_connection()
    cursor = conn.cursor()
    encrypted_password=encrypt(password)
    SQL="INSERT INTO [Hearth].[dbo].[players] VALUES ('"+username+"','"+encrypted_password+"',"+"null"+","+"null"+",CURRENT_USER)"
    #print(SQL)
    cursor.execute(SQL)
    print("Your player info has been successfully created and stored into database.\n")
    conn.commit()
    conn.close()

def create_login(username,stid):#Create database level logins
    conn = get_connection()
    cursor = conn.cursor()
    password="A@"+stid
    cursor.execute("IF NOT EXISTS (SELECT [loginname] FROM master.dbo.syslogins WHERE [name]='"+username+"') CREATE LOGIN ["+username+"] WITH PASSWORD = '"+password+"'")
    cursor.execute("USE [Hearth]")
    cursor.execute("IF NOT EXISTS (SELECT [name] FROM sys.database_principals WHERE [name]='"+username+"') CREATE USER ["+username+"] FOR LOGIN ["+username+"]")
    print("Login ["+username+"] is created \n")
    conn.commit()
    conn.close()
    
def grant_permission(player_db_name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("GRANT SELECT ON [Hearth].[dbo].[card_meta] TO ["+player_db_name+"]")
    cursor.execute("GRANT SELECT ON [Hearth].[dbo].[card_tags] TO ["+player_db_name+"]")
    cursor.execute("GRANT SELECT ON [Hearth].[dbo].[card_abilities] TO ["+player_db_name+"]")
    cursor.execute("GRANT SELECT ON [Hearth].[dbo].[events] TO ["+player_db_name+"]")
    cursor.execute("GRANT INSERT ON [Hearth].[dbo].[events] TO ["+player_db_name+"]")
    cursor.execute("GRANT UPDATE ON [Hearth].[dbo].[events] TO ["+player_db_name+"]")
    cursor.execute("GRANT SELECT ON [Hearth].[dbo].[matches] TO ["+player_db_name+"]")
    cursor.execute("GRANT INSERT ON [Hearth].[dbo].[matches] TO ["+player_db_name+"]")
    cursor.execute("GRANT UPDATE ON [Hearth].[dbo].[matches] TO ["+player_db_name+"]")
    cursor.execute("GRANT SELECT ON [Hearth].[dbo].[players] TO ["+player_db_name+"]")
    cursor.execute("GRANT INSERT ON [Hearth].[dbo].[players] TO ["+player_db_name+"]")
    cursor.execute("GRANT UPDATE ON [Hearth].[dbo].[players] TO ["+player_db_name+"]")
    
    print(player_db_name+" permissions processed.\n")
    conn.commit()
    conn.close()
           
def add_card_to_draft(player,card):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT deck from [Hearth].[dbo].[players] WHERE [username]='"+player.player_name+"'")
    deck_str=cursor.fetchone()
    if deck_str[0] is not None:
        new_deck_str=deck_str[0]+";"+card.name
    else:
        new_deck_str=card.name
    
    cursor.execute("UPDATE [Hearth].[dbo].[players] SET [deck]='"+new_deck_str.replace("'","''")+"' WHERE [username]='"+player.player_name+"'")
    conn.commit()
    conn.close()

def update_current_hero(player):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE [Hearth].[dbo].[players] SET [current_hero]='"+player.hero_name.replace("'","''")+"' WHERE [username]='"+player.player_name+"'")
    conn.commit()
    conn.close()

def update_winner(player):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE [Hearth].[dbo].[matches] SET [winner]='"+player.name+"' WHERE [sessionID]='"+str(player.board.sessionID)+"'")
    conn.commit()
    conn.close()
     
def get_random_cards(filter_str="[cost]>=0",owner="",k=3,standard=True,by_ability=False):
    
    conn = get_connection()
    cursor = conn.cursor()
    
    SQL_TEMPLATE = "SELECT [card_name],[class] FROM [Hearth].[dbo].[card_meta] WHERE ("+filter_str+")"
    if by_ability:
        SQL_TEMPLATE = "SELECT [Hearth].[dbo].[card_meta].[card_name],[Hearth].[dbo].[card_meta].[class] FROM [Hearth].[dbo].[card_meta],[Hearth].[dbo].[card_abilities] \
                        WHERE [Hearth].[dbo].[card_meta].[card_name]=[Hearth].[dbo].[card_abilities].[card_name]\
                        AND ("+filter_str+") AND TRIM([ability])='"+by_ability+"'"
    if standard:
        SQL_TEMPLATE=SQL_TEMPLATE+" AND [format]='standard'"

    print(SQL_TEMPLATE)
    cursor.execute(SQL_TEMPLATE)
    results = cursor.fetchall()
    refined_results = adjust_class_cards(results)
    card_names=random.sample(refined_results,k=min(k,len(refined_results)))
    cards=[]
    for card_name in card_names:
        try:
            card=getattr(card_collection,cleaned(card_name[0]))(owner=owner)
        except:
            card=getattr(card_collection,cleaned("Wisp"))(owner=owner)
        cards.append(card)
    conn.commit()
    conn.close()
    
    return cards

def adjust_class_cards(results):
    refined_results=[]
    neutral_cards=[]
    class_cards=[]
    for result in results:
        card_name=result[0]
        card_class=result[1]
        
        if card_class=="Neutral":
            neutral_cards.append((card_name,card_class))
        else:
            class_cards.append((card_name,card_class))
        
        '''if card_class!="Neutral" or random.uniform(0,1)>class_chance:
            refined_results.append((card_name,card_class))'''

    #return refined_results       
    return class_cards+random.sample(neutral_cards,k=min(max(10,len(class_cards)),len(neutral_cards)))
        
    
def set_standard(card_name,uncollectible_flag=False):
    conn = get_connection()
    cursor = conn.cursor()
    SQL_TEMPLATE = "UPDATE [Hearth].[dbo].[card_meta] SET [format]='$FORMAT$' WHERE [card_name]='$CARD_NAME$'"
    SQL_TEMPLATE=SQL_TEMPLATE.replace("$CARD_NAME$",card_name.replace("'","''"))
    SQL_TEMPLATE=SQL_TEMPLATE.replace("$FORMAT$",{True:'uncollectible',False:'standard'}[uncollectible_flag])
    try:
        cursor.execute(SQL_TEMPLATE)
    except:
        print(SQL_TEMPLATE)
    conn.commit()
    conn.close()

def search_opponent(player):
    conn = get_connection()
    cursor = conn.cursor()
    if player.vsAI:
        sessionID,seed=queue_in(player)
        opponent_name="AI"
        cursor.execute("UPDATE [Hearth].[dbo].[matches] SET [match_time]='"+str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))+"' WHERE [sessionID]='"+str(sessionID)+"'")    
        cursor.execute("UPDATE [Hearth].[dbo].[matches] SET [player2]='AI' WHERE [sessionID]='"+str(sessionID)+"'")  
    else:
        SQL_TEMPLATE = "SELECT TOP (1) [player1],[random_seed],[sessionID] FROM [Hearth].[dbo].[matches] WHERE [player2] is NULL AND [player1]!='"+player.name+"' AND datediff(SECOND, [queue_in_time], CURRENT_TIMESTAMP)<14460 ORDER BY [queue_in_time] DESC"
        results=[]
        try:
            cursor.execute(SQL_TEMPLATE)
            results = cursor.fetchall()    
        except:
            print(SQL_TEMPLATE)
            
        if len(results)>0:
            opponent_name,seed,sessionID=results[0][0],results[0][1],results[0][2]  
            cursor.execute("UPDATE [Hearth].[dbo].[matches] SET [match_time]='"+str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))+"' WHERE [sessionID]='"+str(sessionID)+"'")    
            cursor.execute("UPDATE [Hearth].[dbo].[matches] SET [player2]='"+player.name+"' WHERE [sessionID]='"+str(sessionID)+"'")  
        else:
            sessionID,seed=queue_in(player)
            FOUND = False
            timer=0.0
            while not FOUND:
                time.sleep(5)
                timer+=5.0
                cursor.execute("SELECT TOP (1) [player2],[random_seed],[sessionID] FROM [Hearth].[dbo].[matches] WHERE [player1]='"+player.name+"' AND [player2] IS NOT NULL AND [sessionID]='"+str(sessionID)+"'")
                matches=cursor.fetchall()
                if len(matches)>0:
                    FOUND=True
                    opponent_name,seed,sessionID=matches[0][0],matches[0][1],matches[0][2]
                elif timer>60:
                    print("Updating queue\n")
                    sessionID,seed=queue_in(player) #Requeue
                    timer=0.0
                else:
                    print("Still searching opponent (will only match player who queued in within 60 seconds)")
                        
    conn.commit()
    conn.close() 
    
    return opponent_name,seed,sessionID
 
def queue_in(player):
    conn = get_connection()
    cursor = conn.cursor()
    
    SQL_TEMPLATE = "INSERT INTO [Hearth].[dbo].[matches] ([player1],[player2],[queue_in_time],[random_seed]) VALUES ('$PLAYER1$',NULL,'$QUEUE_TIME$',$SEED$)"
    SQL_TEMPLATE = SQL_TEMPLATE.replace("$PLAYER1$",player.name)
    SQL_TEMPLATE = SQL_TEMPLATE.replace("$QUEUE_TIME$",str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    SQL_TEMPLATE = SQL_TEMPLATE.replace("$SEED$",str(random.randint(1,100)))
    
    try:
        cursor.execute(SQL_TEMPLATE)  
    except:
        print(SQL_TEMPLATE)
        
    cursor.execute("SELECT TOP (1) [sessionID],[random_seed] FROM [Hearth].[dbo].[matches] WHERE [player1]='"+player.name+"' ORDER BY [queue_in_time] DESC") 
    result=cursor.fetchone()
    sessionID=result[0]
    seed=result[1]
    
    conn.commit()
    conn.close()
        
    return sessionID,seed

def update_player_starting_cards(player):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT [player1] FROM [Hearth].[dbo].[matches] WHERE [sessionID]='"+str(player.board.sessionID)+"'")
    player1_name=cursor.fetchone()[0]
    player_no={True:1,False:2}[player1_name==player.name]

    SQL_TEMPLATE1 = "UPDATE [Hearth].[dbo].[matches] SET [player"+str(player_no)+"_hand_str]='$HAND_STR$' WHERE [sessionID]='$SESSION_ID$'"
    SQL_TEMPLATE2 = "UPDATE [Hearth].[dbo].[matches] SET [player"+str(player_no)+"_deck_str]='$DECK_STR$' WHERE [sessionID]='$SESSION_ID$'"
    
    hand_str=""
    for card in player.hand:
        hand_str+=card.name+";"
    
    deck_str=""
    for card in player.deck.cards:
        deck_str+=card.name+";"
    
    SQL_TEMPLATE1=SQL_TEMPLATE1.replace("$HAND_STR$",hand_str.replace("'","''").rstrip(";"))
    SQL_TEMPLATE1=SQL_TEMPLATE1.replace("$SESSION_ID$",str(player.board.sessionID))
    SQL_TEMPLATE2=SQL_TEMPLATE2.replace("$DECK_STR$",deck_str.replace("'","''").rstrip(";"))
    SQL_TEMPLATE2=SQL_TEMPLATE2.replace("$SESSION_ID$",str(player.board.sessionID))
    
    try:
        cursor.execute(SQL_TEMPLATE1)
        cursor.execute(SQL_TEMPLATE2)
    except:
        print(SQL_TEMPLATE1)
        print(SQL_TEMPLATE2)
    
    conn.commit()
    conn.close() 

def encrypt(password):
    enc=""
    for c in password:
        enc+=chr(ord(c)+21)
    enc.replace("'",'"')
    return enc[::-1]

def decrypt(password):
    enc=""
    for c in password:
        enc+=chr(ord(c)-21)
    return enc[::-1]

def str_to_cards(name,player):
    card_names = name.split(";")
    cards=[]
    for card_name in card_names:
        card=getattr(card_collection,cleaned(card_name))(owner=player)
        cards.append(card)
    return cards
        
def synchronize_opponent_starting_cards(player):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT [player1] FROM [Hearth].[dbo].[matches] WHERE [sessionID]='"+str(player.board.sessionID)+"'")
    player1_name=cursor.fetchone()[0]
    player_no={True:1,False:2}[player1_name==player.name]

    FOUND=False
    while not FOUND:
        cursor.execute("SELECT [player"+str(player_no)+"_hand_str],[player"+str(player_no)+"_deck_str] FROM [Hearth].[dbo].[matches] WHERE [sessionID]='"+str(player.board.sessionID)+"'")
        results=cursor.fetchall()
        if len(results)>0 and results[0][0] is not None:
            FOUND=True
            hand_str,deck_str=results[0]
        elif player.name=="AI":#Copy player hand and deck for AI
            FOUND=True
            cursor.execute("SELECT [player"+str(3-player_no)+"_hand_str],[player"+str(3-player_no)+"_deck_str] FROM [Hearth].[dbo].[matches] WHERE [sessionID]='"+str(player.board.sessionID)+"'")
            results=cursor.fetchall()
            hand_str,deck_str=results[0]
        else:
            print("Waiting for opponent mulligan")
            time.sleep(5)
            

    for card in str_to_cards(hand_str,player):
        player.add_hand(card)
        
    player.deck.cards=[]
    for card in str_to_cards(deck_str,player):
        player.deck.add_card(card,randomize=False)

    conn.close() 
        
    
def get_events(player,event_type="play"):
    conn = get_connection()
    cursor = conn.cursor()
    SQL_TEMPLATE = "SELECT [eventID],[event] FROM [Hearth].[dbo].[events] WHERE [sessionID]='"+str(player.board.sessionID)+"' AND [player]='"+player.name+"' AND [resolve_time] is NULL AND [event_type]='"+event_type+"' ORDER BY [register_time] ASC"
    try:
        cursor.execute(SQL_TEMPLATE)
        results = cursor.fetchall()

    except:
        print(SQL_TEMPLATE)
    
    conn.close() 
    
    return results    

def insert_event(player,entity,target,event_pos,event_type="play",instant_resolve=False):
    source_str=player.name+":"+str(int(player.mouse_move_length))+":" #Record mouse length when turn ends
    target_str="::"
    if entity is not None:
        if isinstance(entity,str):#Record mouse length and emote choice when turn ends
            source_str=player.name+":"+str(int(player.mouse_move_length))+":"+entity
        else:
            source_str=str(get_player(entity).name)+":"+entity.get_area()+":"+str(entity.get_index())
    if target is not None:
        if target.__class__==int:
            target_str="::"+str(target)
        else:
            target_str=str(get_player(target).name)+":"+target.get_area()+":"+str(target.get_index())
    event_pos_str=str(event_pos[0])+":"+str(event_pos[1])
    event_str=source_str+";"+target_str+";"+event_pos_str
    
    conn = get_connection()
    cursor = conn.cursor()
    SQL_TEMPLATE = "INSERT INTO [Hearth].[dbo].[events] ([sessionID],[player],[event],[register_time],[resolve_time],[event_type])\
                    VALUES ('$SESSION_ID$','$PLAYER_NAME$','$EVENT$','$REG_TIME$',$RES_TIME$,'$EVENT_TYPE$')"
    SQL_TEMPLATE=SQL_TEMPLATE.replace("$SESSION_ID$",str(player.board.sessionID))
    SQL_TEMPLATE=SQL_TEMPLATE.replace("$PLAYER_NAME$",player.name)
    SQL_TEMPLATE=SQL_TEMPLATE.replace("$EVENT$",event_str)
    SQL_TEMPLATE=SQL_TEMPLATE.replace("$REG_TIME$",str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    if instant_resolve:
        SQL_TEMPLATE=SQL_TEMPLATE.replace("$RES_TIME$","'"+str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))+"'")
    else:
        SQL_TEMPLATE=SQL_TEMPLATE.replace("$RES_TIME$","NULL")
    SQL_TEMPLATE=SQL_TEMPLATE.replace("$EVENT_TYPE$",event_type)

    try:
        cursor.execute(SQL_TEMPLATE)
    except:
        print(SQL_TEMPLATE)
    conn.commit()
    conn.close()

def resolve_event(eventID):
    conn = get_connection()
    cursor = conn.cursor()
    SQL_TEMPLATE = "UPDATE [Hearth].[dbo].[events] SET [resolve_time]='$RES_TIME$' WHERE [eventID]='$EVENT_ID$'"
    SQL_TEMPLATE=SQL_TEMPLATE.replace("$EVENT_ID$",str(eventID))
    SQL_TEMPLATE=SQL_TEMPLATE.replace("$RES_TIME$",str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    try:
        cursor.execute(SQL_TEMPLATE)
    except:
        print(SQL_TEMPLATE)
    conn.commit()
    conn.close()
                        
if __name__ == '__main__':
    create_tables() 
    
    try:
        '''Insert Coin not crawled from gamepedia'''
        
        insert_card("The Coin","Spell","","","Basic","",0,0,0,0,-1,-1,"Ben Thompson","Gain 1 Mana Crystal this turn only.","","",'uncollectible')
        
        '''Insert Basic Hero Powers not crawled from gamepedia'''
        
        insert_card("Armor Up!","Hero Power","Warrior","","Basic","",2,0,0,0,-1,-1,"Efrem Palacios","Hero Power Gain 2 Armor.","","",'uncollectible')
        insert_ability("Armor Up!","Gain Armor")
            
        insert_card("Dagger Mastery","Hero Power","Rogue","","Basic","",2,0,0,0,-1,-1,"Dave Allsop","Hero Power Equip a 1/2 Dagger.","","",'uncollectible')
        insert_ability("Dagger Mastery","Equip")
        insert_tag("Dagger Mastery","Weapon-generating")
        
        insert_card("Demon Claws","Hero Power","Demon Hunter","","Basic","",1,0,0,0,-1,-1,"Virtuos","Hero Power +1 Attack this turn.","","",'uncollectible')
        insert_ability("Demon Claws","Increment attribute")
    
        insert_card("Fireblast","Hero Power","Mage","","Basic","",2,0,0,0,-1,-1,"Jim Nelson","Hero Power Deal 1 damage.","","",'uncollectible')
        insert_ability("Fireblast","Deal damage")
        insert_tag("Fireblast","Targeted")
        
        insert_card("Lesser Heal","Hero Power","Priest","","Basic","",2,0,0,0,-1,-1,"Cos Koniotis","Hero Power Restore 2 Health.","","",'uncollectible')
        insert_ability("Lesser Heal","Restore Health")
        insert_tag("Lesser Heal","Targeted")
        
        insert_card("Life Tap","Hero Power","Warlock","","Basic","",2,0,0,0,-1,-1,"Luca Zontini","Hero Power +1 Attack this turn.","","",'uncollectible')
        insert_ability("Life Tap","Deal damage")
        insert_ability("Life Tap","Draw cards")
        
        insert_card("Reinforce","Hero Power","Paladin","","Basic","",2,0,0,0,-1,-1,"Theodore Park","Hero Power Summon a 1/1 Silver Hand Recruit.","","",'uncollectible')
        insert_ability("Reinforce","Summon")
        insert_tag("Reinforce","Recruit-generating")    
        
        insert_card("Shapeshift","Hero Power","Druid","","Basic","",2,0,0,0,-1,-1,"Aleksi Briclot","Hero Power +1 Attack this turn. +1 Armor.","","",'uncollectible')
        insert_ability("Shapeshift","Increment attribute")
        insert_ability("Shapeshift","Gain Armor")    
        
        insert_card("Steady Shot","Hero Power","Hunter","","Basic","",2,0,0,0,-1,-1,"Glenn Rane","Hero Power Deal 2 damage to the enemy hero.","","",'uncollectible')
        insert_ability("Steady Shot","Deal damage")
     
        insert_card("Totemic Call","Hero Power","Shaman","","Basic","",2,0,0,0,-1,-1,"Massive Black","Hero Power Summon a random Totem.","","",'uncollectible')
        insert_ability("Totemic Call","Summon")
        insert_tag("Totemic Call","Random")  
        insert_tag("Totemic Call","Spell Damage-generating")  
        insert_tag("Totemic Call","Taunt-generating")  
        insert_tag("Totemic Call","Totem-generating")  
    except:
        pass
    '''Sample 
    insert_card("Shattered Sun Cleric","Minion","Neutral","","Basic","Common",3,3,2,0,-1,-1,"Doug Alexander","Battlecry: Give a friendly minion +1/+1.","They always have a spare flask of Sunwell Energy Drink!","The Shattered Sun Offensive is an army of blood elf and draenei priests, paladins, magi and warriors rallied by the naaru to combat Kael'thas Sunstrider's mad bid to use the Sunwell as a portal to summon his master, Kil'jaeden. Their operations are centered around the Isle of Quel'Danas, where the Sunwell is located. The Offensive is the culmination of a plea for unity between the draenei priests of the Aldor and the blood elf wizards of the Scryers in an effort to prevent Kil'jaeden's summoning, which would result in the end of all life on Azeroth.")
    insert_ability("Shattered Sun Cleric","Battlecry")
    insert_ability("Shattered Sun Cleric","Increment Attribute")
    insert_tag("Shattered Sun Cleric","Targeted")
    '''
    insert_card("Sheep (Mean Streets of Gadgetzan)","Minion","Mage, Priest, Warlock","Beast","Mean Streets of Gadgetzan","Common",1,1,1,0,-1,-1,"Evegeniy Zagumennyy","","")