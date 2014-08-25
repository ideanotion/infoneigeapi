import os
import sys
sys.path.append('/home/azureuser/')
sys.path.append('/home/azureuser/infoneige/')
sys.path.append('/home/azureuser/infoneige/infoneige/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'infoneige.settings'
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
