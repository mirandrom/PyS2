from s2.models import S2Paper, S2Author
from typing import MutableMapping, Iterator, TypeVar, Type, Union

PaperId = str
AuthorId = str
S2Identifier = TypeVar("S2Identifier", PaperId, AuthorId)
S2Model = TypeVar("S2Model", S2Paper, S2Author)
S2ModelT = Union[Type[S2Paper],Type[S2Author]]

# TODO: figure out TypeVar behavior for class inheritance.
#       The methods for S2Papers/S2Authors should be the exact same except for
#       argument and return types (and data validation, but that is easily
#       abstracted away via methods that work for both classes). To prevent
#       duplicate code (e.g. in v1.1.0 s2.db module), its better to have
#       the behaviour for S2Paper/S2Author be abstracted away in a single
#       class; the issue becomes making typehints work for both S2Paper and
#       S2Author. TypeVar allows us to define the typehint as a variable with
#       constraints. It's not clear if this variable is set for a class instance
#       (good, ensures consistency across life of instance) or for individual
#       method calls (bad, same instance might have different type hints
#       depending on most recent method call).
#       If TypeVar is inappropriate, consider using overload


class S2DataStore(MutableMapping[S2Identifier,S2Model]):
    """ Base class for storing/retrieving S2 Objects

    """
    def __init__(self, s2model: S2ModelT = S2Paper):
        self.s2model: S2ModelT = s2model

    @classmethod
    def load_papers(cls: Type['S2DataStore'],
                    *args, **kwargs) -> 'S2DataStore[PaperId, S2Paper]':
        """Create datastore for papers with appropriate typehints. """
        kwargs['s2model'] = S2Paper
        return cls(*args, **kwargs)

    @classmethod
    def load_authors(cls: Type['S2DataStore'],
                     *args, **kwargs) -> 'S2DataStore[AuthorId, S2Author]':
        """Create datastore for authors with appropriate typehints. """
        kwargs['s2model'] = S2Author
        return cls(*args, **kwargs)

    def _check_key_type(self, k: S2Identifier):
        if type(k) is not str:
            raise TypeError(f"{type(k)} instead of str")

    def _check_value_type(self, v: S2Model):
        if type(v) is not self.s2model:
            raise TypeError(f"{type(v)} instead of {self.s2model.__name__}")

    def _check_s2id(self, k: S2Identifier, v: S2Model):
        s2id = None
        if self.s2model == S2Paper and type(v) == S2Paper:
            s2id = v.__dict__.get('paperId', None)
        elif self.s2model == S2Author and type(v) == S2Author:
            s2id = v.__dict__.get('authorId', None)
        if s2id and s2id != k:
            raise KeyError(f"Provided key {k} for {self.s2model.__name__} "
                           f"with S2 Identifier {s2id}")

    def __contains__(self, k: S2Identifier) -> bool: ... # type: ignore[override]

    def __delitem__(self, k: S2Identifier) -> None: ...

    def __getitem__(self, k: S2Identifier) -> S2Model: ...

    def __len__(self) -> int: ...

    def __iter__(self) -> Iterator[S2Identifier]: ...

    def __setitem__(self, k: S2Identifier, v: S2Model) -> None: ...
