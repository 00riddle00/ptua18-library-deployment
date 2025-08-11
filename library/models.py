import uuid
from datetime import date

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from PIL import Image
from tinymce.models import HTMLField


class Genre(models.Model):
    name = models.CharField(
        verbose_name=_("Name"),
        max_length=200,
        help_text=_("Enter the book genre (e.g. detective)"),
    )

    class Meta:
        verbose_name = _("Genre")
        verbose_name_plural = _("Genres")

    def __str__(self):
        return self.name


class Author(models.Model):
    """Model representing an author."""

    first_name = models.CharField(verbose_name=_("First Name"), max_length=100)
    last_name = models.CharField(verbose_name=_("Last Name"), max_length=100)
    description = HTMLField(verbose_name=_("Description"))

    class Meta:
        verbose_name = _("Author")
        verbose_name_plural = _("Authors")
        ordering = ["last_name", "first_name"]

    def __str__(self):
        """String for representing the Model object."""
        return f"{self.last_name} {self.first_name}"

    def get_absolute_url(self):
        """Returns the url to access a particular author instance."""
        return reverse("author-detail", args=[str(self.id)])

    def display_books(self):
        return ", ".join(book.title for book in self.books.all()[:3])

    display_books.short_description = _("Books")


class Book(models.Model):
    """Model represents a book (but not a specific copy of a book)"""

    title = models.CharField(verbose_name=_("Title"), max_length=200)
    author = models.ForeignKey(
        Author,
        verbose_name=_("Author"),
        on_delete=models.SET_NULL,
        null=True,
        related_name="books",
    )
    summary = models.TextField(
        verbose_name=_("Description"),
        max_length=1000,
        help_text=_("Short book description"),
    )
    cover = models.ImageField(verbose_name=_("Cover"), upload_to="covers", null=True)
    isbn = models.CharField(
        verbose_name="ISBN",
        max_length=13,
        help_text=(
            f"{_('13 symbols')} <a"
            f' href="https://www.isbn-international.org/content/what-isbn">{_("ISBN code")}</a>'
        ),
    )
    genre = models.ManyToManyField(
        to=Genre,
        verbose_name=_("Genres"),
        help_text=_("Select the genre(s) for this book"),
    )

    class Meta:
        verbose_name = _("Book")
        verbose_name_plural = _("Books")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """Indicates the final endpoint address for a particular description."""
        return reverse("book", args=[str(self.id)])

    def display_genre(self):
        return ", ".join(genre.name for genre in self.genre.all()[:3])

    display_genre.short_description = _("Genre")


class BookInstance(models.Model):
    """Model, describing the state of a particular book copy."""

    id = models.UUIDField(
        verbose_name="ID",
        primary_key=True,
        default=uuid.uuid4,
        help_text=_("Unique ID for a book copy"),
    )
    book = models.ForeignKey(
        to=Book, verbose_name=_("Book"), on_delete=models.SET_NULL, null=True
    )
    due_back = models.DateField(
        verbose_name=_("Will be available"), null=True, blank=True
    )

    LOAN_STATUS = (
        ("a", _("Administered")),
        ("p", _("Taken")),
        ("g", _("Can be taken")),
        ("r", _("Reserved")),
    )

    status = models.CharField(
        verbose_name=_("Status"),
        max_length=1,
        choices=LOAN_STATUS,
        blank=True,
        default="a",
        help_text=_("Book loan status"),
    )

    reader = models.ForeignKey(
        to=User,
        verbose_name=_("Reader"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("Taken book")
        verbose_name_plural = _("Taken books")
        ordering = ["due_back"]

    def __str__(self):
        return f"{self.id} ({self.book.title})"

    @property
    def is_overdue(self):
        """
        property() -> <pre_function(is_overdue)_block> -> is_overdue() -> <post_function(is_overdue)_block>
        """
        if self.due_back and date.today() > self.due_back:
            return True
        return False


class BookReview(models.Model):
    book = models.ForeignKey(
        to=Book,
        verbose_name=_("Book"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    reviewer = models.ForeignKey(
        to=User,
        verbose_name=_("Reviewer"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    date_created = models.DateTimeField(
        verbose_name=_("Submission date"), auto_now_add=True
    )
    content = models.TextField(verbose_name=_("Review"), max_length=2000)

    class Meta:
        verbose_name = _("Book Review")
        verbose_name_plural = _("Book Reviews")

    def __str__(self):
        return f"{self.book.title} ({_('reviewed by')} {self.reviewer.username})"


class Profile(models.Model):
    user = models.OneToOneField(
        to=User, verbose_name=_("User"), on_delete=models.CASCADE
    )
    photo = models.ImageField(
        verbose_name=_("Photo"),
        default="profile_pics/default.png",
        upload_to="profile_pics",
    )

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")

    def __str__(self):
        return f"{self.user.username} {_('profile')}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        img = Image.open(self.photo.path)
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.photo.path)
