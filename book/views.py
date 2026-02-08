from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .models import Book,Category,Author,BorrowRecord
from .serializers import BookSerializer,CategorySerializer, AuthorSerializer, BorrowRecordSerializer, BorrowBookSerializer,ReturnBookSerializer
from book.paginations import DefaultPagination
from django_filters.rest_framework import DjangoFilterBackend 
from rest_framework.filters import SearchFilter,OrderingFilter
from book.filters import BookFilter

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

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


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class AuthorViewSet(ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name',]


class BorrowRecordViewSet(ModelViewSet):
    queryset = BorrowRecord.objects.select_related('book', 'member')
    serializer_class = BorrowRecordSerializer
    def get_queryset(self):
        qs = BorrowRecord.objects.select_related('book', 'member')
        print('kwargs',self.kwargs)
        book_pk = self.kwargs.get('book_pk') 
        print('book pk', book_pk)
        
        if book_pk:
            qs = qs.filter(book_id=book_pk)
        else:
            qs = qs.filter(member=self.request.user)
        return qs
    def get_serializer_class(self):
        if self.action == 'create':
            return BorrowBookSerializer
    
        return BorrowRecordSerializer

    def partial_update(self, request, *args, **kwargs):
        serializer = ReturnBookSerializer(
            data={'borrow_id': kwargs['pk']},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        record = serializer.save()

        return Response({
            "message": f"Book '{record.book.title}' has been successfully returned.",
            "borrow_record": BorrowRecordSerializer(record).data
        }, status=status.HTTP_200_OK)
