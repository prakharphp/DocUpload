from django.urls import path  #, url

from . import views


urlpatterns = [
    path('', views.user_login, name='login'),
    path('Dashboard', views.home, name='Dashboard'),
    path('upload_doc', views.upload_doc, name='upload_doc'),
    path('forgot_password', views.forgot_password, name='forgot_password'),
    path('logout', views.user_logout, name='logout'),
    path('temp/<owner_id>/<file_name>', views.serve_protected_document, name='serve_protected_document'),
    # url(r'^media/protected/documents/(?P<file>.*)$', core.views.serve_protected_document, name='serve_protected_document'),
]
