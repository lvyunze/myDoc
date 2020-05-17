from rest_framework.serializers import ModelSerializer
from app_doc.models import *

# 文集序列化器
class ProjectSerializer(ModelSerializer):
    class Meta:
        model = Project
        fields = ('__all__')

# 文档序列化器
class DocSerializer(ModelSerializer):
    class Meta:
        model = Doc
        fields = ('__all__')

# 文档模板序列化器
class DocTempSerializer(ModelSerializer):
    class Meta:
        model = DocTemp
        fields = ('__all__')

# 图片序列化器
class ImageSerializer(ModelSerializer):
    class Meta:
        model = Image
        fields = ('__all__')

# 图片分组序列化器
class ImageGroupSerializer(ModelSerializer):
    class Meta:
        model = ImageGroup
        fields = ('__all__')

# 附件序列化器
class AttachmentSerializer(ModelSerializer):
    class Meta:
        model = Attachment
        fields = ('__all__')