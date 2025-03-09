from django.utils.deprecation import MiddlewareMixin

class DisableHtmlGzipMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        # Sirf HTML responses par apply karega
        if 'text/html' in response.get('Content-Type', ''):
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        return response
