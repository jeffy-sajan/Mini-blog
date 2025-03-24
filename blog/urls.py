from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='home'),
    path('blog/', views.blog_home, name='blog-home'),
    path('post/<int:pk>/', views.post_detail, name='post-detail'),
    path('post/new/', views.post_create, name='post-create'),
    path('post/<int:pk>/update/', views.post_update, name='post-update'),
    path('post/<int:pk>/delete/', views.post_delete, name='post-delete'),
    path('post/<int:post_pk>/comment/', views.add_comment, name='add-comment'),
    path('post/<int:post_pk>/save/', views.save_post, name='save-post'),
    path('post/<int:post_pk>/is-saved/', views.is_post_saved, name='is-post-saved'),
    path('saved-posts/', views.saved_posts, name='saved-posts'),
    path('bloggers/', views.blogger_list, name='blogger-list'),
    path('bloggers/<int:pk>/', views.blogger_detail, name='blogger-detail'),
    path('profile/', views.profile_update, name='profile-update'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='blog/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
]