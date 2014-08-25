from suds.client import Client
from suds import WebFault
from models import Cote
from pyproj import Proj, transform
import json

url = 'https://servicesenligne2.ville.montreal.qc.ca/api/infoneige/InfoneigeWebService?wsdl'
client = Client(url)
print(client)
request = client.factory.create('ns1:getPlanificationsForDate')

print(request)
request.fromDate = '2014-08-04T05:04:00'
request.tokenString = 'ka71-8850723a-0c14-458f-9e51-94d943dcf39b-84876b3e-864e-4ad2-be96-7407a3ed2cc3-e0c86339-7d04-44b7-8e3a-7d782a2394ee-105362f7-b82e-41ec-84c6-08e5ef0970a7-7df45d79-9d11-4363-b59c-8abd4f50434d'
try:
	response = client.service.GetPlanificationsForDate(request)		
	#planification = response.planifications.planification[0]
	c = 0
	#for planification in response.planifications.planification:
	print(len(response.planifications.planification))
	for r in range(0,100):
		planification = response.planifications.planification[r]		
		cote = Cote.objects.get(properties__COTE_RUE_ID=planification.coteRueId)
		if cote.plan is None:
			cote.plan = Plan()
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
	c = c + 1
	print(c)
	cote.save()
		
	print('updated')
except WebFault as e:
	print('noupdate')