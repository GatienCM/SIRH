"""
URL Configuration for sirh_core project.
"""
# from django.contrib import admin  # Admin désactivé (incompatibilité Python 3.14)
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from .views import home
from .views_app import (
    login_view, logout_view, dashboard, employee_portal,
    employees_view, planning_view, timesheets_view,
    payroll_view, payroll_create, payroll_detail, payroll_export, payroll_delete, contracts_view, vehicles_view, admin_panel,
    employee_create, employee_edit, employee_delete,
    shift_create, shift_edit, shift_delete,
    timesheet_create, timesheet_edit, timesheet_delete, timesheet_auto_fill,
    timesheet_adjustment_add, timesheet_adjustment_approve, timesheet_adjustment_delete,
    contract_create, contract_edit, contract_delete, contract_download, contract_preview, contract_preview_download,
    payroll_settings_view, payroll_calculation_api, financial_report,
    vehicle_create, vehicle_edit, vehicle_delete,
    settings_professions, profession_create, profession_edit, profession_delete,
    settings_shifttypes, shifttype_create, shifttype_edit, shifttype_delete,
    absences_view, absence_delete,
    documents_view, employee_documents_admin, document_delete, employee_documents_view,
    medical_visits_view, medical_visit_edit, medical_visit_delete,
    guides_faq, guide_detail,
    employee_portal_simulate
)
from .viewsets import AuditLogViewSet, SystemSettingViewSet, AdminDashboardViewSet

router = DefaultRouter()
router.register(r'audit-logs', AuditLogViewSet, basename='audit-log')
router.register(r'system-settings', SystemSettingViewSet, basename='system-setting')
router.register(r'admin-dashboard', AdminDashboardViewSet, basename='admin-dashboard')

urlpatterns = [
    path('', home, name='home'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
    path('employee-portal/', employee_portal, name='employee_portal'),
    # path('admin/', admin.site.urls),  # Admin désactivé
    
    # App URLs
    path('employees/', employees_view, name='employees'),
    path('employees/create/', employee_create, name='employee_create'),
    path('employees/<int:employee_id>/edit/', employee_edit, name='employee_edit'),
    path('employees/<int:employee_id>/delete/', employee_delete, name='employee_delete'),
    path('employees/<int:employee_id>/simulate/', employee_portal_simulate, name='employee_portal_simulate'),
    
    path('planning/', planning_view, name='planning'),
    path('planning/create/', shift_create, name='shift_create'),
    path('planning/<int:shift_id>/edit/', shift_edit, name='shift_edit'),
    path('planning/<int:shift_id>/delete/', shift_delete, name='shift_delete'),
    
    path('timesheets/', timesheets_view, name='timesheets'),
    path('timesheets/create/', timesheet_create, name='timesheet_create'),
    path('timesheets/<int:timesheet_id>/edit/', timesheet_edit, name='timesheet_edit'),
    path('timesheets/<int:timesheet_id>/delete/', timesheet_delete, name='timesheet_delete'),
    path('timesheets/<int:timesheet_id>/auto-fill/', timesheet_auto_fill, name='timesheet_auto_fill'),
    path('timesheet/<int:timesheet_id>/adjustment/add/', timesheet_adjustment_add, name='timesheet_adjustment_add'),
    path('timesheet/adjustment/<int:adjustment_id>/approve/', timesheet_adjustment_approve, name='timesheet_adjustment_approve'),
    path('timesheet/adjustment/<int:adjustment_id>/delete/', timesheet_adjustment_delete, name='timesheet_adjustment_delete'),
    
    path('payroll/', payroll_view, name='payroll'),
    path('payroll/settings/', payroll_settings_view, name='payroll_settings'),
    path('payroll/report/', financial_report, name='financial_report'),
    path('payroll/create/', payroll_create, name='payroll_create'),
    path('payroll/<int:payroll_id>/detail/', payroll_detail, name='payroll_detail'),
    path('payroll/<int:payroll_id>/export/', payroll_export, name='payroll_export'),
    path('payroll/<int:payroll_id>/delete/', payroll_delete, name='payroll_delete'),
    path('payroll/<int:payroll_id>/api/calculation/', payroll_calculation_api, name='payroll_calculation_api'),
    
    path('absences/', absences_view, name='absences'),
    path('absences/<int:absence_id>/delete/', absence_delete, name='absence_delete'),
    
    path('documents/', documents_view, name='documents'),
    path('documents/employee/<int:employee_id>/', employee_documents_admin, name='employee_documents_admin'),
    path('documents/<int:document_id>/delete/', document_delete, name='document_delete'),
    path('my-documents/', employee_documents_view, name='employee_documents'),
    
    path('medical-visits/', medical_visits_view, name='medical_visits'),
    path('medical-visits/<int:visit_id>/edit/', medical_visit_edit, name='medical_visit_edit'),
    path('medical-visits/<int:visit_id>/delete/', medical_visit_delete, name='medical_visit_delete'),
    
    path('contracts/', contracts_view, name='contracts'),
    path('contracts/create/', contract_create, name='contract_create'),
    path('contracts/preview/', contract_preview, name='contract_preview'),
    path('contracts/preview/download/', contract_preview_download, name='contract_preview_download'),
    path('contracts/<int:contract_id>/edit/', contract_edit, name='contract_edit'),
    path('contracts/<int:contract_id>/delete/', contract_delete, name='contract_delete'),
    path('contracts/<int:contract_id>/download/', contract_download, name='contract_download'),
    
    path('vehicles/', vehicles_view, name='vehicles'),
    path('vehicles/create/', vehicle_create, name='vehicle_create'),
    path('vehicles/<int:vehicle_id>/edit/', vehicle_edit, name='vehicle_edit'),
    path('vehicles/<int:vehicle_id>/delete/', vehicle_delete, name='vehicle_delete'),

    path('guides/', guides_faq, name='guides'),
    path('guides/<slug:slug>/', guide_detail, name='guide_detail'),
    
    path('admin-panel/', admin_panel, name='admin_panel'),
    
    # Paramètres et administration
    path('settings/professions/', settings_professions, name='settings_professions'),
    path('settings/professions/create/', profession_create, name='profession_create'),
    path('settings/professions/<int:profession_id>/edit/', profession_edit, name='profession_edit'),
    path('settings/professions/<int:profession_id>/delete/', profession_delete, name='profession_delete'),
    
    path('settings/shifttypes/', settings_shifttypes, name='settings_shifttypes'),
    path('settings/shifttypes/create/', shifttype_create, name='shifttype_create'),
    path('settings/shifttypes/<int:shifttype_id>/edit/', shifttype_edit, name='shifttype_edit'),
    path('settings/shifttypes/<int:shifttype_id>/delete/', shifttype_delete, name='shifttype_delete'),
    
    # API endpoints
    path('api/auth/', include('accounts.urls')),
    path('api/employees/', include('employees.urls')),
    path('api/contracts/', include('contracts.urls')),
    path('api/vehicles/', include('vehicles.urls')),
    path('api/planning/', include('planning.urls')),
    path('api/timesheets/', include('timesheets.urls')),
    path('api/payroll/', include('payroll.urls')),
    path('api/portal/', include('portal.urls')),
    path('api/admin/', include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
