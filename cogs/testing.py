import os
import discord
from discord.ext import commands as cmds

class Testing(cmds.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @cmds.command(name="probe")
    async def probe(self, context, *args):
        print("PROBE RESULTS:")
        print(f"\tAuthor: {context.author.id} `{context.author.name}`#{context.author.discriminator}")
        print(f"\tGuild: {context.guild.id} `{context.guild.name}`")
        print(f"\tMessage contents: {' '.join(args)}")
        print()

    @cmds.command(name='user')
    async def getUser(self, context):
        print(context.author.avatar)

def setup(bot):
    bot.add_cog(Testing(bot))