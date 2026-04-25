from django.utils import timezone

def get_current_time(request):
    return {
        'current_time': timezone.localtime(timezone.now())
    }