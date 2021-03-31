s2.api
================================================================================
PyS2 uses :meth:`requests.Session.get` to query Semantic Scholar API
endpoints. Functionality for `Data Partners
<https://pages.semanticscholar.org/data-partners>`_,
rate-limiting, and converting to :class:`.models.S2Paper`
or :class:`.models.S2Author` classes are included.

.. toctree::
    :maxdepth: 2

.. include:: api/get_paper.rst
.. include:: api/get_author.rst