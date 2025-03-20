from django.shortcuts import render
import csv
from django.db import IntegrityError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
# from rest_framework.parsers import FileUploadParser
from .models import User
from .serializers import UserSerializer


class CSVupload(APIView):
    
    parser_classes = (MultiPartParser, FormParser)
    # parser_classes = [FileUploadParser]
    
    def post(self, request):
        file = request.FILES.get('file')
        
        #check if file is provided or not
        if not file:
            return Response({"error": "file not Provided"},status=status.HTTP_400_BAD_REQUEST)
        
        #ensure the file is csv
        if not file.name.endswith('.csv'):
            return Response({"error": "file must be csv"}, status=status.HTTP_400_BAD_REQUEST)
        
        #read csv file 
        decoded_file  = file.read().decode('utf-8').splitlines()
        csv_reader = csv.DictReader(decoded_file)

        success_count = 0
        error_count = 0
        errors = []
        
        for row_idx, row in enumerate(csv_reader, start=1):
            
            try:
                #convert age to int
                if row['age'].strip():
                    row['age'] = int(row['age'])
                else:
                    row['age'] = None
                    
                 # Validate data using serializer
                serializer = UserSerializer(data=row)
                
                if serializer.is_valid():
                    try:
                        serializer.save()
                        success_count += 1
                    except IntegrityError:
                        errors.append({'row': row_idx, 'error': f"Duiplicate email found '{row['email']}'"})
                        error_count += 1
                else:
                    errors.append({"row": row_idx, "error": serializer.errors})
                    error_count += 1         
            except ValueError:
                errors.append({
                    "row": row_idx, "error": {"age": "Age must be a valid integer"}})
                error_count += 1
        
        #collect response data
        response_data = {
            "total_records": success_count + error_count,
            "successful_records": success_count,
            "rejected_records": error_count,
            "errors": errors
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
                
            
        
        
        
            
    
