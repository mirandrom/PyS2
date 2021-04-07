from s2.models import S2Paper, S2Author
from collections import defaultdict

from typing import Dict, List, Tuple, MutableMapping, Optional, Type
from typing_extensions import Literal


class PaperId:
    """A valid S2 Paper Identifier string. """
PaperIdT = PaperId
PaperIdT.__supertype__ = str


class AuthorId:
    """A valid S2 Author Identifier string. """
AuthorIdT = AuthorId
AuthorIdT.__supertype__ = str


class S2PaperMap:
    """:class:`MutableMapping` of :class:`PaperId` to :class:`S2Paper`.

    It is recommended to use objects of type :class:`s2.store.S2DataStore`, but
    for rapid prototyping this can be a simple dictionary.
    """
S2PaperMapT = S2PaperMap
S2PaperMapT.__supertype__ = MutableMapping[PaperIdT, S2Paper]


class S2AuthorMap:
    """:class:`MutableMapping` of :class:`AuthorId` to :class:`S2Author`.

    It is recommended to use objects of type :class:`s2.store.S2DataStore`, but
    for rapid prototyping this can be a simple dictionary.
    """
S2AuthorMapT = S2AuthorMap
S2AuthorMapT.__supertype__ = MutableMapping[AuthorIdT, S2Author]


class EdgeType:
    """ Either of 'references', 'citations', or 'author'. """
EdgeTypeT = EdgeType
EdgeTypeT.__supertype__ = Literal["reference", "citation", " author"]
# instead of EdgeType.__values__/__args__ for py3.6/3.7+ just duplicate
EdgeTypeValues = ["reference", "citation", " author"]
def edge_factory():
    return {k: [] for k in EdgeTypeValues}


class EdgeMeta:
    """ Dict for storing any additional edge meta-information."""
EdgeMetaT = EdgeMeta
EdgeMetaT.__supertype__ = Dict


class Neighbours:
    """ :class:`MutableMapping` of :class:`EdgeType` to list of
    (:class:`PaperId`, :class:`EdgeMeta`) tuples for neighbouring papers.
    """
NeighboursT = Neighbours
NeighboursT.__supertype__ = MutableMapping[EdgeTypeT, List[Tuple[PaperIdT, EdgeMetaT]]]


class EdgeMap:
    """ :class:`MutableMapping` of :class:`PaperId` to :class:`Neighbours`. """
EdgeMapT = EdgeMap
EdgeMapT.__supertype__ = MutableMapping[PaperIdT, NeighboursT]


class HopFrom:
    """ Tuple of :class:`PaperId` (the paper being hopped from)
    and :class:`EdgeType` (the type of the edge being hopped across)

    """
HopFromT = HopFrom
HopFromT.__supertype__ = Tuple[PaperIdT, EdgeTypeT]


class HopTo:
    """ Tuple of :class:`PaperId` (the paper being hopped to)
    and :class:`EdgeType` (the type of the edge being hopped across).

    Note that unlike :class:`HopFrom`, the edge type can be None if the
    paper "being hopped to" is actually the first paper being visited (i.e.
    without any edge traversal).

    """
HopToT = HopTo
HopToT.__supertype__ = Tuple[PaperIdT, Optional[EdgeTypeT]]


class GraphPath:
    """List of :class:`HopTo` for the path traversed in a :class:`S2Graph`. """
GraphPathT = GraphPath
GraphPathT.__supertype__ = List[HopToT]


class S2Graph:
    """Class for storing citation network subgraph.

    Args:
        edges (:class:`EdgeMap`, optional):
            Stores subgraph edge information. While :class:`S2Paper` and
            :class:`S2Author` already contain the information required to
            reconstruct citation graphs, they do not allow arbitrary subgraphs
            and are not as lightweight as a simple mapping of identifiers.

            Defaults to :obj:`defaultdict`
            with factory for :class:`Neighbours` for in-memory storage.

        papers (:class:`S2PaperMap`, optional):
            Stores :class:`S2Paper` objects retrievable by :class:`PaperId`.
            Recommended to use :class:`s2.store.S2DataStore` to avoid keeping
            large amounts of data in memory.

            Defaults to :obj:`dict`.

        authors (:class:`S2AuthorMap`, optional):
            Stores :class:`S2Author` objects retrievable by :class:`AuthorId`.
            Recommended to use :class:`s2.store.S2DataStore` to avoid keeping
            large amounts of data in memory.

            Defaults to :obj:`dict`.
    """
    def __init__(
            self,
            edges: Optional[EdgeMapT] = None,
            papers: Optional[S2PaperMapT] = None,
            authors: Optional[S2AuthorMapT] = None,
    ):


        self.edges = defaultdict(edge_factory) if edges is None else edges
        self.papers = {} if papers is None else papers
        self.authors = {} if authors is None else authors
