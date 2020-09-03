## PURPOSE: to shame people

## Imports
import discord
import random
import os
import psycopg2
from discord.ext import commands
from rabi import Rabi
import urllib.parse as urlparse

bot = commands.Bot(command_prefix = 'rabi ')


@bot.event
async def on_ready():
    await bot.change_presence(status = discord.Status.online, activity = discord.Game('Epic Seven'))
    print('rabi')


@bot.event
async def on_message(message):

    if not message.author.bot: #avoids infinite loops

        ## Misc. commands
        await set_reaction(message)
        await hit_rabi(message)
        #await ssb_user(message)
        await detect_keywords(message)
        
        await bot.process_commands(message)


## Data storage
async def postgres_connect():
    
    url = urlparse.urlparse(Rabi.DATABASE_URL)
    dbname = url.path[1:]
    user = url.username
    password = url.password
    host = url.hostname
    port = url.port

    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
        )

    return conn

async def open_table(command, mode):
    
    conn = await postgres_connect()
    cur = conn.cursor()
    cur.execute(command)
    data = None

    ## 0: commit, 1: fetchone, 2: fetchall
    if mode == 1: data = cur.fetchone() #list representing a row
    if mode == 2: data = cur.fetchall() #list of lists

    conn.commit()
    cur.close()
    conn.close()
    return data


## Keyword detected, check postgres for reaction status
async def rabi_reactions(server_id):

    ## Check if table and row exists
    check1 = "SELECT EXISTS(SELECT * FROM information_schema.tables WHERE table_name = 'rabi_reactions')"
    check2 = f"SELECT EXISTS(SELECT * FROM rabi_reactions WHERE server_id = '{server_id}')"
    create = "CREATE TABLE rabi_reactions (server_id TEXT, status boolean)"
    select = f"SELECT * FROM rabi_reactions WHERE server_id = '{server_id}'"

    if (await open_table(check1, 1))[0]:
        if (await open_table(check2, 1))[0]:

            ## Get status
            return (await open_table(select, 1))[1]

        ## Reactions enabled by default
        else:
            return True

    ## Create table
    else:
        try:
            await open_table(create, 0)

        ## In case a table was created with 0 entries
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

        ## Default setting
        return True
    

## Checks if message is a command before searching for keywords
async def is_command(text):

    for command in Rabi.COMMANDS:
        if text.startswith(command):
            return True

    return False


## Checks for any keywords in message
async def detect_keywords(message):

    text = message.content.lower()
    
    if not await is_command(text):
        await find_rabi(message)
        
        for reaction in Rabi.REACTIONS:
            for keyword in Rabi.REACTIONS[reaction]:
                if await findWholeWord(keyword, text) and await rabi_reactions(message.guild.id):
                    await message.channel.send(reaction)
                    break


## Finding words in a sentence
async def findWholeWord(w, s):
    return f' {w} ' in f' {s} '


## Special case for rabi and arabi
async def find_rabi(message):
    
    text = message.content.lower()
    response = ''

    for emote in Rabi.RABI:
        for keyword in Rabi.RABI[emote]:
            if await findWholeWord(keyword, text) and await rabi_reactions(message.guild.id):
                response += emote
                break
        if response == '<:rabi:646666830651326464><:arabi:648411271334461449>':
            await message.channel.send(response)
            return
    if len(response) > 0:
        await message.channel.send(response)


## Enables and disables reactions
async def set_reaction(message):

    text = message.content.lower()
    
    if text == 'hi rabi' or text == 'hi ravi':
        await message.channel.send('<:rabiwave:648711649838235658>')
        reaction = True

    elif text == 'kill rabi' or text == 'kill ravi':
        await message.channel.send('<:rabidrink:665760786462933012>')
        reaction = False

    else:
        return

    ## Check tables and rows
    server_id = message.guild.id
    check1 = "SELECT EXISTS(SELECT * FROM information_schema.tables WHERE table_name = 'rabi_reactions')"
    check2 = f"SELECT EXISTS(SELECT * FROM rabi_reactions WHERE server_id = '{server_id}')"
    create = "CREATE TABLE rabi_reactions (server_id TEXT, status boolean)"
    add = f"INSERT INTO rabi_reactions(server_id, status) VALUES('{server_id}', {reaction})"
    update = f"UPDATE rabi_reactions SET status = {reaction} WHERE server_id = '{server_id}'"

    ## Table exists
    if (await open_table(check1, 1))[0]:
        if (await open_table(check2, 1))[0]:
            await open_table(update, 0)
        else:
            await open_table(add, 0)

    ## Table may or may not exist
    else:
        try:
            await open_table(add, 0)

        ## Table does not exist, create one, then a new row
        except (Exception, psycopg2.DatabaseError) as error:
            await open_table(create, 0)
            await open_table(add, 0)
            
            print(error)


## Fun feature, 20% to counter
async def hit_rabi(message):
    if message.content.lower() == 'hit rabi' or message.content.lower() == 'hit ravi':
        value = random.random()
        print(value)
        if value < 0.2:
            await message.channel.send('COUNTER ATTAC')
            await message.channel.send('<:rabiflame:648713302360326148>')
        else:
            await message.channel.send('<:rabicry:650976531354615819>')
            

## Run
##bot.run(str(os.environ.get('TOKEN')))
bot.run(Rabi.TOKEN)
