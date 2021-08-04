from utils.result import Result
from typing import Callable, Dict, List, Tuple
from json import loads as jsonLoads
from requests import get as requestGet

class Query:

    def __init__(self, queryTerms: List[str]) -> None:
        
        self.queryTerms = queryTerms
        self.query = ' '.join(queryTerms)

    def __repr__(self) -> str:
        return f"Query(\"{self.query}\")"

    def _querify(self, terms: List[str], **kwargs) -> str:
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

    def _request(self) -> Result:
        response = requestGet(
            type(self).url.format(
                query = self._querify(self.queryTerms)
            )
        )

        if response.status_code != 200:
            return Result(success=False, query=self.query, pages=[])
        
        return self._parse(jsonLoads(response.text))

    def _parse(self, jsonData: Dict) -> Result:
        raise NotImplementedError

    def fulfill(self) -> Result:
        # try:
        return self._request()
        # except:
            # return Result(success=False)
