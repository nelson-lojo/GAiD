from typing import Iterable, List
import sqlalchemy as sa
from utils.keys import keys
import discord
from discord.ext import commands
from discord.ext.commands.errors import ExtensionAlreadyLoaded, ExtensionFailed, ExtensionNotFound, ExtensionNotLoaded

class Modularity(commands.Cog):

    db = sa.create_engine(keys['db'])
    owner = 'Nelson Lojo#7813'
    cogDir = 'cogs'

    def __init__(self, bot):
        self.bot = bot

        md = sa.MetaData()
        md.bind = Modularity.db
        self.table = sa.Table(
            'modularity-authorized', md,
            sa.Column('name', sa.TEXT),
            sa.Column('discord_user_id', sa.TEXT, primary_key=True)
        )
        self.table.create(Modularity.db, checkfirst=True)

    async def getUsers(self, mentions) -> List[discord.User]:
        return [ 
            await self.bot.fetch_user(
                mention.replace('<', '')\
                    .replace('@', '')\
                    .replace('!', '')\
                    .replace('>', '')
            ) for mention in mentions 
        ]

    @staticmethod
    async def sendListMessage(context, message, iterable):
        cogList = [ f'`{cog}`' for cog in iterable ]
        string = ' '.join(cogList)
        s = 's' if len(cogList) > 1 else ''
        await context.send(message.format(s=s, lst=string))

    async def allowed(self, user: discord.User):
        # condition: `usr is owner`` or `usr in authorized_table`
        is_owner = str(user) == Modularity.owner 
        same_users = self.table.select().where(
            self.table.c.discord_user_id == str(user.id)
        ).execute()

        print(is_owner)
        print(same_users)
        return is_owner or same_users.rowcount > 1

    @commands.command(name='load', aliases=['lm'], brief='Load a module', pass_context=True)
    async def loadCog(self, context, *cogs):
        if not await self.allowed(context.author):
            await context.send(f"**You are not authorized**")
            return

        loaded, notFound, failedToLoad, alreadyLoaded = [], [], [], []
        
        for cog in cogs:
            try:
                self.bot.load_extension(f'{Modularity.cogDir}.{cog}')
                loaded.append(cog)
            except ExtensionNotFound:
                notFound.append(cog)
            except ExtensionFailed:
                failedToLoad.append(cog)
            except ExtensionAlreadyLoaded:
                alreadyLoaded.append(cog)

        if len(loaded) > 0:
            await Modularity.sendListMessage(context, "*Loaded cog{s} {lst}*", loaded)
        if len(alreadyLoaded) > 0:
            await Modularity.sendListMessage(context, "**Already loaded cog{s} {lst}**", alreadyLoaded)
        if len(notFound) > 0:
            await Modularity.sendListMessage(context, "**Cannot find cog{s} {lst} in repository**", notFound)
        if len(failedToLoad) > 0:
            await Modularity.sendListMessage(context, "**Failed to load cog{s} {lst}**", failedToLoad)

    @commands.command(name='unload', aliases=['ulm'], brief='Unload a module', pass_context=True)
    async def unloadCog(self, context, *cogs):
        if not await self.allowed(context.author):
            await context.send(f"**You are not authorized**")
            return

        unloaded, notFound, notLoaded = [], [], []

        for cog in cogs:
            try:
                self.bot.unload_extension(f'{Modularity.cogDir}.{cog}')
                unloaded.append(cog)
            except ExtensionNotLoaded:
                notLoaded.append(cog)
            except ExtensionNotFound:
                notFound.append(cog)
        
        if len(unloaded) > 0:
            await Modularity.sendListMessage(context, "*Unloaded cog{s} {lst}*", unloaded)
        if len(notLoaded) > 0:
            await Modularity.sendListMessage(context, "**Cog{s} {lst} are not loaded**")
        if len(notFound) > 0:
            await Modularity.sendListMessage(context, "**Could not find cog{s} {lst} in repository**", notFound)

    @commands.command(name='showload', aliases=['slm'], brief="Show loaded modules", pass_context=True)
    async def showCogs(self, context):
        raise NotImplementedError()
        # TODO: implement

    @commands.command(name='authorize', aliases=['auth'], brief='Allow users to load, unload, and grant and revoke permissions', pass_context=True)
    async def whitelistUsers(self, context, *mentions):
        if not await self.allowed(context.author):
            await context.send(f"**You are not authorized**")
            return

        users: Iterable[discord.User] = await self.getUsers(mentions)
        added, already = [], []

        for user in users: 
            try:
                self.table.insert().values(name=user.name, discord_user_id=str(user.id)).execute()
                added.append(user)
            except sa.exc.IntegrityError:
                already.append(user)

        if len(added) > 0:
            await Modularity.sendListMessage(context, "*User{s} {lst} now authorized*", added)
        if len(already) > 0:
            await Modularity.sendListMessage(context, "*User{s} {lst} are already authorized*", already)

    @commands.command(name='deauthorize', aliases=['deauth'], brief='Disallow users to load, unload, and grant and revoke permissions', pass_context=True)
    async def unwhitelistUser(self, context, *mentions):
        if not await self.allowed(context.author):
            await context.send(f"**You are not authorized**")
            return

        users: List[discord.User] = await self.getUsers(mentions)

        for user in users: 
            self.table.delete().where(self.table.c.discord_user_id == str(user.id)).execute()

        await Modularity.sendListMessage(context, "*User{s} {lst} now not authorized*", users)

    @commands.command(name='show-authorized', aliases=['show-a', 'sauth'], brief='List users allowed to load, unload, and grant permissions', pass_context=True)
    async def showWhitelist(self, context):
        if not await self.allowed(context.author):
            await context.send(f"**You are not authorized**")
            return

        users: List[str] = [ row[0] for row in self.table.select().execute() ]

        if len(users) > 1:
            await context.send(embed=discord.Embed(
                title="Current whitelist:",
                description="\n".join(filter(lambda user: user is not Modularity.owner, users)),
                color=discord.Color.from_rgb(254, 254, 254)
            ))
        else:
            await context.send(embed=discord.Embed(
                title="There is no one added to the current whitelist",
                color=discord.Color.from_rgb(254, 254, 254)
            ))


def setup(client):
    client.add_cog(Modularity(client))