from models.active_record_entity import ActiveRecordEntity
from models.user import User

class Article(ActiveRecordEntity):
    # __tablename__ = 'articles'

    
    _author_id = None
    __author__ = None
    _name = None
    _text = None
    _create_at = None



    def get_author(self):
        return User.get_by_id(self._id)
    
    def get_author_id(self):
        return self._author_id
    
    def get_name(self):
        return self._name

    def get_text(self):
        return self._text

    def get_create_at(self):
        return self._create_at
    
    def set_author_id(self, author_id):
        self._author_id = author_id
    
    def set_name(self, name):
        self._name = name

    def set_text(self, text):
        self._text = text

    # def set_create_at(self, create_at):
    #     self._create_at = create_at

    @staticmethod
    def get_table_name():
        return 'articles'

    @staticmethod
    def search_by_name(search_string):
        return __class__.search('name', search_string)
