from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Subquery, OuterRef
from django.http import JsonResponse
from .models import Thread, Message, UserStatus
from .forms import MessageForm, NewThreadForm
from shared.models import CustomUser
from user.models import StudentProfile
from user.models import StaffProfile
import json
from .forms import MessageForm

@login_required
def chat_home(request):
    # Get the latest message for each thread
    latest_message = Message.objects.filter(
        thread=OuterRef('pk')
    ).order_by('-sent_at')
    
    threads = (
    Thread.objects.filter(
        participants=request.user
    )
    .prefetch_related('participants')  
    .annotate(
        last_message=Subquery(latest_message.values('content')[:1]),
        last_message_time=Subquery(latest_message.values('sent_at')[:1])
    )
    .order_by('-last_message_time')
)

    
    # Get unread count for each thread
    for thread in threads:
        # Add display properties
        thread.display_name = thread.get_display_name(request.user)
        thread.display_avatar = thread.get_display_avatar(request.user)
        thread.unread_count = Message.objects.filter(
            thread=thread,
            is_read=False
        ).exclude(sender=request.user).count()
    
    return render(request, 'chat/chat_home.html', {
        'threads': threads,
    })

@login_required
def thread_detail(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id, participants=request.user)
    
    # Mark messages as read
    Message.objects.filter(thread=thread, is_read=False).exclude(sender=request.user).update(is_read=True)
    
    messages = thread.messages.all().order_by('sent_at')
       
    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.thread = thread
            message.sender = request.user
            
            # Determine message type based on file
            if message.file:
                ext = message.file.name.split('.')[-1].lower()
                if ext in ['jpg', 'jpeg', 'png', 'gif']:
                    message.message_type = 'image'
                elif ext in ['mp4', 'mov', 'avi']:
                    message.message_type = 'video'
                elif ext in ['mp3', 'wav']:
                    message.message_type = 'audio'
                else:
                    message.message_type = 'document'
            
            message.save()
            return redirect('thread_detail', thread_id=thread_id)
    else:
        form = MessageForm()
    
    thread.display_name = thread.get_display_name(request.user)
    thread.display_avatar = thread.get_display_avatar(request.user)
    
    return render(request, 'chat/thread_detail.html', {
        'thread': thread,
        'messages': messages,
        'form': form
    })

@login_required
def start_thread(request):
    if request.method == 'POST':
        form = NewThreadForm(request.POST, user=request.user)
        if form.is_valid():
            thread = form.save(commit=False)
            
            # For direct messages, ensure only 2 participants
            participants = form.cleaned_data['participants']
            if not thread.name and participants.count() == 1:
                thread.thread_type = 'direct'
            
            thread.save()
            thread.participants.add(request.user)
            thread.participants.add(*participants)
            
            return redirect('thread_detail', thread_id=thread.id)
    
    return redirect('chat_home')

@login_required
def search_users(request):
    query = request.GET.get('q', '')
    
    # Search by name, username, or roll number
    users = CustomUser.objects.filter(
        Q(name__icontains=query) | 
        Q(username__icontains=query) |
        Q(student_profile__roll_no__icontains=query)
    ).exclude(id=request.user.id).distinct()[:10]
    
    results = []
    for user in users:
        try:
            if user.groups.filter(name='student').exists():
                profile = user.student_profile
                identifier = f"Roll: {profile.roll_no}" if profile.roll_no else "Student"
            elif user.groups.filter(name='staff').exists():
                profile = user.staff_profile
                identifier = profile.department.name if profile.department else "Staff"
            else:
                identifier = "User"
        except:
            identifier = "User"
        
        results.append({
            'id': user.id,
            'name': user.name,
            'username': user.username,
            'identifier': identifier,
            'avatar_url': user.avatar.url if user.avatar else '/static/default_avatar.png'
        })
    
    return JsonResponse({'results': results})

@login_required
def update_user_status(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        online = data.get('online', False)
        
        status, created = UserStatus.objects.get_or_create(user=request.user)
        status.online = online
        status.save()
        
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)