from django.contrib import admin
from .models import *
# Register your models here.

# class PostLikeAdmin(admin.TabularInline):
#     model = PostLike
    
# class PostAdmin(admin.ModelAdmin):
#     inlines = [PostLikeAdmin]
#     list_display = ['__str__','user']
#     search_fields = ['content','user__username','user__email']
    
#     class Meta:
#         model = Post

admin.site.register(User)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(Activity)
admin.site.register(Follow)
admin.site.register(Bookmark)
admin.site.register(Notification)


