# utf-8
from rest_framework.serializers import ModelSerializer
from app_doc.models import *


class ProjectSerializer(ModelSerializer):
    class Meta:
        model = Project
        fields = ('__all__')


class DocSerializer(ModelSerializer):
    class Meta:
        model = Doc
        fields = ('__all__')


class DocTempSerializer(ModelSerializer):
    class Meta:
        model = DocTemp
        fields = ('__all__')


class ImageSerializer(ModelSerializer):
    class Meta:
        model = Image
        fields = ('__all__')


class ImageGroupSerializer(ModelSerializer):
    class Meta:
        model = ImageGroup
        fields = ('__all__')


class AttachmentSerializer(ModelSerializer):
    class Meta:
        model = Attachment
        fields = ('__all__')
