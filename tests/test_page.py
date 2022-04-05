import dataclasses
from random import randint, randrange
import unittest as ut
from unittest.mock import PropertyMock, patch, MagicMock, call
from utils.result import Field, Page
from discord import Embed, Color

class FieldTests(ut.TestCase):

    def setUp(self):
        self.name = "name"
        self.value = "value"

    def test_creates_all(self):
        self.field = Field(name=self.name, value=self.value)
        self.assertEqual(self.field.name, self.name)
        self.assertEqual(self.field.value, self.value)

    def test_creates_name_with_no_value(self):
        self.field = Field(name=self.name)
        self.assertEqual(self.field.name, self.name)
        self.assertEqual(self.field.value, None)

    def test_errors_if_called_without_args(self):
        def func():
            self.field = Field()
        self.assertRaises(TypeError, func)

    def test_errors_if_called_with_value_only(self):
        def func():
            self.field = Field(value=self.value)
        self.assertRaises(TypeError, func)

    def test_errors_on_mutation_of_name(self):
        self.field = Field(name=self.name)
        def func():
            self.field.name = "xd"
        self.assertRaises(dataclasses.FrozenInstanceError, func)

    def test_errors_on_assignment_of_value(self):
        self.field = Field(name=self.name)
        def func():
            self.field.value = "xd"
        self.assertRaises(dataclasses.FrozenInstanceError, func)

    def test_errors_on_mutation_of_value(self):
        self.field = Field(name=self.name, value=self.value)
        def func():
            self.field.value = "xd"
        self.assertRaises(dataclasses.FrozenInstanceError, func)

class PageTests(ut.TestCase):

    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)

    def setUp(self) -> None:
        self.color = Color.blue()
        self.title = "title"
        self.desc = f"description {{index}} {{ind}} {{number}} {{total}}"
        self.img = "image.url/%27a+b"
        self.foot = "footer"
        n = 6
        self.fields = [ MagicMock() for _ in range(n) ]
        for field in self.fields:
            field.name = PropertyMock()
        for field in self.fields[:n//2]:
            field.value = PropertyMock()

    def test_valid_creation(self):
        self.page = Page(self.color, self.title, self.desc, self.img, footer=self.foot)

        self.assertEqual(self.page.color, self.color)
        self.assertEqual(self.page.title, self.title)
        self.assertEqual(self.page.description, self.desc)
        self.assertEqual(self.page.image, self.img)
        self.assertEqual(self.page.footer, self.foot)
    
    @patch("utils.result.Embed")
    def test_makes_embed_with_all(self, new_embed):
        self.page = Page(self.color, self.title, self.desc, 
                            self.img, fields=self.fields, footer=self.foot)
        
        number = 14
        out_of = 2387
        indexed_string = self.desc.replace(r'{index}', f"{number}/{out_of}")
        embed = self.page.embed(number=number, total=out_of)

        new_embed.assert_called()
        new_embed.assert_called_with(color=self.color)

        self.assertEqual(embed.title, self.title)
        
        self.assertEqual(embed.description, indexed_string)
        
        embed.set_image.assert_called()
        embed.set_image.assert_called_with(url=self.img)
        
        embed.add_field.assert_has_calls([
            call(name=f.name, value=f.value) 
            for f in self.fields ])

        embed.set_footer.assert_called()
        embed.set_footer.assert_called_with(text=self.foot)

    @patch("utils.result.Embed")
    def test_makes_embed_without_fields(self, new_embed):
        self.page = Page(self.color, self.title, self.desc, self.img, footer=self.foot)
        number = 14
        out_of = 2387
        indexed_string = self.desc.replace(r'{index}', f"{number}/{out_of}")
        embed = self.page.embed(number=number, total=out_of)

        new_embed.assert_called()
        new_embed.assert_called_with(color=self.color)

        self.assertEqual(embed.title, self.title)
        
        self.assertEqual(embed.description, indexed_string)
        
        embed.set_image.assert_called()
        embed.set_image.assert_called_with(url=self.img)
        
        embed.set_footer.assert_called()
        embed.set_footer.assert_called_with(text=self.foot)

    @patch("utils.result.Embed")
    def test_makes_embed_with_various_args(self, new_embed):
        page_num  = randint(0, 5)
        tot_pages = page_num + randint(0, 5)
        indexed_string = self.desc.replace(r'{index}', f"{page_num}/{tot_pages}")

        def all_bits(i):
            if i == 0: return []
            if i == 1: return ['0', '1']
            bs = all_bits(i-1)
            bit_strings = []
            for b_string in bs:
                bit_strings.append(b_string + '0')
                bit_strings.append(b_string + '1')
            yield from bit_strings

        def all_arg_sets(arg_legend):
            for bit_string in all_bits(len(arg_legend)):
                args = []
                kwargs = {}
                for bit, arg in zip(bit_string, arg_legend):
                    if int(bit):
                        if arg['keyword']:
                            kwargs[arg['keyword']] = arg['value']
                        else:
                            args.append(arg['value'])
                
                yield Page(*args, **kwargs), args, kwargs

        arg_super_set = [
            { 'value' : self.color },
            { 'keyword' : 'title',
              'value'   : self.title },
            { 'keyword' : 'description',
              'value'   : self.desc },
            { 'keyword' : 'image',
              'value'   : self.img },
            { 'keyword' : 'fields',
              'value'   : self.fields },
            { 'keyword' : 'footer',
              'value'   : self.foot },
        ]
        
        for page, args, kwargs in all_arg_sets(arg_super_set):
            embed = page.embed(number=page_num, total=tot_pages)

            new_embed.assert_called()
            new_embed.assert_called_with(color=args[0])

            if 'title' in kwargs: self.assertEqual(embed.title, self.title)
            if 'description' in kwargs: self.assertEqual(embed.description, indexed_string)
            
            if 'image' in kwargs:
                embed.set_image.assert_called()
                embed.set_image.assert_called_with(url=self.img)

            if 'fields' in kwargs:
                embed.add_field.assert_has_calls(
                    [ call(name=f.name, value=f.value) 
                      for f in self.fields ])

            if 'footer' in kwargs:
                embed.set_footer.assert_called()
                embed.set_footer.assert_called_with(text=self.foot)

            

        


