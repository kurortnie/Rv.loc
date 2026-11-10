import os
import uuid
import json
import base64
from views.view import View
from controller.controller import Controller
from models.article import Article
from models.user import User
from services.db import Db
from exceptions import NotFoundException
from exceptions import UnauthorizedException
from upload_security import validate_upload, safe_filename

# Путь к папке сохранения картинок внутри static/uploads/articles/
UPLOAD_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'static', 'uploads', 'articles'
)
os.makedirs(UPLOAD_DIR, exist_ok=True)


class ArticlesController(Controller):

    # ================= HTML METHODS (ОБЫЧНЫЕ СТРАНИЦЫ) =================

    def index(self, request, response):
        articles = Article.find_all()
        response.text = self.view.render_html(
            'articles/articles.html',
            {'title': 'MVC фреймворк', 'h1': 'Статья:', 'articles': articles}
        )
        return response

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
        return response

    def edit(self, request, response, id):
        article = Article.get_by_id(id)
        if article is None:
            raise NotFoundException('Статья не найдена')

        if self.user is None:
            raise UnauthorizedException('Необходимо авторизоваться')

        if request.method == 'POST':
            article.set_name(request.POST['name'])
            article.set_text(request.POST['text'])
            
            file = request.POST.get('image')
            if file is not None and getattr(file, 'filename', ''):
                ok, error = validate_upload(file)
                if ok:
                    image_name = safe_filename(file.filename)
                    dest_path = os.path.join(UPLOAD_DIR, image_name)
                    if hasattr(file, 'file') and file.file is not None:
                        file.file.seek(0)
                        with open(dest_path, 'wb') as out:
                            out.write(file.file.read())
                    else:
                        with open(dest_path, 'wb') as out:
                            out.write(file.value)
                    article.set_image(image_name)

            article.save()
            response.status_code = 302
            response.location = f'/articles/{article.get_id()}'
            return response

        response.text = self.view.render_html(
            'articles/edit.html',
            {'title': f'Редактирование - {article.get_name()}', 'article': article}
        )
        return response

    def add(self, request, response):
        if request.method == 'GET':
            response.text = self.view.render_html(
                'articles/add.html',
                {'title': 'Новая статья'}
            )
            return response

        name = (request.POST.get('name') or '').strip()
        text = (request.POST.get('text') or '').strip()

        if len(name) < 3 or len(text) < 10:
            response.text = self.view.render_html(
                'articles/add.html',
                {'title': 'Новая статья',
                 'error': 'Название должно быть ≥ 3 символов, текст ≥ 10 символов'}
            )
            return response

        file = request.POST.get('image')
        ok, error = validate_upload(file)
        if not ok:
            response.text = self.view.render_html(
                'articles/add.html',
                {'title': 'Новая статья', 'error': error}
            )
            return response

        image_name = None
        if file is not None and getattr(file, 'filename', ''):
            image_name = safe_filename(file.filename)
            dest_path = os.path.join(UPLOAD_DIR, image_name)

            if hasattr(file, 'file') and file.file is not None:
                file.file.seek(0)
                with open(dest_path, 'wb') as out:
                    out.write(file.file.read())
            else:
                with open(dest_path, 'wb') as out:
                    out.write(file.value)

        article = Article()
        article.set_author_id(1)
        article.set_name(name)
        article.set_text(text)
        article.set_image(image_name)
        article.save()

        response.status_code = 302
        response.location = '/articles'
        return response

    def delete(self, request, response, id):
        article = Article.get_by_id(id)
        if article is None:
            raise NotFoundException('Статья не найдена')

        article.delete()
        response.status_code = 302
        response.location = '/articles'
        return response

    def search(self, request, response):
        if 'q' not in request.GET:
            response.text = self.view.render_html('articles/search.html')
            return response
        articles = Article.search_by_name(request.GET['q'])
        response.text = self.view.render_html(
            'articles/search.html',
            {'q': request.GET['q'], 'articles': articles}
        )
        return response

    # Метод для рендеринга страницы SPA API
    def api_page(self, request, response):
        """Отображает HTML-страницу, взаимодействующую с API."""
        response.text = self.view.render_html(
            'articles/articles_api.html',
            {'title': 'Интерактивное API', 'h1': 'Статьи через API:'}
        )
        return response
    def api_add_page(self, request, response):
        """Отображает отдельную HTML-страницу создания статьи через API."""
        response.text = self.view.render_html(
            'articles/articles_api_add.html',
            {'title': 'Новая статья через API'}
        )
        return response

    def api_edit_page(self, request, response, id):
        """Отображает отдельную HTML-страницу редактирования статьи через API."""
        # Нам нужно передать ID в шаблон, чтобы JS знал, какую статью запрашивать и обновлять
        response.text = self.view.render_html(
            'articles/articles_api_edit.html',
            {'title': 'Редактирование через API', 'article_id': id}
        )
        return response

    # ================= API METHODS (РАБОТА ЧЕРЕЗ JSON) =================

    def api_index(self, request, response):
        """Возвращает список всех статей в формате JSON."""
        articles = Article.find_all()
        data = [article.to_dict() for article in articles]
        response.text = json.dumps(data, ensure_ascii=False)
        response.content_type = 'application/json'
        return response

    def api_view(self, request, response, id):
        """Возвращает одну конкретную статью по ID в формате JSON."""
        article = Article.get_by_id(id)
        if article is None:
            response.status_code = 404
            response.text = json.dumps({'error': 'Статья не найдена'}, ensure_ascii=False)
            response.content_type = 'application/json'
            return response

        response.text = json.dumps(article.to_dict(), ensure_ascii=False)
        response.content_type = 'application/json'
        return response

    def api_add(self, request, response):
        """Создание статьи через API (JSON + опционально Base64 картинка)."""
        if request.method != 'POST':
            response.status_code = 405
            response.text = json.dumps({'error': 'Метод не поддерживается'}, ensure_ascii=False)
            response.content_type = 'application/json'
            return response

        try:
            data = json.loads(request.body.decode('utf-8'))
        except Exception:
            response.status_code = 400
            response.text = json.dumps({'error': 'Некорректный JSON'}, ensure_ascii=False)
            response.content_type = 'application/json'
            return response

        name = (data.get('name') or '').strip()
        text = (data.get('text') or '').strip()

        if len(name) < 3 or len(text) < 10:
            response.status_code = 422
            response.text = json.dumps({'error': 'Название должно быть ≥ 3 символов, текст ≥ 10 символов'}, ensure_ascii=False)
            response.content_type = 'application/json'
            return response

        image_name = None
        image_base64 = data.get('image_base64')
        image_filename = data.get('image_filename') or 'image.png'

        if image_base64:
            try:
                # Безопасное отсечение Data URL заголовка (например, "data:image/png;base64,")
                if ',' in image_base64:
                    image_base64 = image_base64.split(',', 1)[1]
                
                image_data = base64.b64decode(image_base64)
                image_name = safe_filename(image_filename)
                dest_path = os.path.join(UPLOAD_DIR, image_name)
                
                with open(dest_path, 'wb') as out:
                    out.write(image_data)
            except Exception as e:
                response.status_code = 400
                response.text = json.dumps({'error': f'Ошибка изображения: {str(e)}'}, ensure_ascii=False)
                response.content_type = 'application/json'
                return response

        article = Article()
        article.set_author_id(1)
        article.set_name(name)
        article.set_text(text)
        article.set_image(image_name)
        article.save()

        response.status_code = 201
        response.content_type = 'application/json'
        response.text = json.dumps({'success': True, 'article': article.to_dict()}, ensure_ascii=False)
        return response

    def api_edit(self, request, response, id):
        """Редактирование статьи через API."""
        article = Article.get_by_id(id)
        if article is None:
            response.status_code = 404
            response.text = json.dumps({'error': 'Статья не найдена'}, ensure_ascii=False)
            response.content_type = 'application/json'
            return response

        try:
            data = json.loads(request.body.decode('utf-8'))
        except Exception:
            response.status_code = 400
            response.text = json.dumps({'error': 'Некорректный JSON'}, ensure_ascii=False)
            response.content_type = 'application/json'
            return response

        if 'name' in data:
            article.set_name(data['name'].strip())
        if 'text' in data:
            article.set_text(data['text'].strip())

        image_base64 = data.get('image_base64')
        image_filename = data.get('image_filename') or 'image.png'

        if image_base64:
            try:
                if ',' in image_base64:
                    image_base64 = image_base64.split(',', 1)[1]
                
                image_data = base64.b64decode(image_base64)
                image_name = safe_filename(image_filename)
                dest_path = os.path.join(UPLOAD_DIR, image_name)
                
                with open(dest_path, 'wb') as out:
                    out.write(image_data)
                
                article.set_image(image_name)
            except Exception as e:
                response.status_code = 400
                response.text = json.dumps({'error': f'Ошибка изображения: {str(e)}'}, ensure_ascii=False)
                response.content_type = 'application/json'
                return response

        article.save()
        response.content_type = 'application/json'
        response.text = json.dumps({'success': True, 'article': article.to_dict()}, ensure_ascii=False)
        return response

    def api_delete(self, request, response, id):
        """Удаление статьи через API."""
        if request.method not in ['POST', 'DELETE']:
            response.status_code = 405
            response.text = json.dumps({'error': 'Метод не поддерживается'}, ensure_ascii=False)
            response.content_type = 'application/json'
            return response

        article = Article.get_by_id(id)
        if article is None:
            response.status_code = 404
            response.text = json.dumps({'error': 'Статья не найдена'}, ensure_ascii=False)
            response.content_type = 'application/json'
            return response

        if article.get_image():
            old_image_path = os.path.join(UPLOAD_DIR, article.get_image())
            if os.path.exists(old_image_path):
                os.remove(old_image_path)

        article.delete()
        response.content_type = 'application/json'
        response.text = json.dumps({'success': True, 'message': 'Статья успешно удалена'}, ensure_ascii=False)
        return response