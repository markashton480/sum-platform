from django.http import JsonResponse
from django.views import View

from .health import get_health_status


class HealthCheckView(View):
    def get(self, request, *args, **kwargs):
        health_data = get_health_status()
        status_code = 503 if health_data["status"] == "degraded" else 200
        return JsonResponse(health_data, status=status_code)
