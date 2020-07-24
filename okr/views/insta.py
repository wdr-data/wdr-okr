from datetime import date

from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from ..scrapers.insta import scrape_insights, scrape_stories, scrape_posts


def parse_start_date(post_data):
    start_date = post_data.get("start_date")
    if start_date:
        start_date = date.fromisoformat(start_date)
    return start_date


@require_POST
@csrf_exempt
def trigger_insights(request, interval):
    scrape_insights(interval, start_date=parse_start_date(request.POST))
    return HttpResponse("ok")


@require_POST
@csrf_exempt
def trigger_stories(request):
    scrape_stories(start_date=parse_start_date(request.POST))
    return HttpResponse("ok")


@require_POST
@csrf_exempt
def trigger_posts(request):
    scrape_posts(start_date=parse_start_date(request.POST))
    return HttpResponse("ok")
