from discord.colour import Color
from utils.result import Field, Page, Result
from typing import Dict, List, Tuple
from json import loads as jsonLoads
from requests import get as requestGet

class Query:

    def __init__(self, queryTerms: List[str]) -> None:
        
        self.queryTerms = queryTerms
        self.query = ' '.join(queryTerms)
        self.url = type(self).url.format(query = self._urlQuery())

    def __repr__(self) -> str:
        return f"{type(self).__name__}(\"{self.query}\")"

    def _urlQuery(self, **kwargs) -> str:
        mapping: List[Tuple[str]] = [
            ('&', '%26'),
            ('%', '%25'),
            ('#', '%23'),
            ('?', '%3F'),
            ('+', '%2B')
        ]
        exclude : List[str] = kwargs.get('exclude'  , []   )
        plusJoin: bool      = kwargs.get('plusJoin' , True )
        newTerms: List[str] = []
        
        for term in self.queryTerms:
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

    def _request(self) -> Result:
        response = requestGet(self.url)

        if response.status_code != 200:
            return Result(success=False, query=self.query, pages=[],
                failurePage=Page(
                    color=Color.orange(),
                    title = "We encountered a problem",
                    description= f"{type(self)}: Request failed",
                    fields=[Field(
                        name=f"Status code: {response.status_code}",
                        value=f"{response.text}"
                    )]
                )
            )
        
        return self._parse(jsonLoads(response.text))

    def _parse(self, jsonData: Dict) -> Result:
        raise NotImplementedError

    def fulfill(self) -> Result:
        # try:
        return self._request()
        # except:
            # return Result(success=False)
