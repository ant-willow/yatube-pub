from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CreationForm


class SignUp(CreateView):
    """Возвращает страницу регистрации пользователя"""
    form_class = CreationForm
    success_url = reverse_lazy("login") #  где login — это параметр "name" в path()
    template_name = "signup.html"
