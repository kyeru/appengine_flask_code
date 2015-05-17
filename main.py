from flask import Flask
app = Flask(__name__)
app.config['DEBUG'] = True
app.Debug = True

# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.


@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""
    return 'Hello World?'

@app.route('/test/')
def test_page():
    page_header = '<head>test page</head>'
    page_content = '<body><h1>App engine + Flask test</h1></body>'
    page_content += '<p>this is test paragraph</p>'
    page_footer = ''
    page = '<html>' + \
           page_header + \
           page_content + \
           '</html>'
    return page

@app.route('/user/<username>')
def user_page(username):
    return 'Hello, %s' % username

@app.route('/post/<int:post_id>')
def postid_page(post_id):
    return 'Post %d' % post_id

@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, nothing at this URL.', 404
