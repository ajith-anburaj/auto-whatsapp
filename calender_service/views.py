from django.http import JsonResponse

from calender.Calender import Calender

calender_service = Calender()


def get_calenders(request):
    calenders = calender_service.get_calenders()
    return JsonResponse(status=200, data=calenders, safe=False)


def get_events(request, calender):
    calender = request.META['HTTP_REFERER'].split("/")[-2]
    events = calender_service.get_events(calender_id=calender)
    return JsonResponse(status=200, data=events, safe=False)
