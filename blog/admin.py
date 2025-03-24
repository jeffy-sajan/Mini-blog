from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Post, Comment, Profile, SavedPost

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ['date_posted']

    def get_queryset(self, request):
        return super().get_queryset(request).order_by('-date_posted')

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ['bio']

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'date_posted', 'comment_count']
    list_filter = ['date_posted', 'author']
    search_fields = ['title', 'content']
    date_hierarchy = 'date_posted'
    ordering = ['-date_posted']
    readonly_fields = ['date_posted']
    inlines = [CommentInline]

    def comment_count(self, obj):
        return obj.comments.count()
    comment_count.short_description = 'Comments'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['truncated_content', 'author', 'post', 'date_posted']
    list_filter = ['date_posted', 'author']
    search_fields = ['content', 'author__username', 'post__title']
    date_hierarchy = 'date_posted'
    ordering = ['-date_posted']
    readonly_fields = ['date_posted']

    def truncated_content(self, obj):
        return obj.content[:75] + '...' if len(obj.content) > 75 else obj.content
    truncated_content.short_description = 'Comment'

class SavedPostAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'date_saved')
    list_filter = ('date_saved',)
    search_fields = ('user__username', 'post__title')

admin.site.register(SavedPost, SavedPostAdmin)

# Unregister the default User admin and register our custom one
admin.site.unregister(User)

class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'first_name', 'last_name', 'post_count']
    list_filter = UserAdmin.list_filter
    inlines = [ProfileInline]
    
    def post_count(self, obj):
        return obj.post_set.count()
    post_count.short_description = 'Posts'

admin.site.register(User, CustomUserAdmin)
