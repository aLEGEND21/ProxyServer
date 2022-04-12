import requests
from bs4 import BeautifulSoup
from flask import Flask
from flask_session import Session
from urllib.parse import urljoin
from flask import request
from flask import session


app = Flask(__name__)
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)


@app.route("/<website_url>")
def home(website_url):
    if website_url == "":
        website_url = "https://www.google.com"

    if website_url.startswith("http://") or website_url.startswith("https://"):
        session["website_url"] = website_url
    else:
        website_url = "https://" + website_url
        session["website_url"] = website_url
    
    html = get_absolute_url(session["website_url"])
    return html

    """website_link = "https://google.com"
    session["website_link"] = website_link
    sess = requests.session()
    sess.headers["User-Agent"] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
    html = sess.get(website_link).content
    soup = BeautifulSoup(html, "html.parser")"""
    

    """for script in soup.find_all("script"):
        if script.has_attr("src"):
            src = script.get("src")
            if src.startswith("/"):
                script["src"] = urljoin(website_link, src)
    
    for stylesheet in soup.find_all("link", {"rel": "stylesheet"}):
        if stylesheet.has_attr("href"):
            href = stylesheet.get("href")
            if "://" not in href:
                stylesheet["href"] = urljoin(website_link, href)"""
    
    """for link in soup.find_all("a"):
        if link.get("href") is not None:
            if link.get("href").startswith("http://"):
                link["href"] = "/" + link["href"]
            elif link.get("href").startswith("https://"):
                link["href"] = "/" + link["href"]"""
    
    #return str(soup)

@app.errorhandler(404)
def page_not_found(e):
    query_url = request.url[len(request.host_url):]
    if query_url.startswith("http") or query_url.startswith("https"):
        session["website_link"] = query_url
        html = get_absolute_url(query_url)
    else:
        html = get_absolute_url(urljoin(session["website_link"], query_url))
    return html

def get_absolute_url(url):
    sess = requests.session()
    sess.headers["User-Agent"] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
    try:
        html = sess.get(url).content
    except requests.exceptions.ConnectionError:
        html = "<h1>A Connection Error Occured. Please Try Again Later</h1>"
    html = str(clean_page_content(html, url))
    return html

def clean_page_content(html, query_url):
    soup = BeautifulSoup(html, "html.parser")

    # Convert relative stylesheet paths to absolute ones pointing to the query_url
    for stylesheet in soup.find_all("link", {"rel": "stylesheet"}):
        if stylesheet.has_attr("href"):
            href = stylesheet.get("href")
            if "://" not in href:
                stylesheet["href"] = urljoin(query_url, href)
    
    # Replace all links to external webpages as links to other pages in the server
    for link in soup.find_all("a"):
        if link.get("href") is not None:
            if link.get("href").startswith("http://") and request.host_url not in link.get("href"):
                link["href"] = request.host_url + link["href"]
            elif link.get("href").startswith("https://") and request.host_url not in link.get("href"):
                link["href"] = request.host_url + link["href"]
            if link.get("href").startswith("/"):
                link["href"] = f"{request.host_url}/{link['href']}"
    
    return soup


if __name__ == "__main__":
    app.run(debug=True)