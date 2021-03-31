from s2.models import S2Paper, S2Author
from _collections_abc import MutableMapping
from pathlib import Path
import json

import logging
logger = logging.getLogger("s2")

from typing import Iterator, Union

PaperId = str
AuthorId = str


# TODO: look into yapic.json/ujson/orjson for fast encoding/decoding
# TODO: get rid of duplicate code for S2Paper/S2Author, either through:
#       (1) class inheritance (not sure how to properly handle typing
#           without reduplicating every method anyways)
#       (2) a single interface with e.g. paper/author kwarg passed e.g.
#           at class instantiation (once again not sure how to handle
#           typing, and it doesn't feel very user-friendy)
#       whatever gets implemented should be consistent with the s2.api interface


class JsonS2PaperDB(MutableMapping):
    """Dict-like interface to store S2Papers as jsons and retrieve as S2Papers

    Note:
        Types are enforced, so keys must be valid PaperIds and values must
        be instances of :class:`.S2Paper`.

    Args:
        json_dir (str or :class:`~pathlib.Path`):
            Directory where papers are saved as jsons. If directory does not
            exist, it will be created and populated with jsons as values are
            set in the object. For example:

            .. code-block:: python

                pdb = JsonS2PaperDB("db")
                paper = s2.api.get_paper(k)
                pdb[k] = paper

            will first create a directory ``db``, then a file ``db/{k}.json``
            containing the :class:`S2Paper` that was passed,
            in a json-serialized format.

            Similarly, removing items from the object (e.g. ``pdb.pop(k)``)
            will delete the corresponding json file.

        enforce_id (`bool`, optional):
            Enforce that a key be equal to the ``paperId`` field of the
            :class:`.S2Paper` object (if it exists; for handling unknown
            references without a ``paperId`` value, see :any:`saving_unknown`).

    Attributes:
        paperIds (`set` of `str`):
            In-memory lookup of existing keys, updated whenever a key is
            added or removed. Will likely be updated to something less scrappy.
    """
    def __init__(self, json_dir: Union[str, Path], enforce_id: bool = True):
        self.json_dir = Path(json_dir)
        self.json_dir.mkdir(exist_ok=True, parents=True)
        self.enforce_id = enforce_id
        self.paperIds = set([f.stem for f in self.json_dir.glob("*.json")])

    def _check_key_type(self, k: PaperId):
        if type(k) is not str:
            raise TypeError(f"{type(k)} instead of str")

    def _check_val_type(self, v: S2Paper):
        if type(v) is not S2Paper:
            raise TypeError(f"{type(v)} instead of S2Paper")

    def _check_file_exists(self, f: Path):
        if not f.exists():
            raise KeyError(f.stem)

    def _check_key_value(self, k: PaperId, v: S2Paper):
        if v.paperId and v.paperId != k:
            raise KeyError(f"Provided key {k} for S2Paper with id {v.paperId}")

    def __contains__(self, k: PaperId) -> bool:
        return k in self.paperIds

    def __delitem__(self, k: PaperId) -> None:
        self._check_key_type(k)
        f = (self.json_dir / f"{k}.json")
        self._check_file_exists(f)
        self.paperIds.remove(k)
        f.unlink()

    def __getitem__(self, k: PaperId) -> S2Paper:
        self._check_key_type(k)
        f = (self.json_dir / f"{k}.json")
        self._check_file_exists(f)
        return S2Paper(**json.loads(f.read_text()))

    def __len__(self) -> int:
        return len(self.paperIds)

    def __iter__(self) -> Iterator[PaperId]:
        return self.paperIds.__iter__()

    def __setitem__(self, k: PaperId, v: S2Paper) -> None:
        self._check_key_type(k)
        self._check_val_type(v)
        if self.enforce_id:
            self._check_key_value(k, v)
        f = (self.json_dir / f"{k}.json")
        f.write_text(v.json())
        self.paperIds.add(k)


class JsonS2AuthorDB(MutableMapping):
    """Dict-like interface to store S2Authors as jsons and retrieve as S2Authors

    Note:
        Types are enforced, so keys must be valid AuthorIds and values must
        be instances of :class:`.S2Author`.

    Args:
        json_dir (str or :class:`~pathlib.Path`):
            Directory where authors are saved as jsons. If directory does not
            exist, it will be created and populated with jsons as values are
            set in the object. For example:

            .. code-block:: python

                adb = JsonS2AuthorDB("db")
                author = s2.api.get_author(k)
                adb[k] = author

            will first create a directory ``db``, then a file ``db/{k}.json``
            containing the class:`.S2Author` that was passed,
            in a json-serialized format.

            Similarly, removing items from the object (e.g. ``pdb.pop(k)``)
            will delete the corresponding json file.

        enforce_id (`bool`, optional):
            Enforce that a key be equal to the ``authorId`` field of the
            :class:`.S2Author` object (if it exists; for handling unknown
            authors without an ``authorId`` value, see :any:`saving_unknown`).

    Attributes:
        authorIds (`set` of `str`):
            In-memory lookup of existing keys, updated whenever a key is
            added or removed. Will likely be updated to something less scrappy.
    """
    def __init__(self, json_dir: Union[str, Path], enforce_id: bool = True):
        self.json_dir = Path(json_dir)
        self.json_dir.mkdir(exist_ok=True, parents=True)
        self.enforce_id = enforce_id
        self.authorIds = set([f.stem for f in self.json_dir.glob("*.json")])

    def _check_key_type(self, k: AuthorId):
        if type(k) is not str:
            raise TypeError(f"{type(k)} instead of str")

    def _check_val_type(self, v: S2Author):
        if type(v) is not S2Author:
            raise TypeError(f"{type(v)} instead of S2Author")

    def _check_file_exists(self, f: Path):
        if not f.exists():
            raise KeyError(f.stem)

    def _check_key_value(self, k: AuthorId, v: S2Author):
        if v.authorId and v.authorId != k:
            raise KeyError(f"Provided key {k} for S2Author with id {v.authorId}")

    def __contains__(self, k: AuthorId) -> bool:
        return k in self.authorIds

    def __delitem__(self, k: AuthorId) -> None:
        self._check_key_type(k)
        f = (self.json_dir / f"{k}.json")
        self._check_file_exists(f)
        self.authorIds.remove(k)
        f.unlink()

    def __getitem__(self, k: AuthorId) -> S2Author:
        self._check_key_type(k)
        f = (self.json_dir / f"{k}.json")
        self._check_file_exists(f)
        return S2Author(**json.loads(f.read_text()))

    def __len__(self) -> int:
        return len(self.authorIds)

    def __iter__(self) -> Iterator[PaperId]:
        return self.authorIds.__iter__()

    def __setitem__(self, k: PaperId, v: S2Author) -> None:
        self._check_key_type(k)
        self._check_val_type(v)
        if self.enforce_id:
            self._check_key_value(k, v)
        f = (self.json_dir / f"{k}.json")
        f.write_text(v.json())
        self.authorIds.add(k)