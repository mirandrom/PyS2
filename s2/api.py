import requests
import time
from s2.models import S2Paper, S2Author
import logging
from typing import Optional, Union, Dict, Tuple
import copy

API_URL = "https://api.semanticscholar.org/v1"
PARTNER_URL = "https://partner.semanticscholar.org/v1"

logger = logging.getLogger('s2')


def build_url(
        api_id: str,
        endpoint: str = 'paper',
        partner: bool = False,
) -> str:
    """ Build url for different endpoints and api identifiers"""
    return f"{PARTNER_URL if partner else API_URL}/{endpoint}/{api_id}"


def build_session(
        session: Optional[requests.Session] = None,
        api_key: Optional[str] = None,
) -> requests.Session:
    """ Build session and reconcile passing of api key via arg or via session

    If an api key is included in the session headers, and passed through the
    `api_key` arg, then the value in the session headers will be overwritten
    temporarily for this request.
    """
    if api_key and session:
        session = copy.deepcopy(session)
    if session is None:
        session = requests.Session()
    if api_key:
        session.headers['x-api-key'] = api_key
    return session


def get_paper(
        paperId: str,
        api_key: Optional[str] = None,
        session: Optional[requests.Session] = None,
        return_json: Optional[bool] = False,
        retries: Optional[int] = 2,
        wait: Optional[int] = 150,
        **kwargs
) -> Union[Dict, S2Paper]:
    """
    Look up information about a paper in Semantic Scholar using
    :meth:`requests.Session.get`
    Returns a :class:`~s2.models.S2Paper` object describing the paper.

    Args:
        paperId  (:obj:`str`):
            Semantic Scholar paper identifier or URL. 

            Accessible Paper Identifiers and Examples:

            * S2 Paper ID : ``0796f6cd7f0403a854d67d525e9b32af3b277331``
            * DOI : ``10.1038/nrn3241``
            * ArXiv ID : ``arXiv:1705.10311``
            * MAG ID : ``MAG:112218234``
            * ACL ID : ``ACL:W12-3903``
            * PubMed ID : ``PMID:19872477``
            * Corpus ID : ``CorpusID:37220927``
        api_key  (:obj:`str`, optional):
            A `Data Partners <https://pages.semanticscholar.org/data-partners>`_
            API key. Overwrites API key passed through ``session``.
            Defaults to ``None``
        session (:obj:`requests.Session`, optional):
            A :class:`requests.Session` object, can be used to store an API key
            (see :any:`using_an_api_key`). Note that ``api_key`` will overwrite
            this value if it is provided.
            Defaults to ``None``
        return_json (:obj:`bool`, optional):
            Return original json from get request
            (e.g. in case of PyS2-breaking changes to the S2 API).
            Defaults to ``False``
        retries (:obj:`int`, optional):
            Number of retry attempts after rate limit is exceeded.
            Defaults to ``2``
        wait (:obj:`int`, optional):
            Number of seconds to wait between retries if rate limit is exceeded
            (100 per 5 minute window for public API). Defaults to ``150``.
            This can be safely lowered with access to the `Data Partners
            <https://pages.semanticscholar.org/data-partners>`_ API
            (see :any:`using_an_api_key`)
        **kwargs (:obj:`Dict[str, any]`, optional):
            Keyword Args for :meth:`requests.Session.get`. e.g. to include
            unknown references use
            ``params = dict(include_unknown_references=True)``.
            Defaults to ``{}``

    Returns:
        :class:`dict` or :class:`~s2.models.S2Paper`:
        A :class:`~s2.models.S2Paper` or ``dict`` object describing the paper
    """
    session = build_session(session, api_key)
    partner = 'x-api-key' in session.headers
    url = build_url(paperId, endpoint='paper', partner=partner)
    r = session.get(url, **kwargs)

    if r.ok:
        if return_json:
            return r.json()
        else:
            return S2Paper(**r.json())
    # I found I was getting 403 Forbidden errors when exceeding rate limits
    elif r.status_code in [429, 403] and retries > 0:
        logger.warning(f"Error {r.status_code} on paper {paperId}: "
                       f" sleeping for {wait} seconds"
                       f" with {retries} attempts remaining.")
        time.sleep(wait)
        return get_paper(paperId, api_key, session, return_json,
                         retries-1, wait, **kwargs)
    else:
        logger.error(f"Error {r.status_code} on paper {paperId}")
        r.raise_for_status()


def get_author(
        authorId: str,
        api_key: str = None,
        session: Optional[requests.Session] = None,
        return_json: Optional[bool] = False,
        retries: int = 2,
        wait: int = 150,
        **kwargs
) -> Union[Dict, S2Author]:
    """
    Look up information about an author in Semantic Scholar.
    Returns a :class:`~s2.models.S2Author` object describing the author.

    Args:
        authorId  (:obj:`str`):
            Semantic Scholar author identifier.
        api_key  (:obj:`str`, optional):
            A `Data Partners <https://pages.semanticscholar.org/data-partners>`_
            API key. Temporarily overwrites API key passed through ``session``.
            Defaults to ``None``
        session (:obj:`requests.Session`, optional):
            A :class:`requests.Session` object, can be used to store an API key
            (see :any:`using_an_api_key`). Note that ``api_key`` will overwrite
            this value temporarily if it is provided.
            Defaults to ``None``
        return_json (:obj:`bool`, optional):
            Return original json from get request
            (e.g. in case of PyS2-breaking changes to the S2 API).
            Defaults to ``False``
        retries (:obj:`int`, optional):
            Number of retry attempts after rate limit is exceeded.
            Defaults to ``2``
        wait (:obj:`int`, optional):
            Number of seconds to wait between retries if rate limit is exceeded
            (100 per 5 minute window for public API). Defaults to ``150``.
            This can be safely lowered with access to the `Data Partners
            <https://pages.semanticscholar.org/data-partners>`_ API
            (see :any:`using_an_api_key`)
        **kwargs (:obj:`Dict[str, any]`, optional):
            Keyword Args for :meth:`requests.Session.get`.
             Defaults to ``{}``

    Returns:
        :class:`dict` or :class:`~s2.models.S2Author`:
        A :class:`~s2.models.S2Author` or ``dict`` object describing the author
    """
    session = build_session(session, api_key)
    partner = 'x-api-key' in session.headers
    url = build_url(authorId, endpoint='author', partner=partner)
    r = session.get(url, **kwargs)

    if r.ok:
        if return_json:
            return r.json()
        else:
            return S2Author(**r.json())
    # I found I was getting 403 Forbidden errors when exceeding rate limits
    elif r.status_code in [429, 403] and retries > 0:
        logger.warning(f"Error {r.status_code} on author {authorId}: "
                       f" sleeping for {wait} seconds"
                       f" with {retries} attempts remaining.")
        time.sleep(wait)
        return get_author(authorId, api_key, session, return_json,
                          retries-1, wait, **kwargs)
    else:
        logger.error(f"Error {r.status_code} on author {authorId}")
        r.raise_for_status()
