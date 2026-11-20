import pytest
from asyncpg.pool import Pool
from fastapi import FastAPI
from httpx import AsyncClient
from starlette import status

from app.db.repositories.articles import ArticlesRepository
from app.db.repositories.bookmarks import BookmarksRepository
from app.db.repositories.users import UsersRepository
from app.models.domain.articles import Article
from app.models.domain.users import UserInDB
from app.models.schemas.bookmarks import (
    ArticleWithBookmarkInResponse,
    ListOfBookmarkedArticlesInResponse,
)

pytestmark = pytest.mark.asyncio


async def test_user_can_bookmark_article(
    app: FastAPI,
    authorized_client: AsyncClient,
    test_article: Article,
    test_user: UserInDB,
    pool: Pool,
) -> None:
    response = await authorized_client.post(
        app.url_path_for("articles:bookmark-article", slug=test_article.slug)
    )
    assert response.status_code == status.HTTP_200_OK
    response_data = ArticleWithBookmarkInResponse(**response.json())
    assert response_data.article.slug == test_article.slug
    assert response_data.article.bookmarked is True

    async with pool.acquire() as connection:
        bookmarks_repo = BookmarksRepository(connection)
        is_bookmarked = await bookmarks_repo.is_article_bookmarked_by_user(
            slug=test_article.slug,
            user=test_user,
        )
        assert is_bookmarked is True


async def test_user_cannot_bookmark_already_bookmarked_article(
    app: FastAPI,
    authorized_client: AsyncClient,
    test_article: Article,
    test_user: UserInDB,
    pool: Pool,
) -> None:
    async with pool.acquire() as connection:
        bookmarks_repo = BookmarksRepository(connection)
        await bookmarks_repo.add_article_into_bookmarks(
            article=test_article,
            user=test_user,
        )

    response = await authorized_client.post(
        app.url_path_for("articles:bookmark-article", slug=test_article.slug)
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_user_can_unbookmark_article(
    app: FastAPI,
    authorized_client: AsyncClient,
    test_article: Article,
    test_user: UserInDB,
    pool: Pool,
) -> None:
    async with pool.acquire() as connection:
        bookmarks_repo = BookmarksRepository(connection)
        await bookmarks_repo.add_article_into_bookmarks(
            article=test_article,
            user=test_user,
        )

    response = await authorized_client.delete(
        app.url_path_for("articles:unbookmark-article", slug=test_article.slug)
    )
    assert response.status_code == status.HTTP_200_OK
    response_data = ArticleWithBookmarkInResponse(**response.json())
    assert response_data.article.slug == test_article.slug
    assert response_data.article.bookmarked is False

    async with pool.acquire() as connection:
        bookmarks_repo = BookmarksRepository(connection)
        is_bookmarked = await bookmarks_repo.is_article_bookmarked_by_user(
            slug=test_article.slug,
            user=test_user,
        )
        assert is_bookmarked is False


async def test_user_cannot_unbookmark_unbookmarked_article(
    app: FastAPI,
    authorized_client: AsyncClient,
    test_article: Article,
) -> None:
    response = await authorized_client.delete(
        app.url_path_for("articles:unbookmark-article", slug=test_article.slug)
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_unauthorized_user_cannot_bookmark_or_unbookmark(
    app: FastAPI,
    client: AsyncClient,
    test_article: Article,
) -> None:
    post_res = await client.post(
        app.url_path_for("articles:bookmark-article", slug=test_article.slug)
    )
    assert post_res.status_code == status.HTTP_403_FORBIDDEN

    delete_res = await client.delete(
        app.url_path_for("articles:unbookmark-article", slug=test_article.slug)
    )
    assert delete_res.status_code == status.HTTP_403_FORBIDDEN


async def test_user_can_get_empty_bookmarks_list(
    app: FastAPI,
    authorized_client: AsyncClient,
) -> None:
    response = await authorized_client.get(
        app.url_path_for("users:get-user-bookmarks")
    )
    assert response.status_code == status.HTTP_200_OK
    bookmarks = ListOfBookmarkedArticlesInResponse(**response.json())
    assert bookmarks.articles_count == 0
    assert len(bookmarks.articles) == 0


async def test_user_can_list_bookmarked_articles(
    app: FastAPI,
    authorized_client: AsyncClient,
    test_user: UserInDB,
    pool: Pool,
) -> None:
    async with pool.acquire() as connection:
        articles_repo = ArticlesRepository(connection)
        bookmarks_repo = BookmarksRepository(connection)

        article_1 = await articles_repo.create_article(
            slug="bookmarked-article-1",
            title="Bookmarked Article 1",
            description="desc 1",
            body="body 1",
            author=test_user,
            tags=["tag1"],
        )
        article_2 = await articles_repo.create_article(
            slug="bookmarked-article-2",
            title="Bookmarked Article 2",
            description="desc 2",
            body="body 2",
            author=test_user,
            tags=["tag2"],
        )

        await bookmarks_repo.add_article_into_bookmarks(
            article=article_1,
            user=test_user,
        )
        await bookmarks_repo.add_article_into_bookmarks(
            article=article_2,
            user=test_user,
        )

    response = await authorized_client.get(
        app.url_path_for("users:get-user-bookmarks")
    )
    assert response.status_code == status.HTTP_200_OK
    bookmarks = ListOfBookmarkedArticlesInResponse(**response.json())
    assert bookmarks.articles_count == 2
    assert len(bookmarks.articles) == 2
    slugs = {article.slug for article in bookmarks.articles}
    assert slugs == {"bookmarked-article-1", "bookmarked-article-2"}


async def test_user_bookmarks_pagination(
    app: FastAPI,
    authorized_client: AsyncClient,
    test_user: UserInDB,
    pool: Pool,
) -> None:
    async with pool.acquire() as connection:
        articles_repo = ArticlesRepository(connection)
        bookmarks_repo = BookmarksRepository(connection)

        for i in range(5):
            art = await articles_repo.create_article(
                slug=f"paged-bookmark-{i}",
                title=f"Paged Bookmark {i}",
                description="desc",
                body="body",
                author=test_user,
            )
            await bookmarks_repo.add_article_into_bookmarks(
                article=art,
                user=test_user,
            )

    response = await authorized_client.get(
        app.url_path_for("users:get-user-bookmarks"),
        params={"limit": 2, "offset": 1},
    )
    assert response.status_code == status.HTTP_200_OK
    bookmarks = ListOfBookmarkedArticlesInResponse(**response.json())
    assert len(bookmarks.articles) == 2
