from __future__ import unicode_literals
from api.models import *
from rest_framework_mongoengine.serializers import MongoEngineModelSerializer
import warnings
from django.core.exceptions import ValidationError
from mongoengine.errors import ValidationError
from rest_framework import serializers
from rest_framework import fields
import mongoengine
from mongoengine.base import BaseDocument
from django.core.paginator import Page
from django.db import models
from django.forms import widgets
from django.utils.datastructures import SortedDict
from rest_framework.compat import get_concrete_model
from rest_framework_mongoengine.fields import ReferenceField, ListField, EmbeddedDocumentField, DynamicField

#override get_field to include LineStringField in the mapping
class MongoEngineModelSerializer2(MongoEngineModelSerializer):
	def get_field(self, model_field):
		kwargs = {}
		if model_field.__class__ in (mongoengine.ReferenceField, mongoengine.EmbeddedDocumentField, mongoengine.ListField, mongoengine.DynamicField):
			kwargs['model_field'] = model_field
			kwargs['depth'] = self.opts.depth
		if not model_field.__class__ == mongoengine.ObjectIdField:
			kwargs['required'] = model_field.required

		if model_field.__class__ == mongoengine.EmbeddedDocumentField:
			kwargs['document_type'] = model_field.document_type

		if model_field.default:
			kwargs['required'] = False
			kwargs['default'] = model_field.default

		if model_field.__class__ == models.TextField:
			kwargs['widget'] = widgets.Textarea

		field_mapping = {
			mongoengine.FloatField: fields.FloatField,
			mongoengine.IntField: fields.IntegerField,
			mongoengine.DateTimeField: fields.DateTimeField,
			mongoengine.EmailField: fields.EmailField,
			mongoengine.URLField: fields.URLField,
			mongoengine.StringField: fields.CharField,
			mongoengine.BooleanField: fields.BooleanField,
			mongoengine.FileField: fields.FileField,
			mongoengine.ImageField: fields.ImageField,
			mongoengine.ObjectIdField: fields.Field,
			mongoengine.ReferenceField: ReferenceField,
			mongoengine.ListField: ListField,
			mongoengine.EmbeddedDocumentField: EmbeddedDocumentField,
			mongoengine.DynamicField: DynamicField,
			mongoengine.DecimalField: fields.DecimalField,
			mongoengine.LineStringField: fields.CharField,
		}

		attribute_dict = {
			mongoengine.StringField: ['max_length'],
			mongoengine.DecimalField: ['min_value', 'max_value'],
			mongoengine.EmailField: ['max_length'],
			mongoengine.FileField: ['max_length'],
			mongoengine.ImageField: ['max_length'],
			mongoengine.URLField: ['max_length'],
		}

		if model_field.__class__ in attribute_dict:
			attributes = attribute_dict[model_field.__class__]
			for attribute in attributes:
				kwargs.update({attribute: getattr(model_field, attribute)})

		try:
			return field_mapping[model_field.__class__](**kwargs)
		except KeyError:
			return fields.ModelField(model_field=model_field, **kwargs)

class StreetSerializer(MongoEngineModelSerializer2):
	class Meta:
		model = Street
		depth = 8

class CoteSerializer(MongoEngineModelSerializer2):
	class Meta:
		model = Cote
		exclude = ()
		depth = 8

class CotePlanSerializer(MongoEngineModelSerializer2):
	class Meta:
		model = Cote
		exclude = ('id','street','geometry','properties',)
		depth = 1

class CoteGeoSerializer(MongoEngineModelSerializer2):
	class Meta:
		model = Cote
		exclude = ('id','street','plan','properties',)
		depth = 1