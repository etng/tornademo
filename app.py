# coding:utf-8
import tornado
import tornado.web
import tornado.ioloop
import tornado.options
import tornado.httpserver
import settings
import json
import os
import sys
import shutil
from models import *  # noqa
settings.web['login_url'] = settings.LOGIN_URL

tornado.options.define(
    "http_port",
    default=8000,
    type=int,
    help="run server on the given port."
)
tornado.options.define(
    "https_port",
    default=8443,
    type=int,
    help="run server on the given port."
)
tornado.options.define(
    "http_processes",
    default=0,
    type=int,
    help="run server on the given port."
)
tornado.options.define(
    "modules",
    default=[],
    type=str,
    multiple=True,
    help="enabled modules"
)


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        user_cookie = self.get_secure_cookie("user")
        # import ipdb;ipdb.set_trace()
        if user_cookie:
            return json.loads(user_cookie)
        return None


class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie('user')
        return self.redirect('/')


class LoginHandler(BaseHandler):
    def initialize(self, *args, **kwargs):
        print 'args', args
        print 'kwargs', kwargs

    def get(self):
        # print 'next url:', self.get_query_argument("next", '/')
        # self.write(self.__class__.__name__)
        self.render(
            'login.html',
            ui=settings.ui,
            settings=settings,
        )

    def post(self):
        username = self.get_body_argument('username', '')
        password = self.get_body_argument('password', '')
        if username == password:
            # import ipdb;ipdb.set_trace()
            self.set_secure_cookie('user', json.dumps(username), expires_days=0.2)
            return self.redirect(self.get_query_argument("next", '/'))
        else:
            self.redirect(self.settings.login_url)



class ShopSearchHandler(BaseHandler):
    def initialize(self, *args, **kwargs):
        print 'args', args
        print 'kwargs', kwargs

    def get(self):
        self.write(self.__class__.__name__)


class ShopShowHandler(BaseHandler):
    def initialize(self, *args, **kwargs):
        print 'args', args
        print 'kwargs', kwargs

    def get(self):
        self.write(self.__class__.__name__)
        shop_id = self.get_query_argument('id')
        self.write('shop_id: {}'.format(shop_id))
        try:
            missing_arg = self.get_argument("x")
        except tornado.web.MissingArgumentError as e:
            missing_arg = "We catched the MissingArgumentError!"
            print e, missing_arg

        for field in 'method host uri path query version headers body remote_ip'.split():
            print field, getattr(self.request, field)


class IndexHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        if not settings.use_template:
            # import ipdb;ipdb.set_trace()
            # print 'hello world:', self.get_arguments()
            self.write("Hello world!")
            links = []
            links.append('<a href="{}">{}</a>'.format(self.reverse_url('advance_search'), 'Advanced Search'))
            links.append('<a href="{}">{}</a>'.format(self.reverse_url('simple_search'), 'Simple Search'))
            links = map(lambda _: '<li>{}</li>'.format(_), links)
            links.insert(0, '<ul>')
            links.append('</ul>')
            self.write("\n".join(links))
            return

        runtime = {
            'tornado_version': tornado.version,
            'python_path': sys.executable,
            'python_version': '{major}.{minor}.{micro}({releaselevel})'.format(
                **{
                    x: getattr(sys.version_info, x)
                    for x in dir(sys.version_info)
                    if not x.startswith('_')
                }
            ),
        }
        runtime['os'] = dict(zip(
            'sysname nodename release version machine'.split(),
            os.uname(),
        ))
        self.render(
            'index.html',
            ui=settings.ui,
            settings=settings,
            runtime=runtime,
            latest_posts=Post.objects,
        )


class GalleryHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        def format_image(filename):
            return os.path.basename(os.path.dirname(filename)), '/{}'.format(filename)
        per_page = 16
        cur_page = int(self.get_query_argument('page', 0))
        data_file = os.path.join(settings.BASE_DIR, 'data/gallery_files.json')
        images = json.load(open(data_file))
        item_cnt = len(images)
        page_cnt = item_cnt / per_page
        if item_cnt % per_page:
            page_cnt += 1
        cur_page = max(1, min(cur_page, page_cnt))
        offset = (cur_page - 1) * per_page
        self.render(
            'gallery.html',
            ui=settings.ui,
            settings=settings,
            items=map(format_image, images[offset:offset + per_page]),
            per_page=per_page,
            page_cnt=page_cnt,
            cur_page=cur_page,
            offset=offset,
            item_cnt=item_cnt
        )


class DeleteImageHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        # import ipdb;ipdb.set_trace()
        image = self.get_body_argument('image').lstrip('/')
        trash_path = os.path.join(settings.web['media_path'], 'trash')
        dest_path = os.path.join(trash_path, image)
        dest_parent = os.path.dirname(dest_path)
        os.path.exists(dest_parent) or os.makedirs(dest_parent, 0777)
        shutil.move(os.path.join(settings.BASE_DIR, image), dest_path)
        self.write(dict(status=True, message='deleted'))


