import os

import mock
from nose import SkipTest
from nose.tools import ok_, eq_, raises
import requests

import simon_etsy


class test_shop_listings:
    def setup(self):
        api_key = os.environ.get('ETSY_API_KEY', None)
        if not api_key:
            raise SkipTest("No API key present")
        self.api_key = api_key
        self.shop = 'printandclay'  # My friend Amanda's etsy

    def test_basic_request(self):
        data = simon_etsy.get_shop_listings(self.api_key, self.shop)
        ok_(data)
        # Not a *ton* to test here since we don't control the APi responses,
        # but a single live integration test is better than one
        ok_('results' in data)
        ok_('pagination' in data)

    @raises(requests.exceptions.HTTPError)
    def test_request_bad_api_key_errors(self):
        simon_etsy.get_shop_listings('', self.shop)

    # Other things to test, if not limited by time
    def test_request_page_offset(self):
        # Try changing the offset
        ...

    def test_request_page_limit(self):
        # Try changing the limit
        ...

    def test_fields(self):
        # Try limiting fields
        ...


class test_all_shop_listings:
    data = {
        'pagination': {
            'next_offset': None,
        },
        'results': [
            {'title': "Test title", 'description': "Test description"},
        ]
    }

    def test_simple_one_page(self):
        # Mock out API calls with semi-real data
        # We would want to use API fixtures here instead
        with mock.patch('simon_etsy.get_shop_listings') as get_shop_listings:
            get_shop_listings.return_value = self.data.copy()

            results = simon_etsy.get_all_shop_listings('api_key', 'shop_name')

        ok_(results)
        eq_(len(results), 1)

    # If we had more time, more tests
    def test_multipage(self):
        # Multiple pages
        ...

    def test_no_results(self):
        # No pages
        ...
