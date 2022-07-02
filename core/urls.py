from django.urls import path
from .views import *

urlpatterns = [
    path('', home),
    path('signup',signup),
    path('check_username_available',check_username_available),
    path('login',login),
    path('user_profile',user_profile),
    path('logout',logout), 
    path('get_user_details',get_user_details), 
    path('get_user_profile',get_user_profile), 
    path('follow_unfollow_user',follow_unfollow_user), 
    path('get_recommended_users',get_recommended_users), 
    path('add_post',add_post), 
    path('get_feed_posts',get_feed_posts),
    path('get_profile_data',get_profile_data),
    path('get_profile_media_posts',get_profile_media_posts),
    path('get_post_detail',get_post_detail),
    path('bookmark_unbookmark_post',bookmark_unbookmark_post),
    path('like_unlike_post',like_unlike_post),
    path('get_notifications',get_notifications),
    path('mark_notification_read',mark_notification_read),
    # path('get_posts',get_posts), 
    # path('generate_and_send_otp',generate_and_send_otp), 
    # path('verify_otp',verify_otp), 
    # path('delete_otp',delete_otp), 
    # path('reset_password',reset_password), 
]