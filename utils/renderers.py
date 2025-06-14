from rest_framework.renderers import JSONRenderer

'''
Custom JSON renderer for API responses.
'''

class CustomJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get('response', None)
        request = renderer_context.get('request', None)

        status_code = getattr(response, 'status_code', 200)

        # Let errors through unmodified
        if status_code >= 400:
            return super().render(data, accepted_media_type, renderer_context)

        message = "Request was successful"
        pagination = None

        if isinstance(data, dict) and "results" in data and "count" in data:
            results = data.get("results", [])
            pagination = {
                "count": data.get("count"),
                "page_size": len(results),
                "page": int(getattr(request, 'GET', {}).get("page", 1)),
                "next": data.get("next"),
                "previous": data.get("previous"),
            }
            data = results

        formatted = {
            "success": True,
            "code": status_code,
            "message": message,
            "data": data,
            "pagination": pagination,
        }

        return super().render(formatted, accepted_media_type, renderer_context)
