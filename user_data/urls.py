from .views import CSVupload
from django.urls import path


urlpatterns = [
    path('upload-csv', CSVupload.as_view(), name='upload-csv')
]