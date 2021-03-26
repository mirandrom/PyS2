API Endpoints
=============

PyS2 uses :meth:`requests.Session.get` to query Semantic Scholar API
endpoints. Functionality for `Data Partners
<https://pages.semanticscholar.org/data-partners>`_,
rate-limiting, and converting to :class:`.models.S2Paper`
or :class:`.models.S2Author` classes are included.

.. toctree::
    :maxdepth: 2

    api/get_paper
    api/get_author