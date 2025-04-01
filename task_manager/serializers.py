from rest_framework import serializers
from django.contrib.auth import get_user_model  
from .models import Task, Post, Comment

User = get_user_model()  

# ✅ User Serializer
class UserSerializer(serializers.ModelSerializer):
    is_verified_email = serializers.BooleanField(source='is_verified', read_only=True)
    password = serializers.CharField(write_only=True, required=True)
    created_at = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'is_verified_email', 'created_at']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_username(self, value):
        """Custom validation for username uniqueness (excluding current user)."""
        request = self.context.get("request")
        user = request.user if request else None  
        if User.objects.exclude(id=user.id).filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def create(self, validated_data):
        """Creates a user and ensures the password is hashed correctly."""
        password = validated_data.pop('password')  
        user = User(**validated_data)  
        user.set_password(password)  
        user.save()  
        return user 

# ✅ Task Serializer
class TaskSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field='username', read_only=True)  

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'is_completed', 'user']

# ✅ Post Serializer (For News Feed)
class PostSerializer(serializers.ModelSerializer):
    total_likes = serializers.SerializerMethodField() 
    liked_by_user = serializers.SerializerMethodField()  
    author_username = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'privacy', 'created_at', 'total_likes', 'liked_by_user', 'author_username']

    def get_total_likes(self, obj):
        return obj.liked_by.count()

    def get_liked_by_user(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.liked_by.filter(id=request.user.id).exists()
        return False

# ✅ Comment Serializer
class CommentSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field='username', read_only=True)  

    class Meta:
        model = Comment
        fields = ['id', 'post', 'user', 'content', 'created_at']