class FlowHandler(BaseHandler):
    def get(self):
        self.write(self.__class__.__name__)
        import random
        if random.randint(0, 1):
            self.send_error(200)

    def initialize(self):
        print 'initialize'

    def prepare(self):
        print 'prepare'

    def set_default_headers(self):
        print 'set_default_headers'

    def write_error(self, status_code, **kwargs):
        print 'write_error'

    def on_finish(self):
        print 'on_finish'


class ErrorHandler(BaseHandler):
    def get(self, code):
        code = int(code)
        self.send_error(
            code,
            content="error code {}".format(code),
            email='etng2004@gmail.com',
        )

    def write_error(self, status_code, **kwargs):
        self.write(u"<h1>Error Status {}</h1>".format(status_code))
        self.write(u'<pre>{}</pre>'.format(
            json.dumps(kwargs, indent=2)
        ))


class UploadHandler(BaseHandler):
    def get(self):
        self.write('curl -i -L -F img=@avatar.png localhost:8000/upload')

    def post(self):
        files = self.request.files
        if not files:
            self.redirect("/upload")
            return
        save_to = 'media/upload/'
        os.path.exists(save_to) or os.makedirs(save_to)
        for img_file in files.get('img'):
            file = open(os.path.join(save_to, img_file['filename']), 'w+')
            file.write(img_file['body'])
            file.close()
        self.write("OK")


class RewriteHandler(BaseHandler):
    def set_default_headers(self):
        self.set_header("x-powered-by", "Tornademo")

    def get(self, *args, **kwargs):
        fmt = 'text'
        try:
            fmt = self.get_argument('fmt')
        except:
            pass
        self.set_header("respond_type", fmt)
        if fmt == 'text':
            self.write(self.__class__.__name__)
            self.write('args:{}'.format(args))
            self.write('kwargs:{}'.format(kwargs))
        elif fmt == 'json':
            self.write({
                'name': self.__class__.__name__,
                'args': args,
                'kwargs': kwargs,
            })
        self.set_status(256, 'customized status header')


if __name__ == "__main__":
    app = tornado.web.Application([
        (r'^/html/(.*)$', tornado.web.StaticFileHandler, {
                "path": os.path.join(settings.BASE_DIR, "static/html"),
                "default_filename":"index.html",
            }
        ),
        (r'^/media/(.*)$', tornado.web.StaticFileHandler, {
                "path": os.path.join(settings.BASE_DIR, "media"),
                "default_filename":"index.html",
            }
        ),
        (r"/", IndexHandler),
        (r"/logout", LogoutHandler),
        (settings.LOGIN_URL, LoginHandler),
        tornado.web.url(r"/upload", UploadHandler, name='upload'),
        (r"/flow", FlowHandler),
        tornado.web.url(r"/gallery", GalleryHandler, name="gallery"),
        (r"/del-image", DeleteImageHandler),
        (r"/error/(\d+)", ErrorHandler),
        (r"/rewrite_k/(\d+)/(.*)", RewriteHandler),
        (r"/rewrite_n/(?P<id>\d+)/(?P<action>.*)", RewriteHandler),
        (r"/view", ShopShowHandler, {'compact': False}),
        tornado.web.url(r"/search/advanced", ShopSearchHandler, {"mode": 'advanced'}, name='advance_search'),
        tornado.web.url(r"/search/simple", ShopSearchHandler, {"mode": 'simple'}, name='simple_search'),
    ], **settings.web)
    tornado.options.parse_command_line()
    options = tornado.options.options

    # autoreload is incompatible with multi-process mode. When autoreload is enabled you must run only one process.
    # Setting 'debug=True' will enables this setting (autoreload=True) too
    if settings.web.get('debug', False):
        options.http_processes = 1
    print 'listen on {} with {} processes'.format(
        options.http_port,
        options.http_processes if options.http_processes else 'max'
    )
    print 'enabled {} modules: {}'.format(
        len(options.modules),
        ",".join(options.modules)
    )
    if 1:
        ssl_options = {
            "certfile": "data/https/ca.csr",
            "keyfile": "data/https/ca.key",
        }
        ssl_options = None
        http_server = tornado.httpserver.HTTPServer(app, ssl_options=ssl_options)
        if 0:
            http_server.listen(options.http_port)
            http_server.listen(options.https_port)
        else:
            http_server.bind(options.http_port)
            http_server.bind(options.https_port)
            http_server.start(num_processes=options.http_processes)
    else:
        app.listen(options.http_port)
    tornado.ioloop.IOLoop.current().start()
