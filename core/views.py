from django.http import JsonResponse
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.sessions.backends.db import SessionStore
from django.conf import settings
from django.core import serializers
from django.db.models import Q
from .models import *
import hashlib
import random
import json
# Create your views here.

def home(request):
    return JsonResponse({'status':'ok'})

# View to check if the username requested is available, returns True, or False in JsonResponse
def check_username_available(request):
    if request.method == "GET":
        request_username = request.GET['requested_username']
        try:
            user = User.objects.get(username = request_username)
            return JsonResponse({'status':'false','message':'Username not available, please try another one.'},status=200)
        except User.DoesNotExist:
            return JsonResponse({'status':'true','message':'Username available'},status=200)
    return JsonResponse({'status':'failed','message':"Bad Request"},status=405)

# first_name, last_name, username, email, password in the POST request
@csrf_exempt
def signup(request):
    if request.method == "POST":
        try:
            email = request.POST["email"]
            try:
                user = User.objects.get(email=email)
                return JsonResponse({'status':'failed','message':"This email is already registered."},status=400)
            except User.DoesNotExist:
                first_name = request.POST["first_name"]
                last_name =  request.POST["last_name"] if request.POST['last_name'] else ""
                email = request.POST['email']
                print(request.POST)
                username = request.POST['username']
                password = request.POST["password"]
                password_hash = hashlib.sha512(str(password).encode('utf-8')).hexdigest()
                new_user = User.objects.create(first_name=first_name,last_name=last_name,username=username,email=email,password=password_hash)
            return JsonResponse({'status':'ok','message':'Account created succesfully, please login.'},status=201)
        except:
            return JsonResponse({'status':'failed','message':"Something went wrong."},status=400)
    return JsonResponse({'status':'failed','message':"Bad Request"},status=405)


#login api, accepts email, password, returns auth token from session key if login succesfull, else return 
# appropriate JSON response with error description.
@csrf_exempt
def login(request):
    # find a user with the given email, if not found, send error with proper description
    # Now check the password against db, if not correct, send error with proper description
    # If both checks are passed, create a session, and send the session key for authentication in frontend
    if request.method == "POST":
        if "HTTP_AUTH_TOKEN" in request.META:
            auth_token = request.META["HTTP_AUTH_TOKEN"]
            try:
                session = SessionStore(session_key=auth_token)
                return JsonResponse({'status':'failed','message':'User already in session'},status=403)
            except:
                print(f'No session object found, auth token given to backend is {auth_token}')
        email = request.POST['email']
        password = request.POST['password']
        
        try:
            user = User.objects.get(email = email)
        except User.DoesNotExist:
            return JsonResponse({'status':'failed','message':'The email you entered does not belong to any account.'},status=401)
        password_hash = hashlib.sha512(str(password).encode('utf-8')).hexdigest()
        if password_hash == user.password:
            user_details = {}
            user_details['username'] = user.username
            user_details['email'] = user.email
            session = SessionStore()
            session['user_details'] = user_details
            session.create()
            user_details['first_name'] = user.first_name
            user_details['last_name'] = user.last_name
            user_details['profile_image'] = user.profile_image
            user_details['bio'] = user.bio
            user_details['cover_image'] = user.cover_image
            return JsonResponse({'status':'success','message':'Logged in succesfully','user_details':user_details,'auth_token':session.session_key},status=201)
        else:
            return JsonResponse({'status':'failed','message':'Password is incorrect.Please try again.'},status=400)
    return JsonResponse({'status':'failed','message':"Bad Request"},status=405)


@csrf_exempt
def logout(request):
    if "HTTP_AUTH_TOKEN" in request.META:
        auth_token = request.META["HTTP_AUTH_TOKEN"]
        try:
            session = SessionStore(session_key=auth_token)
            session.flush()
            return JsonResponse({'status':'ok','message':'Logged out successfully'},status=200)
        except:
            print(f'No session object found in logout view, auth token given to backend is {auth_token}')
    return JsonResponse({'status':'failed','message':"User not in session"},status=400)

