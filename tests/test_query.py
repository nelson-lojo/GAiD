import unittest as ut
from utils.query import Query

class QuerySanityTests(ut.TestCase):
    
    def reprTest(self):
        q = Query(['term', 'two', '+hi', '-other', '#other', '"longer string"'])
        self.assertEqual(
            q.__repr__(),
            "Query(term two +hi -other #other \"longer string\")"
        )

    def ensureParseNotImplemented(self):
        q = Query([]) # empty query

        self.assertRaises(
            NotImplementedError, q._parse, {},
            "Direct instances of Query should not have ._parse implemented"
        )

    @ut.mock.patch('query.Query.url')
    def urlFormattedCorrectly(self, url):
        url = "something {query}"
        q = Query(['correctly', 'made'])
        q._querify = lambda self, terms, **kwargs: '-'.join(terms)
        self.assertEqual(q.url, "something correctly-made")




class QueryRequestsTests(ut.TestCase):

    testURL = "sample URL"

    @ut.mock.patch('query.Query.url')
    @ut.mock.patch('query.requestGet')
    @ut.mock.patch('query.jsonLoads')
    def setUp(self, url, get, loads) -> None:
        url = type(self).testURL
        get = None
        q = Query([])

    
    def requestUsesClassUrl(self, queryURL, fakeGet):
        q = Query([])
        
        def getSubstitute(url):
            self.assertIs(url, type(self).testURL, 
                "Query instance ._request must use class property url")

            fakeResponse = object()
            fakeResponse.status_code = 200
            fakeResponse.text = "{}"
            return fakeResponse
    
        fakeGet = getSubstitute



