Quick Start
===========

Getting Papers
--------------------------------------------------------------------------------
To scrape a paper from the `Semantic Scholar (S2) API
<https://api.semanticscholar.org/>`_ you first need an S2 paper identifier.
This can be found at the end of the URL of a paper on Semantic Scholar.

For example, this `paper <https://www.semanticscholar.org/paper/
Code-Review-For-and-By-Scientists-Petre-Wilson/
8d8844106e7bc83d49ea3544ab2dfc74cd8f258a>`_
has the S2 identifier ``8d8844106e7bc83d49ea3544ab2dfc74cd8f258a``

The S2 identifier can also be specified based on a paper's identifier from
other platforms. For example, the `same paper on arxiv
<https://arxiv.org/abs/1407.5648>`_ also has the S2 identifier
``arXiv:1407.5648``. The convention for different platforms is described on
the `S2 API <https://api.semanticscholar.org/>`_ page as well as in the
documentation for :func:`.api.get_paper`. In fact, we will use this method
to scrape the paper above with the two different identifiers and show that
they indeed give the same paper.

.. code-block:: python

    import s2

    pid = "8d8844106e7bc83d49ea3544ab2dfc74cd8f258a"
    pid2 = "arXiv:1407.5648"

    paper = s2.api.get_paper(paperId=pid)
    paper2 = s2.api.get_paper(paperId=pid2)

    assert paper == paper2

.. _using_an_api_key:

Using an API Key
--------------------------------------------------------------------------------
.. warning::

    Be aware of the rate limit (100 requests per 5 minute window) for the
    public API. Depending on the nature of your use-case (e.g. research),
    you may apply for the `Data Partners
    <https://pages.semanticscholar.org/data-partners>`_ API Access
    to obtain an API key allowing you to scrape papers at a much faster rate.
    If you share your code, be careful to keep the API key separate.

If you have an API key, it's really easy to use in one of two ways.

Using the ``api_key`` argument
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. code-block:: python

    paper = s2.api.get_paper(paperId=pid, api_key=API_KEY)


Using a custom :class:`requests.Session`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. code-block:: python

    from requests import Session

    session = Session()
    session.headers = {'x-api-key': API_KEY}
    paper = s2.api.get_paper(paperId=pid, session=session)

.. note::

    Passing an API key through the ``api_key`` argument will
    temporarily overwrite a key stored in ``session`` for that request.
    However, the ``session`` object itself will remain unchanged.

The same approaches can be used for the :func:`.api.get_author` function
covered below.

Get all the Papers of an Author
--------------------------------------------------------------------------------

In this example we'll get all the papers of `Bill Gates
<https://www.semanticscholar.org/author/B.-Gates/144794037>`_ who was an
S2 ``AuthorId`` of ``144794037``. This will also allow us to compute his
*h*-index (https://en.wikipedia.org/wiki/H-index).


Obtain S2Author Object
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
To obtain a :class:`.S2Author` Object, simply pass the ``AuthorId`` to
:func:`.api.get_author`.

.. code-block:: python

    import s2

    author = s2.api.get_author(authorId="144794037")

And just like that, we now have an :class:`.S2Author` instance from which we
can extract their papers, stored as :class:`.S2AuthorPaper` instances. However,
this object contains limited information and so we must use
:func:`.api.get_paper` to obtain :class:`.S2Paper` instances which contain
the complete information for a paper.


Obtain S2Paper Objects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
To obtain a :class:`.S2Paper` Object, simply pass the ``PaperId`` to
:func:`.api.get_paper`. If you have an API key, you can also pass it here.
Because we are performing multiple requests, we can include ``retries`` and
``wait`` arguments to work around rate-limiting. The default values of 2 and
150 are conservative but work well for the public API. Lastly, we can specify
that :class:`.S2Paper` instances returned include references or citations
(:class:`.S2Reference`) that are not indexed by Semantic Scholar, e.g. if we
want to attempt recovering them in a different way.

.. code-block:: python

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

Now we have a list of Bill Gates' papers and everything we need to compute
his *h*-index, namely the citations for each of his papers.

Computing *h*-index
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The *h*-index is defined as the maximum value of *h* such that an author has
published *h* papers that have each been cited at least *h* times.

.. code-block:: python

    n_citations = sorted([len(p.citations) for p in papers], reverse=True)
    for n_papers, n_cited in enumerate(n_citations):
        if n_cited < n_papers:
            h_index = n_papers - 1
            break

Which gives us an *h*-index 12 for Bill Gates!

.. _saving_with_db:

Saving and Working Locally with :any:`s2.db`
--------------------------------------------------------------------------------
The :any:`s2.db` API makes it easy to save and retrieve your :class:`.S2Paper`
and :class:`.S2Author` objects through a dict-like interface.

.. code-block:: python

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


.. _saving_unknown:

Saving Objects without S2 Identifiers
--------------------------------------------------------------------------------
Sometimes, a :class:`.S2Reference` object may not have a ``paperId`` value if
you are using ``include_unknown_references=True``.
In this case, you still may want to save it (e.g. to attempt recovering it
via different methods at a later date). To do this, you can cast it to
:class:`.S2Paper` and create a unique placeholder id

.. code-block:: python

    from s2.db.json import JsonS2PaperDB, JsonS2AuthorDB

    # note that enforce_id=False is not necessary
    pdb = JsonS2PaperDB("pdb")

    # lets hunt ourselves an unknown reference from Bill's paper
    paper = s2.api.get_paper(
        "bdfa1a62c964f19b5ce000d7812ba9f66456a4a4",
         params=dict(include_unknown_references=True),
    )
    for r in paper.references:
        if not r.paperId:
            break

    # create a 40-char key from the hashed content and a signpost prefix
    hash = hashlib.md5(r.json().encode("utf-8")).hexdigest()
    placeholder_id = f"unknown_{hash}"
    pdb[placeholder_id] = S2Paper(**r.dict())

