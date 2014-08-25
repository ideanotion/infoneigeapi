from mongoengine import *
from datetime import datetime
from mongoengine.base import BaseField

connect('infoneige')

class StreetProperties(EmbeddedDocument):
	A = StringField()
	SENS_CIR = IntField()
	DE = StringField()
	SUR = StringField()
	TRC_ID = IntField()
	
class Street(Document):
	trcId = IntField()
	geometry = LineStringField()
	properties = EmbeddedDocumentField(StreetProperties)

class Plan(EmbeddedDocument):
	munid = IntField()
	coteRueId = IntField()
	etatDeneig = IntField()
	dateDebutPlanif = DateTimeField(default=datetime.min)
	dateFinPlanif = DateTimeField(default=datetime.min)
	dateDebutReplanif = DateTimeField(default=datetime.min)
	dateFinReplanif = DateTimeField(default=datetime.min)
	dateMaj = DateTimeField(default=datetime.min)

class CoteProperties(EmbeddedDocument):
	COTE_RUE_ID = IntField()
	ID_TRC = IntField()
	DEBUT_ADRESSE = IntField()
	FIN_ADRESSE = IntField()
	ORIENTATION_F = StringField()
	NOM_VOIE = StringField()
	LIEN_F = StringField()
	ARRONDISSEMENT = StringField()
	TYPE_F = StringField()

class Cote(Document):
	coteRueId = IntField()
	geometry = LineStringField()
	properties = EmbeddedDocumentField(CoteProperties)
	street = ReferenceField(Street)
	plan = EmbeddedDocumentField(Plan)
