from django.urls import path
from .views import *
from .friends import *
from .messages import *
from .posts import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('api/get_user_statuses/', GetUserStatuses.as_view(), name='get_user_statuses'),
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/logout/', LogoutView.as_view(), name='login'),
    path('api/protected/', ProtectedView.as_view(), name='protected'),
    path('api/profile/', CurrentUserView.as_view(), name='current_user'),
    path('api/profile_friends/', ProfileFriends.as_view(), name='profile_friends'),
    path('api/check_psw/', CurrentPassword.as_view(), name='current_psw'),
    path('api/get_bio/', GetBio.as_view(), name='get_bio'),
    path('api/online/', isOnline.as_view(), name='online'),
    path('api/friend_request/', FriendRequest.as_view(), name='friend_request'),
    path('api/check_friend_request/', CheckFriendsRequests.as_view(), name='check_friend_request'),
    path('api/check_all_friend_request/', CheckAllFriendsRequests.as_view(), name='check_all_friend_request'),
    path('api/accept_friend_request/', AcceptFriendRequest.as_view(), name='accept_friend_request'),
    path('api/reject_friend_request/', RejectFriendRequest.as_view(), name='reject_friend_request'),
    path('api/check_friend_list/', CheckFriendList.as_view(), name='check_friend_list'),
    path('api/to_be_friends/', ToBeFriends.as_view(), name='to_be_friends'),
    path('api/remove_friend/', RemoveFriend.as_view(), name='remove_friend'),
    path('api/upload_avatar/', UploadAvatar.as_view(), name='upload_avatar'),
    path('api/get_avatar/', GetAvatar.as_view(), name='get_avatar'),
    path('api/messages/create_chat/', CreateChat.as_view(), name='create_chat'),
    path('api/messages/get_chat/', GetChats.as_view(), name='get_chat'),
    path('api/messages/get_companion/', GetCompanion.as_view(), name='get_companion'),
    path('api/messages/send_message/', SendMessage.as_view(), name='send_message'),
    path('api/messages/get_messages/', GetMessages.as_view(), name='get_messages'),
    path('api/posts/publicate/', PublicatePost.as_view(), name='publicate'),
    path('api/posts/get_profile_posts/', GetProfilePosts.as_view(), name='get_profile_posts'),
    path('api/posts/like/', Like.as_view(), name='like')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)