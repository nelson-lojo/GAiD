from typing import List
from utils.tools.misc import log
from discord import Embed, Color
from dataclasses import dataclass, field

from discord.ext.commands.context import Context

@dataclass(frozen=True)
class Field:
    name: str
    value: str = None

@dataclass
class Page:
    color: Color = None
    title: str = None
    description: str = None
    image: str = None
    fields: List[Field] = field(default_factory=list)
    footer: str = None

    def embed(self, number: int = None, total: int = None) -> Embed:
        embed = Embed(
            color=self.color
        )

        if self.title is not None:
            embed.title = self.title

        if self.description is not None:
            if number is not None and total is not None:
                embed.description = self.description.replace('{index}', f"{number}/{total}")
            else:
                embed.description = self.description

        if self.image is not None:
            embed.set_image(url=self.image)

        for field in self.fields:
            embed.add_field(
                name=field.name,
                value=field.value
            )
        
        if self.footer is not None:
            embed.set_footer(text=self.footer)

        return embed

defaultFail = Page(
    color=Color.orange(),
    title="We encountered an error",
    description="Please try again after some time",
)

class Result:

    def __init__(self, success: bool, type: str = "unspecified", query: str = None, pages: List[Page] = [], failurePage: Page = defaultFail) -> None:
        self.success: bool = success
        assert query is not None and isinstance(query, str), "Query must be a string"
        assert isinstance(pages, list), "Must provide a <list> of <Page>s"
        self.query: str = query
        self.pages: List[Page] = pages
        self.fail = failurePage
        self.type = type

    def __repr__(self) -> str:
        rep = f"Result: \n"
        rep+= f"\tSuccess: {self.success}\n"
        if self.success:
            rep+= f"\tQuery: `{self.query}`"
            rep+= f"\tPages: {self.pages}"
        return rep

    def _getFailPage(self) -> Embed:
        return self.fail.embed()

    def addPage(self, page: Page) -> None:
        self.pages.append(page)

    def getPage(self, index: int) -> Embed:
        # get the `index` page of the embed

        if not self.success:
            return self.fail.embed()

        if index >= len(self.pages):
            raise IndexError(
                f"Cannot retrieve page at index {index} as there are only {len(self.pages)} pages"
            )
        
        page = self.pages[index]
        return page.embed(index + 1, len(self.pages))

    async def showFail(self, context: Context) -> None:

        log(f"FAILED {self.type} request with query: `{self.query}`")

        await context.send(embed = self._getFailPage())
