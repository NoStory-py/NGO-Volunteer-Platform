from django.urls import path
from .views import user_register, home, user_login, volunteer_dashboard, ngo_dashboard, user_logout, view_profile, create_task, portfolio, apply_task, update_status, edit_profile, edit_task, delete_task, download_portfolio, task_completion, update_completion
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', home, name='home'),  
    path('user_register/', user_register, name='user_register'),
    path('user_login/', user_login, name='user_login'),
    path('user_logout/', user_logout, name='user_logout'),  

    path('volunteer_dashboard/', volunteer_dashboard, name='volunteer_dashboard'),
    path('ngo_dashboard/', ngo_dashboard, name='ngo_dashboard'),

    path('view_profile/', view_profile, name='view_profile'),

    path('create_task/', create_task, name='create_task'),
    path('apply_task/<int:task_id>/', apply_task, name='apply_task'),

    path('portfolio/', portfolio, name='portfolio'),

    path('update_status/<int:application_id>/', update_status, name='update_status'),

    path('edit_profile/', edit_profile, name='edit_profile'),

    path('edit_task/<int:task_id>/', edit_task, name='edit_task'),
    path('delete_task/<int:task_id>/', delete_task, name='delete_task'),

    path('download_portfolio/<int:application_id>/', download_portfolio, name='download_portfolio'),

    path('task_completion/<int:application_id>/', task_completion, name='task_completion'),
    path('update_completion/<int:application_id>/', update_completion, name='update_completion'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

