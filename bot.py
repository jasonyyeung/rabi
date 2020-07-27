## PURPOSE: to shame people for using SSB
## Lots of help from Chloe
## Collaboration with Kenny's A. Rabi bot

import discord
import linecache
import random
import datetime
import mimetypes
import requests
import re
import json
import os
from discord.ext import commands

rabi_sad = False
reactions = True
client = commands.Bot(command_prefix = '')

@client.event
async def on_ready():

    ## Moods: [online, idle, dnd] [game, music] (Playing/Listening to)
    mood = "Date A Live: Spirit Pledge - Global"
    await set_mood("online", "game", mood)
    print('rabi')

@client.event
async def on_message(message):

    global rabi_sad
    global reactions
    text = message.content.lower()
    
    ## Will only respond if author is not a bot:
    if not message.author.bot and not rabi_sad:

        ## COMMAND KILL
        if text == 'kill rabi' or text == 'kill rabi':
            await client.change_presence(status = discord.Status.do_not_disturb, activity = discord.Activity(name='sad music',type = discord.ActivityType.listening))
            rabi_sad = True
            
            if str(message.author) == 'umbralla#2608':
                await message.channel.send('<:rabisad:650976531354615819>')
            else:
                await message.channel.send('<:rabirage:652709210022215711>')
                await message.channel.send('**+100 FIGHTING SPIRIT**')
        
        ## COMMAND REGISTER
        ## This feature assumes the txt file is already created
        elif len(text) >= 13 and (text[:13] == 'rabi register' or text[:13] == 'ravi register'):

            ## No input
            if len(text) == 13:
                await message.channel.send('**Usage:** `ravi/rabi register [in-game name]`')

            ## Spaces in input
            elif text.count(' ') > 2:
                await message.channel.send('In-game names cannot contain spaces.')

            else:

                ## Search to see if user is already registered
                file = []
                found = False
                with open('guildies.txt', 'r') as f:
                    file = f.read().splitlines()

                for line in file:
                    if str(message.author.id) in line:
                        await message.channel.send('You are already registered as **' + line.split()[2] + '**.')
                        found = True                

                ## Registration
                if not found:
                    await message.channel.send('You are now registered as **' + message.content[14:] + '**.')
                    
                    ## Rewrite existing lines
                    with open('guildies.txt', 'w') as f:
                        for line in file:
                            f.write(line + '\n')

                        ## Add new line
                        f.write('\n' + str(message.author.id) + ' - ' + message.content[14:] + '\n\n')      

                    ## TO-DO: find a way to attach identification with IGN

        ## COMMAND ADD
        elif len(text) >= 8 and (text[:8] == 'rabi add' or text[:8] == 'ravi add'):

            ## Check if the user exists
            file = []
            user_index = 0
            hero_index = 0
            found = False
            with open('guildies.txt', 'r') as f:
                file = f.read().splitlines()

            for i in range(len(file)):
                if len(file[i]) > 0 and str(message.author.id) == file[i].split()[0]:
                    found = True
                    user_index = i

            ## Check URL
            if not found:
                await message.channel.send('You are not registered yet. To register, use `ravi/rabi register [in-game name]`.')

            else:
                url = ''
                attachments = len(message.attachments)
                urls = await find_url(message.content)
                new_line = ''
                

                ## User is griefing
                if attachments > 0 and len(urls) > 0:
                    if len(await find_url(text)) > 1:
                        await message.channel.send('Am I suppose to pick the links or the image? <:rabidrink:665760786462933012>')
                    else:
                        await message.channel.send('Am I suppose to pick the link or the image? <:rabidrink:665760786462933012>')

                ## User is still griefing
                elif len(urls) > 1:
                    await message.channel.send('Which link should I use? <:rabidrink:665760786462933012>')

                ## Maximum grief
                elif attachments == 0 and len(urls) == 0:
                    await message.channel.send('Please include an image.\n**Usage:** `ravi/rabi add [hero name] [url/attached image]`')
                    
                ## Check for attachments
                elif attachments > 0:

                    if text.count(' ') < 2:
                        await message.channel.send('Please include the hero name.\n**Usage:** `ravi/rabi add [hero name] [url/attached image]`')

                    else:
                        url = message.attachments[0].url
                        new_line = text.split()[2:] + [' - ', url]

                        ## Capitalize every word except URL
                        for i in range(len(new_line) - 1):
                            new_line[i] = new_line[i][0].upper() + new_line[i][1:].lower()

                        new_line = " ".join(new_line)

                ## Check for URL
                else:
                    temp_url = urls[0]

                    if text.count(' ') < 3:
                        await message.channel.send('Please include the hero name.')

                    else:

                        ## Converting imgur links
                        if '/imgur.com/' in temp_url:
                            if await is_url_image(temp_url.replace('/imgur.com/', '/i.imgur.com/') + '.png'):
                                temp_url = temp_url.replace('/imgur.com/', '/i.imgur.com/') + '.png'
                            elif await is_url_image(temp_url.replace('/imgur.com/', '/i.imgur.com/') + '.jpg'):
                                temp_url = temp_url.replace('/imgur.com/', '/i.imgur.com/') + '.jpg'

                        ## Check validity
                        if not (await check_url(temp_url)):
                            await message.channel.send('That is not a valid link. <:rabidrink:665760786462933012>')

                        ## Check image
                        elif not (await is_url_image(temp_url)):
                            await message.channel.send('That is not an image. <:rabidrink:665760786462933012>')

                        ## Actually adding the link
                        else:
                            url = temp_url
                            new_line = text.split()[2:-1] + ['-', url]

                            ## Capitalize every word except URL
                            for i in range(len(new_line) - 1):
                                new_line[i] = new_line[i][0].upper() + new_line[i][1:].lower()

                            new_line = " ".join(new_line)
                        
                ## Adding
                if len(url) > 0:
                    found = False

                    ## Start from the user ID and go down until the next empty line (see if hero exists)
                    while user_index < len(file) and file[user_index] != '':
                        if "".join(new_line.split()[0:-2]) == "".join(file[user_index].split()[0:-2]):
                            found = True
                            hero_index = user_index
                        user_index += 1

                    ## Duplicate found
                    if found:
                        file[hero_index] = new_line
                        await message.channel.send('Your **' + " ".join(new_line.split()[0:-2]) + '** has been updated.')

                    ## New entry
                    else:
                        file.insert(user_index, new_line)
                        await message.channel.send('Your **' + " ".join(new_line.split()[0:-2]) + '** has been added.')

                    ## Rewrite existing lines
                    with open('guildies.txt', 'w') as f:
                        for line in file:
                            f.write(line + '\n')
                    
        ## COMMAND SHOW
        elif len(text) >= 9 and (text[:9] == 'rabi show' or text[:9] == 'ravi show'):

            file = []
            collection =[]
            found = False
            guildie = message.content.split()[2]
            hero = ''
            general = True

            ## User has mentioned a hero
            if len(text.split()) > 3:

                general = False
                hero = text.split()[3:]
                image_url = ''

                ## Capitalize hero
                for i in range(len(hero)):
                    hero[i] = hero[i][0].upper() + hero[i][1:].lower()
                hero = " ".join(hero)

            ## Search for guildie
            index = 0
            with open('guildies.txt', 'r') as f:
                file = f.read().splitlines()
                
            for i in range(len(file)):
                if len(file[i]) > 0 and guildie == (file[i].split()[2]).lower():
                    found = True
                    index = i
                    guildie = file[i].split()[2]

            if not found:
                await message.channel.send('Could not find ' + guildie + '.')
                
            ## Search for hero
            else:
                found = False

                ## Start from the user ID and go down until the next empty line (see if hero exists)
                while index < len(file) and file[index] != '':
                    if len(file[index]) > 0 and hero == " ".join(file[index].split()[0:-2]):
                        found = True
                        image_url = file[index].split()[-1]
                    index += 1

                    ## Track all heroes we go through
                    if index < len(file) and file[index] != '':
                        collection.append(" ".join(file[index].split()[0:-2]))

                ## Hero found
                if found:
                    embed = discord.Embed(title = guildie + ' - ' + hero, colour = discord.Colour.blue())
                    embed.set_image(url = image_url)
                    await message.channel.send(embed = embed)

                ## Provide a list of heroes
                else:

                    ## Guildie has no heroes
                    if len(collection) == 0:
                        await message.channel.send(guildie + ' currently has no heroes saved.')

                    ## Provide available heroes
                    else:

                        if not general:
                            reply = 'Could not find ' + hero + '. Here are all the heroes available:\n*'
                        else:
                            reply = 'Here are all the heroes available:\n*'
                            
                        for name in collection:
                            reply += name + ', '
                        await message.channel.send(reply[:-2] + '*')

        ## COMMAND REMOVE
        elif len(text) >= 11 and (text[:11] == 'rabi remove' or text[:11] == 'ravi remove'):

            ## Usage
            if text.count(' ') < 2:
                await message.channel.send('State the name of the hero you want removed.\n**Usage:** `ravi/rabi remove [hero name]`')

            # Find user
            else:
                file = []
                index = 0
                found = False
                hero = text.split()[2:]

                ## Capitalize hero
                for i in range(len(hero)):
                    hero[i] = hero[i][0].upper() + hero[i][1:].lower()
                hero = " ".join(hero)
                
                with open('guildies.txt', 'r') as f:
                    file = f.read().splitlines()

                for i in range(len(file)):
                    if len(file[i]) > 0 and str(message.author.id) == file[i].split()[0]:
                        found = True
                        index = i

                ## Find hero
                if not found:
                    await message.channel.send('You are not registered yet. To register, use `ravi/rabi register [in-game name]`.')

                else:
                    found = False
                    collection =[]

                    ## Start from the user ID and go down until the next empty line (see if hero exists)
                    while index < len(file) and file[index] != '':
                        if len(file[index]) > 0 and hero == " ".join(file[index].split()[0:-2]):
                            found = True
                            file.pop(index)
                            await message.channel.send('**' + hero + '** has been removed from your collection.')

                            ## Rewrite existing lines
                            with open('guildies.txt', 'w') as f:
                                for line in file:
                                    f.write(line + '\n')
                            
                        index += 1

                        ## Track all heroes we go through
                        if index < len(file) and file[index] != '':
                            collection.append(" ".join(file[index].split()[0:-2]))

                    if not found:
                        
                        ## No heroes to remove
                        if len(collection) == 0:
                            await message.channel.send('You have no heroes to remove.')

                        else:
                            reply = 'Could not find ' + hero + '. Here are all the heroes available:\n*'
                            for name in collection:
                                reply += name + ', '
                            await message.channel.send(reply[:-2] + '*')
            
        ## DISABLING/ENABLING REACTIONS
        elif text == 'rabi disable reactions' or text == 'ravi disable reactions':
            reactions = False
            await message.channel.send('ok')
        elif text == 'rabi enable reactions' or text == 'ravi enable reactions':
            await message.channel.send('ok')
            reactions = True        

        ## COMMAND SSBUSER?
        elif len(text) >= 9 and text[:9] == 'ssbuser? ':
            members = message.guild.members
            tagged = await find_member(message.content[9:].lower(), members)

            if str(tagged) == 'None':
                await message.channel.send('<:rabiwut:656819778459140116>')
                await message.channel.send('Rabi does not know who ' + message.content[9:] + ' is.')

            else:                                           
                await message.channel.send(tagged.mention + ' is a fucking ssb user.')

        ## COMMAND HI RABI
        elif text == 'hi rabi' or text == 'hi ravi':
            await message.channel.send('<:rabiwave:648711649838235658>')

        ## COMMAND CRAFT
        elif len(text) >= 10 and (text[:10] == 'rabi craft' or text[:10] == 'ravi craft'):

            ## for steph
            if text[13:].lower() == "boot":
                text = text[:13] + "boots"
            
            ## Error checking before Rabi crafts
            if (await check_craft(text)):
                await craft_gear(message, text)
                
            else:
                await message.channel.send('<:rabiwut:656819778459140116>')
                embed = discord.Embed(title = 'Usage', colour = discord.Colour.blue())
                embed.add_field(
                    name = 'rabi/ravi craft [w, g, b, a] [weapon, helm, chest, neck, ring, boots]',
                    value = 'eg. "rabi craft g neck" will craft a lv. 85 necklace from Golem 11\n\nRabi will craft a new piece of gear and replace your previous one.',
                    inline = False
                    )
                await message.channel.send(embed = embed)

        ## COMMAND ROLL
        elif text == 'rabi roll' or text == 'ravi roll':

            ## Error checking
            response = await check_roll(message)
            if isinstance(response, str):
                await message.channel.send('<:rabiwut:656819778459140116>')
                await message.channel.send(response)
            else:
                await roll_gear(message)

        ## COMMAND STATS
        elif text == 'rabi stats' or text == 'ravi stats':

            if response == "Rabi has no gear to roll.":
                await message.channel.send('<:rabiwut:656819778459140116>')
                await message.channel.send("You didn't craft anything yet.")
                
            else:    
                await user_stats(message)

        ## COMMAND GW
        elif text == 'rabi gw' or text == 'ravi gw':

            ## Make sure its gw day
            weekday = datetime.datetime.now().weekday()
            hour = datetime.datetime.now().hour
            if (weekday in [0, 2, 4] and hour >= 6) or (weekday in [1, 3, 5] and hour < 6):
                
                ## Find all channels with members in it
                channels = []
                for c in message.guild.channels:
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
                    await message.channel.send(dialogue)

                else:
                    await message.channel.send('No one wants to do gw right now.')
                    await message.channel.send('<:rabisad:650976531354615819>')

            else:
                await message.channel.send("There's no gw today.")
                await message.channel.send("<:rabidrink:665760786462933012>")

        ## COMMAND HUNT
        elif len(text) >= 9 and (text[:9] == 'rabi hunt' or text[:9] == 'ravi hunt'):

            ## INFO
            if len(text) == 14 and (text == 'rabi hunt info' or text == 'rabi hunt info'):

                dialogue = ('** Assumptions:**\n' +
                            '- Range for crafting mats are 10-14, 12-17, and 15-19 for hunts 11 to 13 respectively\n' +
                            '- 16 seconds are added to your run to simulate the transition between auto repeats\n' +
                            '- You are the unluckiest person in the game and you will never get the 50 reforge mat drop\n' +
                            '- You are also never getting the Manifestation Stone drop have fun\n\n' +
                            
                            '**For GM Buffs (+50% hunt material events):**\n' +
                            'You should be using your leifs for these events for max efficiency and running the hunt that clears the fastest. ' +
                            'This will most likely be your hunt 11 but if your hunt 12/13 clears around the same time, do those instead.\n\n' +
                            
                            '**For Dailies/General Use:**\n' +
                            'The goal of this feature is to calculate how much energy you are wasting for hunt 11 and time you are wasting for ' +
                            'hunt 12/13. You should aim to clear hunt 12 as fast as you can so that the time wasted in hunt 12 is acceptable and ' +
                            'repeat for hunt 13 (though an acceptable clear time will not be possible for most players). If you only care about ' +
                            'maximizing your material/energy gain, do the highest hunt you can.')
                await message.channel.send(dialogue)

            ## Error checking
            elif not (await check_time(text[10:])):
                await message.channel.send('<:rabiwut:656819778459140116>')
                embed = discord.Embed(title = 'Usage', colour = discord.Colour.blue())
                embed.add_field(
                    name = 'rabi/ravi hunt [hunt 11 time] [hunt 12 time] [hunt 13 time] [condition]',
                    value = ('eg. "rabi hunt 0:57 4:48 7:35 24"\n\n' +
                             'Rabi will show you how many items you get for each hunt after [hours] hours of farming on auto.\n' +
                             'If you do not have a time for a certain hunt, you may put "0" or "0:00".'),
                    inline = False
                    )
                await message.channel.send(embed = embed)

            ## Calculations: runs, gold, mats, energy spent
            else:
                times = text[10:].split()
                hours = float(times[3])
                times = times[:3]
                gold_values = [32292, 33396, 36954]
                mat1_values = [6, 7.25, 8.5]
                mat2_values = [0.5, 1, 1.5]
                energy_costs = [20, 20, 22]
                runs = []

                ## Time conversion
                for time in times:

                    numbers = time.replace(":", " ").split() #[0, 23]
                    seconds = 0

                    for i in range(len(numbers) - 1, -1, -1):
                        seconds += int(numbers[i]) * (60 ** (len(numbers) - i - 1))

                    if seconds == 0:
                        runs.append(0)
                    else:
                        runs.append(int(hours * 3600 / (seconds + 16)))

                ## Display author
                author = str(message.author.nick)
                if author == 'None':
                    author = message.author.name

                ## Display
                embed = discord.Embed(title = 'In ' + str(hours) + ' hours, you get:', colour = discord.Colour.blue())

                for i in range(3):
                    embed.add_field(
                        name = 'Hunt ' + str(11 + i),
                        value = ('**Runs:** ' + str(runs[i]) + '\n' + 
                                 '**Gold:** ' + f'{(gold_values[i] * runs[i]):,}' + '\n' + 
                                 '**Crafting Materials:** ' + str(mat1_values[i] * runs[i]) + '\n' +
                                 '**Reforge Materials:** ' + str(mat2_values[i] * runs[i]) + '\n' +
                                 '**Energy Spent:** ' + str(energy_costs[i] * runs[i]) + '(' + str(energy_costs[i] * runs[i] / 80) + ' leifs)\n'),
                        inline = True
                        )

                ## Post buff
                for i in range(3):
                    embed.add_field(
                        name = 'Post Buff',
                        value = ('**Crafting Materials:** ' + str(mat1_values[i] * 2 * runs[i]) + '\n' +
                                 '**Reforge Materials:** ' + str(mat2_values[i] * 2 * runs[i]) + '\n'),
                        inline = True
                        )
                
                embed.set_author(name = author, icon_url = message.author.avatar_url)
                embed.set_footer(text = 'Type "ravi/rabi hunt info" for more details of this feature')
                await message.channel.send(embed = embed)
                
        
        ## OTHER KEYWORDS        
        elif reactions:
            if 'ssb' in text:
                await message.channel.send('fucking ssb users')

            avildred = ['avild', 'avildred', 'a. vildred', 'a. vild', 'mlvildred', 'mlvild', 'ml vildred', 'ml vild', 'arby']
            if (await find_hero(text, avildred)):
                await message.channel.send('fucking avildred users')

            if 'basar' in text:
                await message.channel.send('fucking basar users')

            if 'dcorvus' in text or 'dark corvus' in text or 'd corvus' in text:
                await message.channel.send('fucking dcorvus users')

            if '<@&572610147604758528>' in text or 'gw' in text or 'gvg' in text:
                await message.channel.send('i love gw')

            if text == "nice":
                
                ## Check that user profile exists, creates one if non-existent
                open('gear/nice.txt', 'a')

                with open('gear/nice.txt', 'r') as f:
                    line = f.readlines()

                    if not line:
                        await message.channel.send('nice')

                with open('gear/nice.txt', 'w') as f:
                    f.write('nice')

            ## Outputs an emote response
            if (await find_double_rabi(text)):
                await message.channel.send('<:rabi:646666830651326464><:arabi:648411271334461449>')
                
            elif (await find_rabi(text)):
                await message.channel.send('<:rabi:646666830651326464>')

            elif (await find_arabi(text)):
                await message.channel.send('<:arabi:648411271334461449>')

            ## Outputs an image response
            if 'attack mont' in text:
                await message.channel.send(file = discord.File('attackmont.png'))

            if 'cant see' in text:
                await message.channel.send(file = discord.File('cantsee.png'))

            if '+15' in text:
                await message.channel.send(file = discord.File('+15.jpg'))

    ## Reactivates bot
    elif not message.author.bot and rabi_sad and (text == 'hi rabi' or text == 'hi ravi'):
        
        await message.channel.send('<:rabiwave:648711649838235658>')
        await on_ready()
        rabi_sad = False

