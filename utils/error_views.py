from django.http import JsonResponse

def custom_404(request, exception):
    return JsonResponse({
        "success": False,
        "code": 404,
        "message": "The requested resource was not found",
        "data": None,
        "errors": None
    }, status=404)

def custom_500(request):
    return JsonResponse({
        "success": False,
        "code": 500,
        "message": "Internal server error",
        "data": None,
        "errors": None
    }, status=500)
