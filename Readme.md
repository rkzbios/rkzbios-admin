https://web.archive.org/web/20190312155833/http://www.rkzbios.nl/Spider-Man-Into-the-Spider-Verse.htm

https://graphene-python.org/
https://relay.dev/docs/en/graphql-server-specification.html

https://wagtail.io/blog/getting-started-with-wagtail-and-graphql/

http://docs.wagtail.io/en/v2.6.2/topics/streamfield.html#structural-block-types

https://nec.is/writing/graphql-with-next-js-and-apollo/
https://github.com/necccc/nextjs-apollo-graphql
https://github.com/humanmade/react-oembed-container

http://localhost:8000/api/graphiql/#query=query%7B%0A%20%20films%7B%0A%20%20%20%20id%2C%0A%20%20%20%20title%2C%0A%20%20%20%20body%2C%0A%20%20%20%20director%2C%0A%20%20%20%20country%2C%0A%20%20%20%20filmDates%7B%0A%20%20%20%20%20%20date%0A%20%20%20%20%7D%0A%20%20%20%20%0A%20%20%7D%0A%7D




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
