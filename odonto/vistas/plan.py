from django.core import serializers
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from odonto.models import Plan
from django.db.models import F


@login_required
def get_for_select(request):
    obra_social = int(request.GET.get('obra_social'))
    planes = Plan.objects.filter(obra_social__clinica_id = request.user.clinica
        ).filter(obra_social__id = obra_social
        ).values('id',
        ).annotate(descrip = F('nombre')) # or simply .values() to get all fields
    p_list = list(planes)  # important: convert the QuerySet to a list object
    return JsonResponse(p_list, safe=False)