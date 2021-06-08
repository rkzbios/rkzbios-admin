from datetime import datetime, timezone, timedelta

from django.db import models
from django import forms
from django.utils import timezone

from modelcluster.fields import ParentalKey
from modelcluster.fields import ParentalManyToManyField

from wagtail.core.models import Page
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core import blocks
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel, InlinePanel, PageChooserPanel, MultiFieldPanel
from wagtail.images.blocks import ImageChooserBlock
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.api import APIField
from wagtail.images.api.fields import ImageRenditionField, Field
from wagtail.core.models import Orderable

from rest_framework import serializers

from wagtail.core.blocks import StreamBlock

class MyStreamBlock(StreamBlock):

    def transform_child(self, child, context):
        return {
            'type': child.block.name,
            'value': child.block.get_api_representation(child.value, context=context),
            'id': child.id
        }

    def get_api_representation(self, value, context=None):
        if value is None:
            # treat None as identical to an empty stream
            return []

        result = []
        for child in value:  # child is a StreamChild instance
            result.append( self.transform_child(child, context))
        return result

from django.db import models


class MyImageChooserBlock(ImageChooserBlock):

    def get_api_representation(self, value, context=None):
        return value.file.url


class HomePage(Page):
    body = StreamField(MyStreamBlock([
        ('heading', blocks.CharBlock(classname="full title")),
        ('paragraph', blocks.TextBlock()),
        ('link',blocks.URLBlock()),
        ('movieList', blocks.BooleanBlock()),
        ('image', MyImageChooserBlock()),
    ], blank=True, null=True))

    content_panels = Page.content_panels + [
        StreamFieldPanel('body'),
    ]

    api_fields = [
        APIField('body'),
    ]


class KijkWijzerClassification(models.Model):
    label = models.CharField(max_length= 36)
    icon  = models.CharField(max_length= 36)

    panels = [
        FieldPanel('label'),
        FieldPanel('icon'),
    ]

    def __str__(self):
        return '{}'.format(self.label)


class ExternalLink(Orderable):
    page = ParentalKey('MoviePage', on_delete=models.CASCADE, related_name='externalLinks')
    typeLink = models.CharField(max_length=256, null=True, blank=True)
    linkExternal = models.URLField("External link", blank=True)

    panels = [
        FieldPanel('typeLink'),
        FieldPanel('linkExternal'),
    ]

def default_movie_date():
     now = timezone.now()
     default = now.replace(hour=20,minute=30,second=0,microsecond=0)
     return default


class Moviedate(Orderable):
    page = ParentalKey('MoviePage', on_delete=models.CASCADE, related_name='movieDates')
    date = models.DateTimeField("Show Date", default=default_movie_date)

    panels = [
        FieldPanel('date'),
    ]

    @property
    def is_passed(self):
        now = timezone.now() + timedelta(minutes=30)
        return now >= self.date

    class Meta:
        ordering = ('-date', )


class MovieDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Moviedate
        fields = ['id','date']


class KijkWijzerClassificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = KijkWijzerClassification
        fields = ['label','icon']


class ExternalLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalLink
        fields = ['typeLink','linkExternal']


