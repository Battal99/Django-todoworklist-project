from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .forms import FormTodo
from .models import Todo
from django.utils import timezone
from django.contrib.auth.decorators import login_required


# Create your views here.

def home(request):
    return render(request, 'todo/home.html')


def signupuser(request):
    if request.method == 'GET':
        return render(request, "todo/signupuser.html", {'form': UserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('currenttodos')
            except IntegrityError:
                return render(request, "todo/signupuser.html",
                              {'form': UserCreationForm(), 'error': 'This user has already exists'})

        else:
            return render(request, "todo/signupuser.html",
                          {'form': UserCreationForm(), 'error': 'Password did not match'})


def loginuser(request):
    if request.method == 'GET':
        return render(request, "todo/loginuser.html", {'form': AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, "todo/loginuser.html",
                          {'form': AuthenticationForm(), 'error': 'Username and password doesnt exists'})
        else:
            login(request, user)
            return redirect('currenttodos')

@login_required
def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')


@login_required
def currenttodos(request):
    todos = Todo.objects.filter(user=request.user, date_end__isnull=True)
    return render(request, "todo/currenttodos.html", {'todos': todos})


@login_required
def completedtodos(request):
    todos = Todo.objects.filter(user=request.user, date_end__isnull=False).order_by('-date_end')
    return render(request, "todo/completedtodos.html", {'todos': todos})


@login_required
def createtodo(request):
    if request.method == 'GET':
        return render(request, "todo/createtodo.html", {'form': FormTodo()})
    else:
        try:
            form = FormTodo(request.POST)
            newtodo = form.save(commit=False)
            newtodo.user = request.user
            newtodo.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request, "todo/createtodo.html", {'form': FormTodo(), 'error': 'Bad data passed in'})


@login_required
def viewtodo(request, todo_pk):
    global form
    task = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == "GET":
        form = FormTodo(instance=task)
        return render(request, "todo/viewtodo.html", {'task': task, 'form': form})
    else:
        try:
            form = FormTodo(request.POST, instance=task)
            form.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request, "todo/viewtodo.html", {'task': task, 'form': form, 'error': "Incorrect information"})


@login_required
def completetodo(request, todo_pk):
    task = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == "POST":
        task.date_end = timezone.now()
        task.save()
        return redirect('currenttodos')


def deletetodo(request, todo_pk):
    task = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == "POST":
        task.delete()
        return redirect('currenttodos')
