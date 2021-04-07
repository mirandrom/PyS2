from s2 import api
from s2.models import S2Reference, S2Paper, S2Author
from s2.graph import GraphHopper, MaxHopHopper, S2Graph, EdgeType, GraphPath, PaperId, HopFrom

from collections import deque
import requests
import hashlib
from pathlib import Path
from datetime import datetime
import time
import pickle
from collections import defaultdict

from typing import Optional, Dict, Deque, Set, Union, List


import logging
logger = logging.getLogger('s2')
logger.setLevel(logging.INFO)

# TODO: reconcile saving of Builder/S2Graph
# TODO: docstring
# TODO: hopper in method or attribute?
# TODO: currently scraping ~1 paper/s; profile to find bottleneck
# TODO: look into batch/async requests


class S2GraphBuilder:
    """ Builds an :class:`S2Graph` object.

    Args:
        graph:
            The :class:`S2Graph` object to build or
            continue buiding.
        hopper:
            The :class:`GraphHopper` object that
            defines the strategy for building the citation
            network subgraph.
        queue:
            A queue of papers that remain to be added. Everytime
            a paper is added, all its neighbours are added to the
            queue and the ``hopper`` will decide whether these papers
            should also be added.
        discovered_from:
            A dictionary for reconstructing graph paths.
        not_found:
            A set of paper identifiers that were not found, to allow
            subsequent follow-up.
        colliding_paperIds:
            A dictionary of papers with inconsistent identifiers.
        log_every:
            Log updates every x paper added.
        save_path:
            Where to save progress in event of interruption.
        **api_kwargs:
            Additional kwargs for the ::`` module.
    """
    def __init__(self,
                 graph: S2Graph = S2Graph(),
                 hopper: GraphHopper = MaxHopHopper(1),
                 queue: Deque = deque(),
                 discovered_from: Dict[PaperId, HopFrom] = None,
                 not_found: Set = None,
                 colliding_paperIds: Dict[PaperId, Set[PaperId]] = None,
                 log_every: int = 10,
                 save_path: Union[str, Path] = None,
                 **api_kwargs
                 ):
        self.graph = graph
        self.hopper = hopper
        self.queue = queue
        self.discovered_from = discovered_from or {}
        self.not_found = not_found or set()
        self.colliding_paperIds = colliding_paperIds or defaultdict(set)

        self.log_every = log_every
        self.save_path = Path(save_path or self._default_save_path())
        self.api_kwargs = api_kwargs or {}

    def _default_save_path(self) -> str:
        t = time.time()
        f = datetime.utcfromtimestamp(t).strftime('%Y%m%d-%H%M%S-%f')[:-3]
        return f + '.pkl'

    def save(self, p: Optional[Union[Path, str]] = None):
        p = Path(p or self.save_path)
        logger.info(f'Saving S2GraphBuilder to {p}')
        p.write_bytes(pickle.dumps(self))

    @classmethod
    def load(cls, p: Union[Path, str]):
        p = Path(p)
        return pickle.loads(p.read_bytes())

    def _get_gpath(self, paperId: PaperId) -> GraphPath:
        """
        Get the path that was traversed to reach ``paperId`` in the ``S2Graph``.
        """
        node_lookup = set()
            # node_lookup.add(paperId)
            # (source, edge_type) = self.discovered_from[paperId]
            # gpath = deque([(paperId, edge_type)])
        gpath = deque()
        while paperId:
            if paperId in node_lookup:
                raise RecursionError(f'Unexpected cycle for paperId {paperId} '
                                     f'in the following path:\n'
                                     f'{"->".join(str(x) for x in gpath)}')
            else:
                node_lookup.add(paperId)
            visit = paperId
            (paperId, edge_type) = self.discovered_from[visit]
            gpath.appendleft((visit, edge_type))

        return list(gpath)

    def _get_paper(self, paperId: PaperId) -> S2Paper:
        """
        Get an ``S2Paper`` via its ``paperId``, checking local db first.
        """
        try:
            return self.graph.papers[paperId]
        except KeyError:
            s2_paper = api._get_s2paper(paperId, **self.api_kwargs)
            if s2_paper.paperId != paperId: # pragma: no cover
                self.colliding_paperIds[paperId].add(s2_paper.paperId)
                self.colliding_paperIds[s2_paper.paperId].add(paperId)
                self.graph.papers[s2_paper.paperId] = s2_paper
                s2_paper.paperId = paperId
            self.graph.papers[paperId] = s2_paper
            return s2_paper

    def _add_to_queue(self, ref: S2Reference, source: PaperId,
                      edge_type: EdgeType) -> None:
        """
        Add ref to queue, record ref visit, and add edge from source to ref.
        """
        pid = ref.paperId
        # The ref has an S2 identifier and hasn't been visited/discovered yet
        # Add it to the queue so its full S2Paper can be recovered
        # Record that ref has been visited so it isn't added to the queue again
        if pid and pid not in self.discovered_from:
            self.queue.append(pid)
            self.discovered_from[pid] = (source, edge_type)

        # The ref does not have an S2 identifier; hash it to create one
        # Note: the resulting pid is 40-chars long as with S2Paper identifiers
        if not pid:
            hash = hashlib.md5(ref.json().encode('utf-8')).hexdigest()
            pid = f'unknown_{hash}'
            self.graph.papers[pid] = S2Paper(**ref.dict())
            self.discovered_from[pid] = (source, edge_type)

        # Create a new edge from the source node to the ref
        # TODO: type and document edge metadata dict?
        # TODO: prevent duplicates in case of error/restart?
        #      probably a try-except block with intermediary values that can
        #      be added/removed; however, the worst that can happen is
        #      duplicated edges which are easy to filter post-hoc
        edge_meta = {'intent': ref.intent, 'isInfluential': ref.isInfluential}
        self.graph.edges[source][edge_type] += [(pid, edge_meta)]

    def from_paper_id(self, paperId: str):
        """ Construct :class:`S2Graph` from :class:`PaperId` based on
        :class:`GraphHopper` strategy.


        Args:
            paperId:
                S2 paper identifier (see :func:`.get_paper` for more info)
        """
        if paperId not in self.discovered_from:
            self.queue.append(paperId)
            self.discovered_from[paperId] = ("", None)
        self.build_from_queue()

    def build_from_queue(self):
        while self.queue:
            try:
                pid = self.queue[0]
                num_papers = len(self.graph.edges)
                if self.log_every and (num_papers % self.log_every == 0):
                    logger.info(f'Queue: {len(self.queue)}, '
                                f'Papers added: {num_papers}')
                s2_paper = self._get_paper(pid)
                gpath = self._get_gpath(pid)
                if self.hopper.hop(gpath, self.graph):
                    for r in s2_paper.citations or []:
                        self._add_to_queue(r, pid, 'citation')
                    for r in s2_paper.references or []:
                        self._add_to_queue(r, pid, 'reference')
                # adds the paper to the graph even if it has no neighbours
                _ = self.graph.edges[pid]
                # only pop the paper once everything else is done to allow
                # retrying if code execution is interrupted.
                _ = self.queue.popleft()

            # error handling
            except requests.HTTPError as e: # pragma: no cover
                if e.response.status_code == 404:
                    self.not_found.add(pid)
                    _ = self.queue.popleft()
                    logger.warning(f'Paper not found: {pid}')
                else:
                    self.save()
                    logger.critical(
                        f'Aborting S2Graph construction on: {pid}\n',
                        exc_info=True
                    )
                    raise e

            except Exception as e: # pragma: no cover
                self.save()
                logger.critical(
                    f'Aborting S2Graph construction on: {pid}\n',
                    exc_info=True
                )
                raise e
            except KeyboardInterrupt: # pragma: no cover
                self.save()
                logger.warning(f'Interrupted S2Graph construction on: {pid}\n')
                raise KeyboardInterrupt
