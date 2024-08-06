import json
import redis
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from participants.socket.utils import (
    check_event_exists,
    get_all_hole_scores_from_redis,
    get_all_participants,
    update_or_create_hole_score_in_db
)
# Redis 클라이언트 설정
redis_client = redis.StrictRedis(host='redis', port=6379, db=0)
class EventParticipantConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.event_id = self.scope['url_route']['kwargs']['event_id']
            if not await check_event_exists(self.event_id):
                raise ValueError('이벤트가 존재하지 않습니다.')

            self.group_name = self.get_event_group_name(self.event_id)

            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()

            # 주기적으로 스코어를 전송하는 태스크를 설정
            self.send_task = asyncio.create_task(self.send_scores_periodically())
        except ValueError as e:
            await self.send_json({'error': str(e)})
            await self.close()

    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
            await self.transfer_scores_to_mysql()
            self.send_task.cancel()  # 주기적인 태스크 취소
        except Exception as e:
            pass

    @staticmethod
    def get_event_group_name(event_id):
        return f"event_{event_id}_group_all"

    async def transfer_scores_to_mysql(self):
        keys_pattern = f'participant:{self.participant_id}:hole:*'
        keys = await sync_to_async(redis_client.keys)(keys_pattern)

        async def update_or_create_hole_score(key):
            hole_number = int(key.decode('utf-8').split(':')[-1])
            score = int(await sync_to_async(redis_client.get)(key))

            await update_or_create_hole_score_in_db(self.participant_id, hole_number, score)

        await asyncio.gather(*(update_or_create_hole_score(key) for key in keys))

        if keys:
            await sync_to_async(redis_client.delete)(*keys)

    async def send_scores(self, participants):
        try:
            all_scores = []
            for participant in participants:
                hole_scores = await get_all_hole_scores_from_redis(participant.id)
                all_scores.append({
                    'participant_id': participant.id,
                    'scores': hole_scores
                })
            await self.send_json(all_scores)
        except Exception as e:
            await self.send_json({'error': '스코어 기록을 가져오는 데 실패했습니다.', 'details': str(e)})

    async def send_scores_periodically(self):
        while True:
            try:
                participants = await get_all_participants(self.event_id)
                await self.send_scores(participants)
            except Exception as e:
                await self.send_json({'error': '주기적인 스코어 전송 실패', 'details': str(e)})
            await asyncio.sleep(10)  # 10초마다 주기적으로 스코어 전송

    async def send_json(self, content):
        await self.send(text_data=json.dumps(content))