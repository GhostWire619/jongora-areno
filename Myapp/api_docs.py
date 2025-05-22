"""
API documentation tools for ArenoApp
This module provides utilities to automatically document all URLs in the application.
"""
from django.urls import get_resolver, URLPattern, URLResolver
from django.conf import settings

def get_all_urls(urlpatterns=None, prefix=''):
    """
    Recursively get all URL patterns and their names.
    Returns a list of (url_pattern, url_name, view_func) tuples.
    """
    if urlpatterns is None:
        urlpatterns = get_resolver().url_patterns
    
    urls = []
    for pattern in urlpatterns:
        if isinstance(pattern, URLPattern):
            # Get the URL pattern, name, and view function
            url = prefix + str(pattern.pattern)
            name = pattern.name or ''
            view_func = pattern.callback
            urls.append((url, name, view_func))
        
        elif isinstance(pattern, URLResolver):
            # Recursively get patterns from included URLs
            new_prefix = prefix + str(pattern.pattern)
            urls.extend(get_all_urls(pattern.url_patterns, new_prefix))
    
    return urls

def categorize_url(url):
    """
    Determine the category of a URL based on its pattern.
    Returns a category name string.
    """
    if url.startswith('/api/'):
        return 'API'
    elif any(s in url for s in ['/product', '/shop', '/cart', '/brand']):
        return 'Shopping'
    elif any(s in url for s in ['/restaurant', '/meal', '/food']):
        return 'Restaurants'
    elif any(s in url for s in ['/booking', '/event', '/sport', '/adventure', '/car_rental', '/arenobnb']):
        return 'Booking'
    elif any(s in url for s in ['/admin', '/dashboard']):
        return 'Admin'
    elif any(s in url for s in ['/register', '/login', '/user', '/profile', '/account']):
        return 'User Management'
    else:
        return 'Others'

def get_categorized_urls():
    """
    Get all URLs categorized by section.
    Returns a dictionary with categories as keys and lists of URLs as values.
    """
    all_urls = get_all_urls()
    categorized = {}
    
    for url, name, _ in all_urls:
        category = categorize_url(url)
        if category not in categorized:
            categorized[category] = []
        
        categorized[category].append({
            'url': url,
            'name': name
        })
    
    return categorized

def generate_swagger_paths():
    """
    Generate OpenAPI paths for all URLs in the application.
    Returns a dictionary of paths compatible with OpenAPI specifications.
    """
    all_urls = get_all_urls()
    paths = {}
    
    for url, name, view_func in all_urls:
        # Convert URL pattern to OpenAPI path format
        # e.g., convert /<int:id>/ to /{id}/
        openapi_path = url.replace('<int:', '{').replace('<str:', '{').replace('>', '}')
        
        # Skip media, static, and debug paths
        if any(p in openapi_path for p in ['media', 'static', '__debug__']):
            continue
        
        # Get view docstring for description
        docstring = view_func.__doc__ or ''
        description = docstring.strip()
        
        # Create OpenAPI path object
        if openapi_path not in paths:
            paths[openapi_path] = {}
        
        # Determine HTTP methods
        methods = ['get']  # Default to GET
        if hasattr(view_func, 'actions'):
            methods = list(view_func.actions.keys())
        
        for method in methods:
            paths[openapi_path][method.lower()] = {
                'tags': [categorize_url(url)],
                'summary': name or openapi_path,
                'description': description,
                'responses': {
                    '200': {
                        'description': 'Successful operation'
                    }
                }
            }
    
    return paths 