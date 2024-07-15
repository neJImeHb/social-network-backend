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
from datetime import timedelta

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
        bio = Bio.objects.get(id=user.bio_id)

        last_activity = ''
        now = timezone.now()
        last_activity_time = user.last_activity

        if last_activity_time and now - last_activity_time > timedelta(minutes=5):
            last_activity_date = last_activity_time.date()
            now_date = now.date()
            
            if last_activity_date != now_date:
                if (now_date - last_activity_date).days > 1:
                    last_activity = 'Last activity: ' + last_activity_time.strftime('%H:%M, %d %B')
                elif (now_date - last_activity_date).days == 1:
                    last_activity = 'Was online Yesterday at ' + last_activity_time.strftime('%H:%M')
            else:
                last_activity = 'Was online Today at ' + last_activity_time.strftime('%H:%M')
        else:
            last_activity = 'Online'

        user_data = {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'username': user.username,
            'email': user.email,
            'phone': user.phone,
            'bio': {
                'id': bio.id,
                'status': bio.status,
                'biography': bio.biography,
                'birthday_day': bio.birthday_day,
                'birthday_month': bio.birthday_month,
                'birthday_year': bio.birthday_year
            },
            'last_activity': last_activity
        }

        isOwner = user.id == current_user.id


        return Response({'user_data': user_data, 'isOwner': isOwner})
    
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
            'status': b.status
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

        b.status=status 
        b.biography=biography
        if birthday_day != 0:
            b.birthday_day=birthday_day
        if birthday_month != 0:
            b.birthday_month=birthday_month
        if birthday_year != 0:
            b.birthday_year=birthday_year
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


            