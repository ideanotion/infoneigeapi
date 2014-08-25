from suds.client import Client
from suds import WebFault
from datetime import datetime

url = 'https://servicesenligne2.ville.montreal.qc.ca/api/infoneige/InfoneigeWebService?wsdl'
client = Client(url)
print(client)
request = client.factory.create('ns1:getPlanificationsForDate')
responseType1 = client.factory.create('ns1:planifications')
responseType2 = client.factory.create('ns1:planification')
responseType3 = client.factory.create('GetPlanificationsForDateResponse')
responseType4 = client.factory.create('ns1:getPlanificationsForDateResponse')

#print(request)
print(responseType1)
print(responseType2)
#print(responseType3)
#print(responseType4)
request.fromDate = '2014-08-04T05:04:00'
request.tokenString = 'ka71-8850723a-0c14-458f-9e51-94d943dcf39b-84876b3e-864e-4ad2-be96-7407a3ed2cc3-e0c86339-7d04-44b7-8e3a-7d782a2394ee-105362f7-b82e-41ec-84c6-08e5ef0970a7-7df45d79-9d11-4363-b59c-8abd4f50434d'
try:
	response = client.service.GetPlanificationsForDate(request)
	for planification in response.planifications.planification:		
		print (planification)
		
except WebFault as e:
	print(e)

	