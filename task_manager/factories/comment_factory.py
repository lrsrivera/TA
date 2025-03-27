from django.contrib.auth import get_user_model
from task_manager.models import Comment, Post

User = get_user_model() 

class CommentFactory:
    @staticmethod
    def create_comment(user_id, post_id, content):
        """Factory method to create a new Comment."""
       
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ValueError("Invalid user ID. User does not exist.")

     
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            raise ValueError("Invalid post ID. Post does not exist.")

        return Comment.objects.create(
            user=user,
            post=post,
            content=content
        )
