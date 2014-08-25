from django.http import HttpResponse
from suds.client import Client
from datetime import datetime, timedelta
from suds import WebFault
from rest_framework_mongoengine.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView, RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import filters
from rest_framework.reverse import reverse
from rest_framework.decorators import api_view
from .serializers import *
from django.http import Http404, HttpResponseBadRequest
from django.core import serializers
from pyproj import Proj, transform
import json

@api_view(('GET',))
def api_root(request, format=None):
	return Response({
		'streets': reverse('Street-list', request=request, format=format),
		'street detail': reverse('Street-detail', args=['1381126'], request=request, format=format),
		'cotes': reverse('Cote-list', request=request, format=format),
		'cote detail': reverse('Cote-detail', args=['13811261'], request=request, format=format),
	})

class CoteList(ListAPIView):
	"""
	Returns a list of snow removal schedules in the Info-Neige system. For more details on the properties, please read Info-Neige offical documentation.
	
	Query Path:
	Use query path ?mode=plan|geo|full to return schedule, GeoJson or both
	To perform bounding box search, please specific two points  ?bbox=lon1,lat1,lon2,lat2.
	To change page size, set ?page_size=number.

	"""
   	paginate_by = 50
	paginate_by_param = 'page_size'
	max_paginate_by = 10000
	def get_serializer_class(self):
		mode = self.request.QUERY_PARAMS.get('mode', None)
		if mode == 'full':
			return CoteSerializer
		elif mode == 'plan':
			return CotePlanSerializer
		elif mode == 'geo':
			return CoteGeoSerializer
		else:
			return CotePlanSerializer

	#bounding box
	def get_queryset(self):
		query = self.request.QUERY_PARAMS.get('bbox', None)
		if query is not None:
			bbox = query.split(',')
			x0 = float(bbox[0])
			y0 = float(bbox[1])
			x1 = float(bbox[2])
			y1 = float(bbox[3])
			return Cote.objects.filter(Q(geometry__geo_intersects={"type": "Polygon","coordinates":[[[x0, y0],[x0, y1],[x1, y1],[x1, y0],[x0, y0]]]}))
		return Cote.objects.all()

class CoteDetails(RetrieveAPIView):
	serializer_class = CoteSerializer
	queryset = Cote.objects.all()
	def get_object(self):
		query_kwargs = self.get_query_kwargs()
		try:		
			return Cote.objects.get(coteRueId=query_kwargs['id'])
		except DoesNotExist:
			raise Http404

class StreetList(ListAPIView):
	"""
	Returns a list of streets in the Info-Neige system. For more details on the properties, please read Info-Neige offical documentation.
	
	Query Path:
	To change page size, set ?page_size=number.

	"""
	serializer_class = StreetSerializer
	queryset = Street.objects.all()
	paginate_by = 50
	paginate_by_param = 'page_size'
	max_paginate_by = 10000	

class StreetDetails(RetrieveAPIView):
	serializer_class = StreetSerializer
	queryset = Street.objects.all()
	def get_object(self):
		query_kwargs = self.get_query_kwargs()
		try:		
			return Street.objects.get(trcId=query_kwargs['id'])
		except DoesNotExist:
			raise Http404
			

def street_load(request):
	json_data = open('/var/www/static/resources/geobase.json')   
	jsonObject = json.load(json_data)
	#jsonObject = json.loads('{"name":"geobase","type":"FeatureCollection","crs":{"type":"name","properties":{"name":"EPSG:32188"}},"features":[{"type":"Feature","geometry":{"type":"LineString","coordinates":[[299490.642005,5041393.743],[299508.116,5041496.575],[299508.915015,5041507.075]]},"properties":{"A":"rue De Bullion","SUR":"rue Saint-Norbert","TRC_ID":1381126,"DE":"rue Saint-Dominique","SENS_CIR":-1}},{"type":"Feature","geometry":{"type":"LineString","coordinates":[[301268.173005,5042909.956],[301269.27799,5042916.772],[301280.90198,5042973.221],[301292.470985,5043018.074],[301340.140985,5043206.157]]},"properties":{"A":"rue DIberville","SUR":"rue Notre-Dame Est","TRC_ID":4009293,"DE":"rue Notre-Dame Est","SENS_CIR":1}}]}')
	src = Proj(init='epsg:32188')
	dest = Proj(init='epsg:4326')
	streets = []
	for feature in jsonObject['features']:
		for coord in feature['geometry']['coordinates']:
			x1,y1 = coord[0],coord[1]
			x2,y2 = transform(src,dest,x1,y1)
			coord[0] = x2
			coord[1] = y2
	
	for feature in jsonObject['features']:	
		try:
			street = Street.objects.get(trcId=feature['properties']['TRC_ID'])
			streets.append(street)
		except DoesNotExist:
			street = Street(geometry=feature['geometry'])
			street.trcId = feature['properties']['TRC_ID']
			street.properties = StreetProperties(A=feature['properties'].get('A', ''),SENS_CIR=feature['properties']['SENS_CIR'],DE=feature['properties'].get('DE', ''),SUR=feature['properties']['SUR'],TRC_ID=feature['properties']['TRC_ID'])
			street.save()
			streets.append(street)
	
	return HttpResponse('done')

