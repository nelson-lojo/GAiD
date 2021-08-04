import os
import asyncio
import discord
import requests
from json import loads
from uuid import uuid4
from discord.ext import commands
from time import time, gmtime, strftime
from utils.engines import WAlphaQuery, DuckQuery, KGraphQuery, JishoQuery
from utils.tools import initNav, log

MAX_QUERIES = 100

def querify(terms, plusJoin=True, exclude=[]):
    mapping = [
        ('&', '%26'),
        ('%', '%25'),
        ('#', '%23'),
        ('?', '%3F'),
        ('+', '%2B')
    ]
    newTerms = []
    for term in terms:
        newTerm = term
        for m in mapping:
            if m[0] in exclude:
                continue
            newTerm = newTerm.replace(*m)
        newTerms.append(newTerm)
    if plusJoin:
        return "+".join(newTerms)
    else:
        return "%20".join(newTerms)


def trackQueries(maxCount):
    queryDir = f"GAiD_Queries_{maxCount}"
    if not os.path.isdir(queryDir):
        os.makedirs(queryDir)
    def check(func, **kwargs):
        i = 0
        creationTimes = [ (os.path.join(queryDir, fname), os.stat(os.path.join(queryDir, fname)).st_ctime) for fname in os.listdir(queryDir) ]
        for f in creationTimes:
            if f[1] < time() - 24 * 60 * 60:
                os.remove(f[0])
        
        if len(creationTimes) < MAX_QUERIES:
            open(str(os.path.join(queryDir, str(uuid4()))), 'w').close()
            return func(**kwargs), len(creationTimes) + 1, True
        else:
            oldestFile = min(creationTimes, key=(lambda pair: pair[1]))
            timeLeft = oldestFile[1] + 24 * 60 * 60 - time()  #  queries[0] + datetime.timedelta(days=1) - datetime.datetime.now()
            return f"Please wait {strftime('%H:%M:%S', gmtime(timeLeft))} before making another query", len(creationTimes), False
    return check

def embed(query, result=None, color=discord.Color.blue(), count=-1,):
    if result is None:
        return discord.Embed(
            title=f"No result found for query{'' if count < 0 else f' ({count}/{MAX_QUERIES})'}: {query}",
            color=color
        )
    else:
        return discord.Embed(
            title=f"Query{f'' if count < 0 else f' {count}/{MAX_QUERIES}'}: {query}",
            description=result,
            color=color
        )


