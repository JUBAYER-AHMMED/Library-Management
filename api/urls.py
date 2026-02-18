from rest_framework.routers import DefaultRouter
from book.views import CategoryViewSet
from django.urls import path, include
from rest_framework_nested import routers
from book.views import BookViewSet, AuthorViewSet,BorrowRecordViewSet,GroupViewSet, AssignUserToGroupView
from .views import UserViewSet
router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='category')
router.register('books', BookViewSet ,basename='books')
router.register('authors', AuthorViewSet, basename='authors')
router.register('members', UserViewSet, basename='members')
router.register('borrow-records', BorrowRecordViewSet, basename='borrow-records')
router.register('groups', GroupViewSet, basename='groups')

author_router = routers.NestedDefaultRouter(router,'authors',lookup='author')
author_router.register('books',BookViewSet,basename='author-books')

book_router = routers.NestedDefaultRouter(router,'books',lookup='book')
book_router.register('borrows',BorrowRecordViewSet,basename='borrow-books')



category_router = routers.NestedDefaultRouter(router,'categories',lookup='category')
category_router.register('books',BookViewSet,basename='category-books')


urlpatterns = [
    path('', include(router.urls)),
    path('',include(category_router.urls)),
    path('',include(author_router.urls)),
    path('', include(book_router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),

    path('assign-role/', AssignUserToGroupView.as_view()),

]
