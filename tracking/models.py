from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db.models import Sum


class CustomUser(AbstractUser):
    JOB_ROLES = [
        ('iro', 'Forgatókönyv Író'),
        ('fotos', 'Fotós'),
        ('videos', 'Videós'),
        ('vago', 'Vágó'),
    ]
    job_role = models.CharField(max_length=20, choices=JOB_ROLES, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    is_boss = models.BooleanField(default=False)

    def get_job_role_display_hu(self):
        mapping = {'iro': 'Forgatókönyv Író', 'fotos': 'Fotós', 'videos': 'Videós', 'vago': 'Vágó'}
        return mapping.get(self.job_role, '-')

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_job_role_display_hu()})"


class Project(models.Model):
    PROJECT_TYPES = [
        ('video', 'Videós projekt'),
        ('photo', 'Fotós projekt'),
        ('both', 'Mindkettő'),
    ]
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    revenue = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    project_type = models.CharField(max_length=10, choices=PROJECT_TYPES, default='video')
    location = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    required_video_count = models.PositiveIntegerField(default=0)

    max_writer_count = models.PositiveIntegerField(default=0)
    max_photographer_count = models.PositiveIntegerField(default=0)
    max_videographer_count = models.PositiveIntegerField(default=0)
    max_editor_count = models.PositiveIntegerField(default=0)

    pay_writer = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    pay_photographer = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    pay_videographer = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    pay_editor = models.DecimalField(max_digits=12, decimal_places=0, default=0)

    writer_deadline = models.DateField(blank=True, null=True)
    editor_deadline = models.DateField(blank=True, null=True)
    videographer_date = models.DateField(blank=True, null=True)
    photo_onsite_date = models.DateField(blank=True, null=True)
    photo_editing_deadline = models.DateField(blank=True, null=True)

    onsite_hours = models.PositiveIntegerField(default=0)
    total_hours_expected = models.PositiveIntegerField(default=0)

    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        'CustomUser', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='created_projects'
    )

    @property
    def is_expired(self):
        today = timezone.now().date()
        deadlines = []
        if self.project_type in ('video', 'both'):
            if self.editor_deadline: deadlines.append(self.editor_deadline)
            if self.writer_deadline: deadlines.append(self.writer_deadline)
        if self.project_type in ('photo', 'both'):
            if self.photo_editing_deadline: deadlines.append(self.photo_editing_deadline)
        return today > max(deadlines) if deadlines else False

    @property
    def is_active(self):
        return not self.is_expired and not self.is_completed

    @property
    def main_deadline(self):
        deadlines = []
        if self.editor_deadline: deadlines.append(self.editor_deadline)
        if self.writer_deadline: deadlines.append(self.writer_deadline)
        if self.photo_editing_deadline: deadlines.append(self.photo_editing_deadline)
        return max(deadlines) if deadlines else None

    def total_logged_hours(self):
        return self.logs.aggregate(total=Sum('hours'))['total'] or 0

    def user_logged_hours(self, user):
        return self.logs.filter(user=user).aggregate(total=Sum('hours'))['total'] or 0

    def completion_percentage_for_user(self, user):
        if user.job_role == 'iro':
            total = self.required_video_count
            if total == 0:
                return 0
            done = self.video_titles.count()
            return min(int((done / total) * 100), 100)
        if user.job_role == 'videos':
            total = self.video_titles.count()
            if total == 0:
                return 0
            done = self.video_titles.filter(raw_uploaded=True).count()
            return min(int((done / total) * 100), 100)
        if user.job_role == 'vago':
            total = self.video_titles.count()
            if total == 0:
                return 0
            done = self.video_titles.filter(editing_done=True).count()
            return min(int((done / total) * 100), 100)
        if user.job_role == 'fotos':
            last_log = self.logs.filter(user=user).order_by('-date').first()
            if not last_log or not hasattr(last_log, 'photo_progress'):
                return 0
            p = last_log.photo_progress
            return 100 if (p.fieldwork_done and p.editing_done) else 0
        return 0

    def role_max_for(self, role):
        return {
            'iro': self.max_writer_count,
            'fotos': self.max_photographer_count,
            'videos': self.max_videographer_count,
            'vago': self.max_editor_count,
        }.get(role, 0)

    def role_pay_for(self, role):
        return {
            'iro': self.pay_writer,
            'fotos': self.pay_photographer,
            'videos': self.pay_videographer,
            'vago': self.pay_editor,
        }.get(role, 0)

    def role_slots_taken(self, role):
        return self.memberships.filter(user__job_role=role).count()

    def role_has_capacity(self, role):
        max_count = self.role_max_for(role)
        return max_count > self.role_slots_taken(role)

    def is_writer_team_done(self):
        if self.project_type not in ('video', 'both'):
            return True
        if self.required_video_count <= 0:
            return False
        return self.video_titles.count() >= self.required_video_count

    def is_videographer_team_done(self):
        if self.project_type not in ('video', 'both'):
            return True
        total = self.video_titles.count()
        if total == 0:
            return False
        return self.video_titles.filter(raw_uploaded=True).count() == total

    def is_editor_team_done(self):
        if self.project_type not in ('video', 'both'):
            return True
        total = self.video_titles.count()
        if total == 0:
            return False
        return self.video_titles.filter(editing_done=True).count() == total

    def is_boss_done_videos(self):
        """Boss jelzés: összes video_title kiyomva-e a vágó által"""
        if self.project_type not in ('video', 'both'):
            return True
        return (
            self.is_writer_team_done()
            and self.is_videographer_team_done()
            and self.is_editor_team_done()
        )

    def is_boss_done_photos(self):
        """Boss jelzés: összes fotósnak mindkét processt kitöltötten-e"""
        if self.project_type not in ('photo', 'both'):
            return True  # Ha nincs fotó, akkor "done" ebből a szempontból
        
        # Meg kell nézni az összes fotónál a logok photo_progress-t
        photo_users = CustomUser.objects.filter(memberships__project=self, job_role='fotos').distinct()
        if not photo_users.exists():
            return False
        for user in photo_users:
            last_log = self.logs.filter(user=user).order_by('-date').first()
            if not last_log or not hasattr(last_log, 'photo_progress'):
                return False
            p = last_log.photo_progress
            if not (p.fieldwork_done and p.editing_done):
                return False
        return True

    def is_boss_done(self):
        """Boss jelzés: a projekt végzett-e (videó és/vagy fotó feltételei teljesültek)"""
        # Videó projekt típusok
        video_check = self.is_boss_done_videos()
        # Fotó projekt típusok
        photo_check = self.is_boss_done_photos()
        
        # Mindkettő feltételének teljesülnie kell az adott típushoz
        return video_check and photo_check

    def __str__(self):
        return f"{self.title} – {self.company}"


