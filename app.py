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
from models import *  # noqa

tornado.options.define(
    "http_port",
    default=8000,
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


class ShopSearchHandler(tornado.web.RequestHandler):
    def initialize(self, *args, **kwargs):
        print 'args', args
        print 'kwargs', kwargs

    def get(self):
        self.write(self.__class__.__name__)


class ShopShowHandler(tornado.web.RequestHandler):
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


class IndexHandler(tornado.web.RequestHandler):
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


class FlowHandler(tornado.web.RequestHandler):
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


class ErrorHandler(tornado.web.RequestHandler):
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


class UploadHandler(tornado.web.RequestHandler):
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


class RewriteHandler(tornado.web.RequestHandler):
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
        tornado.web.url(r"/upload", UploadHandler, name='upload'),
        (r"/flow", FlowHandler),
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
        http_server = tornado.httpserver.HTTPServer(app)
        if 0:
            http_server.listen(options.http_port)
        else:
            http_server.bind(options.http_port)
            http_server.start(num_processes=options.http_processes)
    else:
        app.listen(options.http_port)
    tornado.ioloop.IOLoop.current().start()
