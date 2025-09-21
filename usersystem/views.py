from django.shortcuts import render,HttpResponse
from .models import Usersystem


# Create your views here.
def login(request):
    return render(request, 'login.html')


def register(request):
    return render(request, 'register.html')

def add_user(request):
    newuser = Usersystem(Username='shuxuan1',Password='Guardian1127')
    newuser.save()
    return HttpResponse('Create account successfully!')

def query_user(request):
    # users = Usersystem.objects.all()
    # sort by order
    users = Usersystem.objects.order_by('Username')
    ## search user with feature
    # users = Usersystem.objects.filter(Username='shuxuan1')
    for user in users:
        print(user.Username, user.Password)
    # try:
    #     user = Usersystem.objects.get(Username='shuxuan1111')
    #     print(user.Password)
    # except Usersystem.DoesNotExist:
    #     return HttpResponse("User not found!")

    return HttpResponse("Query user successfully!")

def update_user(request):
    newuser = Usersystem.objects.get(Username='shuxuan1')
    newuser.Password = ''
    newuser.save()
    return HttpResponse("Update user successfully!")


def delete_user(request):
    user = Usersystem.objects.get(id=4,Username='shuxuan1')
    user.delete()
    return HttpResponse("Delete user successfully!")