class ProjectMembership(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='memberships')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='memberships')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'project')

    def __str__(self):
        return f"{self.user} @ {self.project}"


class VideoTitle(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='video_titles')
    title = models.CharField(max_length=500)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='created_titles')
    created_at = models.DateTimeField(auto_now_add=True)

    raw_uploaded = models.BooleanField(default=False)
    raw_uploaded_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='uploaded_titles')
    raw_uploaded_at = models.DateTimeField(null=True, blank=True)

    editing_done = models.BooleanField(default=False)
    editing_done_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='edited_titles')
    editing_done_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} ({self.project.title})"


class Log(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='logs')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='logs')
    date = models.DateTimeField(auto_now_add=True)
    hours = models.DecimalField(max_digits=5, decimal_places=1)
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Log: {self.user} @ {self.project} – {self.hours}h"


class LogVideoTitleAction(models.Model):
    log = models.ForeignKey(Log, on_delete=models.CASCADE, related_name='video_title_actions')
    video_title = models.ForeignKey(VideoTitle, on_delete=models.CASCADE, related_name='log_actions')
    action_type = models.CharField(max_length=20, choices=[('filmed', 'Leforgatva'), ('edited', 'Megvágva')])

    class Meta:
        unique_together = ('log', 'video_title', 'action_type')


class PhotoLogProgress(models.Model):
    log = models.OneToOneField(Log, on_delete=models.CASCADE, related_name='photo_progress')
    fieldwork_done = models.BooleanField(default=False)
    editing_done = models.BooleanField(default=False)

    def __str__(self):
        return f"Photo progress for log {self.log.id}"


class Expense(models.Model):
    amount = models.DecimalField(max_digits=12, decimal_places=0)
    description = models.CharField(max_length=255)
    date = models.DateField(auto_now_add=True)
    created_by = models.ForeignKey(
        'CustomUser', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='created_expenses'
    )

    def __str__(self):
        return f"Kiadás: {self.amount} Ft - {self.description}"
