from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from ..scrapers import youtube


@require_POST
@csrf_exempt
def trigger_analytics(request, interval):
    youtube.scrape_analytics(interval)
    return HttpResponse("ok")
