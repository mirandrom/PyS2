from betamax import Betamax
from requests import Session
from requests.exceptions import HTTPError
from unittest import TestCase
import pytest
from .context import api


with Betamax.configure() as config:
    config.cassette_library_dir = 'tests/fixtures/cassettes'


class TestApi(TestCase):
    def setUp(self):
        self.session = Session()
        self.paperId = "c4e3be316ce0d5dfc9ec7b19298e9483484cc252"
        self.paperId_404 = 'paper'
        self.paper_url = api.build_url(self.paperId, "paper")
        self.authorId = "144794037"
        self.authorId_404 = 'author'
        self.author_url = api.build_url(self.authorId, "author")

    def test_get_paper(self):
        with Betamax(self.session).use_cassette('paper'):
            p = api.get_paper(self.paperId, session=self.session)
            assert p.paperId == self.paperId

    def test_get_paper_with_return_json(self):
        with Betamax(self.session).use_cassette('paper'):
            p = api.get_paper(self.paperId, session=self.session,
                              return_json=True)
            assert p['paperId'] == self.paperId

    def test_get_paper_with_404(self):
        with Betamax(self.session).use_cassette('paper_404'):
            with pytest.raises(HTTPError):
                api.get_paper(self.paperId_404, session=self.session)

    def test_get_paper_with_429(self):
        with Betamax(self.session).use_cassette('paper_429'):
            with pytest.raises(HTTPError):
                api.get_paper(self.paperId, session=self.session,
                              wait=0, retries=1)

    def test_get_author(self):
        with Betamax(self.session).use_cassette('author'):
            a = api.get_author(self.authorId, session=self.session)
            assert a.authorId == self.authorId

    def test_get_author_with_return_json(self):
        with Betamax(self.session).use_cassette('author'):
            a = api.get_author(self.authorId, session=self.session,
                               return_json=True)
            assert a['authorId'] == self.authorId

    def test_get_author_with_404(self):
        with Betamax(self.session).use_cassette('author_404'):
            with pytest.raises(HTTPError):
                api.get_author(self.authorId_404, session=self.session)

    def test_get_author_with_429(self):
        with Betamax(self.session).use_cassette('author_429'):
            with pytest.raises(HTTPError):
                api.get_author(self.authorId, session=self.session,
                               wait=0, retries=1)

    def test_build_url(self):
        # public paper endpoint
        url = api.build_url(self.paperId, 'paper')
        assert url == f"{api.API_URL}/paper/{self.paperId}"
        # partner paper endpoint
        url = api.build_url(self.paperId, 'paper', True)
        assert url == f"{api.PARTNER_URL}/paper/{self.paperId}"
        # public author endpoint
        url = api.build_url(self.authorId, 'author')
        assert url == f"{api.API_URL}/author/{self.authorId}"
        # partner author endpoint
        url = api.build_url(self.authorId, 'author', True)
        assert url == f"{api.PARTNER_URL}/author/{self.authorId}"

    def test_build_session(self):
        # default no session and no api key
        session = api.build_session(None, None)
        assert 'x-api-key' not in session.headers
        # custom session and no api key
        session = api.build_session(Session(), None)
        assert 'x-api-key' not in session.headers
        # custom session and arg api key
        arg_api_key = '123'
        session = api.build_session(Session(), arg_api_key)
        assert session.headers['x-api-key'] == arg_api_key
        # custom session and session api key
        session = Session()
        session_api_key = '456'
        session.headers['x-api-key'] = session_api_key
        session = api.build_session(session, None)
        assert session.headers['x-api-key'] == session_api_key
        # custom session and session+arg api key (allow overriding)
        custom_session = Session()
        custom_session.headers['x-api-key'] = session_api_key
        session = api.build_session(session, arg_api_key)
        assert session.headers['x-api-key'] == arg_api_key
        assert custom_session.headers['x-api-key'] == session_api_key
