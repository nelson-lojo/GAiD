from utils.keys import keys
from sys import argv
from discord.ext.commands import Bot
import discord
import asyncio

if __name__ == '__main__':

    discordToken = argv[1]

    prefix = keys['prefix']
    intent = discord.Intents.default()
    intent.message_content = True
    gaid = Bot(command_prefix=prefix, intents=intent) 

    for ext in ['search', 'modularity']:
        asyncio.run(gaid.load_extension(f'cogs.{ext}'))

    gaid.run(discordToken)


# "hey google ..."
# play music in a voice chat

# black scholes model
