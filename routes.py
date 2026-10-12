from controller.site_controller import SiteController
from controller.article_controller import ArticlesController
from controller.users_controller import UsersController

routes = {
    # ---------- Статьи ----------
    r"^/articles/add$"          : [ArticlesController, ArticlesController.add],
    r"^/articles/search$"       : [ArticlesController, ArticlesController.search],
    r"^/articles/(\d+)/edit$"   : [ArticlesController, ArticlesController.edit],
    r"^/articles/(\d+)/delete$" : [ArticlesController, ArticlesController.delete],
    r"^/articles/(\d+)$"        : [ArticlesController, ArticlesController.view],
    r"^/articles$"              : [ArticlesController, ArticlesController.index],

    # ---------- Пользователи ----------
    r"^/user/register$" : [UsersController, UsersController.sign_up],
    r"^/user/login$"    : [UsersController, UsersController.sign_in],
    r"^/user/logout$"   : [UsersController, UsersController.logout],

    # ---------- Сайт ----------
    r"^/home$"          : [SiteController, SiteController.index],
    r"^/about$"         : [SiteController, SiteController.about],
    r"^/hello/(.*)$"    : [SiteController, SiteController.hello],
}