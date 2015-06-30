from flask import url_for, render_template, session
from mymodules.user import *

def style_url():
    return url_for('static', filename = 'style.css')

def render_page(template, **args):
    return render_template(template,
                           style_url = style_url(),
                           user_id = get_user_id(),
                           **args)

def default_page():
    return render_page('base.html')

def error_page(message, return_to, **args):
    return render_page('error.html',
                       message = message,
                       next_url = url_for(return_to, **args))

def under_construction():
    return render_page('error.html',
                       message = 'Under Construction')
