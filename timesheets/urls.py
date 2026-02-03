from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import TimeSheetViewSet, TimeSheetEntryViewSet, AbsenceRecordViewSet

router = DefaultRouter()
router.register(r'timesheets', TimeSheetViewSet, basename='timesheet')
router.register(r'entries', TimeSheetEntryViewSet, basename='entry')
router.register(r'absences', AbsenceRecordViewSet, basename='absence')

app_name = 'timesheets'

urlpatterns = [
    path('', include(router.urls)),
]
