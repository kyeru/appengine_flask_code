from flask import url_for, render_template, redirect, session

def style_url():
    return url_for('static', filename = 'style.css')

def get_user_id():
    if 'user_id' in session:
        return session['user_id']
    else:
        return None

def render_page(template, **args):
    return render_template(template,
                           style_url = style_url(),
                           user_id = get_user_id(),
                           **args)

def default_page():
    user_id = None
    if 'user_id' in session:
        user_id = session['user_id']
    return render_page('base.html')

def error_page(message, return_to, **args):
    return render_page('error.html',
                       message = message,
                       next_url = url_for(return_to, **args))
