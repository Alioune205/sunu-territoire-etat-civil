import os
import django
import sys
from django.core.management import call_command
from io import StringIO

sys.path.append(r"c:\Users\HP\Documents\Institut_Supérieur_d'enseignement_professionnelle_(ISEP)\Hackathon\backend")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

out = StringIO()
call_command('show_urls', stdout=out)
print(out.getvalue())
