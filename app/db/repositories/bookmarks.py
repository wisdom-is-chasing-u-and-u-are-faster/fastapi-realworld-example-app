from typing import List, Optional

from asyncpg import Connection

from app.db.queries.queries import queries
from app.db.repositories.base import BaseRepository
from app.db.repositories.profiles import ProfilesRepository
from app.db.repositories.tags import TagsRepository
from app.models.domain.articles import Article
from app.models.domain.users import User


class BookmarksRepository(BaseRepository):
    def __init__(self, conn: Connection) -> None:
        super().__init__(conn)
        self._profiles_repo = ProfilesRepository(conn)
        self._tags_repo = TagsRepository(conn)

    async def is_article_bookmarked_by_user(self, *, slug: str, user: User) -> bool:
        return (
            await queries.is_article_in_bookmarks(
                self.connection,
                username=user.username,
                slug=slug,
            )
        )["bookmarked"]

    async def add_article_into_bookmarks(self, *, article: Article, user: User) -> None:
        await queries.add_article_to_bookmarks(
            self.connection,
            username=user.username,
            slug=article.slug,
        )

    async def remove_article_from_bookmarks(
        self,
        *,
        article: Article,
        user: User,
    ) -> None:
        await queries.remove_article_from_bookmarks(
            self.connection,
            username=user.username,
            slug=article.slug,
        )

    async def get_bookmarks_count_for_article(self, *, slug: str) -> int:
        return (
            await queries.get_bookmarks_count_for_article(
                self.connection,
                slug=slug,
            )
        )["bookmarks_count"]

    async def get_bookmarked_articles_for_user(
        self,
        *,
        user: User,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Article]:
        articles_rows = await queries.get_bookmarked_articles_for_user(
            self.connection,
            username=user.username,
            limit=limit,
            offset=offset,
        )

        articles: List[Article] = []
        for article_row in articles_rows:
            slug = article_row["slug"]
            tags_rows = await queries.get_tags_for_article_by_slug(
                self.connection,
                slug=slug,
            )
            tags = [tag_row["tag"] for tag_row in tags_rows]

            fav_row = await queries.get_favorites_count_for_article(
                self.connection,
                slug=slug,
            )
            favorites_count = fav_row["favorites_count"]

            is_fav_row = await queries.is_article_in_favorites(
                self.connection,
                username=user.username,
                slug=slug,
            )
            favorited = is_fav_row["favorited"]

            author = await self._profiles_repo.get_profile_by_username(
                username=article_row["author_username"],
                requested_user=user,
            )

            article = Article(
                id_=article_row["id"],
                slug=slug,
                title=article_row["title"],
                description=article_row["description"],
                body=article_row["body"],
                author=author,
                tags=tags,
                favorites_count=favorites_count,
                favorited=favorited,
                created_at=article_row["created_at"],
                updated_at=article_row["updated_at"],
            )
            articles.append(article)

        return articles
