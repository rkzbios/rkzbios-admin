from __future__ import unicode_literals
import graphene
from graphene_django import DjangoObjectType
from home.models import FilmPage, Filmdates
from api import graphene_wagtail
from django.db import models

class FilmPageNode(DjangoObjectType):
    class Meta:
        model = FilmPage
        fields = ['id', 'title','director','country','body','film_dates','filmPoster','filmBack']


class FilmdatesType(DjangoObjectType):
    class Meta:
        model = Filmdates

class Query(graphene.ObjectType):
    films = graphene.List(FilmPageNode)
    film = graphene.Field(FilmPageNode, film_id=graphene.String())

    @graphene.resolve_only_args
    def resolve_films(self):
        return FilmPage.objects.all()

    def resolve_film(self, info, film_id):
        # Querying a single question
        return FilmPage.objects.get(pk=film_id)

schema = graphene.Schema(query=Query)