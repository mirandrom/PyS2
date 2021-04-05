from s2.models import S2Paper, S2Author
from collections import defaultdict

from typing import Dict, List, Tuple, MutableMapping, Optional
from typing_extensions import Literal, get_args


# Custom types
# TODO: look at https://github.com/pandas-dev/pandas/issues/33025#issuecomment-699636759
#       to get custom types to play nice with docs and typechecker
PaperId = str
AuthorId = str

# instead of EdgeType.__values__/__args__ for py3.6/3.7+ just duplicate
EdgeType = Literal["reference", "citation", " author"]
EdgeTypeValues = ["reference", "citation", " author"]
def edge_factory():
    return {k: [] for k in EdgeTypeValues}

EdgeMeta = Dict
Edges = MutableMapping[EdgeType, List[Tuple[PaperId, EdgeMeta]]]
S2PaperMap = MutableMapping[PaperId, S2Paper]
S2AuthorMap = MutableMapping[AuthorId, S2Author]

PaperId = str
HopFrom = Tuple[PaperId, Optional[EdgeType]]
HopTo = Tuple[PaperId, Optional[EdgeType]]
GraphPath = List[HopTo]


class S2Graph:
    def __init__(
            self,
            edges: Dict[PaperId, Edges] = None,
            papers: MutableMapping[PaperId, S2Paper] = None,
            authors: MutableMapping[AuthorId, S2Author] = None,
    ):

        self.edges = defaultdict(edge_factory) if edges is None else edges
        self.papers = {} if papers is None else papers
        self.authors = {} if authors is None else authors
