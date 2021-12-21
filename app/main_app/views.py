from django.http.response import JsonResponse
from django.shortcuts import render
from time import sleep
from django_q.tasks import async_task


def index(request):
    return render(request, 'main_app/index.html')