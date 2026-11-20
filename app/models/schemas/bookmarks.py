from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.schemas.articles import (
    DEFAULT_ARTICLES_LIMIT,
    DEFAULT_ARTICLES_OFFSET,
    ArticleForResponse,
)
from app.models.schemas.rwschema import RWSchema


class ArticleWithBookmark(ArticleForResponse):
    bookmarked: bool = False


class ArticleWithBookmarkInResponse(RWSchema):
    article: ArticleWithBookmark


class ListOfBookmarkedArticlesInResponse(RWSchema):
    articles: List[ArticleForResponse]
    articles_count: int


class BookmarksFilters(BaseModel):
    limit: int = Field(DEFAULT_ARTICLES_LIMIT, ge=1)
    offset: int = Field(DEFAULT_ARTICLES_OFFSET, ge=0)
