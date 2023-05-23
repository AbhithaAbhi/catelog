from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
def home(request):
    message = "Please Click Home button on the top to purchase your items."
    return render(request,'base.html', {'message': message})