from rest_framework import serializers
from .models import User
import re

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['name', 'email', 'age']
        
        
    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Name cannot be empty.")
        return value
    
    
    def validate_email(self, value):
        """Rejects emails with multiple dots in the domain part (e.g., ja@gmail.com.com)"""
        email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_pattern, value):
            raise serializers.ValidationError("Enter a valid email address.")

        # Reject multiple dots in domain
        if re.search(r'@\w+\.\w+\.\w+\.\w+', value):
            raise serializers.ValidationError("Invalid email format: Too many dots in domain.")
        
        return value
        
    def validate_age(self, value):
        if value < 0 or value > 120:
            raise serializers.ValidationError("Age must be between 0 and 120.")
        return value