class MoviePage(Page):

    moviePoster = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    movieBackDrop = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    director = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255, null=True,blank=True)
    releaseDate = models.DateField(null=True,blank=True)  # releaseYear enough??
    movieType = models.CharField(max_length=255, null=True, blank=True)
    spokenLanguage = models.CharField(max_length=255, null=True, blank=True)
    subtitleLanguage = models.CharField(max_length=255, null=True, blank=True)
    lengthInMinutes = models.IntegerField(null=True, blank=True)
    minimumAge = models.IntegerField(null=True, blank=True)
    premiere = models.BooleanField(default=False)
    showStartDate = models.DateField(null=True, blank=True)
    showEndDate = models.DateField(null=True, blank=True)
    classifications = ParentalManyToManyField(KijkWijzerClassification, blank=True)


    trailer = models.URLField("Trailer", blank=True, null=True)

    doubleBillMovie = models.ForeignKey(
        'MoviePage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    body = StreamField([
        ('heading', blocks.CharBlock(classname="full title")),
        ('paragraph', blocks.TextBlock()),
        ('image', ImageChooserBlock()),
        ('quotation', blocks.StructBlock([
            ('text', blocks.TextBlock()),
            ('author', blocks.CharBlock()),
        ])),
    ], blank=True, null=True)



    content_panels = Page.content_panels + [
        FieldPanel('director'),
        FieldPanel('country'),
        FieldPanel('releaseDate'),
        FieldPanel('movieType'),
        FieldPanel('spokenLanguage'),
        FieldPanel('subtitleLanguage'),
        FieldPanel('lengthInMinutes'),
        FieldPanel('minimumAge'),
        FieldPanel('premiere'),

        PageChooserPanel('doubleBillMovie', 'home.MoviePage'),

        ImageChooserPanel('moviePoster'),
        ImageChooserPanel('movieBackDrop'),

        FieldPanel('trailer'),
        InlinePanel('movieDates', label="Movie dates"),
        InlinePanel('externalLinks', label="External links"),
        FieldPanel('classifications',widget=forms.CheckboxSelectMultiple),
        # InlinePanel( 'classifications', label="Categories"),

        StreamFieldPanel('body'),

    ]

    api_fields = [
        APIField('director'),
        APIField('country'),
        APIField('body'),
        APIField('releaseDate'),
        APIField('movieType'),
        APIField('spokenLanguage'),
        APIField('subtitleLanguage'),
        APIField('lengthInMinutes'),
        APIField('premiere'),
        APIField('minimumAge'),
        APIField('doubleBillMovie'),
        APIField('movieDates', serializer=MovieDateSerializer(many=True, read_only=True)),
        APIField('externalLinks', serializer=ExternalLinkSerializer(many=True, read_only=True)),
        APIField('moviePoster'),
        APIField('moviePosterThumb', serializer=ImageRenditionField('fill-100x100', source='moviePoster')),
        APIField('movieBackDrop'),
        APIField('trailer'),
        APIField('classifications', serializer=KijkWijzerClassificationSerializer(many=True, read_only=True)),

    ]

    def get_start_date(self, current_date, date_to_compare):
        return date_to_compare if (current_date is None) or (date_to_compare < current_date) else current_date

    def get_end_date(self, current_date, date_to_compare):
        return date_to_compare if (current_date is None) or (date_to_compare > current_date) else current_date

    def save(self, *args, **kwargs):
        start_date_time = None
        end_date_time = None
        for movie_date in self.movieDates.all():
            start_date_time = self.get_start_date( start_date_time, movie_date.date)
            end_date_time = self.get_end_date( end_date_time, movie_date.date)

        if start_date_time and end_date_time:
            self.showStartDate = start_date_time.date()
            self.showEndDate = end_date_time.date()

        super().save(*args, **kwargs)  # Call the "real" save() method.

    # promote_panels = [
    #     MultiFieldPanel(Page.promote_panels, "Common page configuration"),
    #
    # ]


#https://www.youtube.com/embed/lp_NiS0sI6I?autoplay=1&playsinline=1&rel=0&modestbranding=1&start=83&end=103&enablejsapi=1&origin=https%3A%2F%2Fforum.nl&widgetid=1

#
# query
# {
#     films
# {
#     id,
#     title,
#     body,
#     filmDates{
#     date
# }
#
# }
# }


class ContentPage(Page):
    pageBackDrop = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    body = StreamField(MyStreamBlock([
        ('heading', blocks.CharBlock(classname="full title")),
        ('paragraph', blocks.TextBlock()),
        ('image', MyImageChooserBlock()),
    ], blank=True, null=True))



    content_panels = Page.content_panels + [
        ImageChooserPanel('pageBackDrop'),
        StreamFieldPanel('body'),
    ]

    api_fields = [
        APIField('pageBackDrop'),
        APIField('body'),
    ]


