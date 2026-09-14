

def home(request, response):
    response.text = "Привет с главной страницы"


def about(request, response):
    response.text = "Привет со страницы about"


def articles(request, response):
    response.text = "Это страница со статьями"
