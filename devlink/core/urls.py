from django.conf import settings
from django.conf.urls.static import static

from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import (
    BookmarkListView,
    HomeView,
    ResourceDeleteView, 
    ResourceDetailView, 
    ResourceCreateView,
    ResourceUpdateView,
    bookmark_resource,
    ResourceListAPI,
    ResourceDetailAPI,
    CategoryListAPI,
    TagListAPI,
    BookmarkCreateAPI,
    register,
    toggle_like,
    resource_share
)

urlpatterns = [
    # HTML URLs
    path('', HomeView.as_view(), name='home'),
    path('resources/<int:pk>/', ResourceDetailView.as_view(), name='resource_detail'),
    path('resources/create/', ResourceCreateView.as_view(), name='resource_create'),
    path('resources/<int:pk>/bookmark/', bookmark_resource, name='bookmark_resource'),
    path('resources/<int:pk>/like/', toggle_like, name='like_resource'),
    path('resources/<int:pk>/edit/', ResourceUpdateView.as_view(), name='resource_edit'),
    path('resources/<int:pk>/delete/', ResourceDeleteView.as_view(), name='resource_delete'),

    # API URLs
    path('api/resources/', ResourceListAPI.as_view(), name='api_resource_list'),
    path('api/resources/<int:pk>/', ResourceDetailAPI.as_view(), name='api_resource_detail'),
    path('api/categories/', CategoryListAPI.as_view(), name='api_category_list'),
    path('api/tags/', TagListAPI.as_view(), name='api_tag_list'),
    path('api/bookmarks/', BookmarkCreateAPI.as_view(), name='api_bookmark_create'),
    path('bookmarks/', BookmarkListView.as_view(), name='bookmark_list'),
    
    # Share
    path('resources/<int:pk>/share/', resource_share, name='resource_share'),
    
    path('register/', register, name='register'),
    path('login/', LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
