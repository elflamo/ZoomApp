from django.db import models


class CreatedModified(models.Model):

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Meeting(CreatedModified):

    uuid = models.CharField(max_length=100, unique=True, primary_key=True)
    meeting_id = models.CharField(max_length=20)
    host_id = models.CharField(max_length=100)
    account_id = models.CharField(max_length=100)
    start_time = models.CharField(max_length=100)
    end_time = models.CharField(max_length=100, null=True, blank=True)
    topic = models.TextField()
    duration = models.IntegerField()
    active_participant_count = models.IntegerField(default=0)
    active_recruiter_count = models.IntegerField(default=0)
    active_participant_breakout_count = models.IntegerField(default=0)
    active_recruiter_breakout_count = models.IntegerField(default=0)

    class Meta:
        db_table = "meeting"


class Participant(CreatedModified):
    participant_id = models.CharField(max_length=100, unique=True)
    email = models.EmailField(null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)
    join_time = models.CharField(max_length=100)
    leave_time = models.CharField(max_length=100, null=True, blank=True)
    is_recruiter = models.BooleanField(default=False)
    in_breakout_room = models.BooleanField(default=False)

    class Meta:
        db_table = "participant"
