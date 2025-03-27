from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from .permissions import IsPostAuthor
from rest_framework import status
from .models import Post, Comment
from .serializers import UserSerializer, PostSerializer, CommentSerializer
from task_manager.singletons.config_manager import ConfigManager
from django.http import JsonResponse
from task_manager.singletons.logger_singleton import LoggerSingleton
from task_manager.factories.post_factory import PostFactory
from task_manager.factories.comment_factory import CommentFactory
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework import status
from .models import Post, Comment
from .serializers import PostSerializer, CommentSerializer
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from django.conf import settings
from rest_framework.generics import ListAPIView
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.pagination import PageNumberPagination

class GoogleLoginView(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter

User = get_user_model()

#Update or Delete Post (Ensures Author Only)
@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated, IsPostAuthor])
def update_or_delete_post(request, post_id):
    """Update or delete a post based on request method."""
    try:
        post = Post.objects.get(id=post_id, author=request.user)
    except Post.DoesNotExist:
        return Response({"error": "Post not found or unauthorized"}, status=404)

    if request.method == 'PUT':  # Update Post
        serializer = PostSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Post updated successfully", "data": serializer.data}, status=200)
        return Response(serializer.errors, status=400)

    elif request.method == 'DELETE':  # Delete Post
        post.delete()
        return Response({"message": "Post deleted successfully"}, status=200)

#  Custom Authentication Token (Login System)
class CustomAuthToken(ObtainAuthToken):
    """Handles user login and token generation."""
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user_id": user.id, "username": user.username}, status=status.HTTP_200_OK)

# Admin-Only View
class AdminOnlyView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        return Response({"message": "Welcome to Connectly, Admin!"})

#Protected View (Authenticated Users Only)
class ProtectedView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "Yey! You are authenticated!", "user": request.user.username})

#  Create a New User
@api_view(['POST'])
@permission_classes([AllowAny])
def create_user(request):
    """Create a new user and generate an authentication token."""
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({"user": serializer.data, "token": token.key}, status=201)
    return Response(serializer.errors, status=400)

#  Get All Users (Admin Only)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_users(request):
    """Retrieve a list of users (Admin Only)."""
    if not request.user.is_superuser:
        return Response({"error": "Only administrators can view user data ;P"}, status=403)

    paginator = PageNumberPagination()
    paginator.page_size = 10  
    users = User.objects.all()
    paginated_users = paginator.paginate_queryset(users, request)
    serializer = UserSerializer(paginated_users, many=True)
    return paginator.get_paginated_response(serializer.data)

# Get User Details
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_details(request, user_id):
    """Retrieve details of a specific user."""
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    serializer = UserSerializer(user)
    return Response(serializer.data, status=200)

#  Verify Email
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def verify_email(request, user_id):
    """Mark a user's email as verified."""
    try:
        user = User.objects.get(id=user_id)
        user.is_verified = True
        user.save()
        return Response({"message": f"Email for {user.username} has been verified."}, status=200)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)
    

#Delete User
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user(request, user_id):
    """Delete a user by ID (Admin Only)."""
    if not request.user.is_superuser:
        return Response({"error": "Only administrators can delete users"}, status=403)
    try:
        user = User.objects.get(id=user_id)
        user.delete()
        return Response({"message": f"User {user.username} has been deleted successfully."}, status=200)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)


# Like/Unlike Post
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_like_post(request, post_id):
    """Toggle like/unlike on a post."""
    post = get_object_or_404(Post, id=post_id)
    
    if request.user in post.liked_by.all():
        post.liked_by.remove(request.user)
        return Response({"message": "Unliked post", "total_likes": post.total_likes()}, status=200)
    else:
        post.liked_by.add(request.user)
        return Response({"message": "Liked post", "total_likes": post.total_likes()}, status=201)

# Create Post
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_post(request):
    """Create a new post."""
    serializer = PostSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(author=request.user)  
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#  Delete a Post (Only the Author Can Delete)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_post(request, post_id):
    """Delete a post if the logged-in user is the author."""
    try:
        post = Post.objects.get(id=post_id, author=request.user)  
    except Post.DoesNotExist:
        return Response({"error": "Post not found or unauthorized"}, status=status.HTTP_404_NOT_FOUND)

    post.delete()
    return Response({"message": "Post deleted successfully"}, status=status.HTTP_200_OK)

# Get All Posts 
@api_view(['GET'])
def get_posts(request):
    """Retrieve all posts with pagination."""
    paginator = PageNumberPagination()
    paginator.page_size = 10  

    posts = Post.objects.all().order_by('-created_at')  
    paginated_posts = paginator.paginate_queryset(posts, request)

    serializer = PostSerializer(paginated_posts, many=True)
    return paginator.get_paginated_response(serializer.data)

