import os
import asyncio
import discord
import requests
from json import loads
from uuid import uuid4
from discord.ext import commands
from time import time, gmtime, strftime
from utils.engines import walpha
from utils.query import Query
from utils.tools import *

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
    def __init__(self, bot, cseToken):
        self.bot = bot
        self.cseToken = cseToken
        self.chargeableCheck = trackQueries(MAX_QUERIES)

    @commands.command(name='walpha', aliases=['wa', 'wolframalpha'], brief="query Wolfram Alpha", pass_context=True)
    async def walpha(self, context, *queryTerms):
        
        query = Query(queryTerms, walpha)
        result = query.fulfill()

        if result.success is False:
            await context.send(embed=result.showFailurePage())
            log(f"FAILED walpha request with query: `{' '.join(queryTerms)}`")
            return
        
        index = 0
        message = await context.send(embed=result.getPage(index))
        if len(result.pages) <= 2:
            return
        log(f"LAUNCHING walpha nav handle for query: `{' '.join(queryTerms)}`")
        await message.add_reaction("⬅️")
        await message.add_reaction("➡️")

        validate = lambda reaction, user: user == context.author and message == reaction.message
        while True:
                try:
                    # 30 sec timeout
                    reaction, user = await self.bot.wait_for("reaction_add", timeout=30, check=validate)
                    
                    await message.remove_reaction(reaction, user) 
                    if reaction.emoji == "⬅️":
                        # show prev
                        index -= 1 if index > 0 else 0
                    elif reaction.emoji == "➡️":
                        # show next
                        index += 1 if index < (len(result.pages) - 1) else 0
                    await message.edit(embed=result.getPage(index))
                except asyncio.TimeoutError: 
                    print(f"DROPPING walpha nav handle for query: `{' '.join(queryTerms)}`")
                    await message.remove_reaction('➡️', self.bot.user)
                    await message.remove_reaction('⬅️', self.bot.user)
                    break

    @commands.command(name='duck', aliases=['duckduckgo', 'd'], brief="query DuckDuckGo", pass_context=True)
    async def duckInstantAnswer(self, context, *queryTerms):
        url = f'https://api.duckduckgo.com/?q={querify(queryTerms)}&format=json'
        res = loads(requests.get(url).text)
        if res['meta']['src_name'] == "hi there":  # why is this in production code?
            response = embed(' '.join(queryTerms), color=discord.Color.orange())
        elif res['Abstract'] == '':
            listing = ''
            from pprint import pprint
            index = 0
            count = 0
            while len(listing) < 1900:
                index += 1
                count += 1
                if index >= len(res['RelatedTopics']):
                    break

                if res['RelatedTopics'][index].get('Topics', None) is not None:
                    for topic in res['RelatedTopics'][index]['Topics']:
                        entry = f"{count}. [{topic['Text']}]({topic['FirstURL']})\n"
                        if len(entry) > 2048 - len(listing):
                            break
                        listing += f"{count}. [{topic['Text']}]({topic['FirstURL']})\n"
                        count += 1
                else:
                    entry = f"{count}. [{res['RelatedTopics'][index]['Text']}]({res['RelatedTopics'][index]['FirstURL']})\n"
                    if len(entry) > 2048 - len(listing):
                        break
                    listing += entry

            listing = listing[:-1]
            response = embed(' '.join(queryTerms), listing, color=discord.Color.orange())
        else:
            response = embed(
                ' '.join(queryTerms), 
                result=res['AbstractText'] + f' [{res["AbstractSource"]}]({res["AbstractURL"]})', 
                color=discord.Color.orange()
            )

        await context.send(embed=response)

    @commands.command(name="kpanel", aliases=['knowledgegraph', 'kgraph', 'kg', 'kp'], brief="query Google's Knowledge Graph", pass_context=True)
    async def kgraph(self, context, *queryTerms):
        key = 'AIzaSyAPaVBs7KsN47_iSPyHwg5ex0oBX8oAkho'
        query = querify(queryTerms)
        url = f'https://kgsearch.googleapis.com/v1/entities:search?query={query}&key={key}&limit=1&indent=True'

        response = loads(requests.get(url).text)
        # print(response)
        if len(response['itemListElement']) > 0:
            data = response['itemListElement'][0]['result']
            if data.get('description', None) is not None:
                panel = discord.Embed(
                    title=data['name'],
                    description=data.get('description', None),
                    color=discord.Color.blue()
                )
            else:
                panel = discord.Embed(
                    title=data['name'],
                    color=discord.Color.blue()
                )
            if data.get('detailedDescription', None) is not None:
                panel.add_field(
                    name=f'Description:',
                    value=f'{data["detailedDescription"]["articleBody"]} [source]({data["detailedDescription"]["url"]})'
                )
        else:
            panel = embed(' '.join(queryTerms), result=None)
        await context.send(embed=panel)

    @commands.command(name='image', aliases=['findimage', 'i'], brief='query Google Images (100 per day)', pass_context=True)
    async def imageSearch(self, context, *queryTerms):
        required = list(filter(lambda term: term[0] == '+', queryTerms))
        exclude = list(filter(lambda term: term[0] == '-', queryTerms))
        normal = list(filter(lambda term: term[0] not in ['+', '-'], queryTerms))

        url = 'https://customsearch.googleapis.com/customsearch/v1'
        content = {
            'key' : self.cseToken,
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
        query = querify(queryTerms, exclude=['#', '"'])
        url = f"https://jisho.org/api/v1/search/words?keyword={query}"
        response = loads(requests.get(url).text)

        if len(response['data']) < 1:
            # this case is that jisho could not find an entry for this
            await context.send(embed=embed(' '.join(queryTerms), color=discord.Color.green()))
            return

        results_count = len(response['data'])

        def getPanel(index):
            try:
                res = response['data'][index]
            except:
                print("Issue found in parsing for data")
                return getPanel(index - 1)

            result = f'Result {index + 1}/{results_count}\n\n'
            slugUrl = f'https://jisho.org/word/{res["slug"]}'
            for form in res['japanese']:
                if form.get('word', None) is not None and form.get('reading', None) is not None:
                    result += f'{form["word"]} - {form["reading"]}、'
                else:
                    result += f'{form["reading"] if form.get("reading", False) else form["word"]}、'
            result = result[:-1]

            for i in range(len(res['senses'])):
                result += f"\n{i}. "
                result += f"{', '.join(res['senses'][i]['parts_of_speech'])} - "
                result += ', '.join(res['senses'][i]['english_definitions']) + '\n'

            result += f"[View this result in jisho]({slugUrl})"

            panel = embed(' '.join(queryTerms), result, discord.Color.green())
            panel.set_footer(text=' '.join(res['jlpt']))
            return panel

        index = 0
        message = await context.send(embed=getPanel(index))
        if results_count > 1:
            await message.add_reaction("⬅️")
            await message.add_reaction("➡️")

        isAuthor = lambda reaction, user: user == context.author
        while True:
            try:
                # 5 min timeout
                reaction, user = await self.bot.wait_for("reaction_add", timeout=300, check=isAuthor)
                
                await message.remove_reaction(reaction, user) 
                if message == reaction.message:
                    if reaction.emoji == "⬅️":
                        # show prev
                        index -= 1 if index > 0 else 0
                    elif reaction.emoji == "➡️":
                        # show next
                        index += 1 if index < results_count - 1 else 0
                    await message.edit(embed=getPanel(index))
            except asyncio.TimeoutError: 
                print(f"DROPPING jisho nav handle for query: `{' '.join(queryTerms)}`")
                await message.remove_reaction('➡️', self.bot.user)
                await message.remove_reaction('⬅️', self.bot.user)
                break

def setup(client):
    client.add_cog(Search(client, 'AIzaSyCtJB-5h7Onbn72PpaaPRY4adsNKcd6CNM'))
