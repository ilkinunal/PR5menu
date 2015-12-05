import webapp2
import jinja2
import os
import time
from google.appengine.ext import ndb


template_dir = os.path.join(os.path.dirname(__file__), 'notes')
JINJA_ENVIRONMENT = jinja2.Environment( loader=jinja2.FileSystemLoader(template_dir),
    extensions=['jinja2.ext.autoescape'], autoescape=True)


class Handler(webapp2.RequestHandler):
    """
    Basic Handler; will be inherited by more specific path Handlers
    """
    def write(self, *a, **kw):
        "Write small strings to the website"
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        "Render jinja2 templates"
        t = JINJA_ENVIRONMENT.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        "Write the jinja template to the website"
        self.write(self.render_str(template, **kw))

class MainHandler(Handler):
    def get(self):
        self.render("menu.html")

class UserComment(ndb.Model):
    user = ndb.StringProperty()
    comment = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)

    def user_key(user):
        return ndb.Key('User', user)

    def comment_key(comment):
        return ndb.Key('Comment', comment)

class CommentsHandler(Handler):
    def get(self):
        error = self.request.get('error','')
        query = UserComment.query().order(UserComment.date)
        max_posts_to_fetch = 20
        usercomment_list = query.fetch(max_posts_to_fetch)

        self.render("content.html",
            usercomments = usercomment_list)

    def post(self):
        user = self.request.get('user')
        comment = self.request.get('comment')

        if comment.lstrip():
            usercomments = UserComment(user=user, comment=comment)
            usercomments.put()
            time_to_wait = .1
            time.sleep(time_to_wait)
            self.redirect('/')
        else:
            self.response.out.write('Please fill out the name and comment sections!')

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/', CommentsHandler)
], debug=True)