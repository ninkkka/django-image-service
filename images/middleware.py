import json
import time
import logging
from datetime import datetime
from django.utils.timezone import now
from user_agents import parse

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware:
    """Middleware для детального логирования всех запросов"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        request.start_time = time.time()
        request.request_time = now()
        
        user = request.user
        user_id = user.id if user.is_authenticated else None
        username = user.username if user.is_authenticated else 'anonymous'
        
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        ip_address = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR', '')
        
        user_agent_string = request.META.get('HTTP_USER_AGENT', '')
        user_agent = parse(user_agent_string)
        
        request_info = {
            'timestamp': request.request_time.isoformat(),
            'method': request.method,
            'path': request.path,
            'full_path': request.get_full_path(),
            'user_id': user_id,
            'username': username,
            'ip_address': ip_address,
            'user_agent': {
                'browser': user_agent.browser.family,
                'browser_version': user_agent.browser.version_string,
                'os': user_agent.os.family,
                'os_version': user_agent.os.version_string,
                'device': user_agent.device.family,
                'is_mobile': user_agent.is_mobile,
                'is_tablet': user_agent.is_tablet,
                'is_pc': user_agent.is_pc,
            },
            'referer': request.META.get('HTTP_REFERER', ''),
            'host': request.META.get('HTTP_HOST', ''),
            'is_ajax': request.headers.get('X-Requested-With') == 'XMLHttpRequest',
            'is_secure': request.is_secure(),
        }
        
        logger.info(f"REQUEST: {json.dumps(request_info, indent=2, ensure_ascii=False)}")
        
        response = self.get_response(request)
        
        duration = time.time() - request.start_time
        
        response_info = {
            'status_code': response.status_code,
            'duration_ms': round(duration * 1000, 2),
            'content_type': response.get('Content-Type', ''),
            'content_length': len(response.content) if hasattr(response, 'content') else 0,
        }
        
        logger.info(f"RESPONSE: {json.dumps(response_info, ensure_ascii=False)}")
        
        response['X-Response-Time'] = str(duration * 1000)
        response['X-User-ID'] = str(user_id) if user_id else 'anonymous'
        
        return response
