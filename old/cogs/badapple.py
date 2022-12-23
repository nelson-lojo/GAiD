from discord.ext.commands.context import Context
from discord.ext import commands
import requests as r
import time

DEFAULT_FRAMERATE = 2.5

class Badapple(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        with open("cogs/play.txt", "r") as raw:
            # frames are 100fps for 220 sec
            frames = raw.read().split("SPLIT")
        
        self.frames = frames

    @commands.command(name='bad', aliases=['ba'], brief="Bad Apple!!", pass_context=True)
    async def bad(self, context: Context, frameRate=DEFAULT_FRAMERATE, *args):

        thumbnail_frame = 800
        start = time.time() # start time in seconds

        message: Message = await context.send(f"```{self.frames[0]}```")
        last_frame = 0
        while (tStamp := time.time() - start) < 220.0:
            # tStamp is in seconds, frame is tStamp * 100 as an int
            frame = int(int(tStamp * frameRate) * (100 // frameRate)) 
            if frame != last_frame:
                last_frame = frame
                await message.edit(content=f"```{self.frames[frame]}```")
                print(f"sent frame at {tStamp} sec")
        
        await message.edit(content=self.frames[thumbnail_frame])
#        await message.add_reaction("🔄")

    @commands.command(name='good', aliases=['play'], brief="Bad Apple!!!", pass_context=True)
    async def good(self, ctx, frameRate=DEFAULT_FRAMERATE, *args):
        thumbnail_frame = 800
        webhook = await ctx.channel.create_webhook(name="Bad Apple!!")
        msg = await webhook.send(content=f"```{self.frames[0]}```", wait=True)
        url = f"https://discordapp.com/api/webhooks/{webhook.id}/{webhook.token}/messages/{msg.id}"
        #                                 /webhooks/{webhook.id}/{webhook.token}/messages/{message.id}

        start = time.time()
        
        last_frame = 0
        while (tStamp := time.time() - start) < 220.0:
            frame = int(int(tStamp * frameRate) * (100 // frameRate))
            if frame != last_frame:
                res = r.patch(url, {'content' : f"```{self.frames[frame]}```"})
                #await msg.edit(content=f"```{self.frames[frame]}```")
                if res.status_code // 100 < 4:
                    print(f'Bad Apple!!: Sent frame {frame} at {tStamp}', end='\r')
                    last_frame = frame
                else:
                    print(f'Bad Apple!!: Failed to send frame {frame} at {tStamp} ({res.status_code})')#, end='\r')
                    print(res.text)
                    
                    try:
                        res_data = json.loads(res.text)
                        retry_time = res_data.get('retry_after', None)
                        await ctx.send(f"Error: {res_data['message']} {'Retry after' + retry_time + 'seconds.' if retry_time else ''}")
                    except:
                        await ctx.send(f"Unknown error, contact host to check logs")
                    
                    await msg.delete()
                    await webhook.delete()
                    return
        
        time.sleep(3)
        await msg.delete()
        await webhook.delete()
        print('Bad Apple!!: finished')


async def setup(client):
    await client.add_cog(Badapple(client))
