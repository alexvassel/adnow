# -*- coding: utf-8 -*-

import unittest

from helpers import get_next_page


class HeaderParsingTest(unittest.TestCase):
    data = '''<https://api.github.com/repositories/4164482/commits?page=782>; rel="next", <https://api.github.com/repositories/4164482/commits?page=782>; rel="last", <https://api.github.com/repositories/4164482/commits?page=1>; rel="first", <https://api.github.com/repositories/4164482/commits?page=780>; rel="prev"'''

    def test_header_parsing(self):
        expect = {'rel="next"': '<https://api.github.com/repositories/4164482/commits?page=782>',
                  'rel="prev"': '<https://api.github.com/repositories/4164482/commits?page=780>',
                  'rel="last"': '<https://api.github.com/repositories/4164482/commits?page=782>',
                  'rel="first"': '<https://api.github.com/repositories/4164482/commits?page=1>'}
        r = get_next_page(self.data)
        self.assertDictEqual(r, expect)

    def test_common(self):
        for kind in (str, list, dict, set, int, float):
            r = get_next_page(kind())
            self.assertIsInstance(r, dict)
            self.assertDictEqual(r, {})
        for obj in ([1], (1,), dict(a=1), 1, 1.0):
            self.assertRaises(AttributeError, get_next_page, obj)
        self.assertRaises(TypeError, get_next_page)
        self.assertRaises(ValueError, get_next_page, ' ')


if __name__ == '__main__':
    unittest.main()
