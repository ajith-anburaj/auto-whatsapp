from json import loads

from django.http import HttpResponse, JsonResponse
from django.views import View

from whatsapp.main import scheduler_instance
from whatsapp.main import client as whats_app


class TasksManager(View):

    def get(self, request):
        tasks = scheduler_instance.get_user_tasks()
        return JsonResponse(status=200, data=tasks, safe=False)

    def post(self, request):
        task = scheduler_instance.store_task_info(task_info=loads(request.body))
        return JsonResponse(status=201, data=task)

    def delete(self, request):
        scheduler_instance.delete_all_tasks()
        return HttpResponse(status=204)


class TaskManager(View):

    def get(self, request, task_id):
        task_info = scheduler_instance.get_task_by_id(task_id=task_id)
        return JsonResponse(status=200, data=loads(task_info)) if task_info else HttpResponse(status=404)

    def put(self, request, task_id):
        task_info = loads(request.body)
        updated_task_info = scheduler_instance.update_task_by_id(task_id=task_id, task_update_info=task_info)
        return JsonResponse(status=200, data=updated_task_info) if updated_task_info else HttpResponse(status=404)

    def delete(self, request, task_id):
        scheduler_instance.delete_task_by_id(task_id=task_id)
        return HttpResponse(status=204)


def get_contacts(request):
    return JsonResponse(status=200, data=whats_app.contacts())
