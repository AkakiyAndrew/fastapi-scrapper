from urllib.parse import urlparse


STATIC_TYPES = (
    ".js", ".css", ".json", ".txt",
    ".jpeg", ".jpg", ".png", ".gif", ".ico", ".swf", ".svg", ".webp", 
    ".gz", ".rar", ".bzip", 
    ".pdf", ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx", ".odt", ".ods", ".odp", ".rtf",
    ".ttf", ".woff", ".woff2", ".otf", ".htc", ".eot"
)

def get_resource_type(url):
    if url.endswith(STATIC_TYPES):
        return "static"
    else:
        return "other"

def get_domain(url):
    parsed_url = urlparse(url)
    domain_parts = parsed_url.netloc.split('.')
    if len(domain_parts) >= 2:
        return '.'.join(domain_parts[-2:])
    return None

def strip_url(url):
    return url.split('?')[0].split('#')[0]