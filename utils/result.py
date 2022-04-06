from multiprocessing.sharedctypes import Value
from typing import List, Type
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

    def __init__(self, success: bool, type: str = "unspecified", query: str = None, 
                    pages: List[Page] = [], failurePage: Page = defaultFail) -> None:
        primitive_args = {
            'success' : [success, bool],
            'type' : [type, str],
            'query' : [query, str],
            'pages' : [pages, list],
        }

        for arg, value in primitive_args.items():
            if value[0] is None:
                raise ValueError(f"Argument {arg} cannot be None")
            if not isinstance(value[0], value[1]):
                raise TypeError(f"Argument {arg} must be type {value[1]}. Got: {type(value[0])}")
            setattr(self, arg, value[0])

        if failurePage is None:
            raise ValueError(f"Argument failurePage cannot be None")
        self.fail: Page = failurePage

    def __repr__(self) -> str:
        rep = f"Result: \n"
        rep+= f"\tSuccess: {self.success}\n"
        if self.success:
            rep+= f"\tQuery: `{self.query}`"
            rep+= f"\tPages: {self.pages}"
        return rep

    def _getFailPage(self) -> Embed:
        log(f"FAILED {self.type} request with query: `{self.query}`")
        return self.fail.embed()

    def addPage(self, page: Page) -> None:
        self.pages.append(page)

    def getPage(self, index: int) -> Embed:
        # get the `index` page of the embed

        if not self.success:
            return self._getFailPage()

        if index >= len(self.pages):
            raise IndexError(
                f"Cannot retrieve page at index {index} as there are only {len(self.pages)} pages"
            )
        
        page = self.pages[index]
        return page.embed(index + 1, len(self.pages))

