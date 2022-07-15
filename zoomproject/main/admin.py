from django.contrib import admin
from main.models import Participant, Meeting


class MeetingAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'start_time', 'end_time', 'topic', 'active_participant_count', 'active_recruiter_count',
                    'active_participant_breakout_count', 'active_recruiter_breakout_count')


class ParticipantsAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'name', 'join_time', 'leave_time', 'is_recruiter', 'in_breakout_room')


admin.site.register(Meeting, MeetingAdmin)
admin.site.register(Participant, ParticipantsAdmin)
