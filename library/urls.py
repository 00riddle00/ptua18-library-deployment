from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("register/", views.register, name="register"),
    path("authors/", views.authors, name="authors"),
    path("authors/<int:author_id>", views.author, name="author"),
    path("books/", views.BookListView.as_view(), name="books"),
    path("books/<int:pk>", views.BookDetailView.as_view(), name="book"),
    path("search/", views.search, name="search"),
    path("mybooks/", views.LoanedBookByUserListView.as_view(), name="my-loaned-books"),
    path(
        "mybooks/<uuid:pk>",
        views.LoanedBookByUserDetailView.as_view(),
        name="my-loaned-book",
    ),
    path(
        "create_new_book_instance/",
        views.create_book_instance,
        name="create-book-instance",
    ),
    path("profile/", views.profile, name="profile"),
]
