from flask import url_for, render_template, redirect

def style_url():
    return url_for('static', filename = 'style.css')

def error_page(message, return_to, **args):
    return render_template('error.html',
                           style_url = style_url(),
                           message = message,
                           next_url = url_for(return_to, **args))
