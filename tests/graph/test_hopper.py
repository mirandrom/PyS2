from unittest import TestCase
from ..context import JsonDS, S2Graph
from ..context import (GraphHopper, MaxHopHopper, MaxPaperHopper, BowtieHopper,
                       LivingLitReviewHopper)


def load_s2graph():
    # this datastore contains 58 papers connected to the paper with PaperId
    # '8d8844106e7bc83d49ea3544ab2dfc74cd8f258a' (Code Review For and By
    # Scientists) by at most two hops. Each S2Paper object also has their
    # citations, references, and authors truncated to two to keep the
    # foot print of this test relatively low.
    paper_ds = JsonDS.load_papers("tests/fixtures/graph/paper_ds")
    s2graph = S2Graph(papers=paper_ds)
    return s2graph


class TestGraphHopper(TestCase):
    def setUp(self):
        self.s2graph = load_s2graph()
        self.root_paperId = '8d8844106e7bc83d49ea3544ab2dfc74cd8f258a'

    def test_hoppers(self):
        hop = GraphHopper()
        maxhop1 = MaxHopHopper(1)
        maxhop2 = MaxHopHopper(2)
        bowtie1 = BowtieHopper(max_citation=1, max_reference=1)
        bowtie2 = BowtieHopper(max_citation=4, max_reference=2,
                               verify_gpath=True)

        root_paper = self.s2graph.papers[self.root_paperId]
        for r in root_paper.references:
            r_edge = (r.paperId, 'reference')
            self.s2graph.edges[self.root_paperId]['reference'] += [r_edge]
            gpath = [(self.root_paperId, None), r_edge]
            assert maxhop1.hop(gpath, self.s2graph)
            assert maxhop2.hop(gpath, self.s2graph)
            assert bowtie1.hop(gpath, self.s2graph)
            assert bowtie2.hop(gpath, self.s2graph)
            r_paper = self.s2graph.papers[r.paperId]
            for rr in r_paper.references:
                rr_edge = (rr.paperId, 'reference')
                self.s2graph.edges[r.paperId]['reference'] += [rr_edge]
                gpath2 = gpath + [rr_edge]
                assert not maxhop1.hop(gpath2, self.s2graph)
                assert maxhop2.hop(gpath2, self.s2graph)
                assert not bowtie1.hop(gpath2, self.s2graph)
                assert bowtie2.hop(gpath2, self.s2graph)
            for rc in r_paper.citations:
                rc_edge = (rc.paperId, 'citation')
                self.s2graph.edges[r.paperId]['citation'] += [rc_edge]
                gpath2 = gpath + [rc_edge]
                assert not maxhop1.hop(gpath2, self.s2graph)
                assert maxhop2.hop(gpath2, self.s2graph)
                assert not bowtie1.hop(gpath2, self.s2graph)
                assert not bowtie2.hop(gpath2, self.s2graph)
        for c in root_paper.citations:
            c_edge = (self.root_paperId, 'citation')
            self.s2graph.edges[self.root_paperId]['citation'] += [c_edge]
            gpath = [(self.root_paperId, None), c_edge]
            assert maxhop1.hop(gpath, self.s2graph)
            assert maxhop2.hop(gpath, self.s2graph)
            assert bowtie1.hop(gpath, self.s2graph)
            assert bowtie2.hop(gpath, self.s2graph)
            c_paper = self.s2graph.papers[c.paperId]
            for cr in c_paper.references:
                cr_edge = (cr.paperId, 'reference')
                self.s2graph.edges[c.paperId]['reference'] += [cr_edge]
                gpath2 = gpath + [cr_edge]
                assert not maxhop1.hop(gpath2, self.s2graph)
                assert maxhop2.hop(gpath2, self.s2graph)
                assert not bowtie1.hop(gpath2, self.s2graph)
                assert not bowtie2.hop(gpath2, self.s2graph)
            for cc in c_paper.citations:
                cc_edge = (cc.paperId, 'citation')
                self.s2graph.edges[c.paperId]['citation'] += [cc_edge]
                gpath2 = gpath + [cc_edge]
                assert not maxhop1.hop(gpath2, self.s2graph)
                assert maxhop2.hop(gpath2, self.s2graph)
                assert not bowtie1.hop(gpath2, self.s2graph)
                assert bowtie2.hop(gpath2, self.s2graph)
                maxpaper1 = MaxPaperHopper(len(self.s2graph.edges) - 1)
                maxpaper2 = MaxPaperHopper(len(self.s2graph.edges))
                maxpaper3 = MaxPaperHopper(len(self.s2graph.edges) + 1)
                assert not maxpaper1.hop(gpath2, self.s2graph)
                assert not maxpaper2.hop(gpath2, self.s2graph)
                assert maxpaper3.hop(gpath2, self.s2graph)
        assert GraphHopper().hop(gpath, self.s2graph)
        # verify_gpath requires gpath of length 3 or greater
        gpath3 = gpath2 + [("some_paperId", "reference")]
        assert not bowtie2.hop(gpath3, self.s2graph)
        gpath3 = gpath2 + [("some_paperId", "citation")]
        assert bowtie2.hop(gpath3, self.s2graph)
        gpath3 = [("0", None), ("1", "reference"), ("1", "citation"), ("2", "citation")]
        assert not bowtie2.hop(gpath3, self.s2graph)
        # LivingLitreview
        # verify max_references/max_citation
        assert LivingLitReviewHopper(1,2).hop(gpath3, self.s2graph)
        assert not LivingLitReviewHopper(1,1).hop(gpath3, self.s2graph)
        # verify first hop is reference
        gpath3 = [("0", None), ("1", "citation"), ("1", "citation"), ("2", "citation")]
        assert not LivingLitReviewHopper(1, 2).hop(gpath3, self.s2graph)
        # verify inconsisent gpath
        gpath3 = [("0", None), ("1", "reference"), ("1", "reference"), ("2", "citation")]
        assert not LivingLitReviewHopper(1, 2).hop(gpath3, self.s2graph)
        gpath3 = [("0", None), ("1", "reference"), ("1", "reference"), ("2", "citation"), ("3", "citation")]
        assert not LivingLitReviewHopper(1, 3, verify_gpath=True).hop(gpath3, self.s2graph)
