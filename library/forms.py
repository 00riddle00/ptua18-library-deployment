from django import forms
from django.contrib.auth.models import User

from .models import BookInstance, BookReview, Profile


class BookReviewForm(forms.ModelForm):
    class Meta:
        model = BookReview
        fields = (
            "content",
            "book",
            "reviewer",
        )
        widgets = {"book": forms.HiddenInput(), "reviewer": forms.HiddenInput()}


class BookInstanceForm(forms.ModelForm):
    class Meta:
        model = BookInstance
        fields = (
            "book",
            "status",
            "due_back",
            "reader",
        )


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ["username", "email"]


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["photo"]