class Search(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.chargeableCheck = trackQueries(MAX_QUERIES)

    @commands.command(name='walpha', aliases=['wa', 'wolframalpha'], brief="query Wolfram Alpha", pass_context=True)
    async def walpha(self, context, *queryTerms):
        
        query = WAlphaQuery(queryTerms)
        result = query.fulfill()

        await initNav(
            self.bot,
            await context.send(embed=result.getPage(0)),
            result,
            context.author,
            purpose="walpha",
            timeout=30
        )

        if result.success is False:
            log(f"FAILED walpha request with query: `{' '.join(queryTerms)}`")
        
    @commands.command(name='duck', aliases=['duckduckgo', 'd'], brief="query DuckDuckGo", pass_context=True)
    async def duckInstantAnswer(self, context, *queryTerms):
        
        query = DuckQuery(queryTerms)
        result = query.fulfill()

        await context.send(embed=result.getPage(0))

    @commands.command(name="kpanel", aliases=['knowledgegraph', 'kgraph', 'kg', 'kp'], brief="query Google's Knowledge Graph", pass_context=True)
    async def kgraph(self, context, *queryTerms):

        query = KGraphQuery(queryTerms)
        result = query.fulfill()

        await context.send(embed=result.getPage(0))

    @commands.command(name='image', aliases=['findimage', 'i'], brief='query Google Images (100 per day)', pass_context=True)
    async def imageSearch(self, context, *queryTerms):
        required = list(filter(lambda term: term[0] == '+', queryTerms))
        exclude = list(filter(lambda term: term[0] == '-', queryTerms))
        normal = list(filter(lambda term: term[0] not in ['+', '-'], queryTerms))

        url = 'https://customsearch.googleapis.com/customsearch/v1'
        content = {
            'key' : 'AIzaSyCtJB-5h7Onbn72PpaaPRY4adsNKcd6CNM',
            'cx' : '15b1428872aa7680b', # Programmable Search Engine ID
            'exactTerms' : ' '.join(required),
            'excludeTerms' : ' '.join(exclude),
            # 'fileType' : 'pdf', # file:pdf
            'q' : ' '.join(normal),
            'searchType' : 'image',  # search for images
        }

        def sendSearch(data=content):
            results = loads(requests.get(url, data).text)
            # print(results)
            return results

        results, queryCount, requested = self.chargeableCheck(sendSearch)

        if requested:
            def getPanel(index):
                nonlocal results, queryCount, requested
                if not requested:
                    # this is the case when the last query failed due to limiting
                    # so we re-query Google to get our stuff
                    results, queryCount, requested = self.chargeableCheck(sendSearch)
                if not requested:
                    # this is the case where we fail again
                    return embed(' '.join(queryTerms), results, count=queryCount)
                
                # so now we can assume results is a proper dictionary with data
                start = results['queries']['request'][0]['startIndex']
                count = results['queries']['request'][0]['count'] 
                if index + 1 < start: 
                    # if we want an image smaller than our last recieved results, we need to requery
                    newPage = content.copy()
                    newPage.update({ 'start' : start - count })
                    results, queryCount, requested = self.chargeableCheck(sendSearch, **{ 'data' : newPage })
                elif index + 1 >= start + count:
                    # if we want an image bigger than our last recieved results, we need to requery
                    newPage = content.copy()
                    newPage.update({ 'start' : start + count })
                    results, queryCount, requested = self.chargeableCheck(sendSearch, **{ 'data' : newPage })

                # if we still have proper data (that we either didn't need to requery or didn't fail our requery)
                if requested:
                    # then we can display our result properly
                    res = results['items'][index % count]
                    display = discord.Embed(
                        title=f"Query {queryCount}/{MAX_QUERIES}: {' '.join(queryTerms)}",
                        description=f"Result {index + 1}: {res['snippet']} [{res['displayLink']}]({res['image']['contextLink']})",
                        color=discord.Color.blue()
                    )
                    display.set_image(url=res['link'])
                else:
                    # we exit with a failure
                    display = embed(' '.join(queryTerms), results, count=queryCount)
                return display

            index = 0
            message = await context.send(embed=getPanel(index))
            await message.add_reaction("⬅️")
            await message.add_reaction("➡️")

            isAuthor = lambda reaction, user: user == context.author
            while True:
                try:
                    # 30 sec timeout
                    reaction, user = await self.bot.wait_for("reaction_add", timeout=30, check=isAuthor)
                    
                    await message.remove_reaction(reaction, user) 
                    if message == reaction.message:
                        if reaction.emoji == "⬅️":
                            # show prev
                            index -= 1 if index > 0 else 0
                        elif reaction.emoji == "➡️":
                            # show next
                            index += 1
                        await message.edit(embed=getPanel(index))
                except asyncio.TimeoutError: 
                    print(f"DROPPING image nav handle for query: `{' '.join(queryTerms)}`")
                    await message.remove_reaction('➡️', self.bot.user)
                    await message.remove_reaction('⬅️', self.bot.user)
                    break
        else:
            # if we get here, then results will have the "Please wait ..." string
            display = embed(' '.join(queryTerms), results, count=queryCount)
            await context.send(embed=display)

    @commands.command(name="page", aliases=['findpage'], brief="query Google to list relevant pages (100 per day)", pass_context=True)
    async def findpage(self, context, *queryTerms):

        required = list(filter(lambda term: term[0] == '+', queryTerms))
        exclude = list(filter(lambda term: term[0] == '-', queryTerms))
        normal = list(filter(lambda term: term[0] not in ['+', '-'], queryTerms))

        url = 'https://customsearch.googleapis.com/customsearch/v1'
        content = {
            'key' : 'AIzaSyCtJB-5h7Onbn72PpaaPRY4adsNKcd6CNM',
            'cx' : '15b1428872aa7680b', # Programmable Search Engine ID
            'exactTerms' : ' '.join(required),
            'excludeTerms' : ' '.join(exclude),
            # 'fileType' : 'pdf', # file:pdf
            'q' : ' '.join(normal),
        }

        def sendQuery():
            response = loads(requests.get(url, content).text)

            results = ""
            for i in range(1, 10):
                results += f"{i}. [{response['items'][i]['displayLink']}]({response['items'][i]['link']})\n"

            return results
        
        results, queryCount, requested = self.chargeableCheck(sendQuery)

        message = await context.send(embed=embed(' '.join(queryTerms), results, count=queryCount))
        if not requested:
            await message.add_reaction("🔄") 
            while not requested:
                try:
                    reaction, user = await self.bot.wait_for("reaction_add")
                    await message.remove_reaction(reaction, user)
                    if message == reaction.message and reaction.emoji == "🔄": 
                        # requery
                        results, queryCount, requested = self.chargeableCheck(sendQuery)
                        await message.edit(embed=embed(' '.join(queryTerms), results, count=queryCount))
                except:
                    print(f"DROPPING refresh handle for query: `{' '.join(queryTerms)}`")
                    await message.remove_reaction('🔄', self.bot.user)
                    break

    @commands.command(name="jisho", aliases=['j'], brief="query jisho.org to get japanese results", pass_context=True)
    async def jisho(self, context, *queryTerms):

        query = JishoQuery(queryTerms)
        result = query.fulfill()

        await initNav(
            self.bot,
            await context.send(embed=result.getPage(0)),
            result,
            context.author,
            purpose="jisho",
            timeout=300
        )


def setup(client):
    client.add_cog(Search(client))
