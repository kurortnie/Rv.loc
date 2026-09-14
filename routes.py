from controller.site_controller import SiteController
# from controller.TestController import TestController
from controller.article_controller import ArticlesController
from controller.users_controller import UsersController

routes = {
    # "/home" :  [SiteController, SiteController.index],
    # "/about" :  [SiteController, SiteController.about],
    # "/test" :  [TestController, TestController.test],
    # "/test-action" :  [TestController, TestController.action],

    r"^/articles/(\d+)/edit$" : [ArticlesController, ArticlesController.edit],
    r"^/articles/(\d+)$" : [ArticlesController, ArticlesController.view],
    r"^/articles/(\d+)/delete$" : [ArticlesController, ArticlesController.delete],
    r"^/articles$" : [ArticlesController, ArticlesController.index],
    r"^/articles/add$" : [ArticlesController, ArticlesController.add],
    r"^/user/register$" : [UsersController, UsersController.sign_up],
    r"^/user/login$" : [UsersController, UsersController.sign_in],
    r"^/user/logout$" : [UsersController, UsersController.logout],
    r"^/articles/search$" : [ArticlesController, ArticlesController.search],
    r"^/home$" : [SiteController, SiteController.index],
    r"^/about$" : [SiteController, SiteController.about],
    r"^/hello/(.*)$" : [SiteController, SiteController.hello],
    # r"^/users$" : [UsersController, UsersController.users],



    # Сделать чтобы /users - выдавало всех существующих user - их email, login
    
}