import os
import django
import sys
from django.urls import get_resolver

sys.path.append(r"c:\Users\HP\Documents\Institut_Supérieur_d'enseignement_professionnelle_(ISEP)\Hackathon\backend")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

def get_urls(url_patterns, prefix=''):
    urls = []
    for pattern in url_patterns:
        if hasattr(pattern, 'url_patterns'):
            urls.extend(get_urls(pattern.url_patterns, prefix + str(pattern.pattern)))
        else:
            urls.append(prefix + str(pattern.pattern))
    return urls

urls = get_urls(get_resolver().url_patterns)
for u in urls:
    print('/' + u)
