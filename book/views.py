from rest_framework.viewsets import ModelViewSet
from .models import Book,Category,Author,BorrowRecord
from book.serializers import BookSerializer,CategorySerializer, AuthorSerializer, BorrowRecordSerializer, BorrowBookSerializer,ReturnBookSerializer,AssignUserToGroupSerializer,GroupSerializer
from book.paginations import DefaultPagination
from django_filters.rest_framework import DjangoFilterBackend 
from rest_framework.filters import SearchFilter,OrderingFilter
from book.filters import BookFilter
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from .permissions import IsLibrarian, IsMember
from django.contrib.auth.models import Group
from drf_yasg.utils import swagger_auto_schema


class GroupViewSet(ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated, IsLibrarian]



class AssignUserToGroupView(APIView):
    """
    API endpoint for assigning users in the library to the role
     - Librarian or
     - Member
     -(Only librarian can assign roles)
    """
    
    permission_classes = [IsAuthenticated, IsLibrarian]

    def post(self, request):
        serializer = AssignUserToGroupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {"message": f"User {user.email} role updated successfully."},
            status=status.HTTP_200_OK
        )

    



class BookViewSet(ModelViewSet):
    """
    API endpoint for managing books in the library
     - Allows authenticated admin, librarian to create , update, delete books
     - Allows users to browse and filter books by category, author , availale, publication date
     - Support searching by title
     - Support ordering by title ad publication date
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = BookFilter
    pagination_class = DefaultPagination
    search_fields = ['title',]
    ordering_fields = ['title', 'publication_date']
    ordering = ['title']
    def get_permissions(self):
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsLibrarian()]
    
    @swagger_auto_schema(
        operation_summary='Retrive a list of books'
    )
    def list(self, request, *args, **kwargs):
        """Retrieve all the books"""
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
            operation_summary = 'Create a book by admin, librarian',
            operation_description='This allow a admin, lirarian to create a book',
            request_body = BookSerializer,
            responses={
                201: BookSerializer,
                400: 'Bad Request'
            }
    )
    def create(self, request, *args, **kwargs):
        """Only autheticated admin, librarian can create book"""
        return super().create(request, *args, **kwargs)

class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    def get_permissions(self):
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsLibrarian()]

    

class AuthorViewSet(ModelViewSet):
    """
    Only Admin and Librarian can create authors.
    Members only can view author list.
    """
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name',]
    def get_permissions(self):
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsLibrarian()]


class BorrowRecordViewSet(ModelViewSet):
    queryset = BorrowRecord.objects.select_related('book', 'member')
    serializer_class = BorrowRecordSerializer
    permission_classes = [IsAuthenticated]    
    
    def get_queryset(self):
        
        qs = BorrowRecord.objects.select_related('book', 'member')
        if getattr(self,'swagger_fake_view', False):
            return BorrowRecord.objects.none()
        # print('kwargs',self.kwargs)
        book_pk = self.kwargs.get('book_pk') 
        # print('book pk', book_pk)
        if book_pk:
            qs = qs.filter(book_id=book_pk)
            if getattr(self,'swagger_fake_view', False):
                return BorrowRecord.objects.none()
        else:
            qs = qs.filter(member=self.request.user)
            if getattr(self,'swagger_fake_view', False):
                return BorrowRecord.objects.none()
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
    
    