from django.db import models
from django.conf import settings
from shared.models import CustomUser
import os
from uuid import uuid4

def chat_file_upload(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid4().hex}.{ext}"
    return os.path.join('chat_files', filename)

class Thread(models.Model):
    THREAD_TYPE = (
        ('direct', 'Direct'),
        ('group', 'Group'),
    )
    
    participants = models.ManyToManyField(CustomUser, related_name='threads')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    thread_type = models.CharField(max_length=10, choices=THREAD_TYPE, default='direct')
    name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['-updated']

    def __str__(self):
        if self.thread_type == 'direct' and self.participants.count() == 2:
            users = list(self.participants.all())
            return f"{users[0].name} and {users[1].name}"
        return self.name or f"Thread {self.id}"
    
    def get_other_participants(self, current_user):
        """Return participants excluding the current user"""
        return self.participants.exclude(id=current_user.id)
    
    def get_display_name(self, current_user):
        """Get display name for the thread"""
        if self.thread_type == 'direct' and self.participants.count() == 2:
            other_user = self.get_other_participants(current_user).first()
            return other_user.name if other_user else "Unknown"
        return self.name or ", ".join([u.name for u in self.get_other_participants(current_user)])
    
    def get_display_avatar(self, current_user):
        """Get avatar for display"""
        if self.thread_type == 'direct' and self.participants.count() == 2:
            other_user = self.get_other_participants(current_user).first()
            return other_user.avatar if other_user and other_user.avatar else None
        return None

class Message(models.Model):
    MESSAGE_TYPE = (
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('document', 'Document'),
        ('call', 'Call'),
    )
    
    CALL_STATUS = (
        ('missed', 'Missed'),
        ('answered', 'Answered'),
        ('rejected', 'Rejected'),
    )
    
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to=chat_file_upload, blank=True, null=True)
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPE, default='text')
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    # For call messages
    call_duration = models.PositiveIntegerField(null=True, blank=True)
    call_status = models.CharField(max_length=10, choices=CALL_STATUS, null=True, blank=True)

    class Meta:
        ordering = ['sent_at']

    def __str__(self):
        return f"{self.sender.name}: {self.content or self.get_message_type_display()}"

class UserStatus(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='chat_status')
    online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.name} - {'Online' if self.online else 'Offline'}"