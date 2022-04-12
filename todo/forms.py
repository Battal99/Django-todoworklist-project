from django.forms import ModelForm
from .models import Todo


class FormTodo(ModelForm):
    class Meta:
        model = Todo
        fields = ['title', 'description', 'important']
