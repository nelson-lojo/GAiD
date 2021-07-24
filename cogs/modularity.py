import os
import discord
from discord.ext import commands
from discord.ext.commands.errors import ExtensionAlreadyLoaded, ExtensionFailed, ExtensionNotFound, ExtensionNotLoaded
import traceback

class Modularity(commands.Cog):

    owner = 'Nelson Lojo#7813'
    whitelistDir = 'whitelists'
    cogDir = 'cogs'

    def __init__(self, bot):
        self.bot = bot
        self.privileged = set([Modularity.owner])
        if not os.path.isdir(Modularity.whitelistDir):
            os.mkdir(Modularity.whitelistDir)

    async def getUsers(self, mentions):
        return [ 
            await self.bot.fetch_user(
                mention.replace('<', '')\
                    .replace('@', '')\
                    .replace('!', '')\
                    .replace('>', '')
            ) for mention in mentions 
        ]

    @staticmethod
    def getWhitelistFiles(names):
        """Returns a list containing paths to whitelists (including filenames)"""
        return [ 
            os.path.join(Modularity.whitelistDir, f"{name}-whitelist.txt")
            for name in names 
        ]

    @staticmethod
    async def sendListMessage(context, message, iterable):
        strList = [ f'`{cog}`' for cog in iterable ]
        string = ' '.join(strList)
        s = 's' if len(strList) > 1 else ''
        await context.send(message.format(s=s, lst=string))

    async def allowed(self, user):
        return str(user) == Modularity.owner

    @commands.command(name='load', aliases=['lm'], brief='Load a module (explicit whitelist)', pass_context=True)
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

    @commands.command(name='unload', aliases=['ulm'], brief='Unload a module (explicit whitelist)', pass_context=True)
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

    @commands.command(name='add-towhitelist', aliases=['atwl', 'awl', 'add-whitelist'], brief='Allow users to load, unload, and grant and revoke permissions')
    async def whitelistUsers(self, context, *mentions):
        if not await self.allowed(context.author):
            await context.send(f"**You are not authorized**")
            return

        old = self.privileged
        self.privileged = old.union(set(map(lambda user: str(user), await self.getUsers(mentions))))
        await Modularity.sendListMessage(
            context, 
            "*Added user{s} {lst} to whitelist*", 
            self.privileged.difference(old)
        )

    @commands.command(name='remove-fromwhitelist', aliases=['rfwl', 'rwl', 'remove-whitelist'], brief='(BROKEN) Disallow users to load, unload, and grant and revoke permissions')
    async def unwhitelistUser(self, context, *mentions):
        if not await self.allowed(context.author):
            await context.send(f"**You are not authorized**")
            return

        users = await Modularity.stripAts(mentions)
        removed, notFound = [], []

        for user in users:
            if not self.allowed(user):
                notFound.append(str(user))
                continue
            elif str(user) == self.owner:
                continue
            self.privileged.remove(str(user))
            removed.append(str(user))

        if len(removed) > 0:
            await Modularity.sendListMessage(context, "*Removed user{s} {lst} from whitelist*", removed)
        if len(notFound) > 0:
            await Modularity.sendListMessage(context, "**User{s} {lst} not in whitelist**", notFound)

    @commands.command(name='write-whitelist', aliases=['save-whitelist', 'wwl'], brief='Saves the current whitelist')
    async def savewhitelist(self, context, saveName):
        if not await self.allowed(context.author):
            await context.send(f"**You are not authorized**")
            return

        file = Modularity.getWhitelistFiles([saveName])[0]

        if os.path.isfile(file):
            await context.send(f"**That whitelist name is already taken, please choose another one**")
            return

        try:
            with open(file, 'w') as wl:
                wl.write('\n'.join([ userID for userID in self.privileged if userID is not Modularity.owner ]))
        except:
            await context.send(f"**There was an error in saving. Try again. You may have to remove this whitelist**")
            return
        
        await context.send(f"*Saved whitelist `{saveName}`*")

    @commands.command(name='load-whitelist', aliases=['lwl'], brief='Imports a saved whitelist')
    async def loadWhitelist(self, context, *whitelists):
        if not await self.allowed(context.author):
            await context.send(f"**You are not authorized**")
            return

        newPriv = set([Modularity.owner])
        loaded, notFound = [], []
        files = zip(Modularity.getWhitelistFiles(whitelists), whitelists)

        for file, wlName in files:
            try:
                with open(file, 'r') as f:
                    newUsers = set(map(lambda line: line.strip(), f.readlines()))
                    newPriv = newPriv.union(newUsers)
            except FileNotFoundError:
                notFound.append(wlName)
                continue
            except:
                await context.send("**There was an unidentified error. Please try again.**")
                return

            loaded.append(wlName)
        
        self.privileged = newPriv
        if len(loaded) > 0:
            await Modularity.sendListMessage(context, "Loaded whitelist{s} {lst}", loaded)
        if len(notFound) > 0:
            await Modularity.sendListMessage(context, "Could not find whitelist{s} {lst}", notFound)

        newPriv.remove(Modularity.owner)
        listing = "\n".join([ user for user in newPriv ])
        updatedList = discord.Embed(
            title="New whitelist",
            description=listing,
            color=discord.Color.from_rgb(254, 254, 254) # white (as in 'white'-list)
        )
        await context.send(embed=updatedList)

    @commands.command(name='delete-whitelist', aliases=['dwl'], brief='Deletes a saved whitelist')
    async def removeWhitelist(self, context, *whitelists):
        if not await self.allowed(context.author):
            await context.send(f"**You are not authorized**")
            return

        removed, failed = [], []

        for file, wlName in zip(Modularity.getWhitelistFiles(whitelists), whitelists):
            try:
                os.remove(file)
            except Exception as e:
                failed.append(wlName)
                continue

            removed.append(wlName)

        if len(removed) > 0:
            await Modularity.sendListMessage(context, "Whitelist{s} {lst} deleted", removed)
        if len(failed) > 0:
            await Modularity.sendListMessage(context, "Could not find whitelist{s} {lst}", failed)

    @commands.command(name='show-whitelist', aliases=['swl'], brief='Shows the current whitelist')
    async def showWhitelist(self, context):
        if not await self.allowed(context.author):
            await context.send(f"**You are not authorized**")
            return
        
        if len(self.privileged) > 1:
            await context.send(embed=discord.Embed(
                title="Current whitelist:",
                description="\n".join(filter(lambda user: user is not Modularity.owner, self.privileged)),
                color=discord.Color.from_rgb(254, 254, 254)
            ))
        else:
            await context.send(embed=discord.Embed(
                title="There is no one added to the current whitelist",
                color=discord.Color.from_rgb(254, 254, 254)
            ))


def setup(client):
    client.add_cog(Modularity(client))