# Create Comment
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_comment(request, post_id):
    """Create a new comment for a post."""
    post = get_object_or_404(Post, id=post_id)
    serializer = CommentSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save(user=request.user, post=post)
        return Response(serializer.data, status=201)

    return Response(serializer.errors, status=400)

# Get Comments for a Post
@api_view(['GET'])
def get_comments(request, post_id):
    """Retrieve all comments for a given post."""
    comments = Comment.objects.filter(post_id=post_id).order_by('-created_at')
    serializer = CommentSerializer(comments, many=True)
    return Response(serializer.data, status=200)

# Delete Comment (Only Author Can Delete)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_comment(request, comment_id):
    """Delete a comment (only if the user is the author)."""
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)
    comment.delete()
    return Response({"message": "Comment deleted successfully"}, status=200)


#Singleton

def test_config_manager(request):
    """View to test the Singleton ConfigManager"""
    
    config = ConfigManager()  
    default_page_size = config.get_setting("DEFAULT_PAGE_SIZE")

    return JsonResponse({
        "message": "ConfigManager Singleton is working!",
        "DEFAULT_PAGE_SIZE": default_page_size
    })


#Logger
def test_logger(request):
    """View to test the Singleton Logger"""
    
    logger = LoggerSingleton().get_logger()
    logger.info("LoggerSingleton is being tested through API.")

    return JsonResponse({"message": "Logger Singleton is working! Check your console."})


#Post Factory

class CreatePostView(APIView):
    def post(self, request):
        data = request.data
        try:
            post = PostFactory.create_post(
                author_id=data.get('author_id'),
                title=data.get('title', ''),
                content=data.get('content', ''),
                is_published=data.get('is_published', True)
            )
            return Response({'message': 'Post created successfully!', 'post_id': post.id}, status=status.HTTP_201_CREATED)

        except ValueError as e:  
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)  
        except Exception as e:  
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)  


#Comment Factory

class CreateCommentView(APIView):
    def post(self, request):
        data = request.data
        try:
            comment = CommentFactory.create_comment(
                user_id=data.get('user_id'),
                post_id=data.get('post_id'),
                content=data.get('content', '')
            )
            return Response({'message': 'Comment created successfully!', 'comment_id': comment.id}, status=status.HTTP_201_CREATED)

        except ValueError as e:  
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e: 
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Custom Pagination for News Feed
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10  
    page_size_query_param = 'page_size'
    max_page_size = 50

#  News Feed API (GET /feed)
class NewsFeedView(ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user = self.request.user
        filter_type = self.request.query_params.get('filter', None)  
        
        queryset = Post.objects.select_related('author').prefetch_related('liked_by').order_by('-created_at')

        if filter_type == "following":
            followed_users = user.following.all()  
            queryset = queryset.filter(author__in=followed_users)  

        elif filter_type == "liked":
            queryset = queryset.filter(liked_by=user)  

        return queryset

    
#toggle_like_post 
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_like_post(request, post_id):
    """Toggle like/unlike on a post."""
    post = get_object_or_404(Post, id=post_id)

    if request.user in post.liked_by.all():
        post.liked_by.remove(request.user)
        liked = False
    else:
        post.liked_by.add(request.user)
        liked = True

    return Response({
        "message": "Post updated successfully",
        "liked_by_user": liked,
        "total_likes": post.liked_by.count()
    }, status=200)

#TO follow and Unfollow a User
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_follow(request, user_id):
    """Follow or Unfollow a user."""
    target_user = get_object_or_404(User, id=user_id)

    if request.user == target_user:
        return Response({"error": "You cannot follow yourself."}, status=400)

    if request.user in target_user.followers.all():
        target_user.followers.remove(request.user)
        return Response({"message": f"You have unfollowed {target_user.username}."}, status=200)
    else:
        target_user.followers.add(request.user) 
        return Response({"message": f"You are now following {target_user.username}."}, status=201)
    
#TO get following list
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_following_list(request, user_id):
    """Retrieve the list of users a person follows."""
    user = get_object_or_404(User, id=user_id)
    following = user.following.all()
    
    serializer = UserSerializer(following, many=True)
    return Response(serializer.data, status=200)

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10  # Number of posts per page
    page_size_query_param = 'page_size'
    max_page_size = 50

@method_decorator(cache_page(60 * 2), name='dispatch')  
class NewsFeedView(ListAPIView):
    queryset = Post.objects.select_related('author').prefetch_related('comments').order_by('-created_at')
    serializer_class = PostSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        print("🚀 NewsFeedView executed (not cached)")
        return super().get(request, *args, **kwargs)