# A proper REST API for User Profile with both GET/POST method handling
@csrf_exempt
def user_profile(request):
    if request.method == "GET":
        #return all editable values, like first_name,last_name,username,email etc
        if "HTTP_AUTH_TOKEN" in request.META:
            auth_token = request.META["HTTP_AUTH_TOKEN"]
            try:
                session = SessionStore(session_key=auth_token)
                user = User.objects.get(username = session['user_details']['username'])
                user_details = {}
                user_details['first_name'] = user.first_name
                user_details['last_name'] = user.last_name
                user_details['profile_image'] = user.profile_image
                user_details['cover_image'] = user.cover_image
                user_details['username'] = user.username
                user_details['email'] = user.email
                return JsonResponse({'status':'ok','data':user_details},status=200)
            except:
                return JsonResponse({'status':'failed','message':"User not found"},status=400) 
        return JsonResponse({'status':'failed','message':"Bad Request"},status=405) 
    else:
        #update any fields posted to be changed from frontend
        #first check for unique fields(username,email) availablity,when user clicks update
        #if username or email is taken by another account, send the proper error message to be displayed on frontend
        #if both are available or belong to this account proceed to update all fields
        if "HTTP_AUTH_TOKEN" in request.META:
            auth_token = request.META["HTTP_AUTH_TOKEN"]
            try:
                session = SessionStore(session_key=auth_token)
                user = User.objects.get(username = session['user_details']['username'])
                # username = request.POST['username']
                # if user.username != username:
                #     #if the above condition is true, then username needs to be updated,if available
                #     try:
                #         existing_user = User.objects.get(username=username)
                #         return JsonResponse({'status':'failed','message':"This username is taken please try another one."},status=400)
                #     except User.DoesNotExist:
                #         #username is available
                #         user.username = username
                # if user.email != email:
                #     #if the above condition is true, email needs to be updated if available
                #     try:
                #         existing_user = User.objects.get(email=email)
                #         return JsonResponse({'status':'failed','message':"This email is taken please try another one."},status=400)
                #     except User.DoesNotExist:
                #         #username is available
                #         user.email = email
                #By now, if the username and/or email posted needed to be updated have been updated (not saved yet)
                #now update the remaining fields
                first_name = request.POST['first_name']
                last_name = request.POST['last_name']
                profile_image = request.POST['profile_image']
                cover_image = request.POST['cover_image']
                bio = request.POST['bio']
                user.first_name = first_name
                user.last_name = last_name
                user.profile_image = profile_image
                user.cover_image = cover_image
                user.bio = bio
                user.save()
                return JsonResponse({'status':'ok','message':'Profile updated successfully.'},status=200)
            except:
                return JsonResponse({'status':'failed','message':"User not found"},status=400)
        return JsonResponse({'status':'failed','message':"No valid user session found.Please login again."},status=400)
    


def get_user_details(request):
    if request.method == "GET":
        #return all values, like first_name,last_name,username,email,profile,cover,bio and created at etc
        if "HTTP_AUTH_TOKEN" in request.META:
            auth_token = request.META["HTTP_AUTH_TOKEN"]
            try:
                session = SessionStore(session_key=auth_token)
                user = User.objects.get(username = session['user_details']['username'])
                user_details = {}
                user_details['first_name'] = user.first_name
                user_details['last_name'] = user.last_name
                user_details['profile_image'] = user.profile_image
                user_details['cover_image'] = user.cover_image
                user_details['username'] = user.username
                user_details['email'] = user.email
                user_details['bio'] = user.bio
                # unread notifications flag, to show badge on bell icon
                notifications = user.notifications.filter(seen=False)
                user_details['unread_notifications'] = bool(notifications)
                return JsonResponse({'status':'ok','user_details':user_details},status=200)
            except:
                return JsonResponse({'status':'failed','message':"User not found"},status=400) 
        return JsonResponse({'status':'failed','message':"User not in session"},status=400)
    return JsonResponse({'status':'failed','message':"Bad Request"},status=405)

