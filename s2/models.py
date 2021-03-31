from pydantic import BaseModel
from typing import List, Optional

# TODO: add data validators for consistent handling of empty types
#       see https://github.com/samuelcolvin/pydantic/discussions/2611#discussion-3300585


class S2Topic(BaseModel):
    """
    Class for topics in :class:`.models.S2Paper`

    Attributes
        topic (:obj:`str`, optional):
            Name of the topic
        topicId (:obj:`str`, optional):
            Semantic Scholar identifier of the topic
        url (:obj:`str`, optional):
            Semantic Scholar URL of the topic page with format
            https://www.semanticscholar.org/topic/topicId
    """
    topic: Optional[str]
    topicId: Optional[str]
    url: Optional[str]


class S2PaperAuthor(BaseModel):
    """
    Class for authors in :class:`.S2Paper`
    or :class:`.S2Reference`

    Attributes
        authorId (:obj:`str`, optional):
            Semantic Scholar identifier of the author
        name (:obj:`str`, optional):
            Name of author
        url (:obj:`str`, optional):
            Semantic Scholar URL to author page.

            Not included for authors from :class:`.S2Reference`,
            but easily reconstructed as
            https://www.semanticscholar.org/author/authorId
    """
    authorId: Optional[str]
    name: Optional[str]
    url: Optional[str] = None


class S2Reference(BaseModel):
    """
    Class for papers that are references/citations in :class:`.S2Paper`

    Attributes
        arxivId (:obj:`str`, optional):
            ArXiv identifier of the paper
        authors (:obj:`list` of :obj:`.S2PaperAuthor`, optional):
            List of authors of the paper
        doi (:obj:`str`, optional):
            Digital Object Identifier registered at doi.org
        intent (:obj:`list` of :obj:`str`, optional):
            List of citation intents, see
            https://medium.com/ai2-blog/citation-intent-classification-bd2bd47559de
        isInfluential: (:obj:`bool`, optional):
            If the paper is influential,
            see https://www.semanticscholar.org/faq#influential-citations)
        paperId: (:obj:`str`, optional):
            Semantic Scholar identifier of the paper
        title: (:obj:`str`, optional):
            Title of the paper
        url: (:obj:`str`, optional):
            Semantic Scholar URL of the paper
        venue: (:obj:`str`, optional):
            Extracted publication venue of the paper
        year: (:obj:`int`, optional):
            Publication year of the paper
    """
    arxivId: Optional[str]
    authors: Optional[List[S2PaperAuthor]]
    doi: Optional[str]
    intent: Optional[List[str]]
    isInfluential: bool
    paperId: Optional[str]
    title: Optional[str]
    url: Optional[str]
    venue: Optional[str]
    year: Optional[int]


class S2Paper(BaseModel):
    """
    Class for Semantic Scholar paper object

    Attributes
        abstract (:obj:`str`, optional):
            Extracted abstract of the paper
        arxivId (:obj:`str`, optional):
            ArXiv identifier of the paper
        authors (:obj:`list` of :obj:`.S2PaperAuthor`, optional):
            List of authors of the paper
        citationVelocity (:obj:`int`, optional):
            Weighted average of the publication’s citations for the last 3 years
        citations (:obj:`list` of :obj:`.S2Reference`, optional):
            List of papers cited by the paper
        corpusId (:obj:`int`, optional):
            Semantic Scholar Corpus ID (or S2CID for short) of the paper
        doi (:obj:`str`, optional):
            Digital Object Identifier registered at doi.org
        fieldsOfStudy (:obj:`list` of :obj:`str`, optional):
            Zero or more fields of study this paper addresses
        influentialCitationCount (:obj:`int`, optional):
            Number of influential citations,
            see https://www.semanticscholar.org/faq#influential-citations)
        is_open_access (:obj:`bool`, optional):
            If the paper is open access.
        is_publisher_licensed (:obj:`bool`, optional):
            If the paper is published licensed.
        paperId (:obj:`str`, optional):
            Semantic Scholar identifier of the paper
        references (:obj:`list` of :obj:`.S2Reference`, optional):
            List of papers referenced by the paper
        title (:obj:`str`, optional):
            Title of the paper
        topics (:obj:`list` of :obj:`.S2Topic`, optional):
            List of extracted topics,
            see https://www.semanticscholar.org/faq#extract-key-phrases
        url (:obj:`str`, optional):
            Semantic Scholar URL of the paper
        venue (:obj:`str`, optional):
            Extracted publication venue of the paper
        year (:obj:`int`, optional):
            Publication year of the paper
    """
    abstract: Optional[str]
    arxivId: Optional[str]
    authors: Optional[List[S2PaperAuthor]]
    citationVelocity: Optional[int]
    citations: Optional[List[S2Reference]]
    corpusId: Optional[int]
    doi: Optional[str]
    fieldsOfStudy: Optional[List[str]]
    influentialCitationCount: Optional[int]
    is_open_access: Optional[bool]
    is_publisher_licensed: Optional[bool]
    paperId: Optional[str]
    references: Optional[List[S2Reference]]
    title: Optional[str]
    topics: Optional[List[S2Topic]]
    url: Optional[str]
    venue: Optional[str]
    year: Optional[int]


class S2AuthorPaper(BaseModel):
    """
    Class for papers in :class:`.S2Author`

    Attributes
        paperId (:obj:`str`, optional):
            Semantic Scholar identifier of the paper
        title (:obj:`str`, optional):
            Title of the paper
        url (:obj:`str`, optional):
            Semantic Scholar URL to paper page
        year (:obj:`int`, optional):
            Publication year of the paper

    """
    paperId: Optional[str]
    title: Optional[str]
    url: Optional[str]
    year: Optional[int]


class S2Author(BaseModel):
    """
    Class for Semantic Scholar author object

    Attributes
        aliases  (:obj:`list` of :obj:`str`, optional):
            Aliases of the author (e.g. "O. Etzioni" and "Oren Et-zioni")
        authorId  (:obj:`str`, optional):
            Semantic Scholar identifier of the author
        influentialCitationCount  (:obj:`int`, optional):
            Number of influential citations,
            see https://www.semanticscholar.org/faq#influential-citations)
        name  (:obj:`str`, optional):
            Name of the author
        papers  (:obj:`list` of :obj:`.S2AuthorPaper`, optional):
            List of papers written by the author
        url  (:obj:`str`, optional):
            Semantic Scholar URL to author page.
    """
    aliases: Optional[List[str]]
    authorId: Optional[str]
    influentialCitationCount: Optional[int]
    name: Optional[str]
    papers: Optional[List[S2AuthorPaper]]
    url: Optional[str]
