# main.py The IE discord bot is launched from here
#
# Copyright (C) 2017-2018 Edern Haumont, Jérome Liermann, François Robion, Nicolas Six
#
# This file is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; see the file LICENSE.  If not see
# <http://www.gnu.org/licenses/>.

import discord
from discord.ext import commands

import random

from config import *
from src_inverted_file.inverted_file import *

description = '''An example bot to showcase the discord.ext.commands extension
module.
There are a number of utility commands being showcased here.'''
bot = commands.Bot(command_prefix='?', description=description)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@bot.command()
async def add(left: int, right: int):
    """Adds two numbers together."""
    await bot.say(left + right)


@bot.command()
async def roll(dice: str):
    """Rolls a dice in NdN format."""
    try:
        rolls, limit = map(int, dice.split('d'))
    except Exception:
        await bot.say('Format has to be in NdN!')
        return

    result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
    await bot.say(result)


@bot.command(description='For when you wanna settle the score some other way')
async def choose(*choices : str):
    """Chooses between multiple choices."""
    await bot.say(random.choice(choices))


@bot.command()
async def repeat(times : int, content='repeating...'):
    """Repeats a message multiple times."""
    for i in range(times):
        await bot.say(content)


@bot.command()
async def joined(member : discord.Member):
    """Says when a member joined."""


@bot.command()
async def update():
    await initialize()


async def initialize():
    await say_and_print("Initializing...")

    print("Looking for bibliographic channel...")
    for channel in bot.get_all_channels():
        if "biblio" in channel.name:
            biblio_channel = channel
            await say_and_print("Hooking on channel : " + biblio_channel.name)
            break

    messages = []
    async for logged_message in bot.logs_from(biblio_channel, limit=1000000):
        if logged_message.author == bot.user:
            continue
        messages.append(logged_message)
    file_path = generate_inverted_file(messages)
    print("Generated inverted file here : {}".format(file_path))
    await say_and_print("Initialization done")


async def say_and_print(message):
    print(message)
    await bot.say(message)

    # counter = 0
    # async for message in client.logs_from(channel, limit=500):
    #     if message.author == client.user:
    #         counter += 1


if __name__ == "__main__":
    bot.run(token)
