from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from book.models import Book,Category,Author,BorrowRecord
from book.serializers import BookSerializer,CategorySerializer, AuthorSerializer
from book.paginations import DefaultPagination
from django_filters.rest_framework import DjangoFilterBackend 
from rest_framework.filters import SearchFilter,OrderingFilter
from book.filters import BookFilter
from .serializers import UserSerializer
from django.contrib.auth import get_user_model

User = get_user_model()
# Create your views here.
class BookViewSet(ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = BookFilter
    pagination_class = DefaultPagination
    search_fields = ['title',]
    # ordering_fields = ['price', 'updated_at']
    ordering_fields = ['title', 'publication_date']
    ordering = ['title'] 
    

# Create your views here.
class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer