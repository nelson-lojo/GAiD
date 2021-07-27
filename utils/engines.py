from typing import List, Tuple
from utils.keys import keys
from utils.result import Page, Result
import requests
import json
from discord import Color

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
    query = querify(queryTerms, False)
    # short answer api
    # url = f"http://api.wolframalpha.com/v2/result?appid={appID}&i={query}"
    
    # full answer api
    
    url = f"http://api.wolframalpha.com/v2/query?appid={keys['walpha']}&input={query}&output=json"

    res = requests.get(url)
    if res.status_code != 200:
        return {}

    # should error if this field is not there
    response = json.loads(res.text)['queryresult']

    result = Result(
        response['success'],
        query=' '.join(queryTerms)
    )
    print(result)
    if result.success:
        for pod in response['pods'][1:]:
            result.addPage(
                Page(
                    Color.red(), 
                    image=pod['subpods'][0]['img']['src']
                )
            )

    return result


