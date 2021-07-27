from typing import Any, Dict, List, Optional
from discord import Embed, Color
from dataclasses import dataclass, field

@dataclass(frozen=True)
class Page:
    color: Color
    title: str = None
    description: str = None
    image: str = None
    fields: List[Dict] = field(default_factory=list)

class Result:

    def __init__(self, success: bool, query: str = None, pages: List[Page] = []) -> None:
        self.success: bool = success
        
        if self.success:
            assert query is not None and isinstance(query, str), "Query must be a string"
            assert isinstance(pages, list), "Must provide a <list> of <Page>s"
            self.query: str = query
            self.pages: List[Page] = pages

    def __repr__(self) -> str:
        rep = f"Result: \n"
        rep+= f"\tSuccess: {self.success}\n"
        if self.success:
            rep+= f"\tQuery: `{self.query}`"
            rep+= f"\tPages: {self.pages}"
        return rep

    def addPage(self, page: Page) -> None:
        self.pages.append(page)

    def getPage(self, index: int) -> Embed:
        # get the `index` page of the embed

        if not self.success:
            return self.showFailurePage()

        if index >= len(self.pages):
            raise IndexError(
                f"Cannot retrieve page at index {index} as there are only {len(self.pages)} pages"
            )
        
        page = self.pages[index]
        embed = Embed(
            title=(page.title if page.title is not None else f"Query: {self.query}"),
            color=page.color
        )
        
        if page.description is not None:
            embed.description = page.description

        if page.image is not None:
            embed.set_image(url=page.image)
        
        for field in page.fields:
            pass

        return embed

    def showFailurePage(self) -> Embed:
        return Embed(
            title="We encountered an error",
            description="Please try again after some time",
            color=Color.orange()
        )
