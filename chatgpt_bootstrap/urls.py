"""
URL configuration for chatgpt_bootstrap project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from django.conf import settings
from django.conf.urls.static import static
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="ChatAI API",
        default_version='v1',
        description="Welcome",
        # terms_of_service="https://www.tweet.org",
        contact=openapi.Contact(email="1755838904@qq.com"),
        # license=openapi.License(name="Awesome IP"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("user/", include("chatgpt_user.urls")),
    path("v1/chat/", include("chatgpt_chat.urls")),
    path("v1/audio/", include("chatgpt_audio.urls")),
    path("config/", include("chatgpt_config.urls")),
    path("dashboard/", include("chatgpt_usage.urls")),
    path("v1/images/", include("chatgpt_image.urls")),
    path("file/", include("chatgpt_image.urls")),

]+ static(settings.STATIC_URL,document_root = settings.STATIC_ROOT)

if settings.DEBUG:  # prod环境不提供swagger服务
    import debug_toolbar
    urlpatterns += [
        
    re_path(r'^doc(?P<format>\.json|\.yaml)$',schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path(r'api-auth/', include(('rest_framework.urls', 'rest_framework'), namespace="api-auth")),
    path('__debug__/', include(debug_toolbar.urls)),
    
    ]