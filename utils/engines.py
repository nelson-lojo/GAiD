from datetime import timedelta, datetime
from typing import Dict, List
from utils.tracking import Tracker
from discord import Color
from utils.query import Query
from utils.result import Result, Page, Field
from utils.keys import keys
from requests import get as requestsGet
from json import loads as jsonLoads

class WAlphaQuery(Query):

    url = f"http://api.wolframalpha.com/v2/query?appid={keys['walpha']}&input={{query}}&output=json"
    emoji = '<:walpha:961460932272345148>'

    def __init__(self, queryTerms: List[str]) -> None:
        super().__init__(queryTerms)

    def _querify(self, terms: List[str], **kwargs) -> str:
        kwargs.update({ 'plusJoin' : False })
        return super()._querify(terms, **kwargs)

    def _parse(self, jsonData: Dict) -> Result:
        data: Dict = jsonData['queryresult']

        result: Result = Result(
            success = data['success'],
            type = "walpha",
            query = self.query,
            pages = []
        )

        if result.success:
            # the first pod is the input interpretation
            for pod in data['pods'][1:]: 
                result.addPage(
                    Page(
                        color = Color.red(),
                        title = f"Query: {result.query}",
                        image = pod['subpods'][0]['img']['src']
                    )
                )
        
        return result

class DuckQuery(Query):

    url = 'https://api.duckduckgo.com/?q={query}&format=json'
    color = Color.orange()
    emoji = '<:duckduck:961460967475138603>'

    def __init__(self, queryTerms: List[str]) -> None:
        super().__init__(queryTerms)

    def _parse(self, jsonData: Dict) -> Result:
        data: Dict = jsonData
        result:Result = Result(
            success = (not data['meta']['src_name'] == 'hi there'), # yes, 'hi there' is literally the signal for failure
            type = "duck",
            query = self.query,
            pages = [],
            failurePage = Page(
                color = self.__class__.color,
                title = f"No result found for query: {self.query}"
            )
        )

        if result.success:
            if data['Abstract'] == '': 
                # if there's no instant answer,
                #   use the page listings
                listing: str = ''
                count: int = 0

                def checkCharLimit(entry: str, total: str) -> bool:
                    return len(entry) > 2048 - len(total)

                for related in data['RelatedTopics']:
                    count += 1
                    if related.get('Topics', False):
                        for topic in related['Topics']:
                            entry: str = f"{count}. [{topic['Text']}]({topic['FirstURL']})\n"
                            if checkCharLimit(entry, listing):
                                break
                            listing += entry
                            count += 1
                    else:
                        entry = f"{count}. [{related['Text']}]({related['FirstURL']})\n"
                        if checkCharLimit(entry, listing):
                            break
                        listing += entry
                
                listing = listing[:-1]
            else:
                # use the instant answer when we have the chance
                listing: str = data['AbstractText'] + \
                    f" [{data['AbstractSource']}]({data['AbstractURL']})"

            result.addPage(
                Page(
                    color = self.__class__.color,
                    title = f"Query: {result.query}",
                    description = listing
                )
            )

        return result

class KGraphQuery(Query):

    url = 'https://kgsearch.googleapis.com/v1/entities:search?' + \
        f'query={{query}}&key={keys["kgraph"]}&limit=1&indent=True'
    emoji = '<:google:961460823778271292>'
    color = Color.blue()

    def __init__(self, queryTerms: List[str]) -> None:
        super().__init__(queryTerms)

    def _parse(self, jsonData: Dict) -> Result:

        result: Result = Result(
            success = ( len(jsonData['itemListElement']) > 0 ),
            type = "kgraph",
            query = self.query,
            pages = [],
            failurePage = Page(
                color = self.__class__.color,
                title = f"No result found for query: {self.query}"
            )
        )

        if result.success:
            data: Dict = jsonData['itemListElement'][0]['result']

            fields: List[Field] = []
            if ddesc := data.get('detailedDescription', False):
                fields = [Field(
                    'Description: ',
                    f"{ddesc['articleBody']} [source]({ddesc['url']})"
                )]
            
            result.addPage(
                Page(
                    color=self.__class__.color,
                    title=data['name'],
                    description=data.get('description', None),
                    fields=fields
                )
            )

        return result

