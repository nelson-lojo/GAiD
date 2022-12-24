from utils.query import Query
from utils.result import Result

# This class is meant to be the event-driven version of the Navigation panel in navigation.py

class Navigator:
    def __init__(self, queries: List[Query], command: ApplicationCommand) -> None:
        self.queries: Dict[str, Query] = {
            query.emoji : query
            for query in queries
        }

        self.results: Dict[str, Result] = {
            query.emoji : None
            for query in queries
        }

        self.query_order = queries
        self.command = command

    def _get_result(self, emoji: str) -> Result:
        """allow user to request another query by reacting with another emoji"""
        if self.results.get(emoji, None) is None:
            self.results[emoji] = self.queries[emoji].fulfill()
        
        if not self.results[emoji].success and emoji in self.queries.keys():
            self.queries.pop(emoji)

        return self.results[emoji]

    def sendNavigator(self) -> Dict[str, Any]:
        """send the initial message to the channel requested by the user"""

        index = 0
        result = self._get_result(self.query_order[index].emoji)

        while (not result.success) and len(self.query_order) > index + 1:
            index += 1
            result = self._get_result(self.query_order[index].emoji)
        
        # TODO:
        # store page index
        # add navigation buttons -- TODO: Add the name of each engine to these
        # send message

        # self.message: Message = await context.send(embed=result.getPage(0))
        # self.current_res = self.query_order[index].emoji
        # self.page_number = 0

    def _check(self, reaction, user):
        """verify that we only change the displayed page if the user that requests is correct"""
        return user == self.author and reaction.message == self.message

    def updateNavigator(self, interaction) -> Dict[str, Any]:
        pass
        # TODO: implement