def cote_load(request):
	json_data = open('/var/www/static/resources/cote.json')   
	jsonObject = json.load(json_data)
	#jsonObject = json.loads('{"name":"geobase","type":"FeatureCollection","crs":{"type":"name","properties":{"name":"EPSG:32188"}},"features":[{"type":"Feature","geometry":{"type":"LineString","coordinates":[[299490.642005,5041393.743],[299508.116,5041496.575],[299508.915015,5041507.075]]},"properties":{"A":"rue De Bullion","SUR":"rue Saint-Norbert","TRC_ID":1381126,"DE":"rue Saint-Dominique","SENS_CIR":-1}},{"type":"Feature","geometry":{"type":"LineString","coordinates":[[301268.173005,5042909.956],[301269.27799,5042916.772],[301280.90198,5042973.221],[301292.470985,5043018.074],[301340.140985,5043206.157]]},"properties":{"A":"rue DIberville","SUR":"rue Notre-Dame Est","TRC_ID":4009293,"DE":"rue Notre-Dame Est","SENS_CIR":1}}]}')
	src = Proj(init='epsg:32188')
	dest = Proj(init='epsg:4326')
	cotes = []
	for feature in jsonObject['features']:
		if feature['geometry'] is not None:
			for coord in feature['geometry']['coordinates']:
				x1,y1 = coord[0],coord[1]
				x2,y2 = transform(src,dest,x1,y1)
				coord[0] = x2
				coord[1] = y2
	
	for feature in jsonObject['features']:	
		try:
			cote = Cote.objects.get(coteRueId=feature['properties']['COTE_RUE_ID'])
			cotes.append(cote)
		except DoesNotExist:
			cote = Cote()
			cote.coteRueId = feature['properties']['COTE_RUE_ID']
			cote.street = Street.objects.get(trcId=feature['properties']['ID_TRC'])
			if (feature['geometry'] is None) or (feature['geometry']['type'] != 'LineString'):
				cote.geometry=cote.street.geometry
			else:
				cote.geometry=feature['geometry']
			cote.plan = Plan()
			cote.properties = CoteProperties(FIN_ADRESSE=feature['properties']['FIN_ADRESSE'],DEBUT_ADRESSE=feature['properties']['DEBUT_ADRESSE'],ORIENTATION_F=feature['properties'].get('ORIENTATION_F', ''),COTE_RUE_ID=feature['properties']['COTE_RUE_ID'],NOM_VOIE=feature['properties'].get('NOM_VOIE', ''),TYPE_F=feature['properties'].get('TYPE_F', ''),ARRONDISSEMENT=feature['properties'].get('ARRONDISSEMENT', ''),LIEN_F=feature['properties'].get('LIEN_F', ''),TRC_ID=feature['properties']['ID_TRC'])
			cote.save()
			cotes.append(cote)
	
	return HttpResponse('done')

def wsdl_load(request):
	url = 'https://servicesenligne2.ville.montreal.qc.ca/api/infoneige/InfoneigeWebService?wsdl'
	client = Client(url)
	print(client)
	request = client.factory.create('ns1:getPlanificationsForDate')

	print(request)	
	
	# have to figure out what value to put it, and adjust the timezone properly
	t1 = timedelta(-1,-0)
	request.fromDate = (datetime.now() + t1).strftime("%Y-%m-%dT%H:%M:%S")
	request.tokenString = 'ka71-8850723a-0c14-458f-9e51-94d943dcf39b-84876b3e-864e-4ad2-be96-7407a3ed2cc3-e0c86339-7d04-44b7-8e3a-7d782a2394ee-105362f7-b82e-41ec-84c6-08e5ef0970a7-7df45d79-9d11-4363-b59c-8abd4f50434d'
	try:
		response = client.service.GetPlanificationsForDate(request)		
		print(response)
		
		if not hasattr(response, 'planifications'):
			return HttpResponse('noupdate ' + str(response.responseStatus) + ' '  + response.responseDesc + ' ' + request.fromDate)
			
		for planification in response.planifications.planification:
			cote = Cote.objects.get(coteRueId=planification.coteRueId)
			
			cote.plan.munid = planification.munid
			cote.plan.coteRueId = planification.coteRueId
			cote.plan.etatDeneig = planification.etatDeneig
			if not hasattr(planification, 'dateDebutPlanif'):
				cote.plan.dateDebutPlanif = datetime.min
			else:
				cote.plan.dateDebutPlanif = planification.dateDebutPlanif
			if not hasattr(planification, 'dateFinPlanif'):
				cote.plan.dateFinPlanif = datetime.min
			else:
				cote.plan.dateFinPlanif = planification.dateFinPlanif
			if not hasattr(planification, 'dateDebutReplanif'):
				cote.plan.dateDebutReplanif = datetime.min
			else:
				cote.plan.dateDebutReplanif = planification.dateDebutReplanif
			if not hasattr(planification, 'dateFinReplanif'):
				cote.plan.dateFinReplanif = datetime.min
			else:
				cote.plan.dateFinReplanif = planification.dateFinReplanif
			if not hasattr(planification, 'dateMaj'):
				cote.plan.dateMaj = datetime.min
			else:
				cote.plan.dateMaj = planification.dateMaj
			cote.save()
			
		return HttpResponse('updated')
	except WebFault as e:
		raise HttpResponseBadRequest
