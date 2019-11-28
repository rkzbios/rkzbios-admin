from datetime import date
from collections import OrderedDict
from django.conf.urls import url

from rest_framework.serializers import ListSerializer
from rest_framework.utils.serializer_helpers import ReturnList

from wagtail.api.v2.endpoints import PagesAPIEndpoint
from wagtail.api.v2.router import WagtailAPIRouter
from wagtail.api.v2.serializers import PageSerializer
from wagtail.images.api.v2.endpoints import ImagesAPIEndpoint
from wagtail.documents.api.v2.endpoints import DocumentsAPIEndpoint

from wagtail.api.v2.filters import FieldsFilter, OrderingFilter, \
    SearchFilter, BaseFilterBackend

from home.models import MoviePage

# Create the router. "wagtailapi" is the URL namespace
api_router = WagtailAPIRouter('wagtailapi')


class CurrentActiveMoveFilter(BaseFilterBackend):
    """
    Implements current active filter.
    """

    def filter_queryset(self, request, queryset, view):
        if 'currentActive' in request.GET:
            today = date.today()

            queryset = queryset.filter(movieDates__date__gte = today).order_by('movieDates__date')

        return queryset


# class CustomListSerializer(ListSerializer):
#
#     @property
#     def data(self):
#         ret = super().data
#         return ReturnList(ret, serializer=self)
#
# class MyMoviePageSerializer(PageSerializer):
#
#     class Meta:
#         list_serializer_class = CustomListSerializer

class MoviePagesAPIEndpoint(PagesAPIEndpoint):
    #base_serializer_class = MyMoviePageSerializer  DOESNOT WORK META FIELD IS IGNORED BY WAGTAIL

    filter_backends = [
        FieldsFilter,
        CurrentActiveMoveFilter,
        OrderingFilter,
        SearchFilter,
    ]

    known_query_parameters = frozenset([
        'limit',
        'offset',
        'fields',
        'order',
        'search',
        'search_operator',
        'currentActive',

        # Used by jQuery for cache-busting. See #1671
        '_',

        # Required by BrowsableAPIRenderer
        'format',
    ])

    def remove_duplicates(self, data):
        cleaned = OrderedDict()

        for item in data:
            _id = item['id']
            if not _id in cleaned:
                cleaned[_id] = item
        cleaned_list = [item for item in cleaned.values()]
        return cleaned_list


    def listing_view(self, request):
        queryset = self.get_queryset()
        self.check_query_parameters(queryset)
        queryset = self.filter_queryset(queryset)
        queryset = self.paginate_queryset(queryset)
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data

        removed_duplicates_data =  self.remove_duplicates(data)
        self.paginator.total_count = len(removed_duplicates_data)
        return self.get_paginated_response(removed_duplicates_data)


    def get_queryset(self):
        request = self.request

        queryset = MoviePage.objects.all()
        # Get live pages that are not in a private section
        queryset = queryset.public().live()

        # Filter by site
        if request.site:
            queryset = queryset.descendant_of(request.site.root_page, inclusive=True)
        else:
            # No sites configured
            queryset = queryset.none()

        return queryset


    def get_object(self):
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        value = self.kwargs[lookup_url_kwarg]
        if value == "_current":
            queryset = self.get_queryset()
            today = date.today()
            base = queryset.filter(movieDates__date__gte=today).order_by('movieDates__date').first()

        else:
            base = super().get_object()
        return base.specific

    @classmethod
    def get_urlpatterns(cls):
        """
        This returns a list of URL patterns for the endpoint
        """
        return [
            url(r'^$', cls.as_view({'get': 'listing_view'}), name='listing'),
            #url(r'^(?P<pk>\d+)/$', cls.as_view({'get': 'detail_view'}), name='detail'),
            url(r'^(?P<pk>[^/]+)/$', cls.as_view({'get': 'detail_view'}), name='detail'),
            url(r'^find/$', cls.as_view({'get': 'find_view'}), name='find'),
        ]

# Add the three endpoints using the "register_endpoint" method.
# The first parameter is the name of the endpoint (eg. pages, images). This
# is used in the URL of the endpoint
# The second parameter is the endpoint class that handles the requests
api_router.register_endpoint('pages', PagesAPIEndpoint)
api_router.register_endpoint('moviePages', MoviePagesAPIEndpoint)
api_router.register_endpoint('images', ImagesAPIEndpoint)
api_router.register_endpoint('documents', DocumentsAPIEndpoint)