def get_user_profile(request):
    if request.method == "GET":
        if "HTTP_AUTH_TOKEN" in request.META:
            auth_token = request.META["HTTP_AUTH_TOKEN"]
            try:
                session = SessionStore(session_key=auth_token)
                self_user = User.objects.get(username=session['user_details']['username'])
                username = request.GET['username']
                user = User.objects.get(username=username)
                try:
                    follows_me = Follow.objects.get(followee=self_user,follower=user)
                    follows_me = 1
                except:
                    follows_me=0
                try:
                    followed_by_me = Follow.objects.get(followee=user,follower=self_user)
                    followed_by_me = 1
                except:
                    followed_by_me=0
                user_details = {}
                user_details['first_name'] = user.first_name
                user_details['last_name'] = user.last_name
                user_details['profile_image'] = user.profile_image
                user_details['cover_image'] = user.cover_image
                user_details['username'] = user.username
                user_details['email'] = user.email
                user_details['bio'] = user.bio
                user_details['doj'] = user.created_at
                user_details['num_of_followers'] = user.num_of_followers
                user_details['num_of_following'] = user.num_of_following
                user_details['follows_me'] = follows_me
                user_details['followed_by_me'] = followed_by_me
                return JsonResponse({'status':'ok','profile_user_details':user_details},status=200)
            except:
                return JsonResponse({'status':'failed','message':"User not found"},status=200) 
        return JsonResponse({'status':'failed','message':"User not in session"},status=400)
    return JsonResponse({'status':'failed','message':"Bad Request"},status=405)


@csrf_exempt
def follow_unfollow_user(request):
    if request.method == "POST":
        if "HTTP_AUTH_TOKEN" in request.META:
            auth_token = request.META["HTTP_AUTH_TOKEN"]
            try:
                session = SessionStore(session_key=auth_token)
                self_user = User.objects.get(username=session['user_details']['username'])
                other_username = request.POST['other_username']
                other_user = User.objects.get(username=other_username)
                try:
                    self_user_follows_other_user = Follow.objects.get(followee__username=other_username,follower__username=self_user.username)
                    # self follows the other user
                    # unfollow by deleting the above found object,update the following followers etc.
                    self_user_follows_other_user.delete()
                    self_user.num_of_following -= 1
                    other_user.num_of_followers -= 1
                    self_user.save()
                    other_user.save()
                    notification = Notification.objects.create(type='follow',user=other_user,generator_username=self_user.username,parent_link=f'/{self_user.username}',text='unfollowed you')
                    return JsonResponse({'status':'ok','message':'Unfollow successfull'},status=200)
                except:
                    # self does not follow
                    # create a follow object and hence start following, update the followers etc.
                    print('no follow object now creating')
                    Follow.objects.create(followee=other_user,follower=self_user)
                    self_user.num_of_following += 1
                    other_user.num_of_followers += 1
                    self_user.save()
                    other_user.save()
                    notification = Notification.objects.create(type='follow',user=other_user,generator_username=self_user.username,parent_link=f'/{self_user.username}',text='followed you')
                    return JsonResponse({'status':'ok','message':'Follow successfull'},status=200)
            except:
                return JsonResponse({'status':'failed','message':'Invalid usernames posted or invalid token.'},status=400)
        return JsonResponse({'status':'failed','message':"User not in session"},status=400)
    return JsonResponse({'status':'failed','message':"Bad Request"},status=405)

def get_recommended_users(request):
    if request.method == "GET":
        if "HTTP_AUTH_TOKEN" in request.META:
            auth_token = request.META["HTTP_AUTH_TOKEN"]
            try:
                session = SessionStore(session_key=auth_token)
                self_user = User.objects.get(username=session['user_details']['username'])
                # get user objects where follower is not user, that is he may be a followee or not present
                # edge case : u'll also get the current user since he does not follow himself, so exclude it
                # print(User.objects.all(follow__followers__username=user.username))
                # not_followed_users = User.objects.exclude(following__id=user.id).exclude(username=user.username)[:5]
                other_users = User.objects.exclude(username=self_user.username)[:5]
                recommended_users_dict = {}
                recommended_users = []
                for user in other_users:
                    try:
                        followed_by_me = Follow.objects.get(followee=user,follower=self_user)
                        followed_by_me = 1
                    except:
                        followed_by_me=0
                    recommended_user = {}
                    recommended_user['first_name'] = user.first_name
                    recommended_user['last_name'] = user.last_name
                    recommended_user['username'] = user.username
                    recommended_user['profile_image'] = user.profile_image
                    recommended_user['followed_by_me'] = followed_by_me
                    if not followed_by_me:
                        recommended_users.append(recommended_user)
                recommended_users_dict['recommended_users'] = recommended_users
                return JsonResponse({'status':'ok','data':recommended_users_dict},status=200)
            except:
                return JsonResponse({'status':'failed','message':'Something went wrong in getting recommended users.'},status=400)
        return JsonResponse({'status':'failed','message':"User not in session"},status=400)
    return JsonResponse({'status':'failed','message':"Bad Request"},status=405)


