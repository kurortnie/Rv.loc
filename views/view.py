import os
from jinja2 import Environment, FileSystemLoader

class View:
    def __init__(self, layout):
        self.layout = layout
        self.extra_vars = {}
        self.env = Environment(loader=FileSystemLoader('views'), autoescape=(["html","xml"]))

    def render_html(self, view_name, vars = {}):
        layout_file = f"layouts/{self.layout}.html"
        file_vars = {"content" : view_name}
        file_vars.update(vars)
        file_vars.update(self.extra_vars)
        template = self.env.get_template(layout_file)
        return template.render(file_vars)
    
    def set_var(self, name, value):
        self.extra_vars[name] = value