https://web.archive.org/web/20190312155833/http://www.rkzbios.nl/Spider-Man-Into-the-Spider-Verse.htm

https://graphene-python.org/
https://relay.dev/docs/en/graphql-server-specification.html

https://wagtail.io/blog/getting-started-with-wagtail-and-graphql/

http://docs.wagtail.io/en/v2.6.2/topics/streamfield.html#structural-block-types

https://nec.is/writing/graphql-with-next-js-and-apollo/
https://github.com/necccc/nextjs-apollo-graphql
https://github.com/humanmade/react-oembed-container

http://localhost:8000/api/graphiql/#query=query%7B%0A%20%20films%7B%0A%20%20%20%20id%2C%0A%20%20%20%20title%2C%0A%20%20%20%20body%2C%0A%20%20%20%20director%2C%0A%20%20%20%20country%2C%0A%20%20%20%20filmDates%7B%0A%20%20%20%20%20%20date%0A%20%20%20%20%7D%0A%20%20%20%20%0A%20%20%7D%0A%7D


https://learnwagtail.com/

Nieuwsbrief heeft elk maand een eigen intro.
* Solving loading multiple at once [Dataloaders n 1](
https://apirobot.me/posts/django-graphql-solving-n-1-problem-using-dataloaders)
* Generating image urls in API [generating image urls](https://stackoverflow.com/questions/45732594/wagtail-getting-generating-image-urls-from-json-api-or-directly)

Double  bill film (Hoe gaan we dat aanpakken.
Andere type.

Filmfestival (Ander type??)

Misschien een structuur maken van 

Kan de standaard tijd op 20.30 gezet worden.

Optioneel afwijkende prijs.
Er kan niet gepinned worden en gereserveerd worden.
Standaard tekst.

Inschrijven nieuwsbrief. 

Analytics

# GraphQL queries

All

```
query{
  films{
    id,
    title,
    body,
    director,
    country,
    filmDates{
      date
    },
    filmPoster{
      url
    },
    filmBack{
      url
    }
    
  }
}
```

```
query{
  films{
    id,
    title,
    filmDates{
      date
    },
    filmPoster{
      url
    }
  }
}
```
Per film

```
query{
  film(filmId:"5"){
    id,
    title,
    body,
    director,
    country,
    filmDates{
      date
    },
    filmPoster{
      url
    },
    filmBack{
      url
    }
  }
}
```

# Docker, initial setup

## Create the peristent volumes
```
# sudo docker volume create --name=rkzbios-mysql-data
sudo docker volume create --name=rkzbios-media-data
```

## Startup the containers

```
sudo docker-compose up 
```
Wait for intialization of the mysql docker container, this can take some time (10minutes), I don't know why it takes
so long.

Don't stop the container, otherwise its not correct initialized!

```
sudo docker-compose exec db mysql -uroot -pxxxxxxx
```

In the mysql console 
```
ALTER USER 'root' IDENTIFIED WITH mysql_native_password BY 'xxxxxxxx';
ALTER USER 'rkzbios' IDENTIFIED WITH mysql_native_password BY 'xxxxxxx';
```

This because otherwise you get this errror

```python
django.db.utils.OperationalError: (1045, 'Plugin caching_sha2_password could not be loaded: /usr//usr/lib/x86_64-linux-gnu/mariadb19/plugin/caching_sha2_password.so: cannot open shared object file: No such file or directory')
```

sudo docker-compose exec rkzbios-admin python3 /code/manage.py migrate --no-input
sudo docker-compose exec rkzbios-admin python3 /code/manage.py collectstatic --no-input
sudo docker-compose exec rkzbios-admin python3 /code/manage.py createsuperuser


# Docker, each upgrade

sudo docker-compose exec rkzbios-admin python3 /code/manage.py migrate --no-input
sudo docker-compose exec rkzbios-admin python3 /code/manage.py collectstatic --no-input



http://localhost:8000/api/v2/moviePages/?fields=doubleBillMovie,director,country,moviePoster,movieDates,externalLinks&currentActive=true
http://localhost:8000/api/v2/moviePages/?fields=doubleBillMovie(moviePoster),director,country,moviePoster,movieDates,externalLinks&currentActive=true
http://localhost:8000/api/v2/pages/?slug=contact&fields=body&type=home.ContentPage


# Docker and docker-compose development commands

Remove containers
```
sudo docker volume rm rkzbios-mysql-data
sudo docker volume rm rkzbios-media-data
```

# Backup Database
sudo docker-compose exec db mysqldump -uroot -pengage --complete-insert  rkzbios > rkzbios-backup.sql
