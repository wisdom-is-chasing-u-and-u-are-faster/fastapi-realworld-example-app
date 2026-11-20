-- name: add-article-to-bookmarks!
INSERT INTO user_article_bookmarks (user_id, article_id)
VALUES ((SELECT id FROM users WHERE username = :username),
        (SELECT id FROM articles WHERE slug = :slug))
ON CONFLICT DO NOTHING;


-- name: remove-article-from-bookmarks!
DELETE
FROM user_article_bookmarks
WHERE user_id = (SELECT id FROM users WHERE username = :username)
  AND article_id = (SELECT id FROM articles WHERE slug = :slug);


-- name: is-article-in-bookmarks^
SELECT CASE WHEN count(user_id) > 0 THEN TRUE ELSE FALSE END AS bookmarked
FROM user_article_bookmarks
WHERE user_id = (SELECT id FROM users WHERE username = :username)
  AND article_id = (SELECT id FROM articles WHERE slug = :slug);


-- name: get-bookmarks-count-for-article^
SELECT count(*) as bookmarks_count
FROM user_article_bookmarks
WHERE article_id = (SELECT id FROM articles WHERE slug = :slug);


-- name: get-bookmarked-articles-for-user
SELECT a.id,
       a.slug,
       a.title,
       a.description,
       a.body,
       a.created_at,
       a.updated_at,
       (
           SELECT username
           FROM users
           WHERE id = a.author_id
       ) AS author_username
FROM articles a
         INNER JOIN user_article_bookmarks b ON
        b.article_id = a.id AND
        b.user_id = (SELECT id FROM users WHERE username = :username)
ORDER BY a.created_at DESC
LIMIT :limit
OFFSET :offset;
