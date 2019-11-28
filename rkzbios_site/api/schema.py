from __future__ import unicode_literals

from datetime import date
import graphene
from graphene_django import DjangoObjectType
from home.models import MoviePage, Moviedate
from api import graphene_wagtail
from django.db import models

class MoviePageNode(DjangoObjectType):
    class Meta:
        model = MoviePage
        fields = ['id', 'title','director','country','body','movieDates','moviePoster','movieBackDrop']


class FilmdatesType(DjangoObjectType):
    class Meta:
        model = Moviedate

class Query(graphene.ObjectType):
    movies = graphene.List(MoviePageNode)
    movie = graphene.Field(MoviePageNode, film_id=graphene.String())
    currentMovie = graphene.Field(MoviePageNode)

    @graphene.resolve_only_args
    def resolve_movies(self):
        today = date.today()

        return MoviePage.objects.filter(movieDates__date__gte=today).order_by('movieDates__date')

    def resolve_movie(self, info, film_id):
        # Querying a single question
        return MoviePage.objects.get(pk=film_id)


    @graphene.resolve_only_args
    def resolve_currentFilm(self):
        return MoviePage.objects.get(pk=3)


schema = graphene.Schema(query=Query)