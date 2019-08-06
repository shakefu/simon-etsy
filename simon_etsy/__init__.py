import html
import nltk
import time
import logging
import itertools
from collections import defaultdict

import requests
from pytool.lang import Namespace


# API Urls for ease of maintenance and review
urls = Namespace()
urls.shop.listings = 'https://openapi.etsy.com/v2/shops/{shop}/listings/active'

# Request session for connection pooling, etc.
session = requests.Session()


def debug(msg):
    """ Logging helper for more verbose output. """
    logging.getLogger('simon-etsy').debug(msg)


def get_shop_listings(api_key, name, params=None):
    """
    Return the JSON response data for the Etsy API for listing all active items
    in a shop.

    This call may be throttled or paginated by the Etsy API. Use
    `get_all_shop_listings` if you need all results.

    You may add arbitrary additional parameters using the *params* dictionary
    argument.

    This method may raise `~request.exceptions.HTTPError` if the request fails.

    :param str api_key: Etsy API key
    :param str name: Esty store name or ID
    :param str params: Optional additional API parameters
    :returns: JSON response data

    """
    # Copy params so we don't unexpectedly mutate
    params = params.copy() if params else {}
    # Sane settings if nothing is specified
    params.setdefault('api_key', api_key)
    params.setdefault('limit', 100)
    params.setdefault('offset', 0)
    # Get our fully formed URL
    url = urls.shop.listings.format(shop=name)
    # Request and error if needed
    resp = session.get(url, params=params)
    resp.raise_for_status()
    # Return the JSON response as a dict
    return resp.json()


def get_all_shop_listings(api_key, name, params=None, rate=5):
    """
    Return the combined results of paginated calls to get a shop's listings.

    This method will attempt to stay under *rate* limit for the Etsy API.

    You may add arbitrary additional parameters using the *params* dictionary
    argument.

    This method may raise `~request.exceptions.HTTPError` if a request fails.

    :param str api_key: Etsy API key
    :param str name: Esty store name or ID
    :param str params: Optional additional API parameters
    :param int rate: Number of requests per second allowed
    :returns: Concatenated list of results

    """
    params = params or {}
    results = []
    offset = 0
    window = time.monotonic()
    count = 0
    rate_count = 0
    while offset is not None:
        count += 1
        rate_count += 1
        debug(f"Getting page {count} at offset {offset}.")
        # Call the API
        data = get_shop_listings(api_key, name, params)
        # Get more results
        results.extend(data['results'])
        # Get the next offset
        offset = data['pagination']['next_offset']
        # And update params
        params['offset'] = offset

        # Rate limit ourselves for API kindness, if the calls themselves don't
        # keep us below the limit
        remaining = 1.0 - (time.monotonic() - window)
        if remaining >= 0 and rate_count >= rate:
            debug(f"Waiting for rate limit: {remaining}s")
            time.sleep(remaining)
            window = time.monotonic()
            rate_count = 0
        elif remaining < 0:
            window = time.monotonic()
            rate_count = 0

    return results


def get_chunks(tagged):
    """
    Group together parsed words into chunks of words composed of adjectives and
    nouns.

    :param list tagged: List of nltk tokenized sentences
    :returns: List of word groups

    """
    # This is too noisy to be useful
    # debug(f"Chunking {len(tagged)} sentences.")
    # Adjectives and nouns
    grammar = r'KT: {(<JJ>* <NN.*>+ <IN>)? <JJ>* <NN.*>+}'
    # Makes chunks using grammar regex
    chunker = nltk.RegexpParser(grammar)
    # Make a list of tagged parsed chunks
    chunks = list(itertools.chain.from_iterable(
        nltk.chunk.tree2conlltags(chunker.parse(s)) for s in tagged))
    # Join phrases based on grammar tags
    chunks = [' '.join(w[0] for w in group).lower()
                for key, group in itertools.groupby(
                    chunks, lambda l: l[2] != 'O') if key]
    return chunks


def analyze(data):
    """
    Return a list of tuples containing words and their relative weightings.

    :param dict data: Data returned from Etsy API for a shop's listings
    :returns: List of weighted words

    """
    weighted = defaultdict(float)

    count = len(data) + 5

    banned_words = set(('in', 'inch', 'inches', 'ft', 'foot', 'feet', 'mm',
                       'cm', 'm', 'meter', 'meters', 'yards', 'length',
                        'please', 'shipping', 'information', 'seller',
                        'package', 'price', 'product', 'time', 'order',
                        'quality', 'value', 'address', 'feedback', 'wash',
                        'request', 'production', 'packages', 'notification',
                        'issue', 'volume', 'print', 'shop', 'tags',
                        'description', 'etsy', 'store', 'sales', 'download',
                        'https', 'http', 'instant download', 'size'))

    debug(f"Parsing {len(data)} results.")
    for item in data:
        # Pull the title, description, and tags for
        title = item['title']
        title = html.unescape(title)
        desc = item['description']
        desc = html.unescape(desc)
        tags = set(item['tags'])

        # Tokenize the title into words and chunks
        title = nltk.word_tokenize(title)
        title = nltk.pos_tag(title)
        title = [(w[0].lower(), w[1]) for w in title]
        title_words = [w[0] for w in title]
        title_chunks = get_chunks([title])

        # Tokenize the description into sentences, nouns, and chunks
        desc = nltk.sent_tokenize(desc)
        desc = nltk.pos_tag_sents(nltk.word_tokenize(s) for s in desc)
        desc_nouns = [w.lower().replace('*', '') for s in desc
                      for w, t in s if t == 'NN']
        desc_proper = [w.lower().replace('*', '') for s in desc
                       for w, t in s if t == 'NNP']
        chunks = get_chunks(desc)

        # Iterate over all the nouns found and weight them based on frequency,
        # intersection with title
        for word in desc_nouns:
            if 'etsy.com' in word:
                continue
            if word in banned_words:
                continue
            if word in title_words:
                weighted[word] += 100
                continue
            # This would probably help results a bit, but the task said to use
            # just title and description, so it feels like cheating
            # if word in tags:
            #     weighted[word] += 100
            #     continue
            weighted[word] += 1

        # Iterate over all the proper nouns and weight them based on frequency,
        # intersection with title
        for word in desc_proper:
            if 'etsy.com' in word:
                continue
            if word in banned_words:
                continue
            if word in title_words:
                weighted[word] += 50
                continue
            # This would probably help results a bit, but the task said to use
            # just title and description, so it feels like cheating
            # if word in tags:
            #     weighted[word] += 100
            #     continue
            weighted[word] += 1

        # Iterate over all the word groups and weight them based on frequency
        # and intersection with title
        for chunk in chunks:
            if 'etsy.com' in chunk:
                continue
            if chunk in banned_words:
                continue
            if chunk in title_chunks:
                weighted[chunk] += 300
                continue
            # This would probably help results a bit, but the task said to use
            # just title and description, so it feels like cheating
            # if chunk in tags:
            #     weighted[chunk] += 500
            #     continue
            weighted[chunk] += 1

    return sorted([(v, k) for k, v in weighted.items() if v > 50],
                  reverse=True)