@csrf_exempt
def add_post(request):
    if request.method == "POST":
        if "HTTP_AUTH_TOKEN" in request.META:
            auth_token = request.META["HTTP_AUTH_TOKEN"]
            try:
                session = SessionStore(session_key=auth_token)
                self_user = User.objects.get(username=session['user_details']['username'])
            except:
                return JsonResponse({'status':'failed','message':"User not in session"},status=400)
            content = request.POST['content']
            is_media = False if request.POST['is_media'] == 'false' else True
            image = request.POST['image'] if is_media else ""
            post = Post.objects.create(user=self_user,content=content,is_media=is_media,image=image)
            new_post = generate_single_post_json(post,self_user)
            return JsonResponse({'status':'ok','message':"Post successfully saved.",'new_post':new_post},status=200)
        return JsonResponse({'status':'failed','message':"Auth token expected"},status=400)
    return JsonResponse({'status':'failed','message':"Bad Request"},status=405)

def generate_single_post_json(post,current_user):
    post_di={}
    user = {}
    user['first_name'] = post.user.first_name
    user['last_name'] = post.user.last_name
    user['profile_image'] = post.user.profile_image
    user['cover_image'] = post.user.cover_image
    user['bio'] = post.user.bio
    user['username'] = post.user.username
    user['full_name'] = f'{post.user.first_name} {post.user.last_name}'
    post_di['user'] = user
    post_di['content'] = post.content
    post_di['image'] = post.image
    post_di['is_media'] = 1 if post.image else 0
    post_di['timestamp'] = post.timestamp
    post_di['id']=post.id
    try:
        post_di['is_bookmark'] = current_user.bookmarks.get(post=post)
        post_di['is_bookmark'] = True
    except:
        post_di['is_bookmark'] = False
    return post_di

def generate_post_json_for_post_queryset(posts,current_user):
    postsFromDBList = []
    for post in posts:
        new_post = generate_single_post_json(post,current_user)
        postsFromDBList.append(new_post)
    return postsFromDBList

'''
Poll.objects.get(
    Q(question__startswith='Who'),
    Q(pub_date=date(2005, 5, 2)) | Q(pub_date=date(2005, 5, 6))
)
Lookup functions can mix the use of Q objects and keyword arguments. All arguments provided to a lookup function (be they keyword arguments or Q objects) are “AND”ed together. However, if a Q object is provided, it must precede the definition of any keyword arguments. For example:

Poll.objects.get(
    Q(pub_date=date(2005, 5, 2)) | Q(pub_date=date(2005, 5, 6)),
    question__startswith='Who',
)
'''

def get_feed_posts(request):
    if request.method == "GET":
        if "HTTP_AUTH_TOKEN" in request.META:
            auth_token = request.META["HTTP_AUTH_TOKEN"]
            try:
                session = SessionStore(session_key=auth_token)
                self_user = User.objects.get(username=session['user_details']['username'])
            except:
                return JsonResponse({'status':'failed','message':"User not in session"},status=400)
            
            # getting posts made by users who have their follower list contain self_user as follower
            # or posts made by the current user
            feed_posts = Post.objects.filter(Q(user__followers__follower=self_user)| Q(user=self_user) ).distinct().order_by('-timestamp').select_related('user')
            # we need posts where the post__user is the self_user), 
            # or where post__user__following is the self_user
            # a q lookup to get on posts to get the correct users
            # all follow objects where followee = self.user, get the post for the users
            # follow, need to update.
            postsFromDBList = generate_post_json_for_post_queryset(feed_posts,self_user)
            return JsonResponse({'status':'ok','postsFromDB':postsFromDBList},status=200)
        return JsonResponse({'status':'failed','message':"Auth token expected"},status=400)
    return JsonResponse({'status':'failed','message':"Bad Request"},status=405)

