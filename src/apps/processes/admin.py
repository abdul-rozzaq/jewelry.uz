from django.contrib import admin

from .models import Process, ProcessInput, ProcessOutput, ProcessTemplate, ProcessType


class ProcessInputInline(admin.TabularInline):
    model = ProcessInput
    extra = 1


class ProcessOutputInline(admin.TabularInline):
    model = ProcessOutput
    extra = 1


@admin.register(ProcessTemplate)
class ProcessTemplateAdmin(admin.ModelAdmin):
    list_display = ["pk", "name"]


@admin.register(ProcessType)
class ProcessTypeAdmin(admin.ModelAdmin):
    list_display = ["pk", "type_name", "type", "template"]

    def type_name(self, obj, *args, **kwargs):
        return obj.get_name().upper()

    type_name.short_description = "Name"


@admin.register(Process)
class ProcessAdmin(admin.ModelAdmin):
    list_display = ["pk", "organization", "process_type", "status", "started_at", "finished_at"]
    list_filter = ["started_at", "finished_at"]
    search_fields = ["organization", "process_type"]

    inlines = [ProcessInputInline, ProcessOutputInline]