## METHODS ----------------------------------------------------------------------------------------------------

## Search through a list of members
async def find_member(text, users):
    if (len(text) == 0):
        return None
        
    text = text.lower()
    for user in users:

        # Check for a partial match
        if (not str(user.nick) == 'None' and text in user.nick.lower()) or (text in user.name.lower()):
            return user
        
    return None

## Find Rabi
async def find_rabi(text):

    if 'rabi' in text or 'ravi' in text:
        counter = 0
        index = -2
        for word in text.split():
            if word == 'a.' or word == 'ml':
                index = counter
            
            elif (await find_hero_ex(word, 'rabi', 'ravi')) and not index == counter - 1:
                return True

            counter += 1
        
    return False

## Find A. Rabi
async def find_arabi(text):

    if 'rabi' in text or 'ravi' in text:
        arabi = ['a. rabi', 'a. ravi', 'a.rabi', 'a.ravi', 'ml rabi', 'ml ravi', 'mlrabi', 'mlravi']

        if (await find_hero(text, arabi)) or (await find_hero_ex(text, 'arabi', 'aravi')):
            return True
        
    return False

## Find hero in message
async def find_hero(text, keywords):

    for word in keywords:
        if word in text:
            return True
    
    return False

## Find hero exactly in message (both rabis will use this)
async def find_hero_ex(text, n1, n2):

    length = len(n1)
    for word in text.split():
        if len(word) == length and (word[:length] == n1 or word[:length] == n2):
            return True

    return False

