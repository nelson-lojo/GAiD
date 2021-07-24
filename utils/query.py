from result import Result
from typing import Callable, List


class Query:

    def __init__(self, queryTerms: List[str], method: Callable) -> None:
        
        self.queryTerms = queryTerms
        self.query = ' '.join(queryTerms)
        
        self.method = method

    def __repr__(self) -> str:
        return f"Query(\"{self.query}\", {self.method.__name__})"

    def fulfill(self) -> Result:
        try:
            return self.method(self.queryTerms)
        except:
            return Result(success=False)
