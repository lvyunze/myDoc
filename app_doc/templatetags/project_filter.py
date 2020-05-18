# utf-8
from app_doc.models import *
from django import template

register = template.Library()


@register.filter(name='get_doc_count')
def get_doc_count(value):
    return Doc.objects.filter(top_doc=int(value)).count()


@register.filter(name='get_new_doc')
def get_new_doc(value):
    new_doc = Doc.objects.filter(top_doc=int(value), status=1).order_by('-modify_time').first()
    if new_doc is None:
        new_doc = '它还没有文档……'
    return new_doc


@register.filter(name='report_status_epub')
def get_report_status_epub(value):
    try:
        project = Project.objects.get(id=int(value))
        status = ProjectReport.objects.get(project=project).allow_epub
    except Exception as e:
        status = 0
        print(e)
    return status


@register.filter(name='report_status_pdf')
def get_report_status_pdf(value):
    try:
        project = Project.objects.get(id=int(value))
        status = ProjectReport.objects.get(project=project).allow_pdf
    except Exception as e:
        status = 0
        print(e)
    return status


@register.filter(name='img_group_cnt')
def get_img_group_cnt(value):
    cnt = Image.objects.filter(group_id=value).count()
    return cnt


@register.filter(name='project_collaborator_cnt')
def get_project_collaborator_cnt(value):
    cnt = ProjectCollaborator.objects.filter(project=value).count()
    return cnt
