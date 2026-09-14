from views.view import View
from models.user_auth_service import UserAuthService

class Controller:
    def __init__(self, request):
        self.layout = "default"
        self.view = View(self.layout)
        token = request.cookies['token'] if 'token' in request.cookies else ''
        self.user = UserAuthService.get_user_by_token(token)
        self.view.set_var('user', self.user)
