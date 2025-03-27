from django.contrib.auth import get_user_model  
from task_manager.models import Post

User = get_user_model()  

class PostFactory:
    @staticmethod
    def create_post(author_id, title, content='', is_published=True):
        try:
            author = User.objects.get(id=author_id) 
        except User.DoesNotExist:
            raise ValueError("Invalid author ID. User does not exist.")

        return Post.objects.create(
            author=author,
            title=title,
            content=content,
            is_published=is_published
        )