'''
Comment on get Feed view : 

another way of getting feed for current user can involve using .values() on the queryset to directly
get the dictionariesin the query set instead of model instances, only problem here is how the client
is right now expecting the api to be otherwise .values() is a much cleaner and shorter syntax than the above code, like here it will be longer, otherwise
it is much shorted no need to run for loops to create lists of dictionaries, like so
feed_posts = Post.objects.all().order_by('-timestamp').values('user__first_name',
                                                                          'user__last_name',
                                                                          'user__profile_image',
                                                                          'user__cover_image',
                                                                          'user__bio',
                                                                          'user__username',
                                                                          'content',
                                                                          'image',
                                                                          'is_media',
                                                                          'timestamp',
                                                                          'id')
            postsFromDBList = []
            postsFromDB = {}
            for post in feed_posts:
                new_post = {}
                user = {}
                user['first_name'] = post['user__first_name']
                user['last_name'] = post['user__last_name']
                user['profile_image'] = post['user__profile_image']
                user['cover_image'] = post['user__cover_image']
                user['bio'] = post['user__bio']
                user['username'] = post['user__username']
                user['full_name'] = f"{post['user__first_name']} { post['user__last_name']}"
                new_post['user'] = user
                new_post['content'] = post['content']
                new_post['image'] = post['image']
                new_post['is_media'] = 'true' if post['image'] else 'false'
                new_post['timestamp'] = post['timestamp']
                new_post['id']=post['id']
                postsFromDBList.append(new_post)
                
Using select_related for single db hit to get even the foreign key fields, and not 
do another db hit when calling post.user,
for e in Entry.objects.filter(pub_date__gt=timezone.now()).select_related('blog'):
    # Without select_related(), this would make a database query for each
    # loop iteration in order to fetch the related blog for each entry.
    blogs.add(e.blog)
'''

# The below view returns the profile data like posts, likes and media, for the profile page
# It is different from get profile details view , which returns username, image and bio

def get_profile_data(request):
    if request.method == "GET":
        if "HTTP_AUTH_TOKEN" in request.META:
            auth_token = request.META["HTTP_AUTH_TOKEN"]
            try:
                session = SessionStore(session_key=auth_token)
                self_user = User.objects.get(username=session['user_details']['username'])
            except:
                return JsonResponse({'status':'failed','message':"User not in session"},status=400)
            username = request.GET['username']
            user = User.objects.get(username=username)
            profile_posts = Post.objects.filter(user=user).order_by('-timestamp')
            postsFromDBList = generate_post_json_for_post_queryset(profile_posts,self_user)
            return JsonResponse({'status':'ok','profilePosts':postsFromDBList},status=200)
        return JsonResponse({'status':'failed','message':"Auth token expected"},status=400)
    return JsonResponse({'status':'failed','message':"Bad Request"},status=405)

def get_profile_media_posts(request):
    if request.method == "GET":
        if "HTTP_AUTH_TOKEN" in request.META:
            auth_token = request.META["HTTP_AUTH_TOKEN"]
            try:
                session = SessionStore(session_key=auth_token)
                self_user = User.objects.get(username=session['user_details']['username'])
            except:
                return JsonResponse({'status':'failed','message':"User not in session"},status=400)
            username = request.GET['username']
            user = User.objects.get(username=username)
            media_posts = Post.objects.filter(user=user,is_media=True).order_by('-timestamp')
            postsFromDBList = generate_post_json_for_post_queryset(media_posts,self_user)
            return JsonResponse({'status':'ok','mediaPosts':postsFromDBList},status=200)
        return JsonResponse({'status':'failed','message':"Auth token expected"},status=400)
    return JsonResponse({'status':'failed','message':"Bad Request"},status=405)

def get_post_detail(request):
    if request.method == "GET":
        if "HTTP_AUTH_TOKEN" in request.META:
            auth_token = request.META["HTTP_AUTH_TOKEN"]
            try:
                session = SessionStore(session_key=auth_token)
                self_user = User.objects.get(username=session['user_details']['username'])
            except:
                return JsonResponse({'status':'failed','message':"User not in session"},status=400)
            post_id = request.GET['post_id']
            post = Post.objects.get(id=post_id)
            post_di = generate_single_post_json(post,self_user)
            return JsonResponse({'status':'ok','post':post_di},status=200)
        return JsonResponse({'status':'failed','message':"Auth token expected"},status=400)
    return JsonResponse({'status':'failed','message':"Bad Request"},status=405)

