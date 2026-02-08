from django_filters.rest_framework import FilterSet
from book.models import Book
from django_filters import rest_framework as filters
class BookFilter(FilterSet):
    publication_date = filters.DateFromToRangeFilter()

    class Meta:
        model = Book
        fields = {
            'category_id': ['exact'],
            'author_id': ['exact'],
            'available': ['exact'],
            # 'price': ['gt','lt']
        }