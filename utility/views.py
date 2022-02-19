from django.http import JsonResponse
from django.shortcuts import render

from utility.models import LocationStore


# Create your views here.

def email_confirm_success(request):
    return render(request, 'utility/emailconfirm.html')


def get_lga(city):
    id_lga = LocationStore.objects.filter(name__exact=city)
    return [x.lga for x in id_lga]


def get_state(city):
    id_state = LocationStore.objects.filter(name__exact=city)
    return [x.state for x in id_state]


def slim(the_list, sub_list):
    for each in sub_list:
        the_list = [x for x in the_list if each not in x]
    return list(set(the_list))


remove_items = ['River', 'Forest', 'Hill']


def nearest_cities(request, city):
    city = str(city).capitalize()
    # lga = get_lga(city)
    state = get_state(city)
    for each in state:
        _state = LocationStore.objects.filter(state=each)
        nearest_state = [x.name for x in _state]
    nearest_state = slim(nearest_state, remove_items)
    return JsonResponse({'found': len(nearest_state), 'location': nearest_state})
