from django.contrib import admin

from .models import Process, ProcessInput, ProcessOutput


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

    inlines = [ProcessInputInline, ProcessOutputInline]
