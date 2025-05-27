
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        message = "Validation failed" if response.status_code == 400 else "Request failed"
        formatted = {
            "success": False,
            "code": response.status_code,
            "message": message,
            "data": None,
            "errors": response.data
        }
        response.data = formatted
    else:
        formatted = {
            "success": False,
            "code": 500,
            "message": "Internal server error",
            "data": None,
            "errors": None
        }
        response = Response(formatted, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return response
