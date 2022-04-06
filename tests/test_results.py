from multiprocessing.sharedctypes import Value
from random import randint
from unittest.mock import PropertyMock, patch, MagicMock, call
import unittest as ut
from utils.result import Result, Page


class ResultTests(ut.TestCase):

    @patch("utils.result.Page", spec=Page)
    def setUp(self, mock_page) -> None:
        self.mock_page = mock_page
        self.success = True
        self.type = "testing"
        self.query = "who is taylor swift"
        self.pages = [ mock_page() for _ in range(randint(0,10))]
        self.fail_page = mock_page()

    def test_proper_init(self):
        self.res = Result(self.success, self.type, self.query, self.pages, self.fail_page)

        self.assertEqual(self.res.success, self.success)
        self.assertEqual(self.res.query, self.query)

        for page, reference in zip(self.res.pages, self.pages):
            self.assertEqual(page, reference)
            reference.assert_not_called()
        
        self.assertEqual(self.res.fail, self.fail_page)
        self.fail_page.assert_not_called()

        self.assertEqual(self.res.type, self.type)

    def test_init_input_sanitization(self):
        bad_inputs = {
            'success' : ["success", 1, 4, []],
            'type'    : [4, 4.2, []],
            'query'   : [4.2, 4, []],
            'pages'   : [1, 1.2],
            # 'failurePage' : ['failed', 2, 4.2, []]
        }

        good_inputs = {
            'success' : self.success,
            'type'    : self.type,
            'query'   : self.query,
            'pages'   : self.pages,
            'failurePage' : self.fail_page
        }

        for arg, values in bad_inputs.items():
            for value in values:
                args = good_inputs.copy()
                args[arg] = value
                try:
                    self.res = Result(**args)
                    self.assertTrue(False, 
                        f"Result init did not fail for invalid {arg}:" + \
                        f" {type(value)}:{repr(value)}")
                except TypeError:
                    pass

    def test_init_none_input(self):
        good_inputs = {
            'success' : self.success,
            'type'    : self.type,
            'query'   : self.query,
            'pages'   : self.pages,
            'failurePage' : self.fail_page
        }
        
        for key in good_inputs.keys():
            args = good_inputs.copy()
            args[key] = None
            
            try:
                self.res = Result(**args)
                self.assertTrue(False, f"Result init did not fail for {key} = None")
            except ValueError:
                pass

    def test_repr_successful(self):
        self.res = Result(True, self.type, self.query, self.pages, self.fail_page)
        string = repr(self.res)
        self.assertTrue("Success: True" in string, "Result repr does not report success")
        self.assertTrue(f"Query: " in string, "successful Result repr does not contain query")
        self.assertTrue(f"Pages: " in string, "successful Result repr does not contain pages")

    def test_repr_failure(self):
        self.res = Result(False, self.type, self.query, self.pages, self.fail_page)
        string = repr(self.res)
        self.assertTrue("Success: False" in string)
        self.assertFalse("Query: " in string)
        self.assertFalse("Pages: " in string)

    @patch("utils.result.log")
    def test_getFailPage(self, log_func):
        # fake_page = "page"
        # self.fail_page.embed.return_value(fake_page)
        self.res = Result(False, self.type, self.query, self.pages, self.fail_page)
        

        page = self.res._getFailPage()
        log_func.assert_called()
        self.fail_page.embed.assert_called()
        # self.assertEqual(page, fake_page)

    def test_add_pages(self):
        self.res = self.res = Result(True, self.type, self.query, self.pages, self.fail_page)
        index = len(self.pages)
        self.res.addPage(self.mock_page())
        try:
            self.res.getPage(index)
            self.assertTrue(False, "Added page is not at expected index")
        except:
            pass

    def test_bad_index_page(self):
        self.res = self.res = Result(True, self.type, self.query, self.pages, self.fail_page)
        index = len(self.pages)
        self.assertRaises(IndexError, lambda: self.res.getPage(index))

    @patch("utils.result.Result._getFailPage")
    def test_returns_fail_page(self, get_page):
        self.res = Result(False, self.type, self.query, self.pages, self.fail_page)
        self.res.getPage(0)
        get_page.assert_called()

