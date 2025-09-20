from django.shortcuts import render

# Create your views here.
def register(request):
    return render(request, 'register.html')

def info(request):
    username = "Username"
    book = {'name':'你是猪', 'author':'施耐庵'}
    context = {'username':username,
               'book':book
               }
    return render(request, 'info.html', context=context)

def if_view(request):
    age = 20
    context = {'age':age}
    return render(request, 'if.html', context=context)

def url_view(request):
    return render(request, 'url.html')
