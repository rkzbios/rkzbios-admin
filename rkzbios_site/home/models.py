from django.db import models

from wagtail.core.models import Page


from wagtail.core.fields import RichTextField, StreamField
from wagtail.core import blocks
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel, InlinePanel, MultiFieldPanel
from wagtail.images.blocks import ImageChooserBlock
from wagtail.images.edit_handlers import ImageChooserPanel


class HomePage(Page):
    pass


from modelcluster.fields import ParentalKey
from wagtail.core.models import Orderable

class FilmPage(Page):


    filmPoster = models.ForeignKey(
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

    trailer =  models.URLField("Trailer", blank=True, null=True)

    body = StreamField([
        ('heading', blocks.CharBlock(classname="full title")),
        ('paragraph', blocks.TextBlock()),
        ('image', ImageChooserBlock()),
        ('quotation', blocks.StructBlock([
            ('text', blocks.TextBlock()),
            ('author', blocks.CharBlock()),
        ])),
    ])


    content_panels = Page.content_panels + [
        FieldPanel('director'),
        FieldPanel('country'),
        FieldPanel('releaseDate'),
        FieldPanel('movieType'),
        FieldPanel('spokenLanguage'),
        FieldPanel('subtitleLanguage'),
        FieldPanel('lengthInMinutes'),
        FieldPanel('minimumAge'),

        ImageChooserPanel('filmPoster'),
        FieldPanel('trailer'),
        InlinePanel('film_dates', label="Film dates"),
        InlinePanel('external_links', label="External links"),
        StreamFieldPanel('body'),

    ]

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

class Filmdates(Orderable):
    page = ParentalKey(FilmPage, on_delete=models.CASCADE, related_name='film_dates')
    date = models.DateTimeField("Show Date")

    panels = [
        FieldPanel('date'),
    ]

class ExternalLinks(Orderable):
    page = ParentalKey(FilmPage, on_delete=models.CASCADE, related_name='external_links')
    typeLink = models.CharField(max_length=256, null=True, blank=True)
    linkExternal = models.URLField("External link", blank=True)

    panels = [
        FieldPanel('typeLink'),
        FieldPanel('linkExternal'),
    ]


