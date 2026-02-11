import logging
import time
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.start_time = time.time()
        
    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            log_data = {
                'method': request.method,
                'path': request.path,
                'status': response.status_code,
                'duration': duration,
                'user': str(request.user) if request.user.is_authenticated else 'anonymous',
                'ip': request.META.get('REMOTE_ADDR'),
                'user_agent': request.META.get('HTTP_USER_AGENT'),
                'referer': request.META.get('HTTP_REFERER'),
                'query_params': dict(request.GET),
            }
            
            logger.info(f"Request processed", extra=log_data)
            
        return response
    