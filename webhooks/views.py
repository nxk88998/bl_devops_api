from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

import json
# @csrf_exempt
# def gitlab_webhook(request):
#     if request.method == 'POST':
#         # Add your code here
#         print('Do something here')
#         return HttpResponse('Done!')
#     return HttpResponse('Hehe! Use POST please!')


@csrf_exempt
def gitlab_webhook(request):
    if request.method == 'POST' and request.body:
        http_x_gitlab_event = request.META.get('HTTP_X_GITLAB_EVENT', '')
        json_data = json.loads(request.body)
        object_kind = json_data.get('object_kind', '')
        project_id = json_data.get('project_id', '')
        repo_data = json_data.get('repository', '')
        user_id = json_data.get('user_id', '')
        user_name = json_data.get('user_name', '')
        user_email = json_data.get('user_email', '')
        if repo_data:
            repo_name = repo_data.get('name', '')
            repo_url = repo_data.get('url', '')
            webhook = gitlab_webhook.objects.filter(
                repo_name = repo_name,
                repo_url = repo_url,
                object_kind = object_kind,
                project_id = project_id,
                http_x_gitlab_event = http_x_gitlab_event
            ).first()
            if webhook:
                # Add your code here
                print('User %s %s %s call this webhook' % (user_id, user_name, user_email))
                return HttpResponse('Done!')

    return HttpResponse('Hehe!')
