import os
import re
from exceptions import NotFoundException
from views.view import View
from webob import Request, Response
from exceptions import UnauthorizedException


from whitenoise import WhiteNoise

import routes
import handlers




class API:
    def __init__(self, static_dir="assets"):
        self.routes = routes.routes
        self.whitenoise = WhiteNoise(self.wsgi_app, root=static_dir)

    def wsgi_app(self, environ, start_response):
        request = Request(environ)

        response = self.handle_request(request)

        return response(environ, start_response)
    
    def __call__(self, environ, start_response):
        # requet = Request(environ)
        # response = self.handle_request(requet)
        # return response(environ, start_response)
        return self.whitenoise(environ, start_response)




        

        # response_body  = ['{key}: {value}'.format(key=key, value=value) for key, value in sorted(environ.items())]
        
        # response.text = '\n'.join(response_body)
        # response.headers.add('Content-type', 'text/plain')

        
        
        
        # status = "200 OK"



        # response_headers = [('Content-type', 'text/plain')]
        # start_response(status, response_headers)

        # return [response_body.encode('utf-8')]

    def handle_request(self, request):
        response = Response()
        
        try:
            result = self.find_handler_re(request_path=request.path)
        
            request_url = request.environ.get("REQUEST_URI")

            result = self.find_handler_re(request_path=request.path)
            if result is None:
                raise NotFoundException('Страница не найдена')

            handler, params = result
            controller = handler[0](request)
            action = handler[1]
            action(controller, request, response, *params)
        
        except NotFoundException as e:
            response.status_code = 404
            response.text = View('default').render_html('errors/404.html', {'error' : e})
        
        except UnauthorizedException as e:
            response.status_code = 401
            response.text = View('default').render_html('errors/401.html', {'error' : e})
            
            # response.text = f"Привет, ты запросил страницу {request_url}"

        return response
    
    def find_handler(self, request_path):
        for path, handler in self.routes.items():
            if path == request_path:
                return handler
            
    def find_handler_re(self, request_path):
        for path, handler in self.routes.items():
            match = re.search(path, request_path)
            if match is not None:
                return handler, match.groups()
    
    def default_response(self, response):
        response.status_code = 404
        response.text = "Page is not found"
    
    def route(self, path):
        def wrapper(handler):
            self.routes[path] = handler
            return handler
        return wrapper

app = API()

# def app (environ, start_response):
