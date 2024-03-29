from typing import List, Union, Dict
from utils.query import Query
from utils.result import Result
from utils.tools.misc import log
from discord import Message, User, Member
from discord.ext.commands import Bot, Context
from asyncio.exceptions import TimeoutError

class Navigator:

    def __init__(self, bot: Bot, queries: List[Query], 
                    purpose: str = "unspecified", timeout: int = 300) -> None:
        self.queries: Dict[str, Query] = {
            query.emoji : query
            for query in queries
        }
        self.results: Dict[str, Result] = {
            query.emoji : None
            for query in queries
        }
        self.query_order = queries
        self.bot: Bot = bot
        self.purpose: str = purpose if purpose != '' else purpose + ' '
        self.timeout: int = timeout
        
    async def send(self, context: Context):
        """send the initial message to the channel requested by the user"""
        self.author: Union[User, Member] = context.author
        index = 0
        result = self._get_result(self.query_order[index].emoji)
        while (not result.success) and len(self.query_order) > index + 1:
            index += 1
            result = self._get_result(self.query_order[index].emoji)
        self.message: Message = await context.send(embed=result.getPage(0))

        self.current_res = self.query_order[index].emoji
        self.page_number = 0

        await self.add_reactions()
        await self.watch()

    def _check(self, reaction, user):
        """verify that we only change the displayed page if the uuser that requests is correct"""
        return user == self.author and reaction.message == self.message

    def _get_result(self, emoji: str) -> Result:
        """allow user to request another query by reacting with another emoji"""
        if self.results.get(emoji, None) is None:
            self.results[emoji] = self.queries[emoji].fulfill()
        
        if not self.results[emoji].success and emoji in self.queries.keys():
            self.queries.pop(emoji)

        return self.results[emoji]

    async def add_reactions(self):
        """reset the emoji reactions on the message"""
        if self.page_number > 0:
            await self.message.add_reaction("⬅️")
        if self.page_number + 1 < self._get_result(self.current_res).numPages():
            await self.message.add_reaction("➡️")
        

        for engine in self.queries.keys():
            if engine != self.current_res:
                await self.message.add_reaction(engine)

    async def watch(self):
        while True:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=self.timeout, check=self._check)
                await self.message.remove_reaction(reaction, user)

                await self.update_embed(reaction)

                await self.message.clear_reactions()
                await self.add_reactions()
            except TimeoutError:
                # there is *not* suppossed to be a space after {self.purpose} (see __init__())
                log(f"DROPPING {self.purpose}Navigation handle") 
                await self.message.clear_reactions()

    async def update_embed(self, reaction):

        if reaction.emoji == "⬅️": self.page_number -= 1 
        elif reaction.emoji == "➡️": self.page_number += 1 
        elif str(reaction.emoji) in self.results.keys(): 
            self.current_res = str(reaction.emoji)
            self.page_number = 0

        await self.message.edit(embed=self
                                    ._get_result(self.current_res)
                                    .getPage(self.page_number)
        )

