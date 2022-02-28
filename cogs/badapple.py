from discord.ext.commands.context import Context
from utils.result import Result
from discord.ext import commands
from utils.engines import CSEImQuery, CSEQuery, WAlphaQuery, DuckQuery, KGraphQuery, JishoQuery
from utils.tools.chat import initNav
import time


class BadApple(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        with open("play.txt", "r") as raw:
            # frames are 100fps for 220 sec
            frames = raw.read().split("SPLIT")
        
        self.frames = frames
        
    async def getFrame(self, timeStamp: float) -> str:
        return ""

    @commands.command(name='bad', aliases=['ba'], brief="Bad Apple!!", pass_context=True)
    async def bad(self, context: Context, *queryTerms):

        thumbnail_frame = 800
        start = time.time() # start time in seconds

        message: Message = await context.send(frames[0])
        while (tStamp := time.time() - start) < 220.0:
            frame = int(tStamp * 100)
            await message.edit(frames[frame])
        
        await message.edit(frames[thumbnail_frame])
        await message.add_reaction("🔄")


def setup(client):
    client.add_cog(Search(client))


