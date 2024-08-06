import redis
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
from participants.models import Participant, HoleScore
from events.models import Event

# Redis 클라이언트 설정
redis_client = redis.StrictRedis(host='redis', port=6379, db=0)

@database_sync_to_async
def get_participant(participant_id):
    try:
        return Participant.objects.get(id=participant_id)
    except Participant.DoesNotExist:
        return None

@database_sync_to_async
def get_event(event_id):
    try:
        return Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return None

@database_sync_to_async
def check_event_exists(event_id):
    return Event.objects.filter(id=event_id).exists()

@database_sync_to_async
def update_participant_sum_score_in_db(participant_id, sum_score):
    Participant.objects.filter(id=participant_id).update(sum_score=sum_score)

@database_sync_to_async
def update_or_create_hole_score_in_db(participant_id, hole_number, score):
    HoleScore.objects.update_or_create(
        participant_id=participant_id,
        hole_number=hole_number,
        defaults={'score': score}
    )

@database_sync_to_async
def get_group_participants(event_id, group_type=None):
    if group_type is not None:
        return Participant.objects.filter(event_id=event_id, group_type=group_type)
    return Participant.objects.filter(event_id=event_id)

@database_sync_to_async
def get_all_participants(event_id):
    return Participant.objects.filter(event_id=event_id)

async def get_all_hole_scores_from_redis(participant_id):
    keys_pattern = f'participant:{participant_id}:hole:*'
    keys = await sync_to_async(redis_client.keys)(keys_pattern)
    hole_scores = []
    for key in keys:
        hole_number = int(key.decode('utf-8').split(':')[-1])
        score = int(await sync_to_async(redis_client.get)(key))
        hole_scores.append({'hole_number': hole_number, 'score': score})
    return hole_scores

async def update_hole_score_in_redis(participant_id, hole_number, score):
    key = f'participant:{participant_id}:hole:{hole_number}'
    await sync_to_async(redis_client.set)(key, score)

async def update_participant_sum_score(participant_id):
    keys_pattern = f'participant:{participant_id}:hole:*'
    keys = await sync_to_async(redis_client.keys)(keys_pattern)

    sum_score = 0
    for key in keys:
        score = await sync_to_async(redis_client.get)(key)
        sum_score += int(score)

    await update_participant_sum_score_in_db(participant_id, sum_score)