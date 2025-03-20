
from django.test import TestCase
import io
import csv
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import User

class CSVUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('upload-csv')
        
    def create_csv_file(self, data):
        csv_file = io.StringIO()
        writer = csv.DictWriter(csv_file, fieldnames=['name', 'email', 'age'])
        writer.writeheader()
        for row in data:
            writer.writerow(row)
        csv_file.seek(0)
        return csv_file.getvalue().encode()
        
    def test_valid_csv(self):
        csv_file = io.BytesIO()
        csv_file.write(b'name,email,age\n')
        csv_file.write(b'John Doe,john@example.com,30\n')
        csv_file.write(b'Jane Smith,jane@example.com,25\n')
        csv_file.seek(0)
        
        # Add a name attribute to the file
        csv_file.name = 'test.csv'
        
        # Send the request
        response = self.client.post(
            self.url,
            {'file': csv_file},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['successful_records'], 2)
        self.assertEqual(response.data['rejected_records'], 0)
        self.assertEqual(User.objects.count(), 2)
        
    def test_invalid_csv(self):
        
        csv_file = io.BytesIO()
        csv_file.write(b'name,email,age\n')
        csv_file.write(b'shabah,invalid-email.com,30\n')
        csv_file.write(b'jhony,ja@gmail.com,25\n')
        csv_file.write(b'Jane Smith,jj@gmail.com,1250\n')
        csv_file.write(b'tony,oo@gmail.com,15\n')
        csv_file.seek(0)
        
        # Add a name attribute to the file
        csv_file.name = 'test.csv'
        
        # Send the request
        response = self.client.post(
            self.url,
            {'file': csv_file},
            format='multipart'
        )
        
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['successful_records'], 2)
        self.assertEqual(response.data['rejected_records'], 2)
        self.assertEqual(User.objects.count(), 2)
        
    def test_duplicate_email(self):
        # First create a user
        User.objects.create(name='tony', email='tony@gmail.com', age=30)
        
        csv_file = io.BytesIO()
        csv_file.write(b'name,email,age\n')
        csv_file.write(b'shabah,tony@gmail.com,30\n')
        csv_file.write(b'sam,oo@gmail.com,15\n')
        csv_file.seek(0)
        
        # Add a name attribute to the file
        csv_file.name = 'test.csv'
        
        # Send the request
        response = self.client.post(
            self.url,
            {'file': csv_file},
            format='multipart'
        )
        
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['successful_records'], 1)
        self.assertEqual(response.data['rejected_records'], 1)
        self.assertEqual(User.objects.count(), 2)  # Original user + sam
        
    def test_non_csv_file(self):
        response = self.client.post(
            self.url,
            {'file': ('test.txt', b'not a csv', 'text/plain')},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        
    def test_no_file(self):
        response = self.client.post(self.url, {}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)