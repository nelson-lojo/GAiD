import discord
from discord.ext import commands

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='joinvoice', aliases=['joinvc', 'joinvoicechat', 'joinvoicechannel', 'join', 'jv', 'jvc'], brief="joins a voice channel", pass_context=True)
    async def joinvc(self, context):
        if context.author.voice is not None:
            voice = discord.utils.get(self.bot.voice_clients, guild=context.guild)
            if voice is not None:
                if voice.channel == context.author.voice.channel:
                    await context.send(f"**Already connected to `{context.author.voice.channel}`**")
                    return
                else:
                    await voice.disconnect()
            await context.author.voice.channel.connect()
            await context.send(f"*Joined `{context.author.voice.channel}`*")
        else:
            await context.send("**You must be connected to a voice channel**")

    @commands.command(name='play', aliases=['p'], brief="plays audio in a voice channel", pass_context=True)
    async def playAudio(self, context, *queryTerms):
        await self.joinvc(context)

        # first check if the first element(s) are urls
            # if so, just rip them
        # otherwise, search youtube and play the first one
        pass
    
    @commands.command(name='pause', aliases=['stop'], brief="pauses audio if playing", pass_context=True)
    async def pause(self, context):
        # check if connected
        # check if playing
            # halt audio, maintain queue
        pass

    @commands.command(name='leave', aliases=['disconnect', 'dc', 'fuckoff', 'gtfo'], brief="disconnects from voice channel", pass_context=True)
    async def leave(self, context):
        voice = discord.utils.get(self.bot.voice_clients, guild=context.guild)
        if voice is not None:
            await voice.disconnect()
        else:
            await context.send("**Not connected to a voice channel**")
        # check if playing
            # if so, pause
        # check if connected
            # if so, leave
        # clear queue
        # reset queue pointer
        pass

    @commands.command(name='nowplaying', aliases=['np', 'status'], brief="shows the current playing audio", pass_context=True)
    async def nowPlaying(self, context):
        # check if connected
        # check if playing
        # fetch status and report in an embed (or maybe some fancy formatting in normal text)
        pass
    
def setup(client):
    client.add_cog(Music(client))