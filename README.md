# Social Distribution Project

- Admin login: admin/admin


# API Usage

See [API Reference](wiki/API-Reference)

- API calls may or may not be prefixed with /api/ 
- - http://localhost:8000/api/author/{author_id} and http://localhost:8000/author/{author_id} point to the same resource
- API urls
- - authors/ - get lists of authors
- - authors/search/{query} - filters list of authors by query
- - author/{author_id}/ - retrieve or update author profile
- - author/{author_id}/posts/{post_id} - create*, retrieve, update or delete* post
- - author/{author_id}/posts/ - retrieve posts or create a new post
- - author/{author_id}/followers - retrieve followers 
- - author/{author_id}/followers/{follower_id} - retrieve, update* or delete* follower
- - author/{author_id}/posts/{post_id}/comments - retrieve or add comment 

\* denotes authentication required


# Citations
- .gitignore: https://github.com/github/gitignore/blob/master/Python.gitignore
- REST nested objects: https://stackoverflow.com/a/50415689
- REST authentication: https://www.django-rest-framework.org/tutorial/4-authentication-and-permissions/
- REST serialization: https://www.django-rest-framework.org/tutorial/1-serialization/
- REST serializer in model: https://stackoverflow.com/a/18396622
- REST setter in model: https://stackoverflow.com/a/51189035
- One to one user model: https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#onetoone
- Unique ID: https://stackoverflow.com/a/30637668
- Styles used from: https://getbootstrap.com/docs/5.0/


Heroku Site: https://team3-socialdistribution.herokuapp.com/
