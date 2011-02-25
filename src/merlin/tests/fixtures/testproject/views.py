from django.http import HttpResponse


def index(request):
    return HttpResponse("Index page")


def more(request):
    return HttpResponse("More page")
