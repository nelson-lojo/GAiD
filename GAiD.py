import os
import discord
import asyncio
from discord.ext.commands.cog import _cog_special_method
import requests
from sys import argv
from uuid import uuid4
from json import loads
from discord.ext.commands import Bot
from time import time, gmtime, strftime

if __name__ == '__main__':

    discordToken = argv[1]

    gaid = Bot(command_prefix='g ') 

    for ext in ['search', 'modularity']:
        gaid.load_extension(f'cog-{ext}')

    # @gaid.command(name='probe')
    # async def probe(context, *args):
    #     auth = context.author
    #     print(f"Author {type(auth)}: {auth} {auth.mention}")
    #     for arg in args:
    #         print (arg)

    gaid.run(discordToken)


# "hey google ..."
# play music in a voice chat

# black scholes model
