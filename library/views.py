from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.forms import User
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.utils.translation import gettext as _
from django.views import generic
from django.views.decorators.csrf import csrf_protect

from .forms import BookInstanceForm, BookReviewForm, ProfileUpdateForm, UserUpdateForm
from .models import Author, Book, BookInstance


def search(request):
    """
    paprasta paieška. query ima informaciją iš paieškos laukelio,
    search_results prafiltruoja pagal įvestą tekstą knygų pavadinimus ir aprašymus.
    Icontains nuo contains skiriasi tuo, kad icontains ignoruoja ar raidės
    didžiosios/mažosios.
    """
    query = request.GET.get("query")
    search_results = Book.objects.filter(
        Q(title__icontains=query)
        | Q(summary__icontains=query)
        | Q(author__first_name__icontains=query)
    )
    return render(
        request, "library/search.html", {"books": search_results, "query": query}
    )


def index(request):
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    num_instances_available = BookInstance.objects.filter(status__exact="g").count()
    num_authors = Author.objects.count()

    # Papildome kintamuoju num_visits, įkeliame jį į kontekstą.

    num_visits = request.session["num_visits"] = (
        request.session.get("num_visits", 0) + 1
    )
    context = {
        "num_books": num_books,
        "num_instances": num_instances,
        "num_instances_available": num_instances_available,
        "num_authors": num_authors,
        "num_visits": num_visits,
    }
    return render(request, "library/index.html", context=context)


def authors(request):
    paginator = Paginator(Author.objects.all(), 2)
    # request.GET['page'] - 'grieztas' traukimas - jeigu nebus tokio rakto -> KeyError
    page_number = request.GET.get("page")
    paged_authors = paginator.get_page(page_number)
    context = {"authors": paged_authors}
    return render(request, "library/authors.html", context=context)


def author(request, author_id):
    single_author = get_object_or_404(Author, pk=author_id)
    return render(request, "library/author.html", {"author": single_author})


class BookListView(generic.ListView):
    model = Book
    # patys galite nustatyti šablonui kintamojo vardą
    context_object_name = "books"
    # šitą jau panaudojome. Neįsivaizduojate, kokį default kelią sukuria :)
    template_name = "library/books.html"
    # puslapyje bus iki dvieju irasu
    paginate_by = 2

    # def get_queryset(self):
    #     # gauti sąrašą 3 knygų su žodžiu pavadinime 'ku'
    #     return Book.objects.filter(title__icontains='ku')[:3]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["custom_message"] = _("Additional context data")
        return context


class BookDetailView(generic.edit.FormMixin, generic.DetailView):
    model = Book
    context_object_name = "book"
    template_name = "library/book.html"
    form_class = BookReviewForm

    # nurodome, kur atsidursime komentaro sėkmės atveju.
    def get_success_url(self):
        return reverse("book", kwargs={"pk": self.object.id})

    # standartinis post metodo perrašymas, naudojant FormMixin, galite kopijuoti tiesiai į savo projektą.
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    # štai čia nurodome, kad knyga bus būtent ta, po kuria komentuojame, o vartotojas bus tas, kuris yra prisijungęs.
    def form_valid(self, form):
        form.instance.book = self.object
        form.instance.reviewer = self.request.user
        form.save()
        return super(BookDetailView, self).form_valid(form)


class LoanedBookByUserListView(
    LoginRequiredMixin, PermissionRequiredMixin, generic.ListView
):
    permission_required = "library.view_bookinstance"
    model = BookInstance
    context_object_name = "loaned_books"
    template_name = "library/user_books.html"
    paginate_by = 10

    def get_queryset(self):
        return (
            BookInstance.objects.filter(reader=self.request.user)
            .filter(status__exact="p")
            .order_by("due_back")
        )


class LoanedBookByUserDetailView(
    LoginRequiredMixin, PermissionRequiredMixin, generic.DetailView
):
    permission_required = "library.view_bookinstance"
    model = BookInstance
    context_object_name = "loaned_book"
    template_name = "library/user_book.html"


@csrf_protect
def register(request):
    if request.method == "POST":
        # pasiimame reikšmes iš registracijos formos
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        password2 = request.POST["password2"]
        # tikriname, ar sutampa slaptažodžiai
        if password == password2:
            # tikriname, ar neužimtas username
            if User.objects.filter(username=username).exists():
                messages.error(request, _("Username %s is already taken!") % username)
                return redirect("register")
            else:
                # tikriname, ar nėra tokio pat email
                if User.objects.filter(email=email).exists():
                    messages.error(
                        request, _("User with email %s is already registered!") % email
                    )
                    return redirect("register")
                else:
                    # jeigu viskas tvarkoje, sukuriame naują vartotoją
                    User.objects.create_user(
                        username=username, email=email, password=password
                    )
                    messages.success(
                        request,
                        _("Account with the name %s has been successfully registered!")
                        % username,
                    )
                    return redirect("login")
        else:
            messages.error(request, "Passwords do not match!")
            return redirect("register")
    return render(request, "registration/register.html")


# @login_required  # can be removed, since we added @permission_required decorator
@permission_required("library.add_bookinstance")
def create_book_instance(request):
    form = BookInstanceForm()
    if request.method == "POST":
        form = BookInstanceForm(request.POST)
        if form.is_valid():
            form.save()  # saves data in database (bookinstance table)
            return HttpResponseRedirect(reverse("index"))

    return render(request, "library/create_book_instance.html", context={"form": form})


@login_required
def profile(request):
    if request.method == "POST":
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=request.user.profile
        )
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile updated!")
            return redirect("profile")
    elif request.method == "GET":
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
        context = {
            "user_form": user_form,
            "profile_form": profile_form,
        }
        return render(request, "registration/profile.html", context)