## Returns true if text contains both Ravi's
async def find_double_rabi(text):
    if '<:rabisad:661786772723990529>' in text:
        return False
    elif (await find_rabi(text)) and (await find_arabi(text)):
        return True
    elif 'double rabi' in text or 'double ravi' in text:
        return True
    elif 'rabis' in text or 'ravis' in text or 'rabi\'s' in text or 'ravi\'s' in text:
        return True
    return False

## Sets the mood like what do you want
async def set_mood(status, activity, message):

    if status == "online":
        status = discord.Status.online
    elif status == "idle":
        status = discord.Status.idle
    elif status == "dnd":
        status = discord.Status.do_not_disturb

    if activity == "game":
        activity = discord.Game(message)
    elif activity == "music":
        activity = discord.Activity(message, type = discord.ActivityType.listening)

    await client.change_presence(status = status, activity = activity)

## Error-checking for crafting
async def check_craft(text):

    ## check length
    if len(text.split()) != 4:
        return False

    ## parameters
    hunts = ['w', 'g', 'b', 'a']
    pieces = ['weapon', 'helm', 'chest', 'neck', 'ring', 'boots']

    if text[11:12] in hunts and text[13:] in pieces:
        return True
    
    return False

## Crafting:
async def craft_gear(message, text):

    ## List of strings containing properties of each hunt and gear
    pieces = ['weapon', 'helm', 'chest', 'neck', 'ring', 'boots']
    piece_index = pieces.index(text[13:])
    piece_names = ['Weapon', 'Helmet', 'Armor', 'Necklace', 'Ring', 'Boots']
    mat_cost = [42, 42, 42, 55, 55, 42]
    gold_cost = [42000, 42000, 42000, 54600, 54600, 42000]
    
    exp_rates = [1, 1.25, 1.5, 2, 3, 4, 5.5, 7, 8.5, 10.5, 13.5, 17, 21, 26, 34]

    hunts = ['w', 'g', 'b', 'a']
    hunt_index = hunts.index(text[11:12])
    full_names = [['Abyss Drake Sword', 'Abyss Drake Mask', 'Abyss Drake Hide Tunic',
                   'Abyss Blade Necklace', 'Awakened Dragon Gem', 'Abyss Drake Boots'],
                  ['Dark Steel Saber', 'Dark Steel Helm', 'Dark Steel Armor',
                   'Dark Steel Warmer', 'Dark Steel Gauntlet', 'Dark Steel Boots'],
                  ['Hellish Essence Orb', 'Hellish Essence Crown', 'Hellish Essence Robe',
                   'Obsidian Amulet', 'Obsidian Ring', 'Hellish Essence Treads'],
                  ['Indomitable Spider Mace', 'Indomitable Spider Helm', 'Indomitable Spider Breastplate',
                   'Indomitable Spider Pendant', 'Indomitable Spider Ring', 'Indomitable Spider Boots']]
    sets = [['Critical Set', 'Hit Set', 'Speed Set'],
            ['Attack Set', 'Health Set', 'Defense Set'],
            ['Resist Set', 'Destruction Set', 'Lifesteal Set', 'Counter Set'],
            ['Unity Set', 'Immunity Set', 'Rage Set']]
    mainstats = ['Attack: 100', 'Health: 540', 'Defense: 60']
    
    new = False
    exp = 0
    gold = 0
    mats = [0, 0, 0, 0]
    base = 0
    tier = 0

    ## Check that user profile exists, creates one if non-existent
    open('gear/' + str(message.author) + '.txt', 'a')

    ## Find previous stats before resetting
    with open('gear/' + str(message.author) + '.txt', 'r') as f:
        line = f.readlines()

        if not line:
            new = True
        else:
            ## exp = current exp + rate sum using base exp(colour) and enhance level
            gold = int(line[1].split()[4])
            for i in range(4):
                mats[i] = int(line[2].split()[i + 4])
            base = int(line[4].split()[3])
            level = int(line[7].split()[3])
            exp = int(line[0].split()[4]) + await add_exp(base, level, exp_rates)
            
    ## Writing
    with open('gear/' + str(message.author) + '.txt', 'w') as f:
        if new:
            f.write('1. exp spent = 0\n')
        else:
            f.write('1. exp spent = ' + str(exp) + '\n')

        f.write('2. crafting gold = ' + str(gold + gold_cost[piece_index]) + '\n')
        f.write('3. crafting mats = ')
        for i in range(4):
            if i == hunt_index:
                f.write(str(mats[i] + mat_cost[piece_index]) + ' ')
            else:
                f.write(str(mats[i]) + ' ')
        f.write('\n')
                
        ## Colour 35 53 12
        grade = 100 * random.random() + 1
        if grade <= 12:
            f.write('4. tier = Epic\n')
            f.write('5. base = 525\n')
            base = 525
            tier = 4
        elif grade <= 47:
            f.write('4. tier = Rare\n')
            f.write('5. base = 420\n')
            base = 420
            tier = 2
        else:
            f.write('4. tier = Heroic\n')
            f.write('5. base = 473\n')
            base = 473
            tier = 3

        f.write('6. type = ' + piece_names[pieces.index(text[13:])] + '\n')
        f.write('7. name = ' + full_names[hunt_index][piece_index] + '\n')
        f.write('8. level = 0\n')

        ## Assign gear a set
        f.write('9. set = ' + random.choice(sets[hunt_index]) + '\n')

        ## Mainstat
        mainstat = ''
        if piece_index <= 2:
            mainstat = mainstats[piece_index]
        else:
            mainstat = await roll_main(piece_index)
            
        f.write('10. main = ' + mainstat + '\n')

        ## Substats
        current_subs = []
        for i in range(tier):
            rolled_sub = await roll_subs(piece_index, mainstat.split()[0] + ' ', current_subs, 'craft')
            current_subs.append(rolled_sub)
            f.write(rolled_sub + '\n')

        ## Clear lines lol
        f.write(' \n')
        f.write(' \n')

    ## Display
    await display_gear(message)
    return
        
