# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- Implemented Article Bookmarking and Reading List feature (Option A direct table relationship via `user_article_bookmarks`).
- Added endpoints:
  - `POST /api/articles/{slug}/bookmark`: Bookmark an article for current user.
  - `DELETE /api/articles/{slug}/bookmark`: Unbookmark an article.
  - `GET /api/user/bookmarks`: Retrieve current user's bookmarked reading list with pagination.
- Added `BookmarksRepository` and `BookmarkService` with asyncpg queries.
- Added Pydantic schemas in `app/models/schemas/bookmarks.py`.
- Added comprehensive unit and integration tests in `tests/test_api/test_routes/test_bookmarks.py`.
- Added Alembic migration `a1b2c3d4e5f6_add_user_article_bookmarks.py`.
