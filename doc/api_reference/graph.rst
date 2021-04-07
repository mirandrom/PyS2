.. _s2.graph:

s2.graph
================================================================================

PyS2 allows you to construct arbitrary subgraphs of a paper's citation network
via :class:`GraphHopper` which can be used with :class:`S2GraphBuilder` to
create :class:`S2Graph` objects. These leverage :class:`S2DataStore` to
reduce memory footprint or API calls when working with large amounts of papers.


.. toctree::
    :maxdepth: 2

.. include:: graph/types.rst
.. include:: graph/graph.rst
.. include:: graph/builder.rst
.. include:: graph/hopper.rst
