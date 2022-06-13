from operator import mod
from django.db import models
from datetime import datetime

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
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    image = models.CharField(max_length=256,blank=True)
    is_media = models.BooleanField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.content[:30]}...'

class Comment(models.Model):
    text = models.TextField(blank=True)
    post = models.ForeignKey(Post,on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.text[:5]}...'

class Like(models.Model):
    # if true, the activity_id will be of post, else of comment, useful to know where to look
    # for parent
    is_parent_post = models.BooleanField()
    # This id can be either the pk of the post or pk of the comment
    activity_id = models.IntegerField()
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    

class Activity(models.Model):
    # CAUTION : the below field is not the pk, and will have many same values across the table
    # coz it can be for a comment or a post
    is_activity_post = models.BooleanField()
    activity_id = models.IntegerField()
    no_of_likes = models.IntegerField()

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
    
    
    
    
    
# class PostLike(models.Model):
#     user = models.ForeignKey('User',on_delete=models.CASCADE)
#     post = models.ForeignKey('Post',on_delete=models.CASCADE)
#     timestamp = models.DateTimeField(auto_now_add=True)
    
#     def __str__(self):
#         return f'{self.id}'