from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import datetime,timezone

@login_required
def index(request):
    today = datetime.now(timezone.utc)
    prueba = today.strftime('%Y-%m-%dT%H:%M:%S %p')
    formatedDay = today.strftime('%Y-%m-%d')
    context = {
        'today': formatedDay,
        'prueba':prueba
    }
    return render(request, 'turno/index.html',context)