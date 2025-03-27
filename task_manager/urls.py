from django.urls import path, include
from . import views
from .views import CustomAuthToken, ProtectedView, AdminOnlyView
from .views import test_config_manager
from .views import test_logger
from .views import CreatePostView
from .views import CreateCommentView
from .views import GoogleLoginView
from .views import NewsFeedView
from .views import toggle_like_post
from .views import toggle_follow, get_following_list

urlpatterns = [
    # User URLs
    path('users/', views.get_users, name='get_users'),
    path('users/create/', views.create_user, name='create_user'),
    path('users/<int:user_id>/verify/', views.verify_email, name='verify_email'),
    path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('users/<int:user_id>/details/', views.get_user_details, name='get_user_details'),

    # Post URLs
    path('posts/', views.get_posts, name='get_posts'),
    path('posts/create/', views.create_post, name='create_post'),
    path('posts/<int:post_id>/modify/', views.update_or_delete_post, name='update_or_delete_post'),
    path('posts/<int:post_id>/like/', views.toggle_like_post, name='toggle_like_post'),

    # Comments
    path('comments/create/', views.create_comment, name='create_comment'),
    path('comments/', views.get_comments, name='get_comments'),
    path('comments/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('posts/<int:post_id>/comments/', views.get_comments, name='get_comments'),
    path('posts/<int:post_id>/comments/create/', views.create_comment, name='create_comment'),
    path('comments/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    
    # Token Authentication
    path('api/token/', CustomAuthToken.as_view(), name='api_token_auth'),

    # Other URLs
    path('protected/', ProtectedView.as_view(), name='protected_view'),
    path('admin-only/', AdminOnlyView.as_view(), name='admin_only'),
    path('test-config/', test_config_manager, name='test-config'),
    path('test-logger/', test_logger, name='test-logger'),
    path('create-post/', CreatePostView.as_view(), name='create-post'),
    path('create-comment/', CreateCommentView.as_view(), name='create-comment'),
    
    path('auth/google/login/', GoogleLoginView.as_view(), name='google_login'),
    path('accounts/', include('allauth.urls')), 

    path('feed/', NewsFeedView.as_view(), name='news-feed'),
    path('posts/<int:post_id>/like/', toggle_like_post, name='toggle-like-post'),
    path('users/<int:user_id>/follow/', toggle_follow, name='toggle-follow'),
    path('users/<int:user_id>/following/', get_following_list, name='get-following-list'),
    
    

]
