import asyncio
from typing import Callable, Dict, Union
from utils.result import Result
from discord import Message, User, Member
from discord.ext.commands import Bot


def log(msg: str):
    print(msg)

async def initNav(bot: Bot, message: Message, result: Result, author: Union[User, Member], purpose: str = "", timeout: int = 300) -> None:
    index = 0
    if len(result.pages) > 1:
        await message.add_reaction("⬅️")
        await message.add_reaction("➡️")
    
    check = lambda reaction, user: user == author and message == reaction.message
    while True:
        try:
            # 5 min timeout
            reaction, user = await bot.wait_for('reaction_add', timeout=timeout, check=check)
            await message.remove_reaction(reaction, user)

            if reaction.emoji == "⬅️":
                # show prev
                index -= 1 if index > 0 else 0
            elif reaction.emoji == "➡️":
                # show next
                index += 1 if index + 1 < len(result.pages) else 0
            await message.edit(embed=result.getPage(index))
        except asyncio.TimeoutError:
            if purpose != '':
                purpose += ' '
            log(f"DROPPING {purpose}nav handle for query: {result.query}")
            await message.remove_reaction('➡️', bot.user)
            await message.remove_reaction('⬅️', bot.user)
            break

def limitExecutions(mappings: Dict) -> Callable[[str, Callable], Result]:
    dbName = "GAiD.db"
    # make the table
    # |  id  |  category  |  insertion date  |  query  |  pages  |
    # mappings = {
    #     'cse' : {
    #         'max' : 100,
    #         'interval' : timedelta(days=1)
    #     }
    # }
    def check(category: str, func: Callable[[], Result]) -> Result:
        if category in mappings.keys():
            pass
            # select * from limits where limits.category == :category
            # clear out the old requests
            # if count < mappings[category][max]
            #   run
            # else
            #   return failure()
        return None