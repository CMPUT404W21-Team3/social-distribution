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


# Citations
- .gitignore: https://github.com/github/gitignore/blob/master/Python.gitignore
- REST nested objects: https://stackoverflow.com/questions/41312558/django-rest-framework-post-nested-objects
- REST authentication: https://www.django-rest-framework.org/tutorial/4-authentication-and-permissions/
- REST serialization: https://www.django-rest-framework.org/tutorial/1-serialization/
- REST serializer in model: https://stackoverflow.com/questions/18396547/django-rest-framework-adding-additional-field-to-modelserializer
- REST setter in model: https://stackoverflow.com/questions/35584059/django-cant-set-attribute-in-model
- One to one user model: https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#onetoone
- Unique ID: https://stackoverflow.com/questions/16925129/generate-unique-id-in-django-from-a-model-field/30637668