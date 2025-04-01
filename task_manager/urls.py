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
    path('account/delete/', views.delete_account, name='delete_account'),
    path('users/<int:user_id>/details/', views.get_user_details, name='get_user_details'),

    # Post URLs
    path('posts/', views.get_posts, name='get_posts'),
    path('posts/my/', views.get_my_posts, name='get_my_posts'),
    path('posts/create/', views.create_post, name='create_post'),
    path('posts/<int:post_id>/modify/', views.update_or_delete_post, name='update_or_delete_post'),
    path('posts/<int:post_id>/like/', views.toggle_like_post, name='toggle_like_post'),
    path('posts/<int:post_id>/like/', toggle_like_post, name='toggle-like-post'),


    # Comments
    path('comments/create/', views.create_comment, name='create_comment'),
    path('comments/', views.get_comments, name='get_comments'),
    path('comments/my/', views.get_my_comments, name='get_my_comments'),
    path('posts/<int:post_id>/comments/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('posts/<int:post_id>/comments/', views.get_comments, name='get_comments'),
    path('posts/<int:post_id>/comments/create/', views.create_comment, name='create_comment'),
    path('posts/<int:post_id>/comments/<int:comment_id>/toggle-like/', views.toggle_like_comment, name='toggle_like_comment'),
    path('comments/all/', views.get_all_comments, name='get_all_comments'),

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
    path('accounts/', include('allauth.urls')),  # Required for django-allauth

    #Newsfeed
    path('feed/', NewsFeedView.as_view(), name='news-feed'),
    path('posts/<int:post_id>/', views.get_post_detail, name='get_post_detail'),

    # Follwers
    path('users/<int:user_id>/followers/', views.get_followers_list, name='get_followers_list'),
    path('users/<int:user_id>/following/', views.get_following_list, name='get_following_list'),
    path('users/<int:user_id>/follow/', toggle_follow, name='toggle-follow'),


]