class JishoQuery(Query):

    url = "https://jisho.org/api/v1/search/words?keyword={query}"
    color = Color.green()
    emoji = '<:jisho:961460904074051644>'

    def __init__(self, queryTerms: List[str]) -> None:
        super().__init__(queryTerms)

    # jisho query urls need some chars in the actual query
    def _urlQuery(self) -> str:
        return super()._urlQuery(exclude=['#', '"'])

    def _parse(self, jsonData: Dict) -> Result:
        data: Dict = jsonData['data']

        result: Result = Result(
            success = bool(len(data)),
            type = "jisho",
            query = self.query,
            pages = [],
            failurePage = Page(
                color = self.__class__.color,
                title = f"No result found for query: {self.query}"
            )
        )

        if result.success:
            for answer in data:
                desc: str = f"Result {{index}}\n\n"
                
                # put in readings 
                for form in answer['japanese']:
                    if form.get('word', False) and form.get('reading', False):
                        desc += f"{form['word']} - {form['reading']}"
                    elif form.get('reading', False):
                        desc += f"{form['reading']}"
                    else:
                        desc += f"{form['word']}"
                    desc += '、'
                desc = desc[:-1]

                desc += '\n'

                # put in definitions
                for sense in answer['senses']:
                    desc += f"\n{answer['senses'].index(sense) + 1}. "      # number
                    desc += ', '.join(sense['parts_of_speech']) + ' - ' # parts of speech
                    desc += ', '.join(sense['english_definitions'])     # definitions
                    desc += '\n'                                        # next

                desc += f"[View this result in jisho](https://jisho.org/word/{answer['slug']})"

                result.addPage(
                    Page(
                        color = self.__class__.color,
                        title = f"Query: {self.query}",
                        description = desc,
                        footer = ' '.join(answer['jlpt'])
                    )
                )

        return result

class CSEQuery(Query):

    url = 'https://customsearch.googleapis.com/customsearch/v1'
    pseID = '15b1428872aa7680b' # Programmable Search Engine ID
    color = Color.blue()
    emoji = '<:gsearch:961462326966509579>'

    def __init__(self, queryTerms: List[str]) -> None:
        super().__init__(queryTerms)

    def _getContent(self) -> Dict:
        required = list(filter(lambda term: term[0] == '+', self.queryTerms))
        exclude = list(filter(lambda term: term[0] == '-', self.queryTerms))
        normal = list(filter(lambda term: term[0] not in ['+', '-'], self.queryTerms))

        return {
            'key' : keys['cse'],
            'cx' : CSEQuery.pseID, 
            'exactTerms' : ' '.join(required),
            'excludeTerms' : ' '.join(exclude),
            'q' : ' '.join(normal),
        }

    @Tracker.limit(count = 100, age = timedelta(days = 1), label = "cse")
    def _request(self) -> Result:
        content = self._getContent()

        response = requestsGet(CSEQuery.url, content)

        if response.status_code != 200:
            return Result(success = False, query = self.query, pages = [])
        
        return self._parse(jsonLoads(response.text))


    def _parse(self, jsonData: Dict) -> Result:
        data = jsonData['items']

        # construct the list of sites found
        desc = ""
        for item in data:
            desc += f"{data.index(item) + 1}. [{item['displayLink']}]({item['link']})\n"
        
        # then package it all into a result
        return Result(
            success = True,
            type = "custom page search",
            query = self.query,
            pages = [ Page(
                color = self.__class__.color,
                title = f"Query ({{count}} today): {self.query}",
                description = desc
            )]
        )

class CSEImQuery(CSEQuery):

    emoji = '<:gimages:961462300945035314>'

    def __init__(self, queryTerms: List[str]) -> None:
        super().__init__(queryTerms)

    def _getContent(self) -> Dict:
        # this will feed into <CSEQuery>'s ._request() and thus be tracked
        content = super()._getContent()
        content.update({
            'searchType' : 'image'
        })
        return content

    def _parse(self, jsonData: Dict) -> Result:
        data: List[Dict] = jsonData['items']

        result: Result = Result(
            success=True,
            type = "custom image search",
            query = self.query,
            pages = []
        )
        for item in data:
            result.addPage(
                Page(
                    color = self.__class__.color,
                    title = f"Query {{count}} today: {self.query}",
                    description = f"Result {{index}}: {item['snippet']} [{item['displayLink']}]({item['image']['contextLink']})",
                    image = item['link'],
                )
            )
        
        return result

class UDictQuery(Query):
    
    url = 'https://api.urbandictionary.com/v0/define?term={query}'
    color = Color.from_rgb(0,0,0)
    emoji = '<:urban:961460875309498428>'

    def __init__(self, queryTerms: List[str]) -> None:
        super().__init__(queryTerms)

    def _urlQuery(self) -> str:
        return super()._urlQuery(plusJoin=True)

    def _parse(self, jsonData: Dict) -> Result:
        data: List[Dict] = jsonData['list']

        result: Result = Result(
            success = bool(len(data)),
            type = "urban dictionary",
            query = self.query,
            pages = [],
            failurePage = Page(
                color = self.__class__.color,
                title = f"No result found for query: {self.query}"
            )
        )

        if result.success:
            for answer in data:
                desc: str = f"Result {{index}}: {answer['word']}\n\n"
                
                date = datetime.strptime(answer['written_on'], "%Y-%m-%dT%H:%M:%S.%fZ")

                def clean(string: str) -> str:
                    return string.replace('[', '').replace(']', '')

                # definition, example, author, link
                desc += f"{clean(answer['definition'])}\n\n"
                desc += f"*{clean(answer['example'])}*\n\n"
                desc += f"**by {answer['author']} on {date.strftime('%c')}**\n"
                desc += f"[View this result in urban dictionary]({answer['permalink']})"

                result.addPage(
                    Page(
                        color = self.__class__.color,
                        title = f"Query: {self.query}",
                        description = desc
                    )
                )

        return result
