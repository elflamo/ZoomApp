from django.contrib import admin
from main.models import Participant, Meeting, Recruiter, ZoomToken


class MeetingAdmin(admin.ModelAdmin):
    list_display = (
        'uuid', 'topic', 'active_participant_count', 'active_recruiter_count', 'active_participant_breakout_count',
        'active_recruiter_breakout_count', 'start_time', 'end_time'
    )


class ParticipantsAdmin(admin.ModelAdmin):
    list_display = (
        'participant_id', 'name', 'is_recruiter', 'in_breakout_room', 'get_meeting', 'join_time', 'leave_time'
    )

    def get_meeting(self, obj):
        return f'{obj.meeting.topic} : {obj.meeting.meeting_id}'

    get_meeting.short_description = 'Meeting'


admin.site.register(Meeting, MeetingAdmin)
admin.site.register(Participant, ParticipantsAdmin)
admin.site.register(ZoomToken)
admin.site.register(Recruiter)
