from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import AssignmentForm
from .models import Assignment

def create_assignment(request):
    if request.method == "POST":
        form = AssignmentForm(request.POST or None)
        if form.is_valid():
            subject = form.cleaned_data.get('subject')
            assignment_title = form.cleaned_data.get('assignment_title')
            due_date = form.cleaned_data.get('due_date')
            assignment_type = form.cleaned_data.get('assignment_type')
            Assignment.objects.create(
                subject=subject,
                assignment_title=assignment_title,
                due_date=due_date,
                assignment_type=assignment_type
            )

            return HttpResponse('good') # 替换为你的路由名
    else:
        form = AssignmentForm()
    return render(request, "Assignment.html", {"form": form})

def query_assignment(request):
    assignments = Assignment.objects.all()
    for assignment in assignments:
        print('id: ',assignment.id)
        print('subject: ',assignment.subject)
        print('title: ',assignment.assignment_title)
        print('due: ',assignment.due_date)
        print('type: ',assignment.assignment_type)
    return HttpResponse("query completed")

def AIUseScale(request):
    return render(request, "AIUseScale.html")