## Add exp
async def add_exp(base, level, rates):
    total_exp = 0
    for i in range(level):
        total_exp += rates[i] * base
        i += 1
    return int(total_exp)

## Roll mainstat, return as str
async def roll_main(piece_index):
    if piece_index == 3:
        return random.choice(['%Critical_Hit_Chance: 11', '%Critical_Hit_Damage: 13',
                              'Attack: 100', '%Attack: 12', 'Health: 540', '%Health: 12',
                              'Defence: 60', '%Defence: 12'])
    elif piece_index == 4:
        return random.choice(['%Effectiveness: 12', '%Effect_Resistance: 12',
                              'Attack: 100', '%Attack: 12', 'Health: 540', '%Health: 12',
                              'Defence: 60', '%Defence: 12'])
    elif piece_index == 5:
        return random.choice(['Speed: 8',
                              'Attack: 100', '%Attack: 12', 'Health: 540', '%Health: 12',
                              'Defence: 60', '%Defence: 12'])

## generate 1 substat since it will gain 1 at a time later on when rolling
async def roll_subs(piece_index, mainstat, current_subs, mode):

    ## Pool of substats
    sub_pool = ['Attack: ', '%Attack: ', 'Health: ', '%Health: ', 'Defence: ', '%Defence: ', 'Speed: ',
                '%Critical_Hit_Chance: ', '%Critical_Hit_Damage: ', '%Effectiveness: ', '%Effect_Resistance: ']
    bounds = [[35, 11], [4, 5], [150, 31], [4, 5], [25, 16], [4, 5], [1, 4],
              [3, 3], [3, 5], [4, 5], [4, 5]]
    sub_index = -1

    if mode == 'craft':
        
        ## LEFT SIDES
        if piece_index <= 2:
            
            left_subs = [[1, 2, 3, 6, 7, 8, 9, 10],
                         [0, 1, 3, 4, 5, 6, 7, 8, 9, 10],
                         [2, 3, 5, 6, 7, 8, 9, 10]]
            
            ## remove dupe subs
            for sub in current_subs:
                remove_index = sub_pool.index(sub.split()[0] + ' ')
                left_subs[piece_index].remove(remove_index)

            ## create the sub
            sub_index = random.choice(left_subs[piece_index])

        ## RIGHT SIDES
        else:

            ## remove mainstat
            right_subs = list(range(0, 11))
            remove_index = sub_pool.index(mainstat.split()[0] + ' ')
            right_subs.remove(remove_index)
            
            ## store available subs for piece then removing dupes
            for sub in current_subs:
                remove_index = sub_pool.index(sub.split()[0] + ' ')
                right_subs.remove(remove_index)

            ## create the sub
            sub_index = random.choice(right_subs)

        value = int(bounds[sub_index][1] * random.random() + bounds[sub_index][0])
        return sub_pool[sub_index] + str(value)

    ## Increase existing stats
    else:
        stat_up = int(len(current_subs) * random.random())
        index = sub_pool.index(current_subs[stat_up].split()[0] + ' ')
        new_sub = int(bounds[index][1] * random.random() + bounds[index][0] + int(current_subs[stat_up].split()[1]))
        del current_subs[stat_up]
        current_subs.insert(stat_up, sub_pool[index] + str(new_sub))
        return current_subs
        

