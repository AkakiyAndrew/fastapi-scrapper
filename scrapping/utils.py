from urllib.parse import urlparse, urljoin

NON_STATIC_TYPES = (
    "/", ".html", ".htm", "index.php"
)

STATIC_TYPES = (
    ".js", ".css", ".json", ".txt", ".php",
    ".jpeg", ".jpg", ".png", ".gif", ".ico", ".swf", ".svg", ".webp", 
    ".gz", ".rar", ".bzip", 
    ".pdf", ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx", ".odt", ".ods", ".odp", ".rtf",
    ".ttf", ".woff", ".woff2", ".otf", ".htc", ".eot"
)

def get_resource_type(url):
    url_path = urlparse(url).path

    if url_path.endswith(NON_STATIC_TYPES):
        return "other"
    
    if url_path.endswith(STATIC_TYPES):
        return "static"
    else:
        return "other"

def get_url_domain(url):
    parsed_url = urlparse(url)
    return parsed_url.netloc

def strip_url(url):
    return url.split('?')[0].split('#')[0]

def prepare_url(url, domain):
    if not url.startswith('http'):
        return urljoin(domain, url)
    return url