from elasticsearch import Elasticsearch, helpers

es = Elasticsearch("http://localhost:9200")

print(es.info())

resp = es.index(
 index='common_index',
 document={"event": "meeting.participant_joined", "event_ts": 1657537430837, "meeting_uuid": "r1MDHHJ+SzOaOU1QfjPezQ==", "meeting_id": "98094723551", "meeting_duration": 60, "meeting_host_id": "AyqzcWT1RPO_3trrzLKEXw", "participant_user_id": "16780288", "participant_user_name": "Danish Arora", "participant_id": "kqQf38nMTgCE6aFvhqyrZw", "participant_email": "danish@gmail.com", "participant_join_time": "2022-07-11T11:03:47Z", "is_recruiter": False},
)

print(resp)

# resp = es.indices.delete(index='meeting.participant_joined')

print(resp)
