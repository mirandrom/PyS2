Installing PyS2
===============

PyS2 supports Python 3.6+. The recommended way to install PyS2 is via ``pip``.

.. code-block:: bash

    pip install pys2

.. note::

    Depending on your system, you may need to use ``pip3`` to install packages for
    Python 3.

.. warning::

    Avoid using ``sudo`` to install packages. Do you `really` trust this package?

For instructions on installing Python and pip see "The Hitchhiker's Guide to Python"
`Installation Guides <https://docs.python-guide.org/en/latest/starting/installation/>`_.

Updating PyS2
-------------

PyS2 can be updated by running:

.. code-block:: bash

    pip install --upgrade pys2


Installing the Latest Development Version
-----------------------------------------

You can install PyS2 directly from GitHub like so:

.. code-block:: bash

    pip install --upgrade https://github.com/mirandrom/pys2/archive/master.zip

You can also directly clone a copy of the repository using git, like so:

.. code-block:: bash

    pip install --upgrade git+https://github.com/mirandrom/pys2.git