from django.contrib import admin

from .models import Process, ProcessInput, ProcessOutput, ProcessTemplate, ProcessTemplateInputItem, ProcessTemplateOutputItem, ProcessType


class ProcessTemplateInputItemInline(admin.TabularInline):
    model = ProcessTemplateInputItem
    extra = 1
    fields = ["material", "role", "use_all_material"]


class ProcessTemplateOutputItemInline(admin.TabularInline):
    model = ProcessTemplateOutputItem
    extra = 1
    fields = ["material", "role", "use_all_material"]


@admin.register(ProcessTemplate)
class ProcessTemplateAdmin(admin.ModelAdmin):
    list_display = ["pk", "name"]
    inlines = [ProcessTemplateInputItemInline, ProcessTemplateOutputItemInline]


# @admin.register(ProcessTemplateInputItem)
# class ProcessTemplateInputItemAdmin(admin.ModelAdmin):
#     list_display = ["pk", "template", "material", "role", "use_all_material"]
#     list_filter = ["role", "use_all_material"]
#     search_fields = ["template__name", "material__name"]


# @admin.register(ProcessTemplateOutputItem)
# class ProcessTemplateOutputItemAdmin(admin.ModelAdmin):
#     list_display = ["pk", "template", "material", "role", "use_all_material"]
#     list_filter = ["role", "use_all_material"]
#     search_fields = ["template__name", "material__name"]


@admin.register(ProcessType)
class ProcessTypeAdmin(admin.ModelAdmin):
    list_display = ["pk", "type_name", "type", "template"]

    def type_name(self, obj, *args, **kwargs):
        return obj.get_name().upper()

    type_name.short_description = "Name"


class ProcessInputInline(admin.TabularInline):
    model = ProcessInput
    extra = 1


class ProcessOutputInline(admin.TabularInline):
    model = ProcessOutput
    extra = 1


@admin.register(Process)
class ProcessAdmin(admin.ModelAdmin):
    list_display = ["pk", "organization", "process_type", "status", "started_at", "finished_at"]
    list_filter = ["started_at", "finished_at"]
    search_fields = ["organization", "process_type"]
    list_editable = ["status", "process_type"]

    inlines = [ProcessInputInline, ProcessOutputInline]
