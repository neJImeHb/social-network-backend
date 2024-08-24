from .models import Posts, Likes, Comments
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers
import os
from .DataBase import GetDate

class PostsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Posts
        fields = ['id', 'user_id', 'file_name', 'description', 'archived', 'disabled_comments', 'only_friends_can_see']
       
class LikesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Likes
        fields = ['id', 'post_id', 'from_user']
         

class PublicatePost(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        file = request.data.get('file')
        description = request.data.get('description')
        only_friends_can_see = request.data.get('only_friends_can_see')
        
        canSee = None
        
        if only_friends_can_see == 'true':
            canSee = True
        else: canSee = False
        
        post = Posts.objects.create(user_id=user.id, description=description, only_friends_can_see=canSee)
        post.save()
        
        if file:
            file_name = os.path.join('myapp/images/posts', f"post_{post.id}.jpg")
            with open(file_name, 'wb') as new_file:
                for chunk in file.chunks():
                    new_file.write(chunk)
                    
            post.file_name = f"post_{post.id}.jpg"
            post.save()
        
        # Логика для создания поста
        return Response({"message": "Post created successfully"})
    
class GetProfilePosts(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        user_id = request.data['user_id']
        is_friends = request.data['is_friends']
        
        if user.id == user_id: p = Posts.objects.filter(user_id=user_id).order_by('-date').all()
        elif user.id != user_id and is_friends: p = Posts.objects.filter(user_id=user_id, archived=False).order_by('-date').all()
        else: p = Posts.objects.filter(user_id=user_id, archived=False, only_friends_can_see=False).order_by('-date').all()
        
        l = Likes.objects.filter(post_id__in=p.values('id'))
        
        posts = PostsSerializer(p, many=True).data
        likes = LikesSerializer(l, many=True).data
        
        posts_images = []
        posts_date = []
        
        for el in p:
            formatted = GetDate(el.date)
            posts_date.append({'id': el.id, 'date': formatted})
            if el.file_name:
                image_path = os.path.join('myapp/images/posts', el.file_name)

                if os.path.exists(image_path):
                    image_url = request.build_absolute_uri(f'/images/posts/{el.file_name}')
                    posts_images.append({'id': el.id, 'file_name': el.file_name, 'url': image_url})
        
        return Response({'posts': posts, 'posts_images': posts_images, 'posts_date': posts_date, 'likes': likes})
    
    
class Like(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        post_id = request.data['post_id']
        deleting = request.data['deleting']
        
        if not deleting: Likes(post_id=post_id, from_user=user.id).save()
        else: Likes.objects.get(post_id=post_id, from_user=user.id).delete()
        return Response(None)
        