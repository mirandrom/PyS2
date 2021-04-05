from pathlib import Path
from unittest import TestCase
import pytest
from ..context import rm_tree, JsonDS


class TestJson(TestCase):
    def setUp(self):
        fixtures = Path("tests/fixtures/store/json")
        self.pds_path = fixtures / "s2papers"
        self.pds_path_tmp = fixtures / "s2papers_tmp"
        self.ads_path = fixtures / "s2authors"
        self.ads_path_tmp = fixtures / "s2authors_tmp"
        assert self.pds_path.exists()
        assert self.ads_path.exists()
        assert not self.pds_path_tmp.exists()
        assert not self.ads_path_tmp.exists()
        self.addCleanup(lambda: rm_tree(self.pds_path_tmp))
        self.addCleanup(lambda: rm_tree(self.ads_path_tmp))

    def test_pds(self):
        # create new pds (paper datastore)
        pds_tmp = JsonDS.load_papers(self.pds_path_tmp)
        assert pds_tmp.json_dir.exists()

        # load existing ds and check values; testing contains and len methods
        pds = JsonDS.load_papers(self.pds_path)
        assert "a04fc380c61040c7ffa21375bf2a0c9d30b674a4" in pds
        assert "bdfa1a62c964f19b5ce000d7812ba9f66456a4a4" in pds
        assert "c656a68a2bf155fa1a8ef4dd38a0af2cac3911da" in pds
        assert len(pds) == 3

        # copy values into temp pds; testing iter, set, and get methods
        for k,v in pds.items():
            pds_tmp[k] = v
        for k in pds_tmp.keys():
            assert pds[k] == pds_tmp[k]

        # delete key and check for keyerrors
        p = pds_tmp.pop(k)
        with pytest.raises(KeyError):
            _ = pds_tmp[k]

        # enforce_id behavior
        with pytest.raises(KeyError):
            wrong_key = k[:-1]
            pds_tmp[wrong_key] = p

        # check for type errors
        p = pds[k]
        for invalid_value in [k, 0, None, p.dict(), p.json()]:
            with pytest.raises(TypeError):
                pds_tmp[k] = invalid_value
        for invalid_key in [0, None]:
            with pytest.raises(TypeError):
                _ = pds_tmp[invalid_key]

    def test_ads(self):
        # create new ads (author datastore)
        assert not self.ads_path_tmp.exists()
        ads_tmp = JsonDS.load_authors(self.ads_path_tmp)
        assert ads_tmp.json_dir.exists()

        # load existing ds and check values; testing contains and len methods
        assert self.ads_path.exists()
        ads = JsonDS.load_authors(self.ads_path)
        assert "80806115" in ads
        assert "144794037" in ads
        assert "2051526200" in ads
        assert len(ads) == 3

        # copy values into temp pds; testing iter, set, and get methods
        for k,v in ads.items():
            ads_tmp[k] = v
        for k in ads_tmp.keys():
            assert ads[k] == ads_tmp[k]

        # delete key and check for keyerrors
        a = ads_tmp.pop(k)
        with pytest.raises(KeyError):
            _ = ads_tmp[k]

        # enforce_id behavior
        with pytest.raises(KeyError):
            wrong_key = k[:-1]
            ads_tmp[wrong_key] = a

        # check for type errors
        a = ads[k]
        for invalid_value in [k, 0, None, a.dict(), a.json()]:
            with pytest.raises(TypeError):
                ads_tmp[k] = invalid_value
        for invalid_key in [0, None]:
            with pytest.raises(TypeError):
                _ = ads_tmp[invalid_key]