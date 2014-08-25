import os
import sys
sys.path.append('/home/azureuser/')
sys.path.append('/home/azureuser/infoneigeapi/')
sys.path.append('/home/azureuser/infoneigapie/infoneige/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'infoneige.settings'
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
