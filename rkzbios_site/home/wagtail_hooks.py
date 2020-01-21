from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from home.models import KijkWijzerClassification


class KijkWijzerClassificationAdmin(ModelAdmin):
    model = KijkWijzerClassification
    menu_label = "KijkWijzerClassifications"
    menu_icon = "pick"
    menu_order = 200
    add_to_settings_menu = False
    exclude_from_explorer = False

modeladmin_register(KijkWijzerClassificationAdmin)