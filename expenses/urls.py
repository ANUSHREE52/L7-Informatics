from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'expenses'

urlpatterns = [
    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='expenses/login.html', form_class=views.LoginForm), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='expenses:login'), name='logout'),
    path('signup/', views.signup, name='signup'),
    
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Profile
    path('profile/', views.profile, name='profile'),
    
    # Categories
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.category_add, name='category_add'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    
    # Expenses
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/add/', views.expense_add, name='expense_add'),
    path('expenses/<int:pk>/edit/', views.expense_edit, name='expense_edit'),
    path('expenses/<int:pk>/delete/', views.expense_delete, name='expense_delete'),
    
    # Budgets
    path('budgets/', views.budget_list, name='budget_list'),
    path('budgets/set/', views.budget_set, name='budget_set'),
    path('budgets/<int:pk>/edit/', views.budget_edit, name='budget_edit'),
    path('budgets/<int:pk>/delete/', views.budget_delete, name='budget_delete'),
    
    # Reports
    path('reports/', views.reports, name='reports'),
    
    # Alerts
    path('alerts/', views.alerts, name='alerts'),
    path('alerts/<int:alert_id>/delete/', views.delete_alert, name='delete_alert'),
    path('alerts/clear/', views.clear_alerts, name='clear_alerts'),
    
    # API Endpoints
    path('api/expense-summary/', views.api_expense_summary, name='api_expense_summary'),
    path('api/expense-chart-data/', views.api_expense_chart_data, name='api_expense_chart_data'),
]
