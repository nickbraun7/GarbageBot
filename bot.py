#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random, string, datetime, time

import discord, asyncio
import youtube_dl
from discord.ext import commands

import load, update

update.update()
print("Files Have Been Updated")

DiscordToken = load.token()

mDict = load.memes() #load dictionary of memes
sList = load.stops() #load list of stops

client = commands.Bot(command_prefix='>')
client.remove_command("help") #remove help to add custom help command
    
@client.event
async def on_ready():
    print("Garbage Bot Operational")

    global PlayFlag, voice, queue_list
    PlayFlag = False #flag to keep track if the bot is playing or not
    voice = False #current connceted voice channel
    queue_list = [] #list of memes in the queue

    await client.change_presence(status=discord.Status.online, activity=discord.Game("Spiting Meme's since 1976! | "))

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(":stop_sign: command not found")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(":stop_sign: meme required")
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(":stop_sign: Aye do you have a license for that? Try again after " + await convert(error.retry_after) + ".")
    raise error

@client.command()
async def porn(ctx): #send user a stop meme in a direct message
    channel = await ctx.author.create_dm()
    await channel.send(random.choice(sList))

@client.command()
async def help(ctx):
    embed = discord.Embed()

    embed.set_author(name="Garbage Man")

    embed.add_field(
        name=">catalog",
        value="list all psible memes",
        inline=False
        )

    embed.add_field(
        name=">play <meme>",
        value="play selected meme",
        inline=False
        )

    embed.add_field(
        name=">garbage",
        value="play random meme",
        inline=False
        )

    embed.add_field(
        name=">suggest <text suggest (youtube link prefered)>",
        value="suggest a meme to add to the bot",
        inline=False
    )

    embed.add_field(
        name=">leave",
        value="-",
        inline=False
        )

    embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
    await ctx.send(embed=embed)

@client.command()
async def catalog(ctx): #print a catalog of memes in the database
    embed = discord.Embed()
    embed.set_author(name="Garbage Rat")

    for letter in string.ascii_lowercase:
        embed.add_field(
            name=letter.upper() + ":",
            value=":arrow_forward: " + ", ".join(mDict[letter]),
            inline=False
            )
    
    await ctx.send(embed=embed, delete_after=120)

@client.command()
@commands.cooldown(1, 1800, commands.BucketType.user)
async def play(ctx, *, arg):
    global queue_lit, PlayFlag

    meme = arg.lower()

    if meme not in mDict[clip[0]]:
        await ctx.send(":stop_sign: **ERROR 404**")
        play.reset_cooldown(ctx)
    elif not ctx.author.voice:
        await ctx.send(":stop_sign: **You aren't in a Voice Channel**") 
        garbage.reset_cooldown(ctx)
    elif PlayFlag:
        await ctx.send(":arrows_counterclockwise: **Queued: **" + meme)
        queue_list.append([ctx.author.voice.channel, arg])
    else:
        await ctx.send(":white_check_mark: **Playing: **" + meme)

        queue_list.append([ctx.author.voice.channel, meme])
        await play_meme()

@client.command()
@commands.cooldown(1, 1800, commands.BucketType.user)
async def garbage(ctx):
    global queue_list, PlayFlag

    ls = []
    for key in mDict:
        ls.extend(mDict[key])

    arg = random.choice(ls)

    if not ctx.author.voice:
        await ctx.send(":stop_sign: **You aren't in a Voice Channel**") 
        garbage.reset_cooldown(ctx)
    elif PlayFlag: 
        await ctx.send(":arrows_counterclockwise: **Queued: **" + arg)
        queue_list.append([ctx.author.voice.channel, arg])
    else:
        await ctx.send(":white_check_mark: **Garbage Selected**: " + arg)

        queue_list.append([ctx.author.voice.channel, arg])
        await play_meme()

@client.command()
async def suggest(ctx, *args): #store suggestions in seperate files
    with open("./suggestion/" + str(datetime.datetime.now()) + " - " + ctx.author.name + ".txt", "w+") as filehandler:
        for arg in args:
            filehandler.write(arg + " ")
        filehandler.write("\n")
    await ctx.send("**Thank you for the Garbage!**")

@client.command()
async def leave(ctx):
    global voice

    if voice:
        await voice.disconnect()
        voice = False
    else:
        await ctx.send(":stop_sign: **Currently not Conncted to Voice Channel**")

async def convert(secs):
    min, sec = divmod(secs, 60)
    hour, min = divmod(min, 60)
    return "%02d:%02d" % (min, sec)

async def play_meme():
    global queue_list, voice, PlayFlag

    channel = queue_list[0][0]
    meme = queue_list[0][1]
    queue_list.pop(0)

    if not voice:
        voice = await channel.connect()
    elif voice != channel:
        await voice.move_to(channel)

    PlayFlag = True

    voice.play(discord.FFmpegPCMAudio("./mp3/" + meme + ".mp3"))

    while voice.is_playing():
        await asyncio.sleep(1)

    if not queue_list:
        PlayFlag = False
    else:
        time.sleep(3)
        await play_meme()
    
client.run(DiscordToken)
