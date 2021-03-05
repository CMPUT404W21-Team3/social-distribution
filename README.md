# Social Distribution Project

- Admin login: admin/admin


# API Usage

- API calls may or may not be prefixed with /api/ 
- - http://localhost:8000/api/author/{author_id} and http://localhost:8000/author/{author_id} point to the same resource
- API urls
- - author/{author_id}/ - retrieve or update author profile
- - author/{author_id}/posts/{post_id} - create*, retrieve, update or delete* post
- - author/{author_id}/posts/ - retrieve posts or create a new post
- - author/{author_id}/followers - retrieve followers 
- - author/{author_id}/followers/{follower_id} - retrieve, update* or delete* follower
- - author/{author_id}/posts/{post_id}/comments - retrieve or add comment 

\* denotes authentication required
