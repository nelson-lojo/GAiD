from utils.keys import keys
from sys import argv
from discord.ext.commands import Bot
import discord

if __name__ == '__main__':

    discordToken = argv[1]

    prefix = keys['prefix']
    gaid = Bot(command_prefix=prefix, intents=discord.Intents.default()) 

    for ext in ['search', 'modularity']:
        gaid.load_extension(f'cogs.{ext}')

    gaid.run(discordToken)


# "hey google ..."
# play music in a voice chat

# black scholes model
