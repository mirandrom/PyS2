from s2.graph import S2Graph, GraphPath


class GraphHopper:
    """
    The primary role of this class is to implement the :meth:`~GraphHopper.hop`
    method, which decides whether to traverse an edge and hop to a new node.

    This simple binary decision-making process allows us to create diverse
    strategies for constructing a subset of a root paper's citation graph, with
    specific properties. In particular, subclasses implementing
    :meth:`~GraphHopper.hop` can be passed to :class:`S2GraphBuilder` to create
    :class:`S2Graph` instances with arbitrary structures.

    For example, this default implementation always hops, and will eventually
    cover the entire citation graph of the root paper (i.e. the connected
    component of the full citation graph that contains the root paper).
    However, the interface of :meth:`~GraphHopper.hop` allows complex
    decision-making based on the current state of the graph and the path
    traversed to reach the current candidate paper from the root paper.
    """

    def hop(self, gpath: GraphPath, graph: S2Graph) -> bool:
        """
        Decide whether to hop from ``gpath[-2]`` to ``gpath[-1]``

        Args:
            gpath (:class:`GraphPath`) :
                The path traversed to reach the candidate paper (``gpath[-1]``)
                 from the root paper (``gpath[0]``), via the current paper
                 (``gpath[-2]``). Note that :class:`GraphPath` objects store
                paper identifiers, which can be used to lookup a complete
                :class:`S2Paper` in the :class:`S2DataStore` objects
                of ``graph``.

            graph (:class:`S2Graph`) :
                The current state of the graph.

        Returns (:obj:`bool`):
            ``True`` if hop, else ``False``.

        """
        return True


class MaxHopHopper(GraphHopper):
    """Hops until a max distance from the root paper is exceeded.

    Args:
        max_hops (:obj:`int`, optional):
            Max number of hops from the root paper (``len(gpath) - 1``)
            beyond which :meth:`GraphHopper.hop` returns False.
            Defaults to ``1``.
    """
    def __init__(self, max_hops: int = 1):
        self.max_hops = max_hops

    def hop(self, gpath: GraphPath, graph: S2Graph) -> bool:
        if len(gpath)-1 > self.max_hops:
            return False
        else:
            return True


class MaxPaperHopper(GraphHopper):
    """Hops until a max number of papers are added to the graph.

    Args:
        max_papers (:obj:`int`, optional):
            Max number of papers in ``graph`` beyond which
            :meth:`GraphHopper.hop` returns False. Defaults to ``1``.

            Note that the number of papers is ``len(graph.edges)``, as
            ``graph.papers`` is an instance of :class:``S2DataStore`` which
            may contain papers not in the graph.
    """
    def __init__(self, max_papers: int = 10):
        self.max_papers = max_papers

    def hop(self, gpath: GraphPath, graph: S2Graph) -> bool:
        if len(graph.edges) >= self.max_papers:
            return False
        else:
            return True


class BowtieHopper(GraphHopper):
    """Creates a bowtie or funnel shaped subset of a citation graph.

    i.e. hops only if the traversed path consists of citations of citations or
    of references of references, up to specified lengths.

    Args:
        max_reference (:obj:`int`, optional):
            Max distance allowed from the root paper in path of references.
            Defaults to ``1``.

        max_citation (:obj:`int`, optional):
            Max distance allowed from the root paper in path of citations.
            Defaults to ``1``.

        verify_gpath (:obj:`bool`, optional):
            If ``False``, then assume that the path leading to the current
            node already consists exclusively of citations of citations or of
            references of references. Otherwise, checks every paper in ``gpath``
            to ensure this condition is met. Defaults to ``False``.
    """
    def __init__(self,
                 max_reference: int = 1,
                 max_citation: int = 1,
                 verify_gpath: bool = False
                 ):
        self.max_reference = max_reference
        self.max_citation = max_citation
        self.verify_gpath = verify_gpath

    def hop(self, gpath: GraphPath, graph: S2Graph) -> bool:
        edge_type = gpath[-1][1]
        if len(gpath) - 1 > getattr(self, f"max_{edge_type}"):
            return False
        # edge type on root node will be None and != edge_type for len(gpath)=2
        if len(gpath) > 2 and gpath[-2][1] != edge_type:
            return False
        if self.verify_gpath:
            # gpath[0] is the root node with edge_type None
            if len(set([p[1] for p in gpath[1:]])) != 1:
                return False
        return True


class LivingLitReviewHopper(GraphHopper):
    """Similar to :class:`BowtieHopper` except on the references of a paper.

    Used for the Living LitReview project to obtain papers that are more likely
    to be topically related to the content from the original literature review.

    Args:
        max_reference (:obj:`int`, optional):
            Max distance allowed from the root paper references in path of
            references.
            Defaults to ``1``.

        max_citation (:obj:`int`, optional):
            Max distance allowed from the root paper references
            in path of citations.
            Defaults to ``1``.

        verify_gpath (:obj:`bool`, optional):
            If ``False``, then assume that the path leading to the current
            node already consists exclusively of citations of citations or of
            references of references. Otherwise, checks every paper in ``gpath``
            to ensure this condition is met. Defaults to ``False``.
    """
    def __init__(self,
                 max_reference: int = 1,
                 max_citation: int = 1,
                 verify_gpath: bool = False
                 ):
        self.max_reference = max_reference
        self.max_citation = max_citation
        self.verify_gpath = verify_gpath

    def hop(self, gpath: GraphPath, graph: S2Graph) -> bool:
        edge_type = gpath[-1][1]
        if gpath[1][1] != 'reference':
            return False
        if len(gpath) - 2 > getattr(self, f"max_{edge_type}"):
            return False
        # edge type on root node will be None and != edge_type for len(gpath)=2
        if len(gpath) > 2 and gpath[-2][1] != edge_type:
            return False
        if self.verify_gpath:
            # gpath[0] is the root node with edge_type None
            if len(set([p[1] for p in gpath[2:]])) != 1:
                return False
        return True
