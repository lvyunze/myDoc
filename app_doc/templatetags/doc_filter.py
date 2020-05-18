# utf-8
from app_doc.models import *
from django import template

register = template.Library()


@register.filter(name='get_next_doc')
def get_next_doc(value):
    return Doc.objects.filter(parent_doc=value, status=1).order_by('sort')


@register.filter(name='get_doc_top')
def get_doc_top(value):
    return Project.objects.get(id=int(value))


@register.filter(name='is_colla_pro')
def is_colla_pro(pro, user):
    p = Project.objects.filter(id=pro, create_user=user)
    if p.exists():
        return ''
    else:
        return '【协作】'


@register.filter(name='get_doc_parent')
def get_doc_parent(value):
    if int(value) != 0:
        return Doc.objects.get(id=int(value))
    else:
        return '无上级文档'


@register.filter(name='get_doc_next')
def get_doc_next(value):
    try:
        doc_id = value
        doc = Doc.objects.get(id=int(doc_id))
        docs = Doc.objects.filter(
            parent_doc=doc.parent_doc, top_doc=doc.top_doc, status=1
        ).order_by('sort')
        docs_list = [d.id for d in docs]

        subdoc = Doc.objects.filter(parent_doc=doc.id, top_doc=doc.top_doc, status=1)

        if subdoc.count() == 0:
            if docs_list.index(doc.id) == len(docs_list) - 1:
                try:
                    parentdoc = Doc.objects.get(id=doc.parent_doc)
                    parents = Doc.objects.filter(
                        parent_doc=parentdoc.parent_doc, top_doc=doc.top_doc, status=1
                    ).order_by('sort')
                    parent_list = [d.id for d in parents]
                except Exception as e:
                    return e
                if parent_list.index(parentdoc.id) == len(parent_list) - 1:
                    try:
                        parentdoc2 = Doc.objects.get(id=parentdoc.parent_doc)
                        parents2 = Doc.objects.filter(
                            parent_doc=parentdoc2.parent_doc, top_doc=parentdoc.top_doc,
                            status=1
                        ).order_by('sort')
                        parent_list2 = [d.id for d in parents2]
                    except Exception as e:
                        return e
                    if parent_list2.index(parentdoc2.id) == len(parent_list2) - 1:
                        next_doc = None
                        return next_doc
                    else:
                        next_id = parent_list2[parent_list2.index(parentdoc2.id) + 1]
                        return next_id
                else:
                    next_id = parent_list[parent_list.index(parentdoc.id) + 1]
                    return next_id
            else:
                next_id = docs_list[docs_list.index(doc.id) + 1]
                next_doc = Doc.objects.get(id=next_id)
                return next_doc.id
        else:
            next_doc = subdoc.order_by('sort')[0]
            return next_doc.id
    except Exception as e:
        import traceback
        print(traceback.print_exc())
        return e


@register.filter(name='get_doc_previous')
def get_doc_previous(value):
    try:
        doc_id = value
        doc = Doc.objects.get(id=int(doc_id))
        docs = Doc.objects.filter(parent_doc=doc.parent_doc, top_doc=doc.top_doc, status=1).order_by('sort')
        docs_list = [d.id for d in docs]
        if docs_list.index(doc.id) == 0:
            if doc.parent_doc == 0:
                previous = None
                return previous
            else:
                previous = Doc.objects.get(id=doc.parent_doc)
                return previous.id
        else:
            previou_id = docs_list[docs_list.index(doc.id) - 1]
            previous = Doc.objects.get(id=previou_id)
            previous_subdoc = Doc.objects.filter(parent_doc=previous.id, top_doc=doc.top_doc, status=1).order_by(
                '-sort')
            if previous_subdoc.count() == 0:
                return previou_id
            else:
                previous = previous_subdoc[:1][0]
                parent_list = Doc.objects.filter(
                    parent_doc=previous.id, top_doc=doc.top_doc, status=1
                ).order_by('-sort')
                if parent_list.count() == 0:
                    return previous.id
                else:
                    previous = parent_list[:1][0]
                    return previous.id
    except Exception as e:
        import traceback
        print(traceback.print_exc())
        return e
