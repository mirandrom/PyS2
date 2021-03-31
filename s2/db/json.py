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
    def __init__(self, json_dir: Union[str, Path]):
        self.json_dir = Path(json_dir)
        self.json_dir.mkdir(exist_ok=True, parents=True)
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
        f = (self.json_dir / f"{k}.json")
        f.write_text(v.json())
        self.paperIds.add(k)


class JsonS2AuthorDB(MutableMapping):
    def __init__(self, json_dir: Union[str, Path]):
        self.json_dir = Path(json_dir)
        self.json_dir.mkdir(exist_ok=True, parents=True)
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
        f = (self.json_dir / f"{k}.json")
        f.write_text(v.json())
        self.authorIds.add(k)