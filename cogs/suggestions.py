from discord import Color
import sqlalchemy as sa
from utils.keys import keys
from discord.ext import commands
from datetime import datetime
from utils.result import Field, Result, Page

class Suggestion_Box(commands.Cog):

    _db = sa.create_engine(keys['db'])


    def __init__(self, bot):
        self.bot = bot

        # Initialize the table for storing suggestions
        self.metaData = sa.MetaData()
        self.metaData.bind = type(self)._db
        self.table = sa.Table(
            'suggestions', self.metaData,
            sa.Column('id', sa.INTEGER, primary_key=True, autoincrement=True), 
            sa.Column('content', sa.TEXT), 
            sa.Column('time', sa.TIMESTAMP, default=sa.func.now())
        )
        self.table.create(type(self)._db, checkfirst=True)

    @commands.command(name='suggest', aliases=['sugg'], brief="Give a suggestion to the developer", pass_context=True)
    async def pause(self, context, *text):
        suggestion = ' '.join(text)

        successPage = Page(
            color=Color.blue(),
            title="New suggestion added",
            fields=[ Field("Suggestion", suggestion),
                        Field("Time", datetime.now()) ]
        )
        failurePage = Page(
            color=Color.orange(),
            title="Failed to add new suggestion",
            description="Please try again after some time. If the problem persists, contact the developer"
        )

        try:
            self.table.insert().values(content=suggestion, time=datetime.now()).execute()
            success = True
        except:
            success = False
        finally:
            result = Result(
                success,
                "New Suggestion",
                query=suggestion,
                pages=[successPage],
                failurePage=failurePage
            )
        
        await context.send(embed=result.getPage(0))


def setup(client):
    client.add_cog(Suggestion_Box(client))