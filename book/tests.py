from django.test import TestCase, Client
from .models import Book

class BookModelTest(TestCase):
    def setUp(self):
        self.book = Book.objects.create(
            name='Test Book',
            author='Test Author',
            price=99.99
        )
    
    def test_book_creation(self):
        self.assertEqual(self.book.name, 'Test Book')
        self.assertEqual(self.book.author, 'Test Author')
        self.assertEqual(float(self.book.price), 99.99)
        self.assertIsNotNone(self.book.pub_time)
    
    def test_book_str_representation(self):
        self.assertEqual(str(self.book), 'Test Book')

class BookViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
    
    def test_add_book_view(self):
        response = self.client.get('/book/add/')
        self.assertEqual(response.status_code, 200)
    
    def test_query_book_view(self):
        response = self.client.get('/book/query/')
        self.assertEqual(response.status_code, 200)
    
    def test_index_view(self):
        response = self.client.get('/book/')
        self.assertEqual(response.status_code, 200)
