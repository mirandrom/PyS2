from s2.store import S2DataStore, S2Identifier, S2ModelT, S2Model
from s2.models import S2Paper
import json

from typing import Union, Optional, Type
from pathlib import Path


class JsonDS(S2DataStore):

    def __init__(self,
                 json_dir: Union[str, Path],
                 enforce_id: Optional[bool] = True,
                 s2model: S2ModelT = S2Paper
                 ):
        super().__init__(s2model=s2model)
        self.json_dir = Path(json_dir).absolute()
        self.json_dir.mkdir(exist_ok=True, parents=True)
        self.enforce_id = enforce_id
        # TODO: check if this slows things down considerably
        self.s2ids = set([f.stem for f in self.json_dir.glob("*.json")])

    def _check_file_exists(self, f: Union[str, Path]):
        if not Path(f).exists():
            raise KeyError(f"{f.stem} (No such file '{f}')")

    def __contains__(self, k):
        return k in self.s2ids

    def __delitem__(self, k):
        self._check_key_type(k)
        f = (self.json_dir / f"{k}.json")
        self._check_file_exists(f)
        self.s2ids.remove(k)
        f.unlink()

    def __getitem__(self, k):
        self._check_key_type(k)
        f = (self.json_dir / f"{k}.json")
        self._check_file_exists(f)
        d = json.loads(f.read_bytes())
        # TODO: figure out how to use construct and keep nested models
        return self.s2model(**d)

    def __len__(self):
        return len(self.s2ids)

    def __iter__(self):
        return self.s2ids.__iter__()

    def __setitem__(self, k: S2Identifier, v: S2Model):
        self._check_key_type(k)
        self._check_value_type(v)
        if self.enforce_id:
            self._check_s2id(k, v)
        f = (self.json_dir / f"{k}.json")
        f.write_text(v.json())
        self.s2ids.add(k)

