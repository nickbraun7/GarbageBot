#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random, string, datetime, difflib

import discord, asyncio
import youtube_dl
from discord.ext import commands

import load, update

DiscordToken = load.token()
OwnerID = 124686030631731203

update.update()
print("Files Have Been Updated")

mDict = load.memes() #load dictionary of memes
sList = load.stops() #load list of stops

#class with necessary information for each server
class guild_info():
    PlayFlag = False
    MuteFlag = False
    voice = False
    queue = []

guilds = {}

client = commands.Bot(command_prefix='>')
client.remove_command("help") #remove help to add custom help command

@client.event
async def on_ready():
    for guild in client.guilds:
        guilds[guild.id] = guild_info()

    await client.change_presence(activity=discord.Game("Spiting Meme's Since 1976! | >help"))

    print("Garbage Bot Operational")

@client.event
async def on_guild_join(guild):
    guilds[guild.id] = guild_info()

@client.event
async def on_guild_remove(guild):
    guilds.pop(guild.id)

@client.event
async def on_disconnect():
    for guild, guild_info in guilds.items():
        guild_info.PlayFlag = False
        guild_info.voice = False
        guild_info.queue = []

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(":stop_sign: **Command Not Found**")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(":stop_sign: **Invalied Argument**")
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(":stop_sign: **Aye do you have a license for that?** Try again after " + convert(error.retry_after) + ".")
    elif isinstance(error, commands.MissingRole):
        await ctx.send(":stop_sign: **Role Required: **" + error.missing_role)
    elif isinstance(error, commands.NotOwner):
        await ctx.send(":stop_sign: **You think you have the power!**")

    raise error

"""
Discord Command for a meme
"""
@client.command()
async def porn(ctx): #send user a stop meme in a direct message
    channel = await ctx.author.create_dm()
    await channel.send(random.choice(sList))

"""
Discord Command help screen
"""
@client.command()
async def help(ctx):
    embed = discord.Embed()

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
        name=">mute",
        value="mute the bot",
        inline=False
        )

    embed.add_field(
        name='>invite',
        value="send invite link to guild",
        inline=False
        )

    embed.add_field(
        name=">suggest <text suggest (youtube link prefered)>",
        value="suggest a meme to add to the bot",
        inline=False
    )

    embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
    await ctx.send(embed=embed, delete_after=60)

"""
Discord Command to join the author's current channel
"""
@client.command()
async def join(ctx):
    guild = ctx.guild.id
    guild_voice = guilds[guild].voice
    author_voice = ctx.message.author.voice

    if author_voice:
        if guild_voice:
            await guild_voice.disconnect()
        guilds[guild].voice = await author_voice.channel.connect()
        return True
    else:
        await ctx.send(":stop_sign: **You're Not Connected to a Voice Channel**")
        return False

"""
Discord Command to leave the current channel
"""
@client.command()
async def leave(ctx):
    guild = ctx.guild.id
    guild_voice = guilds[guild].voice

    if guild_voice:
        await guild_voice.disconnect()
        guilds[guild].PlayFlag = False
        guilds[guild].voice = False
        guilds[guild].queue = []
    else:
        await ctx.send(":stop_sign: **Not Connected to a Voice Channel**")


"""
Discord Command which sends a link to a google spreadsheet
of all the current memes loaded into the bot.
"""
@client.command()
async def catalog(ctx):
    embed = discord.Embed()

    embed.add_field(
        name=":rat: :book:",
        value="[Catalog Link](https://docs.google.com/spreadsheets/d/1K6a-J7q8tnHO-aQQLWlczioM5s2lyp4KOiEbkjWEeQk/edit?usp=sharing)",
        inline=False
        )
    
    embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
    await ctx.send(embed=embed, delete_after=60)

