from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportMixin
from import_export.formats import base_formats
from .models import ImageCsvModel, ImageLinkModel

# Register your models here.
class ImageResource(resources.ModelResource):
    class Meta:
        model = ImageCsvModel
        fields = ('id', 'image_name', 'title')
        import_id_fields = ['id']


class ImageAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display  = (
        'image_name',
        'title'
    )

    resource_class = ImageResource
    formats = [base_formats.CSV]

admin.site.register(ImageCsvModel, ImageAdmin)


class LinkResource(resources.ModelResource):
    class Meta:
        model = ImageLinkModel
        fields = ('id', 'image_name', 'link')
        import_id_fields = ['id']



class LinkAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display  = (
        'image_name',
        'link'
    )

    resource_class = LinkResource
    formats = [base_formats.CSV]

admin.site.register(ImageLinkModel, LinkAdmin)