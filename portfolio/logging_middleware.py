import json
import logging

class LoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger('main')

    def __call__(self, request):
        self.log_request(request)
        response = self.get_response(request)
        self.log_response(request, response)

        return response

    def log_request(self, request):
        # Полный URL с параметрами
        full_url = request.build_absolute_uri()
        # Заголовки
        headers = {k: v for k, v in request.headers.items()}
        # Тело запроса
        body = request.body.decode('utf-8') if request.body else ''

        self.logger.info(f'Incoming request: {request.method} {full_url}, Headers: {headers}, Body: {body}')

    def log_response(self, request, response):
        # Тело ответа
        response_body = response.content.decode('utf-8') if response.content else ''

        self.logger.info(
            f'Outgoing response: {response.status_code} for {request.method} {request.path}, Body: {response_body}')
