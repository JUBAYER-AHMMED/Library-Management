from rest_framework import serializers
from decimal import Decimal
from .models import Category, Author, Book, BorrowRecord
# from .serializers import AuthorSerializer, CategorySerializer
from django.utils import timezone
from django.contrib.auth.models import Group


from api.serializers import UserSerializer2

from django.contrib.auth import get_user_model
User = get_user_model()


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class BookSerializer(serializers.ModelSerializer):
    author_detail = AuthorSerializer(source='author', read_only=True)
    category_detail = CategorySerializer(source='category', read_only=True)
    # author = AuthorSerializer(source='author')
    class Meta:
        model = Book
        fields = [
            'id',
            'title',
            'isbn',
            'publication_date',
            'available',
            'author',
            'author_detail',
            'category',
            'category_detail',
            'created_at',
        ]
        read_only_fields = ['available', 'created_at']


class BorrowRecordSerializer(serializers.ModelSerializer):
    book_detail = BookSerializer(source='book', read_only=True)
    member_detail = UserSerializer2(source='member', read_only=True)
    class Meta:
        model = BorrowRecord
        fields = [
            'id',
            'book',
            'book_detail',
            'member',
            'member_detail',
            'borrow_date',
            'return_date',
            'returned',
        ]
        read_only_fields = [
            'borrow_date',
            'return_date',
            'returned',
        ]


class BorrowBookSerializer(serializers.Serializer):
    book_id = serializers.IntegerField()

    def validate(self, data):
        try:
            book = Book.objects.get(id=data['book_id'])
        except Book.DoesNotExist:
            raise serializers.ValidationError("Book does not exist.")

        if not book.available:
            raise serializers.ValidationError("Book is not available.")

        data['book'] = book
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        book = validated_data['book']

        book.available = False
        book.save()

        borrow_record = BorrowRecord.objects.create(
            book=book,
            member=user
        )

        return borrow_record


class ReturnBookSerializer(serializers.Serializer):
    borrow_id = serializers.IntegerField()

    def validate(self, data):
        try:
            record = BorrowRecord.objects.get(id=data['borrow_id'])
        except BorrowRecord.DoesNotExist:
            raise serializers.ValidationError("Borrow record not found.")

        if record.member != self.context['request'].user:
            raise serializers.ValidationError(
                "You can only return your own borrowed books."
            )


        if record.returned:
            raise serializers.ValidationError("Book already returned.")

        data['record'] = record
        return data

    def save(self, **kwargs):
        record = self.validated_data['record']
        record.returned = True
        record.return_date = timezone.now()
        record.book.available = True
        record.book.save()
        record.save()
        return record
    

# users/serializers.py


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']

# users/serializers.py



class AssignUserToGroupSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    group_name = serializers.CharField()

    def validate(self, data):
        try:
            user = User.objects.get(id=data['user_id'])
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found.")

        try:
            group = Group.objects.get(name=data['group_name'])
        except Group.DoesNotExist:
            raise serializers.ValidationError("Group not found.")

        data['user'] = user
        data['group'] = group
        return data

    def save(self):
        user = self.validated_data['user']
        group = self.validated_data['group']

        user.groups.clear()
        user.groups.add(group)
        return user
