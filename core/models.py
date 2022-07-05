from operator import mod
from django.db import models
from datetime import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json
# Create your models here.


class User(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100,blank=True,null=True)
    username = models.CharField(max_length=256,unique=True)
    email = models.EmailField(max_length=254,unique=True)
    password = models.CharField(max_length=256)
    bio = models.CharField(max_length=256,null=True,blank=True)
    profile_image = models.TextField(default="https://res.cloudinary.com/kaustubh-apps/image/upload/v1654495391/default_avatar.png")
    cover_image = models.TextField(default="https://res.cloudinary.com/kaustubh-apps/image/upload/v1654496317/cover_placeholder.png")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    num_of_followers = models.IntegerField(default=0)
    num_of_following = models.IntegerField(default=0)
    
    def __str__(self):
        return self.username
    
# class UserFollowing(models.Model):

#     user = models.ForeignKey(User, related_name="following", on_delete=models.CASCADE)
#     follower = models.ForeignKey(User, related_name="followers", on_delete=models.CASCADE)
#     created = models.DateTimeField(auto_now_add=True, db_index=True)

#     # class Meta:
#     #     constraints = [
#     #         models.UniqueConstraint(fields=['user_id','following_user_id'],  name="unique_followers")
#     #     ]
#     #     ordering = ["-created"]

#     def __str__(self):
#         f"{self.follower.username} follows {self.user.username}" or ''
        
        
class Post(models.Model):
    parent = models.ForeignKey("self",on_delete=models.CASCADE,null=True,blank=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    image = models.CharField(max_length=256,blank=True)
    is_media = models.BooleanField()
    timestamp = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    share_count = models.IntegerField(default=0)
    
    @property
    def is_repost(self):
        return self.parent is not None
    
    def __str__(self):
        return f'{self.content[:30]}...'

class PostLike(models.Model):
    post = models.ForeignKey(Post,on_delete=models.CASCADE,related_query_name='like')
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='likes',related_query_name='like')
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return f'{self.user} liked {self.post.content[:10]}'

class Comment(models.Model):
    text = models.TextField(blank=True)
    post = models.ForeignKey(Post,on_delete=models.CASCADE,related_name='comments',related_query_name='comment')
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='comments',related_query_name='comment')
    timestamp = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(default=0)
    
    def __str__(self):
        return f'{self.text[:5]}...'
    
class CommentLike(models.Model):
    comment = models.ForeignKey(Comment,on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='commentLikes',related_query_name='commentLike')
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return f'{self.user} liked {self.comment.text[:10]}'

class Follow(models.Model):
    # When unique_user_instance.following.all() is queried, we get all user objects for which the
    # follower is the unique_user_instance, and hence the count of such objects
    # will give the no of users unique_user is following
    follower = models.ForeignKey(User,on_delete=models.CASCADE,related_name='following')
    # When unique_user.followers.all() is queried, we recieve all the follow objects
    # where the unique_user is a followee, that is if a count is done, we get the no of 
    # followers of the unique_user since he is the followe for all of them.
    followee = models.ForeignKey(User,on_delete=models.CASCADE,related_name='followers')
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.follower} follows {self.followee}'
    

class Bookmark(models.Model):
    post = models.ForeignKey(Post,on_delete=models.CASCADE,related_name='bookmarks',related_query_name='bookmark')
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='bookmarks',related_query_name='bookmark')
    
    def __str__(self):
        return f'{self.user} bookmarked {self.post}'
    
NOTIFICATION_CHOICES = (
    ('like','like'),
    ('comment','comment'),
    ('rewuphf','rewuphf'),
    ('follow','follow'),
)

class Notification(models.Model):
    # notification can be of 3 types : 'like','comment','rewuphf','follow'
    type = models.CharField(max_length=32,choices=NOTIFICATION_CHOICES,null=True,blank=True)
    text = models.CharField(max_length=100,null=True,blank=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='notifications',related_query_name='notification')
    # The parent link could be link to the post which was liked, reposted, or commented on
    # or in case of type follow, the link of generator_username
    parent_link = models.CharField(max_length=256,null=True,blank=True)
    generator_username = models.CharField(max_length=100,null=True,blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    seen = models.BooleanField(default=False)
    notification_for_content = models.CharField(max_length=256,null=True,blank=True)
    
    def __str__(self) -> str:
        return f'{self.generator_username} - engaged ({self.type}) with - {self.user.username}'
    
    @staticmethod
    def generate_notification_di(id):
        notification = Notification.objects.get(id=id)
        generator_user = User.objects.get(username=notification.generator_username)
        notification_di = {}
        notification_di['id']=notification.id
        notification_di['type']=notification.type
        notification_di['text']=notification.text
        notification_di['userFullName']=f'{generator_user.first_name} {generator_user.last_name}'
        notification_di['postLink']=notification.parent_link
        notification_di['userProfileLink']=f'/{notification.generator_username}'
        notification_di['userProfilePhoto']=generator_user.profile_image
        notification_di['time']=notification.timestamp
        return notification_di
    
@receiver(post_save,sender=Notification)
def notification_created_handler(instance,created,**kwargs):
    if created:
        notification = instance
        generator_user = User.objects.get(username=notification.generator_username)
        notification_di = {}
        notification_di['id']=notification.id
        notification_di['type']=notification.type
        notification_di['text']=notification.text
        notification_di['userFullName']=f'{generator_user.first_name} {generator_user.last_name}'
        channel_layer = get_channel_layer()
        data = {'count':1,'current_notification':notification_di}
        print('prepared data to be sent, now performing the async to sync call')
        try:
            async_to_sync(channel_layer.group_send)(f'user_{notification.user.username}',{
                'type':'notification_send',
                'value':notification_di,
            })
        except Exception as e:
            print('error')
            print(e)
        print('async call complet,should call consumers')
        print(notification.generator_username)
        print(notification.user.username)
        print(notification.seen)
# class PostLike(models.Model):
#     user = models.ForeignKey('User',on_delete=models.CASCADE)
#     post = models.ForeignKey('Post',on_delete=models.CASCADE)
#     timestamp = models.DateTimeField(auto_now_add=True)
    
#     def __str__(self):
#         return f'{self.id}'