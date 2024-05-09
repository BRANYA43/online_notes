![Static Badge](https://img.shields.io/badge/Python-%23?style=for-the-badge&logo=python&logoColor=white&labelColor=%230a0a0a&color=%233776AB)
![Static Badge](https://img.shields.io/badge/Django-%23?style=for-the-badge&logo=django&logoColor=white&labelColor=%230a0a0a&color=%23092E20)
![Static Badge](https://img.shields.io/badge/Postgres-%23?style=for-the-badge&logo=postgresql&logoColor=white&labelColor=%230a0a0a&color=%234169E1)
![Static Badge](https://img.shields.io/badge/Docker-%23?style=for-the-badge&logo=docker&logoColor=white&labelColor=%230a0a0a&color=%232496ED)
![Static Badge](https://img.shields.io/badge/%20pre%20commit-%23?style=for-the-badge&logo=pre-commit&logoColor=white&labelColor=%230a0a0a&color=%23FAB040)
![Static Badge](https://img.shields.io/badge/Ruff-%23?style=for-the-badge&logo=ruff&logoColor=white&labelColor=%230a0a0a&color=%23D7FF64)
![Static Badge](https://img.shields.io/badge/nginx-%23?style=for-the-badge&logo=nginx&logoColor=white&labelColor=%230a0a0a&color=%23009639)
![Static Badge](https://img.shields.io/badge/poetry-%23?style=for-the-badge&logo=poetry&logoColor=white&labelColor=%230a0a0a&color=%2360A5FA)
![Static Badge](https://img.shields.io/badge/gunicorn-%23?style=for-the-badge&logo=gunicorn&logoColor=white&labelColor=%230a0a0a&color=%23499848)
![Static Badge](https://img.shields.io/badge/selenium-%23?style=for-the-badge&logo=selenium&logoColor=white&labelColor=%230a0a0a&color=%2343B02A)
***
# Online Notes
## Description
Online Notes - web application to make notes. User can use all opportunities and 
instruments without registration, but if his doesn't enter to site for 14 days 
all his data will be deleted.

User opportunities:
- CRUD operations for a note and category;
- Archive a note;
- Set a color for a category;
- Colored a note if a category was set;
- Filter by:
  - status(active, archived);
  - category;
  - range of quantity of words in the text;
  - range of quantity of unique words in the text 
    (words that aren't repited more one time);
  - range of creation date

***

# Docker
## How deploy app to server
In any folder download or clone files by this command:

```commandline
git clone -b deploy https://github.com/BRANYA43/online_notes.git
```
```commandline
git archive --remote=https://github.com/BRANYA43/online_notes.git --format=zip deploy > online_notes.zip
```
Then set up environments in the `your_folder/.env` by this template:

```dotenv
# Django
DJANGO_SECRET_KEY=<secret key>
DJANGO_ALLOWED_HOSTS='localhost [::1] 127.0.0.1 0.0.0.0'
DJANGO_SUPERUSER_EMAIL=admin@admin.com
DJANGO_SUPERUSER_PASSWORD=123

# PostgreSQL
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=db
```

### Django environments
- DJANGO_SECRET_KEY - secret key to encrypt data and security; 
- DJANGO_ALLOWED_HOSTS - list of allowed hosts; 
- DJANGO_SUPERUSER_EMAIL and DJANGO_SUPERUSER_PASSWORD - owner credential to
enter to admin site;
#### Not Required environments
- DJANGO_SETTINGS_ENV - switch `dev` or `prod` mode for running app. It's `prod` 
  by default;

### PostgreSQL environments
- POSTGRES_DB - name of db to use for app;
- POSTGRES_USER and POSTGRES_PASSWORD - credentials to connect to db for app;
- POSTGRES_HOST - host of db to connect. It must be container name of db. It's 
  `db` by default;

Next step is to run this command in the folder where `your_folder/docker-compose.yml` 
is located:
```commandline
docker compose up
```
or
```commandline
docker-compose up
```

***