"""
Discord Command which allows the user to choose a meme
from a list and play in a specific channel, adding the
meme to a queue if the bot is currently playing.
"""
@client.command()
async def play(ctx, *args):
    guild = ctx.guild.id
    guild_info = guilds[guild]

    if not guild_info.voice:
        if not await join(ctx):
            return
    
    if not guild_info.voice:
        await ctx.send(":stop_sign: **Not Connected to Voice Channel**")
    elif guild_info.MuteFlag:
        await ctx.send(":stop_sign: **Currently Muted**")
    elif len(guild_info.queue) >= 10:
        await ctx.send(":stop_sign: **Queue too Long**")
    else:
        arg = " ".join(args)
        key = arg[0].upper()
        match = difflib.get_close_matches(arg, mDict[key], n=1, cutoff=0.2)
        
        meme = ""
        for element in mDict[key]:
            if element.lower() == arg.lower():
                meme = element
                break

        if not meme and match:
            meme = match[0]

        if not meme:
            await ctx.send(":stop_sign: **Error 404: **" + arg)
        else:
            guild_info.queue.append(meme)

            if guild_info.PlayFlag:
                await ctx.send(":arrows_counterclockwise: **Queued: **" + meme)
            else:
                await ctx.send(":white_check_mark: **Playing: **" + meme)
                await check_queue(ctx, guild_info)

"""
Discord Command to pull a random meme from
the dictionary and play via the play command.
"""
@client.command()
async def garbage(ctx):
    ls = []
    for key in mDict:
        ls.extend(mDict[key])

    await play(ctx, random.choice(ls))

"""
Discord Command to mute the bot, which stops
all incomming play commands and removes the
current queue.
"""
@client.command()
@commands.has_role("Garbage")
async def mute(ctx):
    guild = ctx.guild.id
    guild_info = guilds[guild]

    if guild_info.MuteFlag:
        guild_info.MuteFlag = False
        await ctx.send(":white_check_mark: **Unmuted**")
    else:
        guild_info.MuteFlag = True
        guild_info.queue = []
        await ctx.send(":stop_sign: **Muted**")

"""
Discord Command which sends a invite link to the
author via DM's if they want to add the bot to
their guild.
"""
@client.command()
async def invite(ctx):
    channel = await ctx.author.create_dm()
    embed = discord.Embed()
    
    embed.add_field(
        name=":rat: :book:",
        value="[Invite Link](https://discord.com/api/oauth2/authorize?client_id=814056074717691915&permissions=3148800&scope=bot)",
        inline=False
        )

    embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
    await channel.send(embed=embed)

"""
Discord Command to suggest a meme to add, sends the
suggestion to me via discord DM
"""
@client.command()
@commands.cooldown(5, 3600, commands.BucketType.user)
async def suggest(ctx, *args):
    owner = await client.fetch_user(OwnerID)
    channel = await owner.create_dm()

    await channel.send(":point_right: **%s: **" % (ctx.author) + " ".join(args))
    await ctx.send("**Thank you for the Garbage!**")

"""
Discord Command to allow the owner to reload the
current dictionary, incase an mp3 was added while
the bot is running.
"""
@client.command()
@commands.is_owner()
async def reload(ctx):
    update.update()

    global mDict, sList
    mDict = load.memes() #load dictionary of memes
    sList = load.stops() #load list of stops

    await ctx.send(":white_check_mark: **Files Reloaded**")


def convert(sec):
    mins, secs = divmod(sec, 60)
    hours, mins = divmod(mins, 60)
    return "%02d:%02d:%02d" % (hours, mins, secs)
        
"""
Function to check the queue and disconnect the
bot if 60 seconds without use has passed.
"""
async def check_queue(ctx, guild_info):
    while guild_info.queue:
        guild_info.PlayFlag = True
        guild_info.voice.play(discord.FFmpegPCMAudio("./mp3/" + guild_info.queue[0] + ".mp3"))

        while guild_info.voice.is_playing():
            await asyncio.sleep(1)
        guild_info.queue.pop(0)
        await asyncio.sleep(3)

    guild_info.PlayFlag = False

    for sec in range(60):
        await asyncio.sleep(1)
        
        if guild_info.queue:
            return

    await leave(ctx)

client.run(DiscordToken)
