import asyncio
from typing import Union
from utils.result import Result
from utils.tools.misc import log
from discord import Message, User, Member
from discord.ext.commands import Bot, Context


async def initNav(bot: Bot, result: Result, context: Context, purpose: str = "", timeout: int = 300) -> None:
    index = 0
    
    message: Message = await context.send(embed=result.getPage(index))
    
    author: Union[User, Member] = context.author

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
            log(f"DROPPING {purpose} nav handle for query: {result.query}")
            await message.remove_reaction('➡️', bot.user)
            await message.remove_reaction('⬅️', bot.user)
            break