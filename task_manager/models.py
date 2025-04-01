from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import AbstractUser
from rest_framework import serializers

# AbstractUser
class User(AbstractUser): 
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    groups = models.ManyToManyField(
        "auth.Group",
        blank=True
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        blank=True
    )

    # Follow System: Users can follow each other
    following = models.ManyToManyField("self", symmetrical=False, related_name="followers", blank=True)

    def __str__(self):
        return self.username

# User Serializer
class UserSerializer(serializers.ModelSerializer):
    is_verified_email = serializers.BooleanField(source='is_verified', read_only=True)
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'is_verified_email', 'created_at']
        extra_kwargs = {'password': {'write_only': True}}
        
    def to_representation(self, instance):
        """Customize response to hide emails for non-admin users."""
        data = super().to_representation(instance)
        request = self.context.get('request')
        
        if request and not request.user.is_superuser:
            data.pop('email')  
        
        return data

# Task Model
class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')

    def __str__(self):
        return self.title

# Post Model (For News Feed)
class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='author_posts')
    title = models.CharField(max_length=100, blank=True, null=True)  # Title is optional
    content = models.TextField()
    is_published = models.BooleanField(default=True)
    # New privacy field:
    privacy = models.CharField(
        max_length=10,
        choices=[('public', 'Public'), ('private', 'Private')],
        default='public'
    )
    liked_by = models.ManyToManyField(User, related_name="liked_posts", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def total_likes(self):
        return self.liked_by.count()

    def __str__(self):
        return f"{self.author.username} - {self.title or 'No Title'}"

# Comment Model
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')  
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')  
    content = models.TextField()
    # New field for likes on comments
    liked_by = models.ManyToManyField(User, related_name="liked_comments", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.title}"


