from pathlib import Path
from unittest import TestCase
from ..context import models, rm_tree
from ..context import JsonDS, S2Graph, S2GraphBuilder, MaxHopHopper

from betamax import Betamax
from requests import Session
from requests.exceptions import HTTPError
import pytest

with Betamax.configure() as config:
    config.cassette_library_dir = 'tests/fixtures/cassettes'


def load_s2graph():
    # this datastore contains 58 papers connected to the paper with PaperId
    # '8d8844106e7bc83d49ea3544ab2dfc74cd8f258a' (Code Review For and By
    # Scientists) by at most two hops. Each S2Paper object also has their
    # citations, references, and authors truncated to two to keep the
    # foot print of this test relatively low.
    paper_ds = JsonDS.load_papers("tests/fixtures/graph/paper_ds")
    paper_ds = {k:v for k,v in paper_ds.items()}
    colliding_paperId = list(paper_ds.keys())[0]
    paper_ds[colliding_paperId].paperId = "collision"
    s2graph = S2Graph(papers=paper_ds)
    return s2graph


class TestGraphBuilder(TestCase):
    def setUp(self):
        self.save_path = Path('tests/fixtures/graph/tmp_builder.pkl')
        self.builder = S2GraphBuilder(graph=load_s2graph(),
                                      hopper=MaxHopHopper(2),
                                      )
        self.builder.save_path = self.save_path
        self.root_paperId = '8d8844106e7bc83d49ea3544ab2dfc74cd8f258a'
        self.session = Session()
        self.missing_paperId = 'c4e3be316ce0d5dfc9ec7b19298e9483484cc252'
        self.missing_paperId_404 = 'paper'
        self.missing_paperId_429 = 'c4e3be316ce0d5dfc9ec7b19298e9483484cc252'
        self.addCleanup(lambda: rm_tree(self.save_path))

    def test_builder(self):
        # integrated-ish test
        self.builder.from_paper_id(self.root_paperId)
        # save/load
        self.builder.save()
        self.builder.load(self.save_path)
        # handling unknown refs
        unknown_ref = models.S2Reference(title='Unknown reference')
        self.builder._add_to_queue(unknown_ref, self.root_paperId, 'citation')
        # get paper with 429
        with Betamax(self.session).use_cassette('paper_429'):
            self.builder.api_kwargs['session'] = self.session
            self.builder.api_kwargs['retries'] = 0
            with pytest.raises(HTTPError):
                _ = self.builder._get_paper(self.missing_paperId_429)
        # get paper with 404
        with Betamax(self.session).use_cassette('paper_404'):
            self.builder.api_kwargs['session'] = self.session
            with pytest.raises(HTTPError):
                _ = self.builder._get_paper(self.missing_paperId_404)
        # get paper not in datastore
        with Betamax(self.session).use_cassette('paper'):
            self.builder.api_kwargs['session'] = self.session
            _ = self.builder._get_paper(self.missing_paperId)
        # test recursion error
        self.builder.discovered_from[self.root_paperId] = (self.root_paperId, "citation")
        with pytest.raises(RecursionError):
            self.builder._get_gpath(self.root_paperId)

