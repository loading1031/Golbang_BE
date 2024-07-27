'''
MVP demo ver 0.0.4
2024.07.27
events/serializers.py

역할:
Django REST Framework에서 데이터의 직렬화(Serialization)와 역직렬화(Deserialization)를 처리하는 역할로
이벤트(Event) 모델에 대한 직렬화(Serialization) 로직을 정의
기능:
- 이벤트를 JSON 형식으로 변환
- 모임 생성 / 조회 Serializer 구현
'''

# events/serializers.py
from django.db import transaction
from django.db.models import Q
from rest_framework import serializers

from clubs.models import ClubMember, Club
from .models import Event
from participants.serializers import ParticipantCreateSerializer, ParticipantDetailSerializer


class EventCreateSerializer(serializers.ModelSerializer):
    event_id = serializers.PrimaryKeyRelatedField(source='id', read_only=True)
    participants = ParticipantCreateSerializer(source='participant_set', many=True)
    club_id = serializers.PrimaryKeyRelatedField(
        queryset=Club.objects.all(),
        write_only=True,
        required=True,
        source='club'
    )
    member_id = serializers.PrimaryKeyRelatedField(
        queryset=ClubMember.objects.all(),
        write_only=True,
        required=False,
        source='club_member'
    )

    class Meta:
        model = Event
        fields = ['event_id', 'club_id', 'member_id', 'participants', 'event_title', 'location',
                  'start_date_time', 'end_date_time', 'repeat_type', 'game_mode', 'alert_date_time']
        # club_id: param으로 받는 값도 추가해야한다. param -> view (request data에 param 데이터 추가) -> serial

    def create(self, validated_data):
        with transaction.atomic():
            participant_data = validated_data.pop('participant_set', [])
            #  이유 불명, member_id를 이벤트 객체 생성시 param으로든 입력받으면,
            #  validated_data.pop('participants_set',[])에서 clubMember(id)가 아닌 ClubMember 객체로 바뀜

            event = Event.objects.create(**validated_data)

            # 이벤트 ID를 이용해 각 참가자의 이벤트 필드를 설정
            for participant in participant_data:
                participant['event_id']  = event.pk
                participant['member_id'] = participant['club_member'].pk  # 객체에서 다시 pk로 변경
                participant_serializer   = ParticipantCreateSerializer(data=participant)
                if participant_serializer.is_valid(raise_exception=True):
                    participant_serializer.save()
            return event


class EventDetailSerializer(serializers.ModelSerializer):
    participants = ParticipantDetailSerializer(source='participant_set', many=True, read_only=True)
    event_id = serializers.PrimaryKeyRelatedField(source='id', read_only=True)
    member_id = serializers.PrimaryKeyRelatedField(
        queryset=ClubMember.objects.all(),
        required=True,
        source='club_member'
    )
    participants_count = serializers.SerializerMethodField(read_only=True)
    party_count = serializers.SerializerMethodField(read_only=True)
    accept_count = serializers.SerializerMethodField(read_only=True)
    deny_count = serializers.SerializerMethodField(read_only=True)
    pending_count = serializers.SerializerMethodField(read_only=True)
    #TODO: 토큰에서 user_Id 추출하고, 이벤트에서 속한 조, 같은 조 인원을 반환하는 필드 2개 추가해야함
    member_group = serializers.SerializerMethodField(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    date = serializers.DateField(write_only=True, required=False)
    status_type = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Event
        fields = ['event_id', 'member_id', 'participants', 'participants_count', 'party_count','accept_count',
                  'deny_count', 'pending_count', 'event_title', 'location', 'start_date_time', 'end_date_time',
                  'repeat_type', 'game_mode', 'alert_date_time', 'member_group',
                  'user_id', 'date', 'status_type']

    def get_participants_count(self, obj):
        return obj.participant_set.count()
    def get_party_count(self, obj):
        return obj.participant_set.filter(status_type="PARTY").count()
    def get_accept_count(self, obj):
        return obj.participant_set.filter(Q(status_type="ACCEPT") | Q(status_type="PARTY")).count()
    def get_deny_count(self, obj):
        return obj.participant_set.filter(status_type="DENY").count()
    def get_pending_count(self, obj):
        return obj.participant_set.filter(status_type="PENDING").count()
    def get_member_group(self, obj):
        return self.context.get('group_type')


