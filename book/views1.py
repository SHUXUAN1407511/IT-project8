from django.shortcuts import render, HttpResponse
from django.db import connection
from .models import Book

# Create your views here.
def index(request):
    cursor = connection.cursor()
    cursor.execute('select * from username')
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    return HttpResponse("Success!")

def add_book(request):
    book = Book(name='11111',author='罗',price=100)
    book.save()
    return HttpResponse("Successfully ADD book!")

def query_book(request):
    books = Book.objects.all()
    for book in books:
        print(book.name, book.author, book.price)
    return HttpResponse("Success search!")
