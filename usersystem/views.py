from django.shortcuts import render,HttpResponse, redirect
from .forms import LoginForm,RegisterForm
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your views here.
def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    else:
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = User.objects.get(username=username)
            if user.check_password(password):
                return redirect('Assignment:create_assignment')
        return render(request, 'login.html', {'form': form})


def register(request):
    if request.method == 'GET':
        return render(request, 'register.html')
    else:
        form = RegisterForm(request.POST or None)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            confirmation = form.cleaned_data.get('confirmpassword')
            User.objects.create_user(username=username, password=password)
            return redirect('usersystem:login')
        else:
            print(form.errors)
            return render(request, 'register.html', {'form': form})

def query_user(request):
    # users = Usersystem.objects.all()
    # sort by order
    users = User.objects.order_by('username')
    ## search user with feature
    # users = Usersystem.objects.filter(username='shuxuan1')
    for user in users:
        print(user.username, user.password)
    # try:
    #     user = Usersystem.objects.get(username='shuxuan1111')
    #     print(user.password)
    # except Usersystem.DoesNotExist:
    #     return HttpResponse("User not found!")
    return HttpResponse("Query user successfully!")

def update_user(request):
    newuser = User.objects.get(username='shuxuan1')
    newuser.password = ''
    newuser.save()
    return HttpResponse("Update user successfully!")


def delete_user(request):
    user = User.objects.get(id=4,username='shuxuan1')
    user.delete()
    return HttpResponse("Delete user successfully!")



