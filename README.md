# PyS2: Python Library for the Semantic Scholar API

[![Latest PyS2 Version](https://img.shields.io/pypi/v/pys2.svg)](https://pypi.python.org/pypi/pys2)
[![License](https://img.shields.io/github/license/mirandrom/pys2.svg)](https://pypi.python.org/pypi/pys2)
[![CI](https://github.com/mirandrom/pys2/actions/workflows/ci.yml/badge.svg)](https://github.com/mirandrom/pys2/actions?query=branch%3Amaster)
[![codecov](https://codecov.io/gh/mirandrom/PyS2/branch/master/graph/badge.svg?token=4GTVZ5P6S2)](https://codecov.io/gh/mirandrom/PyS2)
[![ReadTheDocs](https://readthedocs.org/projects/pys2/badge/?version=latest)](https://pys2.readthedocs.io/)


A python library for the [Semantic Scholar (S2) API](api.semanticscholar.org/) 
with typed [pydantic](https://pydantic-docs.helpmanual.io/) objects 
and various nifty functionalities. 

For more information, check out the [documentation](https://pys2.readthedocs.io) 

## Install PyS2
PyS2 is supported on Python 3.6+. 
The recommended way to install PyS2 is via pip.
```bash
pip install pys2
```
To install the latest development version of PyS2 run the following instead:
```bash
pip install --upgrade https://github.com/mirandrom/pys2/archive/master.zip
```

## Examples
### Obtaining an [``S2Paper``](https://pys2.readthedocs.io/en/latest/api_reference/models.html#s2paper) Object
To scrape a paper from the S2 API, you first need an S2 paper identifier.
This can be found at the end of the URL of a paper on Semantic Scholar.

For example, this [paper](https://www.semanticscholar.org/paper/Code-Review-For-and-By-Scientists-Petre-Wilson/8d8844106e7bc83d49ea3544ab2dfc74cd8f258a)
has the S2 identifier ``8d8844106e7bc83d49ea3544ab2dfc74cd8f258a``

The S2 identifier can also be specified based on a paper's identifier from
other platforms. For example, the [same paper on arxiv](https://arxiv.org/abs/1407.5648) also has the S2 identifier
``arXiv:1407.5648``. The convention for different platforms is described on
the [S2 API page](https://api.semanticscholar.org/), as well as in the
PyS2 documentation for [``get_paper``](https://pys2.readthedocs.io/en/latest/api_reference/api.html#get-paper). 
In fact, we will use this method to scrape the paper above with the two 
different identifiers and show that they indeed give the same paper.

```python
import s2

pid = "8d8844106e7bc83d49ea3544ab2dfc74cd8f258a"
pid2 = "arXiv:1407.5648"

paper = s2.api.get_paper(paperId=pid)
paper2 = s2.api.get_paper(paperId=pid2)

assert paper == paper2
```

### Using an API Key
Be aware of the rate limit (100 requests per 5 minute window) for the
public API. Depending on the nature of your use-case (e.g. research),
you may apply for the [Data Partners API Access](https://pages.semanticscholar.org/data-partners)
 to obtain an API key allowing you to scrape papers at a much faster rate.
If you share your code, be careful to keep the API key separate.

If you have an API key, it's really easy to use in one of two ways.

#### Using the ``api_key`` argument
```python
paper = s2.api.get_paper(paperId=pid, api_key=API_KEY)
```

#### Using a custom [``Session``](https://requests.readthedocs.io/en/latest/api/#requests.Session)
```python
from requests import Session

session = Session()
session.headers = {'x-api-key': API_KEY}
paper = s2.api.get_paper(paperId=pid, session=session)
```

The same approaches can be used for the PyS2 function 
[``get_author``](https://pys2.readthedocs.io/en/latest/api_reference/api.html#get-paper) 
 covered below.

### Get all the Papers of an Author
In this example we'll get all the papers of 
[Bill Gates](https://www.semanticscholar.org/author/B.-Gates/144794037) 
who was an S2 ``AuthorId`` of ``144794037``. This will also allow us to compute his
[*h*-index](https://en.wikipedia.org/wiki/H-index).


#### Obtain [``S2Author``](https://pys2.readthedocs.io/en/latest/api_reference/models.html#s2author) Object
Simply pass the ``AuthorId`` to
the PyS2 function [``get_author``](https://pys2.readthedocs.io/en/latest/api_reference/api.html#get-author):

```python
import s2

author = s2.api.get_author(authorId="144794037")
```

And just like that, we now have an [``S2Author``](https://pys2.readthedocs.io/en/latest/api_reference/models.html#s2author) instance from which we
can extract their papers, stored as 
[``S2AuthorPaper``](https://pys2.readthedocs.io/en/latest/api_reference/models.html#s2author#s2.models.S2AuthorPaper) 
instances. However,
this object contains limited information and so we must use
[``get_paper``](https://pys2.readthedocs.io/en/latest/api_reference/api.html#get-paper)
to obtain the [``S2Paper``](https://pys2.readthedocs.io/en/latest/api_reference/models.html#s2paper) instances which contain
the complete information for a paper.


#### Obtain Multiple [``S2Paper``](https://pys2.readthedocs.io/en/latest/api_reference/models.html#s2paper)  Objects
Because we are performing multiple requests, we can include ``retries`` and
``wait`` arguments to [``get_paper``](https://pys2.readthedocs.io/en/latest/api_reference/api.html#get-paper)
to work around rate-limiting. The default values of 2 and
150 are conservative but work well for the public API. Lastly, we can specify
that [``S2Paper``](https://pys2.readthedocs.io/en/latest/api_reference/models.html#s2paper)  
instances returned include references or citations
([``S2Reference``](https://pys2.readthedocs.io/en/latest/api_reference/models.html#s2paper#s2.models.S2Reference)) that are not indexed by Semantic Scholar, e.g. if we
want to attempt recovering them in a different way.

```python
paperIds = [p.paperId for p in author.papers]
papers = []
for pid in paperIds:
    paper = s2.api.get_paper(
        paperId=pid,
        retries=2,
        wait=150,
        params=dict(include_unknown_references=True)
    )
    papers += [paper]
```

Now we have a list of Bill Gates' papers and everything we need to compute
his *h*-index, namely the citations for each of his papers.

#### Computing *h*-index
The *h*-index is defined as the maximum value of *h* such that an author has
published *h* papers that have each been cited at least *h* times.

```python
n_citations = sorted([len(p.citations) for p in papers], reverse=True)
for n_papers, n_cited in enumerate(n_citations):
    if n_cited < n_papers:
        h_index = n_papers - 1
        break
```
Which gives us an *h*-index 12 for Bill Gates!

### Working locally with [``s2.db``](https://pys2.readthedocs.io/en/latest/api_reference/db.html)
The [``s2.db``](https://pys2.readthedocs.io/en/latest/api_reference/db.html) 
API makes it easy to save and retrieve your ``S2Paper``
and ``S2Author`` objects through a dict-like interface.

```python
from s2.db.json import JsonS2PaperDB, JsonS2AuthorDB

# path of directory where S2Papers will be saved as jsons
s2paper_json_dir = "pdb"

# if the directory does not exist, it is created
# otherwise, previously saved S2Papers become accessible
pdb = JsonS2PaperDB(s2paper_json_dir)

# lets save Bill's papers from the previous example
for p in papers:
    pdb[p.paperId] = p

# now lets delete pdb and recover Bill's papers
del pdb
pdb = JsonS2PaperDB(s2paper_json_dir)
for p in papers:
    p2 = pdb[p.paperId]
    assert p2 == p

# we can do the same for S2Author objects
adb = JsonS2AuthorDB("adb")
adb[author.authorId] = author

# note that setting a value requires the key to be equal to the
# S2 identifier of the object, but this behaviour can be disabled
adb = JsonS2AuthorDB("adb", enforce_id=False)
adb["billy"] = author
```