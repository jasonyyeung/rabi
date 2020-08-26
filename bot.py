## PURPOSE: to shame people

## Imports
import discord
import linecache
import random
import datetime
import mimetypes
import requests
import re
import json
import os
import boto3
from discord.ext import commands
from rabi import Rabi


## Stuff
bot = commands.Bot(command_prefix = 'rabi ')
s3_get = boto3.resource('s3',
                        aws_access_key_id = Rabi.ACCESS_KEY,
                        aws_secret_access_key = Rabi.SECRET_ACCESS_KEY)
s3_put = boto3.client('s3',
                      aws_access_key_id = Rabi.ACCESS_KEY,
                      aws_secret_access_key = Rabi.SECRET_ACCESS_KEY)


@bot.event
async def on_ready():
    await bot.change_presence(status = discord.Status.online, activity = discord.Game('Epic Seven'))
    print('rabi')


@bot.event
async def on_message(message):

    if not message.author.bot: #avoids infinite loops

        ## Misc. commands
        await hi_rabi(message)
        await kill_rabi(message)
        await hit_rabi(message)
        #await ssb_user(message)
        await detect_keywords(message)
        
        await bot.process_commands(message)


## Keyword detected, checks rabi_mood from s3 before sending message
async def rabi_sad(server_id):
    json_content = await get_bucket(f'{server_id}/rabi_sad.json')
    return json_content['status']


## Sends get request, returns dictionary
async def get_bucket(path):
    
    content_object = s3_get.Object('rabi-bucket', path)
    file_content = content_object.get()['Body'].read().decode('utf-8')
    return json.loads(file_content)


## Takes in dictionary, puts json file to bucket
async def put_bucket(file_name, dictionary, server_id):

    with open(file_name, 'w') as fp:
        json.dump(dictionary, fp)

    s3_put.upload_file(file_name, 'rabi-bucket', f'{server_id}/{file_name}')
    os.remove(file_name)
    

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
                if await findWholeWord(keyword, text) and not await rabi_sad(message.guild.id):
                    await message.channel.send(reaction)
                    break


## Finding words in a sentence
async def findWholeWord(w, s):
    return f' {w} ' in f' {s} '


## Special case for rabi and arabi
async def find_rabi(message):

    rabi = False
    rabi_keys = ['ravi', 'rabi']
    arabi = False
    arabi_keys = ['arabi', 'mlravi', 'ml ravi', 'ml rabi', 'mlrabi',
                  'aravi', 'arabi', 'a.rabi', 'a.ravi']
    double_rabi = ["double ravi", "double rabi", "rabis", "ravis"]

    for keyword in double_rabi:
        if await findWholeWord(keyword, message.content.lower() and not await rabi_sad(message.guild.id)):
            await message.channel.send('<:rabi:646666830651326464><:arabi:648411271334461449>')
            return

    for keyword in rabi_keys:
        if await findWholeWord(keyword, message.content.lower() and not await rabi_sad(message.guild.id)):
            rabi = True
            break

    for keyword in arabi_keys:
        if await findWholeWord(keyword, message.content.lower() and not await rabi_sad(message.guild.id)):
            arabi = True
            break

    if rabi and arabi:
        await message.channel.send('<:rabi:646666830651326464><:arabi:648411271334461449>')
        return
        
    if rabi:
        await message.channel.send('<:rabi:646666830651326464>')

    if arabi:
        await message.channel.send('<:arabi:648411271334461449>') 


## Enables reactions
async def hi_rabi(message):
    if message.content.lower() == 'hi rabi' or message.content.lower() == 'hi ravi':
        data = {'status': False}
        await put_bucket('rabi_sad.json', data, message.guild.id)
        await message.channel.send('<:rabiwave:648711649838235658>')


## Disables reactions
async def kill_rabi(message):
    if message.content.lower() == 'kill rabi' or message.content.lower() == 'kill ravi':
        data = {'status': True}
        await put_bucket('rabi_sad.json', data, message.guild.id)
        await message.channel.send('<:rabidrink:665760786462933012>')


## Fun feature, 30% to counter
async def hit_rabi(message):
    if message.content.lower() == 'hit rabi' or message.content.lower() == 'hit ravi':
        if random.random() < 0.3:
            await message.channel.send('COUNTER ATTAC')
            await message.channel.send('<:rabiflame:648713302360326148>')
        else:
            await message.channel.send('<:rabicry:650976531354615819>')
            

## Run
bot.run(Rabi.TOKEN)