## Display gear (for both crafting and rolling)
async def display_gear(message):
    with open('gear/' + str(message.author) + '.txt', 'r') as f:
        line = f.readlines()

        sets = ['Critical Set', 'Hit Set', 'Speed Set', 'Attack Set', 'Health Set', 'Defense Set',
                'Resist Set', 'Destruction Set', 'Lifesteal Set', 'Counter Set',
                'Unity Set', 'Immunity Set', 'Rage Set']
        images = ['https://epic7x.com/wp-content/themes/epic-seven/assets/img/Crit%20Rate-set.png',
                  'https://epic7x.com/wp-content/themes/epic-seven/assets/img/Hit%20Rate-set.png',
                  'https://epic7x.com/wp-content/themes/epic-seven/assets/img/Speed-set.png',
                  'https://epic7x.com/wp-content/themes/epic-seven/assets/img/Atk-set.png',
                  'https://epic7x.com/wp-content/themes/epic-seven/assets/img/Hp-set.png',
                  'https://epic7x.com/wp-content/themes/epic-seven/assets/img/Def-set.png',
                  'https://epic7x.com/wp-content/themes/epic-seven/assets/img/Resist-set.png',
                  'https://epic7x.com/wp-content/themes/epic-seven/assets/img/Destruction-set.png',
                  'https://epic7x.com/wp-content/themes/epic-seven/assets/img/Lifesteal-set.png',
                  'https://epic7x.com/wp-content/themes/epic-seven/assets/img/Counter-set.png',
                  'https://epic7x.com/wp-content/themes/epic-seven/assets/img/Unity-set.png',
                  'https://epic7x.com/wp-content/themes/epic-seven/assets/img/Immunity-set.png',
                  'https://epic7x.com/wp-content/themes/epic-seven/assets/img/Rage-set.png']

        ## Display Colour
        gear_bg = ''
        tier = 0
        level = int(line[7].split()[3])

        if line[3].split()[3] == 'Rare':
            gear_bg = discord.Colour.blue()
            if level >= 12:
                tier = 4
            elif level >= 9:
                tier = 3
            else:
                tier = 2
        elif line[3].split()[3] == 'Heroic':
            gear_bg = discord.Colour.purple()
            if level >= 12:
                tier = 4
            else:
                tier = 3
        else:
            gear_bg = discord.Colour.red()
            tier = 4

        ## Display author
        author = str(message.author.nick)
        if author == 'None':
            author = message.author.name

        ## Store subs
        subs = '\n\n'
        for i in range(tier):
            subs += await display_stat(line[10 + i], 'sub', level) + '\n'

        ## DISPLAY
        display_level = ''
        if level != 0:
            display_level = ' (+' + str(level) + ')'
        embed = discord.Embed(
            title = line[6][10:len(line[6]) - 1] + display_level,
            colour = gear_bg)
        
        embed.add_field(
            name = line[3][10:len(line[3]) - 1] + ' ' + line[5][10:],
            value = await display_stat(line[9][11:], 'main', level) + subs,
            inline = True
            )
        embed.add_field(
            name = 'Set:',
            value = line[8][9:],
            inline = True)

        embed.set_footer(text = 'Options: rabi craft | rabi roll | rabi stats')
        embed.set_author(name = author, icon_url = message.author.avatar_url)
        embed.set_thumbnail(url = images[sets.index(line[8][9:len(line[8]) - 1])])
        await message.channel.send(embed = embed)
    

