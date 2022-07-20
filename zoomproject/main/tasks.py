from celery import shared_task
from zoomproject.celery import app
import json
from main.models import Meeting, Participant
import os

file_name = "log.json"

ADMIN_DOMAINS = ["vertexglobalservices.com", "vertexcosmos.com"]


def get_or_create_participant(meeting_info, meeting_obj):

    created = False
    recruiter = False

    participant_domain = meeting_info["participant"]["email"].split("@")[1]

    if participant_domain in ADMIN_DOMAINS or meeting_info["participant"]["email"] == "vertexglobalservices@gmail.com":
        recruiter = True

    participant = Participant.objects.filter(
        email=meeting_info["participant"]["email"],
        meeting__uuid=meeting_info["uuid"]
    ).first()

    if not participant:
        created = True
        participant = Participant.objects.create(
            email=meeting_info["participant"]["email"],
            name=meeting_info["participant"]["user_name"],
            meeting=meeting_obj,
            join_time=meeting_info["participant"]["join_time"],
            is_recruiter=recruiter
        )

    return participant, created, recruiter


def prepare_participant_data(file_dict, meeting_info, meeting_obj):
    file_dict["participant_user_id"] = meeting_info["participant"]["user_id"]
    file_dict["participant_user_name"] = meeting_info["participant"]["user_name"]
    file_dict["participant_id"] = meeting_info["participant"]["id"]
    file_dict["participant_email"] = meeting_info["participant"]["email"]
    file_dict["active_participant_count"] = meeting_obj.active_participant_count
    file_dict["active_recruiter_count"] = meeting_obj.active_recruiter_count
    file_dict["active_participant_breakout_count"] = meeting_obj.active_participant_breakout_count
    file_dict["active_recruiter_breakout_count"] = meeting_obj.active_recruiter_breakout_count
    return file_dict


@app.task(bind=True)
def handle_queue(self, request_data):
    print(f'Request: {self.request.id}')

    file_dict = dict()
    file_dict["event"] = request_data["event"]
    file_dict["event_ts"] = request_data["event_ts"]

    meeting_info = request_data["payload"]["object"]

    file_dict["meeting_uuid"] = meeting_info["uuid"]
    file_dict["meeting_id"] = meeting_info["id"]
    file_dict["meeting_duration"] = meeting_info["duration"]
    file_dict["meeting_host_id"] = meeting_info["host_id"]

    meeting_obj = Meeting.objects.filter(uuid=meeting_info["uuid"], meeting_id=meeting_info["id"]).first()

    if request_data["event"] == "meeting.started":

        if meeting_obj is None:
            meeting_obj = Meeting.objects.create(
                uuid=meeting_info["uuid"],
                meeting_id=meeting_info["id"],
                host_id=meeting_info["host_id"],
                account_id=request_data["payload"]["account_id"],
                start_time=meeting_info["start_time"],
                topic=meeting_info["topic"],
                duration=meeting_info["duration"]
            )

        file_dict["meeting_topic"] = meeting_info["topic"]
        file_dict["meeting_start_time"] = meeting_info["start_time"]

    elif request_data["event"] == "meeting.participant_joined":

        participant, created, recruiter = get_or_create_participant(meeting_info, meeting_obj)
        if created:
            if recruiter:
                meeting_obj.active_recruiter_count += 1
            else:
                meeting_obj.active_participant_count += 1
            meeting_obj.save()

        file_dict = prepare_participant_data(file_dict, meeting_info, meeting_obj)
        file_dict["participant_join_time"] = meeting_info["participant"]["join_time"]
        file_dict["participant_leave_time"] = ""

    elif request_data["event"] == "meeting.participant_left":

        participant, created, recruiter = get_or_create_participant(meeting_info, meeting_obj)
        if recruiter:
            meeting_obj.active_recruiter_count -= 1
        else:
            meeting_obj.active_participant_count -= 1

        meeting_obj.save()
        participant.leave_time = meeting_info["participant"]["leave_time"]
        participant.save()
        file_dict = prepare_participant_data(file_dict, meeting_info, meeting_obj)
        file_dict["participant_leave_time"] = meeting_info["participant"]["leave_time"]
        file_dict["participant_join_time"] = participant.join_time

    elif request_data["event"] == "meeting.participant_joined_breakout_room":

        participant, created, recruiter = get_or_create_participant(meeting_info, meeting_obj)

        if participant.is_recruiter:
            meeting_obj.active_recruiter_breakout_count += 1
        else:
            meeting_obj.active_participant_breakout_count += 1
        meeting_obj.save()

        file_dict["breakout_room_uuid"] = meeting_info["breakout_room_uuid"]
        file_dict = prepare_participant_data(file_dict, meeting_info, meeting_obj)
        file_dict["participant_join_time"] = meeting_info["participant"]["join_time"]

    elif request_data["event"] == "meeting.participant_left_breakout_room":

        participant, created, recruiter = get_or_create_participant(meeting_info, meeting_obj)

        if participant.is_recruiter:
            meeting_obj.active_recruiter_breakout_count -= 1
        else:
            meeting_obj.active_participant_breakout_count -= 1
        meeting_obj.save()

        file_dict["breakout_room_uuid"] = meeting_info["breakout_room_uuid"]
        file_dict = prepare_participant_data(file_dict, meeting_info, meeting_obj)
        file_dict["participant_leave_time"] = meeting_info["participant"]["leave_time"]

    elif request_data["event"] == "meeting.ended":
        meeting_obj.end_time = meeting_info["end_time"]
        meeting_obj.save()

        file_dict["meeting_topic"] = meeting_info["topic"]
        file_dict["meeting_end_time"] = meeting_info["end_time"]

    with open(file_name, "a") as file:
        file.write(f"{json.dumps(file_dict)}\n")
        file.close()

    print(f"Task completed: {self.request.id}")
