from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
]

from django.conf.urls import include
from django.urls import path

urlpatterns += [
    path('syllabus_app/', include('syllabus_app.urls')),
]

from django.views.generic import RedirectView
urlpatterns += [
    path('', RedirectView.as_view(url='/syllabus_app/welcome/')), # Alterado para redirecionar para a página de boas-vindas
]

from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Remova ou comente a importação de auth_views se não for mais usada diretamente aqui
# from django.contrib.auth import views as auth_views 
from syllabus_app import views as syllabus_app_views # Importe suas views customizadas
from syllabus_app.forms import CustomAuthenticationForm # Importe seu formulário customizado

urlpatterns += [
    # URLs de login e logout customizadas
    path('accounts/login/', syllabus_app_views.CustomLoginView.as_view(), name='login'),
    path('accounts/logout/', syllabus_app_views.CustomLogoutView.as_view(), name='logout'),
    # Inclui as outras URLs de autenticação (mudança de senha, reset, etc.)
    path('accounts/', include('django.contrib.auth.urls')), # Inclui as outras URLs de autenticação (logout, password_reset, etc.)
]