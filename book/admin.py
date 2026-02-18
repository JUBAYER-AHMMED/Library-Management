from django.contrib import admin
from book.models import Author, Category, Book, BorrowRecord
# Register your models here.

admin.site.register(Author)
admin.site.register(Category)
admin.site.register(Book)
admin.site.register(BorrowRecord)
