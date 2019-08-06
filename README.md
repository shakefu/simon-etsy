# Simon-etsy

This is a small CLI project for getting relevant terms from Etsy shop listings.

## Installation

This section describes how to install the project.

### Python

You may want to install this into a virtualenv instead of to your system.

This package is not published to PyPI to avoid polluting the repository
namespace.

**Installing via GitHub**:

```bash
$ pip install git+git://github.com/shakefu/simon-etsy.git
```

After installation, you must download the nltk word libraries for parsing to
work. These will be installed into your `$HOME` or globally depending on if you
run this command as an administrator.

```bash
# All nltk corpora
$ python -m nltk.downloader all
# OR just the bare minimum
$ python -m nltk.downloader punkt averaged_perceptron_tagger
```

### Docker

This section describes how to 