## Format stats:
async def display_stat(stat, stat_type, level):

    stat = stat.split()
    mainstat_ratio = [1, 1.6, 2.2, 2.8, 3.6, 5]
    
    value = str(int(int(stat[1]) * mainstat_ratio[int(level / 3)]))
    if stat_type == 'main':
        if stat[0][0:1] == '%':
            return '**' + stat[0][1:].replace('_', ' ') + '** ***' + value + '%***'
        else:
            return '**' + stat[0].replace('_', ' ') + '** ***' + value + '***'
    else:
        if stat[0][0:1] == '%':
            return stat[0][1:].replace('_', ' ') + ' *' + stat[1] + '%*'
        else:
            return stat[0].replace('_', ' ') + ' *' + stat[1] + '*'

## Check that file exists
async def check_roll(message):

    ## Check that user profile exists, creates one if non-existent
    open('gear/' + str(message.author) + '.txt', 'a')

    ## Find previous stats before resetting
    with open('gear/' + str(message.author) + '.txt', 'r') as f:
        line = f.readlines()
        
        if not line:
            return 'Rabi has no gear to roll.'
        
        elif line[7].split()[3] == '15':
            return 'Rabi can\'t roll that anymore.'
        
    return True


## Rolling
async def roll_gear(message):

    line = []
    
    with open('gear/' + str(message.author) + '.txt', 'r') as f:
        line = f.readlines()

    with open('gear/' + str(message.author) + '.txt', 'w') as f:
        for i in range(7):
            f.write(line[i])

        ## update level
        level = int(line[7].split()[3]) + 3
        f.write('8. level = ' + str(level) + '\n')
        f.write(line[8])
        f.write(line[9])

        ## to roll, we need to know: piece_index, mainstat, current_subs, mode
        pieces = ['Weapon', 'Helmet', 'Armor', 'Necklace', 'Ring', 'Boots']
        piece_index = piece_index = pieces.index(line[5].split()[3])
        mainstat = line[9][11:]

        tier_name = line[3].split()[3]
        add = False

        ## find the number of subs
        if tier_name == 'Rare':
            if level >= 15:
                tier = 4
            elif level >= 12:
                tier = 3
            else:
                tier = 2 
        elif tier_name == 'Heroic':
            if level >= 15:
                tier = 4
            else:
                tier = 3
        else:
            tier = 4

        ## Get current subs
        current_subs = []
        for i in range(tier):
            current_subs.append(line[10 + i][0:len(line[10 + i]) - 1])

        ## New stat
        if (tier_name == 'Rare' and (level == 9 or level == 12)) or (tier_name == 'Heroic' and level == 12):
            for i in range(len(current_subs)):
                f.write(current_subs[i] + '\n')
            f.write(await roll_subs(piece_index, mainstat, current_subs, 'craft') + '\n')

        ## Current stat goes up
        else:
            current_subs = await roll_subs(piece_index, mainstat, current_subs, 'roll')
            for i in range(len(current_subs)):
                f.write(current_subs[i] + '\n')
        
    ## Display
    await display_gear(message)
    return

