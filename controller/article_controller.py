import os
import uuid
from views.view import View
from controller.controller import Controller
from models.article import Article
from models.user import User
from services.db import Db
from exceptions import NotFoundException
from exceptions import UnauthorizedException
from upload_security import validate_upload, safe_filename


UPLOAD_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'static', 'uploads', 'articles'
)
os.makedirs(UPLOAD_DIR, exist_ok=True)


class ArticlesController(Controller):

    def index(self, request, response):
        articles = Article.find_all()
        response.text = self.view.render_html(
            'articles/articles.html',
            {'title': 'MVC фреймворк', 'h1': 'Статья:', 'articles': articles}
        )

    def view(self, request, response, id):
        article = Article.get_by_id(id)
        if article is None:
            raise NotFoundException('Статья не найдена')

        user = User.get_by_id(article.get_author_id())
        response.text = self.view.render_html(
            'articles/view.html',
            {'title': f'MVC фреймворк - {article.get_name()}',
             'h1': f'Статья: {article.get_name()}',
             'article': article}
        )

    def edit(self, request, response, id):
        article = Article.get_by_id(id)
        if article is None:
            raise NotFoundException('Статья не найдена')
            return

        if self.user is None:
            raise UnauthorizedException('Необходимо авторизоваться')

        if request.method == 'POST':
            article.set_name(request.POST['name'])
            article.set_text(request.POST['text'])
            article.save()
            response.status_code = 302
           
            response.headers = [('Location', f'/articles/{article.get_id()}')]
            return

        response.text = self.view.render_html(
            'articles/edit.html',
            {'title': f'Редактирование - {article.get_name()}', 'article': article}
        )

    def add(self, request, response):
        
        if request.method == 'GET':
            response.text = self.view.render_html(
                'articles/add.html',
                {'title': 'Новая статья'}
            )
            return

        
        name = (request.POST.get('name') or '').strip()
        text = (request.POST.get('text') or '').strip()

        
        if len(name) < 3 or len(text) < 10:
            response.text = self.view.render_html(
                'articles/add.html',
                {'title': 'Новая статья',
                 'error': 'Название должно быть ≥ 3 символов, текст ≥ 10 символов'}
            )
            return

        
        file = request.POST.get('image')
        ok, error = validate_upload(file)
        if not ok:
            response.text = self.view.render_html(
                'articles/add.html',
                {'title': 'Новая статья', 'error': error}
            )
            return

        
        image_name = None
        if file is not None and getattr(file, 'filename', ''):
            image_name = safe_filename(file.filename)
            dest_path = os.path.join(UPLOAD_DIR, image_name)

            if hasattr(file, 'file') and file.file is not None:
                with open(dest_path, 'wb') as out:
                    file.file.seek(0)
                    out.write(file.file.read())
            else:
                with open(dest_path, 'wb') as out:
                    out.write(file.value)

        
        article = Article()
        article.set_author_id(1)
        article.set_name(name)
        article.set_text(text)
        if image_name:
            article.set_image(image_name)
        article.save()

        
        response.status_code = 302
        response.headers = [('Location', '/articles')]

    def delete(self, request, response, id):
        article = Article.get_by_id(id)
        if article is None:
            raise NotFoundException('Статья не найдена')
            return

        article.delete()
        response.status_code = 302
        response.headers = [('Location', '/articles')]

    def search(self, request, response):
        if 'q' not in request.GET:
            response.text = self.view.render_html('articles/search.html')
            return
        articles = Article.search_by_name(request.GET['q'])
        response.text = self.view.render_html(
            'articles/search.html',
            {'q': request.GET['q'], 'articles': articles}
        )