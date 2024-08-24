import os
from rest_framework import generics
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny
from .serializers import *
from .models import *
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from .DataBase import *

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        try:
            serializer.save()
        except ValidationError as e:
            raise ValidationError(e.detail)


class LoginView(TokenObtainPairView):
    serializer_class = CustomJWTSerializer
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        try:
            serializer.save()
        except ValidationError as e:
            raise ValidationError(e.detail)

class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user_data = {
            'id': user.id,
            'first_name': user.first_name,
            "auth": True,
            'username': user.username
        }
        return Response(user_data)
    
class isOnline(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        result = update_activity(username=request.user.username)
        return Response({'msg': result})

class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        username = request.data.get('username')
        current_user = request.user
        user = get_object_or_404(User, username=username)
        if user:
            bio = Bio.objects.get(id=user.bio_id)

            user_data = {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'username': user.username,
                'email': user.email,
                'phone': user.phone,
                'avatar': user.avatar,
                'bio': {
                    'id': bio.id,
                    'status': bio.status,
                    'biography': bio.biography,
                    'birthday_day': bio.birthday_day,
                    'birthday_month': bio.birthday_month,
                    'birthday_year': bio.birthday_year,
                    'show': bio.show
                }
            }

            isOwner = user.id == current_user.id


            return Response({'user_data': user_data, 'isOwner': isOwner})
        else: return Response(False)
    
class GetBio(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        b = Bio.objects.get(id=user.bio_id)
        bio = {
            'biography': b.biography,
            'birthday_day': b.birthday_day,
            'birthday_month': b.birthday_month,
            'birthday_year': b.birthday_year,
            'status': b.status,
            'show': b.show
        }
        return Response(bio)
    
    def post(self, request):
        user = request.user
        b = Bio.objects.get(id=user.bio_id)
        status = request.data['status']
        biography = request.data['biography']
        birthday_day = request.data['birthday_day']
        birthday_month = request.data['birthday_month']
        birthday_year = request.data['birthday_year']
        show = request.data['show']

        b.status=status 
        b.biography=biography
        if birthday_day != 0:
            b.birthday_day=birthday_day
        if birthday_month != 0:
            b.birthday_month=birthday_month
        if birthday_year != 0:
            b.birthday_year=birthday_year
        b.show=show
        b.save()

        return Response({'msg': 'Data saved successful!'})

class BioCreateView(generics.CreateAPIView):
    queryset = Bio.objects.all()
    serializer_class = BioSerializer

class CurrentPassword(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        psw = request.data['password']

        if user.check_password(psw) == True:
            return Response({'msg': 'Current password!'})
        else: 
            return Response({'msg': 'Uncurrent password!'})

class UploadAvatar(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        image = request.data['image']  # Accessing the image with the correct key

        print(f'Uploaded image: {image.name}')

        db = CustomUser.objects.get(id=user.id)
        db.avatar_id=user.avatar_id + 1
        db.avatar=f"avatar_{user.id}_{user.avatar_id + 1}.jpg"
        db.save()

        file_name = os.path.join('myapp/images/avatars', f"avatar_{user.id}_{user.avatar_id + 1}.jpg")
        with open(file_name, 'wb') as new_file:
            for chunk in image.chunks():
                new_file.write(chunk)

        image_path = f"myapp/images/avatars/avatar_{user.id}_{user.avatar_id}.jpg"

        print(image_path)

        if os.path.exists(image_path):
            os.remove(image_path)

        return Response('Image received')
    
class GetAvatar(APIView):
    def get(self, request):
        username = request.GET.get('username')
        file_name = CustomUser.objects.filter(username=username).values('avatar').first()

        if file_name:
            avatar_path = os.path.join('myapp/images/avatars', file_name['avatar'])

            if os.path.exists(avatar_path):
                # Return the URL path instead of the file itself
                avatar_url = request.build_absolute_uri(f'/images/avatars/{file_name["avatar"]}')
                return Response({'avatar_url': avatar_url})
        else:
            return Response(False, status=status.HTTP_404_NOT_FOUND)
        
        
class GetUserStatuses(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        ids = request.data['user_ids']
        if ids:
            print(ids)
            currentStatuses = []
            for el in ids:
                u = CustomUser.objects.filter(id=el).first()
                currentStatuses.append([{'user_id': u.id, 'new_status': u.online_status}])
            
            print(currentStatuses)
        
        return Response({'statuses': currentStatuses})