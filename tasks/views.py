from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import TaskForm
from .models import Task
from django.utils import timezone
from django.contrib.auth.decorators import login_required

def home(request):

    return render(request, 'index.html', {})


def signup(request):

    if request.method == 'GET':

        return render(request, 'signup.html', {
            'form': UserCreationForm
        })
    else:
        if request.POST['password1'] == request.POST['password2']:
            # register user
            try:
                user = User.objects.create_user(
                    username=request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('tasks')
            except IntegrityError:
                return render(request, 'signup.html', {
                    'form': UserCreationForm,
                    'error': 'Username already exists'
                })

        return render(request, 'signup.html', {
            'form': UserCreationForm,
            'error': 'Password do not match'
        })


def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {
            'form': AuthenticationForm
        })
    else:
        # Autentica el user
        user = authenticate(
            request, username=request.POST['username'], password=request.POST['password'])
        # verifica si el user es valido y muestra un error
        if user is None:
            return render(request, 'signin.html', {
                'form': AuthenticationForm,
                'error': 'Username or password is incorrect'
            })
        # Guarda la sesion del user y redirecciona
        else:
            login(request, user)
            return redirect('tasks')


@login_required
def signout(request):

    logout(request)

    return redirect('home')


@login_required
def tasks(request):
    # filtra las tareas del usuario actual
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=True)
    
    return render(request, 'tasks.html', {
        'tasks': tasks,
        'status':'Pending'

    })


@login_required    
def tasks_completed(request):
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted')

    return render(request, 'tasks.html', {
        'tasks' : tasks,
        'status':'Completed'
    })

@login_required
def create_task(request):
    if request.method == 'GET':

        return render(request, 'create_task.html', {
            'form': TaskForm,
        })

    else:
        try:
            # obtiene el formulario
            form = TaskForm(request.POST)
            # asigna el usuario de la tarea al usuario logeado
            new_task = form.save(commit=False)
            new_task.user = request.user
            # guarda la tarea en la base de datos
            new_task.save()
        except ValueError:
            return render(request, 'create_task.html', {
                'form': TaskForm,
                'error': 'Please provide valid data'
            })

        return redirect('tasks')


@login_required
def task_detail(request, task_id):
    if request.method == 'GET':
        # Obtiene el objeto por el parametro task_id
        task = get_object_or_404(Task, pk=task_id, user=request.user)
        # Crea el form y rellena los datos existentes
        form = TaskForm(instance=task)

        return render(request, 'task_detail.html', {
            'task': task,
            'form': form
        })
    else:
        try:
            # Obtener las tareas del user actual
            task = get_object_or_404(Task, pk=task_id, user=request.user)
            # crea la instancia de la tarea en el form
            form = TaskForm(request.POST, instance=task)
            # guarda la nueva tarea
            form.save()
            # redirecciona a tasks
            return redirect('tasks')
        except ValueError:
            return render(request, 'task_detail.html', {
                'task': task,
                'form': form,
                'error' : 'Error updating task'
            })


@login_required
def complete_task(request, task_id):
    # Obtiene la tarea
    task = get_object_or_404(Task, pk = task_id, user=request.user)
    # verifica que sea un metodo post
    if request.method == 'POST':
        if task.datecompleted == None: 
            # se le asigna una fecha de completado
            task.datecompleted = timezone.now()
            task.save()
            return redirect('tasks_completed')
        else:
            task.datecompleted = None
            task.save()
            return redirect('tasks')  
            

@login_required
def delete_task(request, task_id):
    # Obtiene la tarea
    task = get_object_or_404(Task, pk = task_id, user=request.user)
    # verifica que sea un metodo post
    if request.method == 'POST':
        task.delete()
        return redirect('tasks')