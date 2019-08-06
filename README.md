# Simon-etsy

This is a small CLI project for getting relevant terms from Etsy shop listings.

## Installation

This section describes how to install the project.

### Python

You may want to install this into a virtualenv instead of to your system.

This package is not published to PyPI to avoid polluting the repository
namespace, so instead we install from GitHub.

```bash
$ pip install git+git://github.com/shakefu/simon-etsy.git
```

After installation, you must download the nltk word libraries for parsing to
work. These will be installed into your `$HOME` or globally depending on if you
run this command as an administrator.

```bash
# All nltk corpora, this may be slow
$ python -m nltk.downloader all

# OR just the bare minimum
$ python -m nltk.downloader punkt averaged_perceptron_tagger
```

### Docker

This section describes how to build a container for usage with Docker, as well
as how to extract an Ubuntu compatible standalone binary from that container.

```bash
# Run these commands in the cloned repository
# Build the iamge
$ docker build -t shakefu/simon-etsy .
```

That's it. Once you have the container you may use it like any other CLI
container.

#### Extracting standalone binary

Once the docker image is built, it's possible to get a standalone command from
it to run locally. This is built against Ubuntu 18.04, but it should work on
any Linux system with a compatible glibc version and x86_64.

All the dependencies and nltk data files should be bundled into this binary.

```bash
# Create a stopped container
$ docker create --name simon-etsy shakefu/simon-etsy

# Get the executable binary out
$ docker cp simon-etsy:/usr/local/bin/simon-etsy .

# Clean up
$ docker rm simon-etsy
```

## Usage

This section describes how to use the *simon-etsy* CLI.

Get help on the command line options with `simon-etsy --help`.

### Python install

Invoking the command directly after installing with Python is very straight
forward.

```bash
# View help
$ simon-etsy --help

# Get a store's listing
$ simon-etsy --api-key XXXX printandclay
printandclay
------------
bowl                           (+4555.0)
mug                            (+4470.0)
yarn                           (+4305.0)
doctor                         (+1557.0)
snape                          (+751.0)

# Run the command with debug information
$ simon-etsy --api-key XXXX --debug printandclay
DEBUG:simon-etsy:Getting page 1 at offset 0.
DEBUG:urllib3.connectionpool:Starting new HTTPS connection (1): openapi.etsy.com:443
DEBUG:urllib3.connectionpool:https://openapi.etsy.com:443 "GET /v2/shops/printandclay/listings/active?api_key=XXXX&limit=100&offset=0 HTTP/1.1" 200 None
DEBUG:simon-etsy:Getting page 2 at offset 100.
DEBUG:urllib3.connectionpool:https://openapi.etsy.com:443 "GET /v2/shops/printandclay/listings/active?offset=100&api_key=XXXX&limit=100 HTTP/1.1" 200 None
DEBUG:simon-etsy:Parsing 119 results.
printandclay
------------
bowl                           (+4555.0)
mug                            (+4470.0)
yarn                           (+4305.0)
doctor                         (+1557.0)
snape                          (+751.0)

# Use an environment variable for injecting the API key
$ ETSY_API_KEY=XXXX simon-etsy --api-key XXXX printandclay

# You can invoke the command with multiple shops at once
$ simon-etsy --api-key XXXX printandclay dbforge
printandclay
------------
bowl                           (+4555.0)
mug                            (+4470.0)
yarn                           (+4305.0)
doctor                         (+1557.0)
snape                          (+751.0)

dbforge
-------
knife                          (+6418.0)
blade                          (+1569.0)
damascus                       (+1559.0)
wootz                          (+950.0)
edge                           (+921.0)

# You can use the DEBUG environment variable to increase logging
$ DEBUG=true simon-etsy --api-key XXXX printandclay
```

### Docker install

All the same command options are available for container CLI. Simply run via
*docker* instead of directly.

```bash
# View help
$ docker run -it --rm shakefu/simon-etsy --help

# Get terms
$ docker run -it --rm shakefu/simon-etsy --api-key XXXX printandclay

# etc.
```

## Testing

This section describes how to run tests.

*TODO: More tests, with better integration and fixtures.*

Tests can be run using the standard Python test hook:

```bash
# Run in the cloned repository
$ python setup.py test
```

If you wish to run API integration tests, you'll need to provide an API key
otherwise they will be skipped.

```bash
# Run in the cloned repository
$ ETSY_API_KEY=XXX python setup.py test
```