@csrf_exempt
def bookmark_unbookmark_post(request):
    if request.method == "POST":
        if "HTTP_AUTH_TOKEN" in request.META:
            auth_token = request.META["HTTP_AUTH_TOKEN"]
            try:
                session = SessionStore(session_key=auth_token)
                self_user = User.objects.get(username=session['user_details']['username'])
            except:
                return JsonResponse({'status':'failed','message':"User not in session"},status=400)
            try:
                post = Post.objects.get(id=request.POST['post_id'])
            except Post.DoesNotExist:
                return JsonResponse({'status':'failed','message':"Post Id Expected"},status=400)
            try:
                old_bookmark = Bookmark.objects.get(post=post,user=self_user)
                old_bookmark.delete()
                return JsonResponse({'status':'removed','message':'Post removed from bookmarks.'},status=200)
            except Bookmark.DoesNotExist:
                Bookmark.objects.create(user=self_user,post=post)
                return JsonResponse({'status':'added','message':'Post added to bookmarks.'},status=200)
        return JsonResponse({'status':'failed','message':"Auth token expected"},status=400)
    return JsonResponse({'status':'failed','message':"Bad Request"},status=405)

def get_bookmarks(request):
    if request.method == "GET":
        if "HTTP_AUTH_TOKEN" in request.META:
            auth_token = request.META["HTTP_AUTH_TOKEN"]
            try:
                session = SessionStore(session_key=auth_token)
                self_user = User.objects.get(username=session['user_details']['username'])
            except:
                return JsonResponse({'status':'failed','message':"User not in session"},status=400)
            try:
                # get bookmarks for session  user here
                bookmarks = Post.objects.filter(bookmark__user=self_user)
                bookmarks_li = generate_post_json_for_post_queryset(bookmarks,self_user)
                return JsonResponse({'status':'ok','bookmarks':bookmarks_li},status=200) 
            except:
                return JsonResponse({'status':'failed','message':"Post Id Expected"},status=400)
        return JsonResponse({'status':'failed','message':"Auth token expected"},status=400)
    return JsonResponse({'status':'failed','message':"Bad Request"},status=405)

def generate_notifications_li(notifications):
    notifications_li = []
    for notification in notifications:
        generator_user = User.objects.get(username=notification.generator_username)
        notification_di = {}
        notification_di['id']=notification.id
        notification_di['type']=notification.type
        notification_di['text']=notification.text
        notification_di['userFullName']=f'{generator_user.first_name} {generator_user.last_name}'
        notification_di['postLink']=notification.parent_link
        notification_di['userProfileLink']=f'/{notification.generator_username}'
        notification_di['userProfilePhoto']=generator_user.profile_image
        notification_di['seen']=notification.seen
        notification_di['time']=notification.timestamp
        notifications_li.append(notification_di)
    return notifications_li

def get_notifications(request):
    if request.method == "GET":
        if "HTTP_AUTH_TOKEN" in request.META:
            auth_token = request.META["HTTP_AUTH_TOKEN"]
            try:
                session = SessionStore(session_key=auth_token)
                self_user = User.objects.get(username=session['user_details']['username'])
            except:
                return JsonResponse({'status':'failed','message':"User not in session"},status=400)
            try:
                # get notifications for session  user here
                notifications = self_user.notifications.all().order_by('-timestamp')
                notifications_li = generate_notifications_li(notifications)
                return JsonResponse({'status':'ok','notifications':notifications_li},status=200) 
            except:
                return JsonResponse({'status':'failed','message':"Invalid user session"},status=400)
        return JsonResponse({'status':'failed','message':"Auth token expected"},status=400)
    return JsonResponse({'status':'failed','message':"Bad Request"},status=405)

def mark_notification_read(request):
    if request.method == "GET":
        if "HTTP_AUTH_TOKEN" in request.META:
            auth_token = request.META["HTTP_AUTH_TOKEN"]
            try:
                session = SessionStore(session_key=auth_token)
                self_user = User.objects.get(username=session['user_details']['username'])
            except:
                return JsonResponse({'status':'failed','message':"User not in session"},status=400)
            try:
                # get notifications for session  user here
                notifications = self_user.notifications.filter(seen=False)
                for notif in notifications:
                    notif.seen = True
                    notif.save()
                return JsonResponse({'status':'ok','message':'All unread notifications are marked read.'},status=200) 
            except:
                return JsonResponse({'status':'failed','message':"Invalid user session"},status=400)
        return JsonResponse({'status':'failed','message':"Auth token expected"},status=400)
    return JsonResponse({'status':'failed','message':"Bad Request"},status=405)