from typing import List, Tuple
from keys import keys
import requests
import json
from result import Page, Result
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

    if result.success:
        for pod in result['pods'][1:]:
            result.pages.append(
                Page(
                    Color.red(), 
                    image=pod['subpods'][0]['img']['src']
                )
            )

    return result


