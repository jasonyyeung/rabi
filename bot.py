## PURPOSE: to shame people

## Imports
import discord
import random
import os
import psycopg2
import re
from datetime import datetime, timedelta
from pytz import timezone 
import asyncio
from discord.ext import commands
from rabi import Rabi
#from arabi import Arabi
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
        await detect_keywords(message)
        await gw_timer(message)
        
        await bot.process_commands(message)


## Data storage
async def postgres_connect():
    
    url = urlparse.urlparse(os.environ.get('DATABASE_URL'))
    ##url = urlparse.urlparse(Arabi.DATABASE_URL)
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


## Fun feature, 20% to counter into 35% to mute user
async def hit_rabi(message):
    if message.content.lower() == 'hit rabi' or message.content.lower() == 'hit ravi':
        value = random.random()

        if value < 0.2:
            await message.channel.send('COUNTER ATTAC <:rabiflame:648713302360326148>')
            value2 = random.random()
            if value2 < 0.35:
                perms = message.channel.overwrites_for(message.author)
                await message.channel.send('STUN PROCC')
                await message.channel.set_permissions(message.author, send_messages=False)
                await asyncio.sleep(30)
                await message.channel.set_permissions(message.author, send_messages=True)
        else:
            await message.channel.send('<:rabicry:650976531354615819>')


## I love gw
@bot.command()
async def gw(ctx):
    
    ## Make sure its gw day
    weekday = datetime.datetime.now().weekday()
    hour = datetime.datetime.now().hour
    if (weekday in [0, 2, 4] and hour >= 6) or (weekday in [1, 3, 5] and hour < 6):
        
        ## Find all channels with members in it
        channels = []
        for c in ctx.guild.channels:
            if str(c.type) == "voice" and len(c.members) > 0:
                channels.append(c)

        ## Tag all members in channel randomly
        if len(channels) > 0:
            dialogue = "I love gw.\n"
            members = channels[0].members
            for member in range(len(channels[0].members)):
                tagged = random.choice(members)
                dialogue = dialogue + str(member + 1) + ". " + tagged.mention

                if str(tagged) == 'Snow#9697' and member == len(channels[0].members) - 1:
                    dialogue = dialogue + " " + '<:rabidrink:665760786462933012>'

                dialogue = dialogue + "\n"
                members.remove(tagged)

            ## Send message in 1 block
            await ctx.send(dialogue)

        else:
            await ctx.send('No one wants to do gw right now.')
            await ctx.send('<:rabisad:650976531354615819>')

    else:
        await ctx.send("There's no gw today.")
    

## For adding/updating builds (or any screenshot really)
@bot.command()
async def add(ctx):
    return
    

## For removing builds (or any screenshot really)
@bot.command()
async def remove(ctx):
    return


## Imagine memorizing time zones
@bot.command()
async def time(ctx):
    
    chow = datetime.now(timezone('Australia/Sydney'))
    steph = datetime.now(timezone('Australia/Brisbane'))
    utc = datetime.now(timezone('UTC'))
    edt = datetime.now(timezone('Canada/Eastern'))
    
    await ctx.send("Chow: " + chow.strftime('%#I:%M %p') + "\n" +
                   "Steph: " + steph.strftime('%#I:%M %p') + "\n" +
                   "UTC: " + utc.strftime('%#I:%M %p') + "\n" +
                   "Rabi: " + edt.strftime('%#I:%M %p') + "\n")
    
    
# Command for rabi to remind someone
@bot.command()
async def remindme(ctx, time, *, task):
    def convert(time):
        form = ['s', 'm', 'h', 'd']

        time_dict = {"s": 1, "m": 60, "h": 3600, "d": 3600*24}

        days = re.findall(r"(\d+)d", time)
        hours = re.findall(r"(\d+)h", time)
        minutes = re.findall(r"(\d+)m", time)
        seconds = re.findall(r"(\d+)s", time)

        new_time = []

        if len(days) != 0:
            new_time.append(int(days[0])*time_dict['d'])
        if len(hours) != 0:
            new_time.append(int(hours[0])*time_dict['h'])
        if len(minutes) != 0:
            new_time.append(int(minutes[0])*time_dict['m'])
        if len(seconds) != 0:
            new_time.append(int(seconds[0])*time_dict['s'])
        
        return sum(new_time)

    parsed_time = convert(time)

    await ctx.send(f"your reminder for **{task}** has been recorded and i will remind you in **{time}** <:rabikewl:846747935752454155>")
    await asyncio.sleep(parsed_time)
    await ctx.send(f"<:rabiwave:648711649838235658> {ctx.author.mention}, here's your reminder for **{task}**")
    
    
# To listen for maintenance notice in e7-news, then promptly remind friends 5 hrs early to do their gws before maint hits
async def gw_timer(message):
    if "e7-news" in message.channel.name:
        if 'Maintenance Notice' in message.content:
            await message.channel.send("<:rabilurk:836261305916456970>")
            # grab current time
            cur_time = datetime.now()
            # grab current time + 1 day
            day = timedelta(days=1)
            tomorrow = cur_time + day 
            # rabi bot lives in UTC, and maint happens in 3am UTC
            dt3 = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 3, 0 , 0, 0)
            # 5 hrs notice for guild members
            diff = dt3 - cur_time - timedelta(hours=5)
            # which channel to post in 
            gw_channel = discord.utils.get(message.guild.text_channels, name="guild-wars")
            await asyncio.sleep(diff.total_seconds())
            await gw_channel.send("rabi is here to remind everyone there is a maint in 5 hrs, int your attacks soon")
            await gw_channel.send("<:rabifighting:703995623350730812>")
    
    
## Sends an automatic message at regular intervals
##async def background_task():
##    
##    await bot.wait_until_ready()
##    counter = 0
##    channel = bot.get_channel(590177033586475008) # For now it's just rule, may implement adding server IDs to Heroku later
##    
##    ## Check for gw
##    weekday = datetime.datetime.now().weekday()
##    hour = datetime.datetime.now().hour
##    #if (weekday in [0, 2, 4] and hour >= 6) or (weekday in [1, 3, 5] and hour < 6):
##    while not bot.is_closed():
##        counter += 1
##        await channel.send(f'{str(counter)} seconds have passed.')
##        await asyncio.sleep(10)
    

## Background checks
#bot.loop.create_task(background_task())
    

## Run
bot.run(os.environ.get('TOKEN'))
##bot.run(Arabi.TOKEN)
