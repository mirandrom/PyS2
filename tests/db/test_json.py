from pathlib import Path
from unittest import TestCase
import pytest
from ..context import JsonS2PaperDB, JsonS2AuthorDB


def rm_tree(pth: Path):
    """ Utility for removing directory recursively"""
    pth = Path(pth)
    if pth.exists():
        for child in pth.glob('*'):
            if child.is_file():
                child.unlink()
            else:
                rm_tree(child)
        pth.rmdir()


class TestJson(TestCase):
    def setUp(self):
        fixtures = Path("tests/fixtures/db/json")
        self.pdb_path = fixtures / "s2papers"
        self.pdb_path_tmp = fixtures / "s2papers_tmp"
        self.adb_path = fixtures / "s2authors"
        self.adb_path_tmp = fixtures / "s2authors_tmp"
        assert self.pdb_path.exists()
        assert self.adb_path.exists()
        assert not self.pdb_path_tmp.exists()
        assert not self.adb_path_tmp.exists()
        self.addCleanup(lambda: rm_tree(self.pdb_path_tmp))
        self.addCleanup(lambda: rm_tree(self.adb_path_tmp))

    def test_pdb(self):
        # create new pdb (paper database)
        pdb_tmp = JsonS2PaperDB(self.pdb_path_tmp)
        assert pdb_tmp.json_dir.exists()

        # load existing db and check values; testing contains and len methods
        pdb = JsonS2PaperDB(self.pdb_path)
        assert "a04fc380c61040c7ffa21375bf2a0c9d30b674a4" in pdb
        assert "bdfa1a62c964f19b5ce000d7812ba9f66456a4a4" in pdb
        assert "c656a68a2bf155fa1a8ef4dd38a0af2cac3911da" in pdb
        assert len(pdb) == 3

        # copy values into temp pdb; testing iter, set, and get methods
        for k,v in pdb.items():
            pdb_tmp[k] = v
        for k in pdb_tmp.keys():
            assert pdb[k] == pdb_tmp[k]

        # delete key and check for keyerrors
        p = pdb_tmp.pop(k)
        with pytest.raises(KeyError):
            _ = pdb_tmp[k]

        # enforce_id behavior
        with pytest.raises(KeyError):
            wrong_key = k[:-1]
            pdb_tmp[wrong_key] = p

        # check for type errors
        p = pdb[k]
        for invalid_value in [k, 0, None, p.dict(), p.json()]:
            with pytest.raises(TypeError):
                pdb_tmp[k] = invalid_value
        for invalid_key in [0, None]:
            with pytest.raises(TypeError):
                _ = pdb_tmp[invalid_key]

    def test_adb(self):
        # create new adb (author database)
        assert not self.adb_path_tmp.exists()
        adb_tmp = JsonS2AuthorDB(self.adb_path_tmp)
        assert adb_tmp.json_dir.exists()

        # load existing db and check values; testing contains and len methods
        assert self.adb_path.exists()
        adb = JsonS2AuthorDB(self.adb_path)
        assert "80806115" in adb
        assert "144794037" in adb
        assert "2051526200" in adb
        assert len(adb) == 3

        # copy values into temp pdb; testing iter, set, and get methods
        for k,v in adb.items():
            adb_tmp[k] = v
        for k in adb_tmp.keys():
            assert adb[k] == adb_tmp[k]

        # delete key and check for keyerrors
        a = adb_tmp.pop(k)
        with pytest.raises(KeyError):
            _ = adb_tmp[k]

        # enforce_id behavior
        with pytest.raises(KeyError):
            wrong_key = k[:-1]
            adb_tmp[wrong_key] = a

        # check for type errors
        a = adb[k]
        for invalid_value in [k, 0, None, a.dict(), a.json()]:
            with pytest.raises(TypeError):
                adb_tmp[k] = invalid_value
        for invalid_key in [0, None]:
            with pytest.raises(TypeError):
                _ = adb_tmp[invalid_key]