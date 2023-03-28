from django.shortcuts import render

# Create your views here.


from django.shortcuts import render
import random


def home(request):
    return render(request,'home.html')

def mental_math_tricks(request):
    return render(request, 'mental_math_tricks.html')

# Erreur 400
def handler400(request, exception):
    return render(request, '400.html', status=400)

# Erreur 403
def handler403(request, exception):
    return render(request, '403.html', status=403)

# Erreur 404
def handler404(request, exception):
    rd = random.random()
    if rd <= 0.5 :
        return render(request, '404-1.html', status=404)
    else :
        return render(request, '404-2.html', status=404)

# Erreur 500
def handler500(request):
    return render(request, '500.html', status=500)