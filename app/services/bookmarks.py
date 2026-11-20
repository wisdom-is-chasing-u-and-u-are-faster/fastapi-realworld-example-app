from app.db.repositories.bookmarks import BookmarksRepository
from app.models.domain.articles import Article
from app.models.domain.users import User


class BookmarkService:
    @staticmethod
    async def bookmark_article(
        *,
        bookmarks_repo: BookmarksRepository,
        article: Article,
        user: User,
    ) -> bool:
        is_bookmarked = await bookmarks_repo.is_article_bookmarked_by_user(
            slug=article.slug,
            user=user,
        )
        if is_bookmarked:
            return False

        await bookmarks_repo.add_article_into_bookmarks(
            article=article,
            user=user,
        )
        return True

    @staticmethod
    async def unbookmark_article(
        *,
        bookmarks_repo: BookmarksRepository,
        article: Article,
        user: User,
    ) -> bool:
        is_bookmarked = await bookmarks_repo.is_article_bookmarked_by_user(
            slug=article.slug,
            user=user,
        )
        if not is_bookmarked:
            return False

        await bookmarks_repo.remove_article_from_bookmarks(
            article=article,
            user=user,
        )
        return True
