from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = "library_v1"
router = DefaultRouter()
router.register("books", views.BookViewSet, basename="book")
router.register("checkouts", views.CheckoutViewSet, basename="checkout")

urlpatterns = [
    path("", include(router.urls)),
    path("profile/", views.LibrarianProfileView.as_view(), name="librarian_profile"),
]
