import sys
import logging

from pytool.cmd import Command

import simon_etsy


class Main(Command):
    """
    simon-etsy CLI command

    This command provides the ability to find weighted terms for a given Etsy
    store.

    You must provide an API key in order to access the Etsy API.

    See the command ``--help`` for CLI options and arguments.

    Example usage::

        simon-etsy --api-key XXXXwmysl2m0gmdije57XXXX --top 5 printandclay

    """

    def set_opts(self):
        """ Set CLI flags and arguments. """
        self.opt('--api-key', '-a', required=True, help="Etsy API key")
        self.opt('--top', '-t', type=int, default=5,
                 help="Number of top keywords to display")
        self.opt('--debug', action='store_true', help="Debug output")
        self.opt('store', nargs='+', help="Store name or ID")

    def parser_opts(self):
        """ Set options for the argument parser. """
        return dict(auto_env_var_prefix='etsy_')

    def run(self):
        """ Main method. """
        self.init_logging(self.args.debug)

        for store in self.args.store:
            data = simon_etsy.get_all_shop_listings(self.args.api_key, store)
            weights = simon_etsy.analyze(data)

        for weight, phrase in weights[:self.args.top]:
            print(f"{phrase.ljust(30)} (+{weight})")

    def init_logging(self, debug):
        """ Turn on Python logging. """
        logging.basicConfig()
        logging.getLogger().setLevel(logging.NOTSET if debug else logging.INFO)


if __name__ == '__main__':
    Main().start(sys.argv[1:])
