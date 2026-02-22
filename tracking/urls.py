from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.home_view, name='home'),
    path('password-change/', views.password_change_view, name='password_change'),

    path('boss/', views.boss_dashboard_view, name='boss_dashboard'),
    path('boss/employees/', views.employees_list_view, name='employees_list'),
    path('boss/employees/<int:employee_id>/delete/', views.delete_employee_view, name='delete_employee'),
    path('boss/employees/<int:employee_id>/', views.employee_detail_view, name='employee_detail'),
    path('boss/employees/<int:employee_id>/projects/<int:project_id>/', views.employee_project_view, name='employee_project_view'),
    path('boss/employees/<int:employee_id>/projects/<int:project_id>/logs/<int:log_id>/', views.employee_log_view, name='employee_log_view'),
    path('boss/projects/', views.all_projects_view, name='all_projects'),
    path('boss/projects/manage/', views.boss_manage_projects_view, name='boss_manage_projects'),
    path('boss/projects/<int:project_id>/', views.boss_project_view, name='boss_project_view'),
    path('boss/projects/<int:project_id>/edit/', views.edit_project_view, name='edit_project'),
    path('boss/projects/<int:project_id>/delete/', views.delete_project_view, name='delete_project'),
    path('boss/expenses/', views.expenses_view, name='expenses'),
    path('boss/expenses/<int:expense_id>/delete/', views.delete_expense_view, name='delete_expense'),
    path('boss/create-project/', views.create_project_view, name='create_project'),
    path('boss/new-employee/', views.new_employee_view, name='new_employee'),

    path('my-projects/', views.my_projects_view, name='my_projects'),
    path('my-projects/new/', views.new_project_signup_view, name='new_project_signup'),
    path('my-projects/<int:project_id>/', views.project_page_view, name='project_page'),
    path('my-projects/<int:project_id>/new-log/', views.new_log_view, name='new_log'),
    path('my-projects/<int:project_id>/logs/<int:log_id>/', views.log_detail_view, name='log_detail'),

    path('ajax/employees/', views.employee_autocomplete, name='employee_autocomplete'),
]
