from views.view import View
from controller.controller import Controller
from services.db import Db

class SiteController(Controller):
    

    def index(self, request, response):

        response.text = self.view.render_html('site/index.html', {'title' : 'MVC фреймворк', 'h1' : 'Главная страница'})

    def about(self, request, response):
        response.text = self.view.render_html('site/about.html', {'title' : 'О нас', 'h1' : 'Вы на странице "о нас"'})
    
    def hello(self, request, response, user_name):
        response.text = self.view.render_html('site/hello.html', {'title' : 'Вы пользователь', 'h1' : 'Страница пользователя', 'user' : user_name})
        