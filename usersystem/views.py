from django.shortcuts import render,HttpResponse, redirect
from .models import Usersystem
from .forms import LoginForm,RegisterForm
from django.contrib.auth import get_user_model

# Create your views here.
def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    return HttpResponse("error")
    # else:
    #     form = LoginForm(request.POST)
    #     if form.is_valid():
    #         username = form.cleaned_data.get('username')
    #         password = form.cleaned_data.get('password')
    #         user = Usersystem.objects.get(username=username)
    #         if user.check_password(password):


def register(request):
    if request.method == 'GET':
        return render(request, 'register.html')
    else:
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            confirmation = form.cleaned_data.get('confirmpassword')
            Usersystem.objects.create(username=username, password=password, confirmpassword=confirmation)
            return render(request, 'register.html')
        else:
            return render(request, 'register.html', {'form': form})

def add_user(request):
    newuser = Usersystem(username='shuxuan1',Password='Guardian1127')
    newuser.save()
    return HttpResponse('Create account successfully!')

def query_user(request):
    # users = Usersystem.objects.all()
    # sort by order
    users = Usersystem.objects.order_by('username')
    ## search user with feature
    # users = Usersystem.objects.filter(username='shuxuan1')
    for user in users:
        print(user.username, user.Password)
    # try:
    #     user = Usersystem.objects.get(username='shuxuan1111')
    #     print(user.Password)
    # except Usersystem.DoesNotExist:
    #     return HttpResponse("User not found!")

    return HttpResponse("Query user successfully!")

def update_user(request):
    newuser = Usersystem.objects.get(username='shuxuan1')
    newuser.Password = ''
    newuser.save()
    return HttpResponse("Update user successfully!")


def delete_user(request):
    user = Usersystem.objects.get(id=4,username='shuxuan1')
    user.delete()
    return HttpResponse("Delete user successfully!")



