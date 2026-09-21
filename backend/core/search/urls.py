from core.search.views import GlobalSearchView
from django.urls import path

app_name = "search"

urlpatterns = [
    path("", GlobalSearchView.as_view(), name="global"),
]
