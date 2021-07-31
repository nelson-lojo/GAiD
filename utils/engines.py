from typing import Dict, List, Tuple
from utils.keys import keys
from utils.result import Field, Page, Result
import requests
import json
from discord import Color

def failure(query: str = None) -> Result:
    return Result(success=False, query=query, pages=[])

def querify(terms: List[str], plusJoin: bool=True, exclude: List[str]=[]) -> str:
    mapping: List[Tuple[str]] = [
        ('&', '%26'),
        ('%', '%25'),
        ('#', '%23'),
        ('?', '%3F'),
        ('+', '%2B')
    ]
    newTerms: List[str] = []
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

def walpha(queryTerms: List[str]) -> Result:
    query: str = querify(queryTerms, False)
    # short answer api
    # url = f"http://api.wolframalpha.com/v2/result?appid={appID}&i={query}"
    
    # full answer api

    res = requests.get(
        f"http://api.wolframalpha.com/v2/query?appid={keys['walpha']}&input={query}&output=json"
    )
    if res.status_code != 200:
        return failure(' '.join(queryTerms))

    # should error if this field is not there
    response: Dict = json.loads(res.text)['queryresult']

    result: Result = Result(
        response['success'],
        query=' '.join(queryTerms),
        pages=[]
    )
    
    if result.success:
        for pod in response['pods'][1:]:
            result.addPage(
                Page(
                    color=Color.red(),
                    title=f"Query: {result.query}",
                    image=pod['subpods'][0]['img']['src']
                )
            )

    return result

def duck(queryTerms: List[str]) -> Result:

    res = requests.get(
        f'https://api.duckduckgo.com/?q={querify(queryTerms)}&format=json'
    )

    if res.status_code != 200:
        return failure(' '.join(queryTerms))

    response: Dict = json.loads(res.text)
    result: Result = Result(
        success=(not response['meta']['src_name'] == 'hi there'), # yes, 'hi there' is literally the string
        query=' '.join(queryTerms),
        pages=[]
    )
    if result.success:
        if response['Abstract'] == '':
            listing: str = ''
            count: int = 0

            def checkCharLimit(entry: str, total: str) -> bool:
                return len(entry) > 2048 - len(total)

            for related in response['RelatedTopics']:
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
            listing: str = response['AbstractText'] + \
                f" [{response['AbstractSource']}]({response['AbstractURL']})"

        result.addPage(
            Page(
                color=Color.orange(),
                title=f"Query: {result.query}",
                description=listing
            )
        )
    return result

def kgraph(queryTerms: List[str]) -> Result:
    res = requests.get(
        'https://kgsearch.googleapis.com/v1/entities:search?' + \
        f'query={querify(queryTerms)}&key={keys["kgraph"]}&limit=1&indent=True'
    )
    if res.status_code != 200:
        return failure(' '.join(queryTerms))

    response: Dict = json.loads(res.text)
    
    result: Result = Result(
        success=(len(response['itemListElement'] )> 0),
        query=' '.join(queryTerms),
        pages=[]
    )

    if result.success:
        data: Dict = response['itemListElement'][0]['result']

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

def jisho(queryTerms: List[str]) -> Result:

    res = requests.get(
        "https://jisho.org/api/v1/search/words?keyword=" + \
            querify(queryTerms, exclude=['#', '"'])
    )

    if res.status_code != 200:
        return failure(' '.join(queryTerms))
    
    data: Dict = json.loads(res.text)['data']
    
    result: Result = Result(
        success=bool(len(data)),
        query=' '.join(queryTerms),
        pages=[],
        failurePage=Page(
            color=Color.green(),
            title=f"No result found for query: {' '.join(queryTerms)}"
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

            # desc += '、'.join([
            #     f"{form['word']} - {form['reading']}" \
            #         if form.get('word', False) and form.get('reading', False) \
            #         else (
            #             f"{form['reading']}" \
            #                 if form.get('reading', False) \
            #                 else f"{form['word']}"
            #         )
            #     for form in answer['japanese']
            # ])

            desc += '\n'

            # put in definitions
            for sense in answer['senses']:
                desc += f"\n{answer['senses'].index(sense) + 1}. "      # number
                desc += ', '.join(sense['parts_of_speech']) + ' - ' # parts of speech
                desc += ', '.join(sense['english_definitions'])     # definitions
                desc += '\n'                                        # next

            # desc += '\n\n'.join([
            #     f"{answer['senses'].index(sense)}. {', '.join(sense['parts_of_speech'])} - " + \
            #         ', '.join(sense['english_definitions'])
            #     for sense in answer['senses']
            # ])

            # desc += '\n'
            desc += f"[View this result in jisho](https://jisho.org/word/{answer['slug']})"

            result.addPage(
                Page(
                    color=Color.green(),
                    title=f"Query: {' '.join(queryTerms)}",
                    description=desc,
                    footer=' '.join(answer['jlpt'])
                )
            )
            pageNum += 1

    return result

def cse(queryTerms: List[str]) -> Result:
    
    # filetype = None
    # for term in queryTerms:
    #     if term.startswith('file:'):
    #         filetype = term[5:]
    # if filetype is not None:
    #     queryTerms = queryTerms.remove(f"file:{filetype}")
    
    required = list(filter(lambda term: term[0] == '+', queryTerms))
    exclude = list(filter(lambda term: term[0] == '-', queryTerms))
    normal = list(filter(lambda term: term[0] not in ['+', '-'], queryTerms))

    url = 'https://customsearch.googleapis.com/customsearch/v1'
    content = {
        'key' : keys['cse'],
        'cx' : '15b1428872aa7680b', # Programmable Search Engine ID
        'exactTerms' : ' '.join(required),
        'excludeTerms' : ' '.join(exclude),
        'q' : ' '.join(normal),
    }

    # if filetype is not None:
    #     content.update({'fileType' : filetype})

    res = requests.get(url, content)

    if res.status_code != 200:
        return failure(' '.join(queryTerms))
    
    response = json.loads(res.text)

    desc = ""
    for item in response['items']:
        desc += f"{response['items'].index(item) + 1}. [{item['displayLink']}]({item['link']})\n"
    
    return Result(
        success=True,
        query=' '.join(queryTerms),
        pages=[Page(
            color=Color.blue(),
            title=f"Query: {' '.join(queryTerms)}",
            description=desc
        )]
    )
