import requests
from bs4 import BeautifulSoup
from flask import Flask
from flask_session import Session
from urllib.parse import urljoin
from urllib.parse import urlparse
from flask import request
from flask import session

from config import Config


app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)


@app.errorhandler(404)
def page_not_found(e):
    url = request.url[len(request.host_url):]

    # Set the url to google.com if there was no url provided
    if url == "":
        url = "https://google.com"

    """# Set the main page url to the current url if it is a complete url
    if url.startswith("http://") or url.startswith("https://"):
        session["query_url"] = url
        session["domain"] = "https://" + urlparse(url).netloc + "/" # TODO: This should be http or https based on the actual url
        query_url = url
    # Otherwise, add the main page url to the incomplete url to get the query url
    else:
        query_url = urljoin(session.get("query_url"), "/" + url)
    
    # Make the query and get all page contents
    html = get_page_contents(query_url)

    # Return the html
    return html"""

    # Fix urls that don't have :// after http(s)
    if url.startswith("http:/"):
        if url[6] != "/":
            url = url.replace("http:/", "http://")
    elif url.startswith("https:/"):
        if url[7] != "/":
            url = url.replace("https:/", "https://")

    # Set the main page url to the current url if it is a complete url
    if url.startswith("http:/") or url.startswith("https:/"): # Also allows https:/ and http:/ urls
        session["query_url"] = url
        # TODO: Make the domain http or https based on which one it is
        if urlparse(url).netloc.startswith("www."):
            session["domain"] = "https://" + urlparse(url).netloc + "/"
        else:
            session["domain"] = "https://www." + urlparse(url).netloc + "/"
        print(session["domain"])
        query_url = url
    # Otherwise, add the main page url to the incomplete url to get the query url
    else:
        query_url = urljoin(session.get("query_url") + "/", url)
        print(query_url)
        print(query_url == "https://www.microsoft.com/en-us/d/surface-pro-7-and-surface-pro-type-cover-bundle/8s6t3hp3ct18")
    
    # Make the request and get the page contents
    content = get_page_contents(query_url)

    # Try to decode the bytes object into a string. If there is an error, then just return the 
    # bytes object to the user. Otherwise, clean the page contents and return it
    try: 
        content = bytes.decode(content)
    except UnicodeDecodeError:
        print("Error Decoding Bytes")
        return content
    else:
        clean_content = clean_page_contents(content)
        return clean_content


def get_page_contents(url):
    sess = requests.session()
    sess.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36"
    content = sess.get(url).content
    return content


def clean_page_contents(content):
    # Load the page contents into BeautifulSoup
    soup = BeautifulSoup(content, "html.parser")
    
    # Replace all relative <link> links with domain + relative link
    for link in soup.find_all("link"):
        # Replace all relative links to stylesheets with the domain + relative link
        if link.get("rel") == "stylesheet":
            if not link["href"].startswith("http"): # Check if it is not an absolute link
                link["href"] = urljoin(session.get("domain"), link["href"])
        # Replace other links with domain + relative link
        elif link.get("href") is not None:
            if not link["href"].startswith("http"): # Check if it is not an absolute link
                link["href"] = urljoin(session.get("domain"), link["href"])
    
    # Replace all links that are directing to the actual page with the webserver's links
    for self_link in soup.find_all(text=session.get("domain")):
        fixed_link = self_link.replace(session.get("domain"), f"{request.host_url}/{session.get('domain')}")
        soup.replace_with(fixed_link)

    # Replace all relative img links with absolute ones
    for img in soup.find_all("img"):
        if img.get("src") is not None:
            if not img.get("src").startswith("http"):
                img["src"] = urljoin(session.get("domain"), img["src"])
        # If an srcset exists, replace all relative links with absolute ones
        if img.get("srcset") is not None:
            srcset = img.get("srcset").split(" ")
            for src in srcset: # Iterate through all the links in the srcset
                if src.startswith("/"):
                    srcset[srcset.index(src)] = urljoin(session.get("domain"), src)
            img["srcset"] = " ".join(srcset)
    
    # Replace external <a> links. This must be done last as the return type is a string
    soup = replace_all_links(str(soup))

    # Return the parsed html
    return str(soup)


def replace_all_links(html):
    """Replaces all absolute <a> links to other pages in the html with links directing to other
    pages in the webserver. Ex: "https://www.google.com" -> 127.0.0.1/https://www.google.com

    Args:
        html (str): The byte-decoded html string to be parsed.

    Returns:
        str: The fully parsed html.
    """
    soup = BeautifulSoup(html, "html.parser")
    # Replace all absolute <a> links to other sub-pages in the html with relative links
    for a in soup.find_all("a"):
        if a.get("href") is not None: # Check for href attr
            if a["href"].startswith("http"): # Check if it is an absolute link
                a["href"] = urljoin(request.host_url, "/" + a["href"])
    return str(soup)


if __name__ == "__main__":
    app.run(debug=Config.DEBUG, host=Config.SERVER)


# TODO: Fix the issue on first found on Microsoft's store, where a 404 error is given when clicking
# on a specific product. This is likely because the domain is not saved correctly, which is why when
# it is attached to the relative url, there is a 404 error.