from django.urls import path

from .views.process import ProcessCompleteApiView, ProcessCreateApiView, ProcessDestroyApiView, ProcessListApiView
from .views.process_output import ProcessOutputUpdateDeleteApiView
from .views.process_input import ProcessInputUpdateDeleteApiView


urlpatterns = [
    # ProcessOutput
    path("output/<int:pk>/", ProcessOutputUpdateDeleteApiView.as_view(), name="process-output-update-delete"),
    
    # ProcessInput
    path("input/<int:pk>/", ProcessInputUpdateDeleteApiView.as_view(), name="process-output-update-delete"),

    # Process
    path("list/", ProcessListApiView.as_view(), name="process-list"),
    path("create/", ProcessCreateApiView.as_view(), name="process-create"),
    path("<int:pk>/complete/", ProcessCompleteApiView.as_view(), name="process-complete"),
    path("<int:pk>/delete/", ProcessDestroyApiView.as_view(), name="process-delete"),
]
