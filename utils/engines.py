from datetime import timedelta
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

    def __init__(self, queryTerms: List[str]) -> None:
        super().__init__(queryTerms)

    def _querify(self, terms: List[str], **kwargs) -> str:
        kwargs.update({ 'plusJoin' : False })
        return super()._querify(terms, **kwargs)

    def _parse(self, jsonData: Dict) -> Result:
        data: Dict = jsonData['queryresult']

        result: Result = Result(
            success = data['success'],
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

    def __init__(self, queryTerms: List[str]) -> None:
        super().__init__(queryTerms)

    def _parse(self, jsonData: Dict) -> Result:
        data: Dict = jsonData
        result:Result = Result(
            success = (not data['meta']['src_name'] == 'hi there'), # yes, 'hi there' is literally the signal for failure
            query = self.query,
            pages = []
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
                    color=Color.orange(),
                    title=f"Query: {result.query}",
                    description=listing
                )
            )

        return result

class KGraphQuery(Query):

    url = 'https://kgsearch.googleapis.com/v1/entities:search?' + \
        f'query={{query}}&key={keys["kgraph"]}&limit=1&indent=True'

    def __init__(self, queryTerms: List[str]) -> None:
        super().__init__(queryTerms)

    def _parse(self, jsonData: Dict) -> Result:

        result: Result = Result(
            success = ( len(jsonData['itemListElement']) > 0 ),
            query = self.query,
            pages = []
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
                    color=Color.blue(),
                    title=data['name'],
                    description=data.get('description', None),
                    fields=fields
                )
            )

        return result

class JishoQuery(Query):

    url = "https://jisho.org/api/v1/search/words?keyword={query}"

    def __init__(self, queryTerms: List[str]) -> None:
        super().__init__(queryTerms)

    # jisho query urls need some chars in the actual query
    def _urlQuery(self) -> str:
        return super()._urlQuery(exclude=['#', '"'])

    def _parse(self, jsonData: Dict) -> Result:
        data: Dict = jsonData['data']

        result: Result = Result(
            success = bool(len(data)),
            query = self.query,
            pages = [],
            failurePage = Page(
                color = Color.green(),
                title = f"No result found for query: {self.query}"
            )
        )

        if result.success:
            numPages: int = len(data)
            pageNum: int = 1
            for answer in data:
                desc: str = f"Result {pageNum}/{numPages}\n\n"
                
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
                        color = Color.green(),
                        title = f"Query: {self.query}",
                        description = desc,
                        footer = ' '.join(answer['jlpt'])
                    )
                )
                pageNum += 1

        return result

class CSEQuery(Query):

    url = 'https://customsearch.googleapis.com/customsearch/v1'
    pseID = '15b1428872aa7680b' # Programmable Search Engine ID

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
            query = self.query,
            pages = [ Page(
                color = Color.blue(),
                title = f"Query ({{count}} today): {self.query}",
                description = desc
            )]
        )

class CSEImQuery(CSEQuery):

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
            query = self.query,
            pages = []
        )
        for item in data:
            result.addPage(
                Page(
                    color = Color.blue(),
                    title = f"Query {{count}}: {self.query}",
                    description = f"Result {{index}}: {item['snippet']} [{item['displayLink']}]({item['image']['contextLink']})",
                    image = item['link'],
                )
            )
        
        return result

class SerpMQuery(Query):

    url = ""
    def __init__(self, queryTerms: List[str]) -> None:
        super().__init__(queryTerms)

    @Tracker.limit(count = 250, age = timedelta(days = 30), label = "Serp Master")
    def _request(self) -> Result:
        headers = {
            'Content-Type': 'application/json'
        }

        content = {
            'scraper' : 'google_search',
            'q' : self.query,
            'parse' : 'true',
            'access': ''
        }

        


    def _parse(self, jsonData: Dict) -> Result:
        return super()._parse(jsonData)

        title = f"Query ({{count}} this month): {self.query}"