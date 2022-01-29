# Building Docker image

python build.py {username nexus} {password nexus}


# Etc

http://docs.wagtail.io/en/v2.6.2/topics/streamfield.html#structural-block-types



https://learnwagtail.com/

Nieuwsbrief heeft elk maand een eigen intro.
* https://wagtail.io/blog/getting-started-with-wagtail-and-graphql/
* Solving loading multiple at once [Dataloaders n 1](
https://apirobot.me/posts/django-graphql-solving-n-1-problem-using-dataloaders)
* Generating image urls in API [generating image urls](https://stackoverflow.com/questions/45732594/wagtail-getting-generating-image-urls-from-json-api-or-directly)


Optioneel afwijkende prijs.
Standaard tekst kunnen aanpassen.

Inschrijven nieuwsbrief. 

Analytics

# Docker, initial setup

## Create the peristent volumes
```
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

```
sudo docker-compose exec rkzbios-admin python3 /code/manage.py migrate --no-input
sudo docker-compose exec rkzbios-admin python3 /code/manage.py collectstatic --no-input
sudo docker-compose exec rkzbios-admin python3 /code/manage.py createsuperuser
```


# Docker, each upgrade

```
sudo docker-compose exec rkzbios-admin python3 /code/manage.py migrate --no-input
sudo docker-compose exec rkzbios-admin python3 /code/manage.py collectstatic --no-input
```

# Backup 

Docker container for run cron jobs which a performed by other containers!
* https://github.com/cshtdd/docker-cron





## Database

'''
sudo docker-compose exec db mysqldump -uroot -pxxxxxxx --complete-insert  rkzbios > ~/rkzbios-backup.sql
'''

Note that the datebase backup has a first line notification that must be removed.


## Data

sudo  docker run --rm --volumes-from rkzbios-admin -v $(pwd):/backup ubuntu bash -c "cd /code && tar cvf /backup/backup.tar files"

* https://docs.docker.com/storage/volumes/#backup-restore-or-migrate-data-volumes

sudo docker volume inspect rkzbios-media-data

```
[
    {
        "CreatedAt": "2019-11-28T14:06:10Z",
        "Driver": "local",
        "Labels": {},
        "Mountpoint": "/var/lib/docker/volumes/rkzbios-media-data/_data",
        "Name": "rkzbios-media-data",
        "Options": {},
        "Scope": "local"
    }
]
```

# Restoring backups

## Database
docker exec -i rkzbios-compose_db_1 mysql -uroot -pxxxxx rkzbios < ~/rkzbios-backup.sql

## Data

sudo docker run --rm --volumes-from rkzbios-admin -v $(pwd):/backup ubuntu bash -c "cd /code && tar xvf /backup/backup.tar"




# Example queries 

http://localhost:8000/api/v2/moviePages/?fields=doubleBillMovie,director,country,moviePoster,movieDates,externalLinks&currentActive=true
http://localhost:8000/api/v2/moviePages/?fields=doubleBillMovie(moviePoster),director,country,moviePoster,movieDates,externalLinks&currentActive=true
http://localhost:8000/api/v2/pages/?slug=contact&fields=body&type=home.ContentPage

Get all the child pages of the homepage
```
http://rkzbiosapi.jimboplatform.nl/api/v2/pages/?child_of=2&show_in_menus=true
```

http://rkzbiosapi.jimboplatform.nl/api/v2/pages/14/


# Docker and docker-compose development commands

Remove containers
```
sudo docker volume rm rkzbios-media-data
```



# Mailing, newsletter

## NodeJs/React
* https://mjml.io/
* https://github.com/chromakode/react-html-email
* https://github.com/unlayer/react-email-editor

## Python

Transform css stylesheets to inline styles
Transform relative urls to full urls

* https://github.com/peterbe/premailer

* https://weasyprint.readthedocs.io/

# GraphQL queries

Note this is experimental and not used for production.

* https://nec.is/writing/graphql-with-next-js-and-apollo/
* https://github.com/necccc/nextjs-apollo-graphql\
* http://localhost:8000/api/graphiql/#query=query%7B%0A%20%20films%7B%0A%20%20%20%20id%2C%0A%20%20%20%20title%2C%0A%20%20%20%20body%2C%0A%20%20%20%20director%2C%0A%20%20%20%20country%2C%0A%20%20%20%20filmDates%7B%0A%20%20%20%20%20%20date%0A%20%20%20%20%7D%0A%20%20%20%20%0A%20%20%7D%0A%7D


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
# TODO 

* Mailgun productie gereed maken
* Toevoegen logging ticketing/payment
* Printen van tickets
* Teksten aanpassen




# Naar productie brengen ticketing

Pas de mailgun connection aan voor productie:

http://rkzbiosapi.jimboplatform.nl/django-admin/jimbo_mail/mailserverconnection/f479b691-ea6d-436e-a088-5645467e0849/change/


# Logging

## check docker logs

sudo docker-compose logs rkzbios-admin

## django and ticketing log

The log files are in this dir:
/var/log/docker-logs/rkzbios


## Todo logging configuration
https://mattsegal.dev/django-gunicorn-nginx-logging.html

Use of https://github.com/Preston-Landers/concurrent-log-handler rotating, so email addresses are not stored.
https://xxx-cook-book.gitbooks.io/django-cook-book/content/Logs/Handlers/FileHandler/concurrent-log-handler.html
Or we have to obfuscate data that is returned from mollie.

# Configuration

THIS IS NOT USED!!! The configuration for rkz-admin 

{docker-compose-dir}/config/django/settings
