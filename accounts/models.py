from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    """
    Extends the built-in Django User model with a role field.
    Roles:
    - 'admin': Can create/manage topics, questions, quizzes, and view all student analytics.
    - 'student': Can attempt quizzes, view scores, and track personal performance.
    """
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('admin', 'Admin'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_admin_user(self):
        """Check if user has admin privileges in the portal."""
        return self.role == 'admin' or self.user.is_superuser or self.user.is_staff

    def is_student_user(self):
        """Check if user has student role."""
        return self.role == 'student'

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Signal receiver that automatically creates a Profile whenever a new User is created.
    If superuser is created, automatically sets role to admin.
    """
    if created:
        role = 'admin' if instance.is_superuser or instance.is_staff else 'student'
        Profile.objects.create(user=instance, role=role)
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()