## User stats
async def user_stats(message):

    author = str(message.author.nick)
    if author == 'None':
        author = message.author.name
    
    with open('gear/' + str(message.author) + '.txt', 'r') as f:
        line = f.readlines()

        base = int(line[4].split()[3])
        level = int(line[7].split()[3])
        exp_rates = [1, 1.25, 1.5, 2, 3, 4, 5.5, 7, 8.5, 10.5, 13.5, 17, 21, 26, 34]
        current_exp = await add_exp(base, level, exp_rates)
        exp = int(line[0][15:-1]) + current_exp 
        roll_gold = int(exp * 10.3636364)
        mats = line[2][19:].split()
        
        ## DISPLAY
        l1 = "**EXP Spent: **" + '{:,}'.format(exp) + " (around {0} epic charms)".format(str(exp // 13500)) + "\n"
        l2 = "**Gold Spent (Crafting): **" + '{:,}'.format(int(line[1][19:-1])) + "\n"
        l3 = "**Gold Spent (Rolling): **" + '{:,}'.format(roll_gold) + "\n\n"
        
        l4 = "**Abyss Drake Claws: **" + '{:,}'.format(int(mats[0])) + "\n"
        l5 = "**Dark Steel: **" + '{:,}'.format(int(mats[1])) + "\n"
        l6 = "**Hellish Essence: **" + '{:,}'.format(int(mats[2])) + "\n"
        l7 = "**Altus Anak Shells: **" + '{:,}'.format(int(mats[3]))
        
        embed = discord.Embed(title = "Gear Rolling Stats",
                              description = l1 + l2 + l3 + l4 + l5 + l6 + l7)

        embed.set_footer(text = 'Options: rabi craft | rabi roll | rabi stats')
        embed.set_author(name = author, icon_url = message.author.avatar_url)
        embed.set_thumbnail(url = "https://assets.epicsevendb.com/item/gold.png")
        await message.channel.send(embed = embed)

## Check for valid timestamps
async def check_time(text):

    times = text.split() ## [0:59, 1:34, 1:21, 24]

    ## Check for 4 entries
    if not len(times) == 4:
        return False

    ## Timestamps
    for i in range(3):
        run = times[i].replace(":", " ").split() ## should look like this

        for num in run:
            if (not num.isdigit()) or not (0 <= int(num) < 60):
                return False

    ## Hours
    if (not times[3].replace(".", "").isdigit()) or (float(times[3]) < 0):
        return False

    return True

## Check for valid image links
async def is_url_image(image_url):
   image_formats = ("image/png", "image/jpeg", "image/jpg")
   r = requests.head(image_url)
   if r.headers.get("content-type") in image_formats:
      return True
   return False

async def check_url(url):
    try:

        response = requests.get(url)

        return True

    except Exception:

        return False

async def is_image_and_ready(url):
    return await is_url_image(url) and await check_url(url)

## Find URLs in a string
async def find_url(string):

    # findall() has been used  
    # with valid conditions for urls in string 
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex,string)       
    return [x[0] for x in url] 

## I hate my entire guild
##myjsonfile = open('config.json', 'r')
##data = myjsonfile.read()
##myjsonfile.close()
##config = json.loads(data)
##client.run(config['token'])

client.run(str(os.environ.get('TOKEN')))



