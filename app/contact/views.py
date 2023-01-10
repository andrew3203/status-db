from django.http import JsonResponse
from contact.tasks import *

import json

# Create your views here.
 
def upload(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        load_data_task2.delay(
            instance_str=data['instance_str'],
            data=data['data']
        )
    return JsonResponse({'result': 'OK'})