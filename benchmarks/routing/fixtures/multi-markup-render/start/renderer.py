from html import escape

def render(title, body):
    return f'<h1>{escape(title)}</h1><p>{body}</p>'
