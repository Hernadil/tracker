from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser, Project, ProjectMembership, VideoTitle,
    Log, LogVideoTitleAction, PhotoLogProgress, Expense
)

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "get_full_name", "email", "job_role", "is_boss", "is_active")
    list_filter = ("job_role", "is_boss", "is_active")
    fieldsets = UserAdmin.fieldsets + (
        ("Extra", {"fields": ("job_role", "phone_number", "is_boss")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Extra", {"fields": ("first_name", "last_name", "email", "job_role", "phone_number", "is_boss")}),
    )
    search_fields = ("username", "first_name", "last_name", "email")

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "project_type", "revenue", "main_deadline", "is_completed")
    list_filter = ("project_type", "is_completed")
    search_fields = ("title", "company")

@admin.register(ProjectMembership)
class ProjectMembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "project", "joined_at")
    list_filter = ("project",)

@admin.register(VideoTitle)
class VideoTitleAdmin(admin.ModelAdmin):
    list_display = ("title", "project", "created_by", "raw_uploaded", "editing_done")
    list_filter = ("project", "raw_uploaded", "editing_done")

@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ("user", "project", "date", "hours")
    list_filter = ("project", "user")

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("amount", "description", "date", "created_by")
    list_filter = ("date", "created_by")
    search_fields = ("description",)

admin.site.register(LogVideoTitleAction)
admin.site.register(PhotoLogProgress)
