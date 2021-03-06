import webapp2
import jinja2
import os
import logging

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)


def render_str(template, **params):
	'''
	create the jinja templating environment
	'''
	t = jinja_env.get_template(template)
	return t.render(params)


class BlogHandler(webapp2.RequestHandler):
	'''
	functions for rendering pages
	'''
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)
	def render_str(self, template, **params):
		return render_str(template, **params)
	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))
