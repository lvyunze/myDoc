# ut-8
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from app_doc.models import Doc, Project


class HomeSitemap(Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return ['pro_list']

    def location(self, item):
        return reverse(item)


class ProjectSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return Project.objects.filter(role=0)


class DocSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def __init__(self, pro):
        self.pro = pro

    def items(self):
        return Doc.objects.filter(status=1, top_doc=self.pro)

    def lastmod(self, obj):
        return obj.modify_time


class SitemapAll():
    def __init__(self):
        self.sitemaps = {}

    def __iter__(self):
        self._generate_sitemaps_dict()
        return self.sitemaps.__iter__()

    def __getitem__(self, key):
        self._generate_sitemaps_dict()
        return self.sitemaps[key]

    def items(self):
        self._generate_sitemaps_dict()
        return self.sitemaps.items()

    def _generate_sitemaps_dict(self):
        if self.sitemaps:
            return
        for project in Project.objects.filter(role=0):
            sitemap = DocSitemap(pro=project.id)
            self.sitemaps[str(project.id)] = sitemap
        self.sitemaps['home'] = HomeSitemap()
