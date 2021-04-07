.. _s2.store:

s2.store
================================================================================

PyS2 allows you to interact with :class:`S2Paper` and :class:`S2Author` via
:class:`S2DataStore` which provides a dict-like interface that can be inherited
and adapted for any custom backend. :class:`JsonDS` is an example that simply
uses json files to reduce the memory footprint of working with many papers
while creating human-readable records.


.. toctree::
    :maxdepth: 2

.. include:: store/base.rst
.. include:: store/json.rst

