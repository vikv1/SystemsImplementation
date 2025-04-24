from flask import Flask, request, redirect, url_for, render_template
from URLShortener import URLShortener

app = Flask(__name__)
url_shortener = URLShortener()

@app.route('/')
def index():
    return render_template('index.html')
    
@app.route('/shorten', methods=['POST'])
def shorten():
    long_url = request.form['long_url']
    short_url = url_shortener.shorten(long_url)
    return render_template('index.html', short_url=short_url)

@app.route('/<short_url>')
def redirect_to_long_url(short_url):
    long_url = url_shortener.redirect(short_url)
    if long_url is None:
        return "URL not found", 404
    return redirect(long_url)

if __name__ == '__main__':
    app.run(debug=True)