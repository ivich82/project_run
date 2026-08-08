from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from .models import Run, AthleteInfo, Challenge, Position, CollectibleItem, Subscribe
from django.contrib.auth.models import User
from django.db.models import Sum, Max, Min, Count, Q, Avg

class AthleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'last_name', 'first_name']


class RunSerializer(serializers.ModelSerializer):
    athlete_data = AthleteSerializer(source='athlete', read_only=True)
    speed = serializers.SerializerMethodField()

    class Meta:
        model = Run
        fields = '__all__'

    def get_speed(self, obj):
        return round(obj.speed, 2) if obj.speed else obj.speed

class UserSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    runs_finished = serializers.IntegerField()
    rating = serializers.FloatField()

    class Meta:
        model = User
        fields = ['id', 'date_joined', 'username', 'last_name', 'first_name', 'type', 'runs_finished', 'rating']

    def get_type(self, obj):
        return 'coach' if obj.is_staff else 'athlete'

    # def get_runs_finished(self,obj):
    #     # annotated_queryset = User.objects.annotate(
    #     #     runs_finished=Count('run', filter=Q(run__status='finished'))
    #     # )
    #     return getattr(obj, 'runs_finished', 0)
        # return annotated_queryset.get(id=obj.id).runs_finished

class AthleteDetailSerializer(UserSerializer):
    items = serializers.SerializerMethodField()
    coach = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        model = User
        fields = UserSerializer.Meta.fields + ['items',  'coach']

    def get_items(self, obj):
        items = obj.collectibleitems.all()
        serializer = CollectibleItemSerializer(items, many=True)
        return serializer.data


    def get_coach(self, obj):
        subscribe = Subscribe.objects.filter(athlete_id=obj.id).first()
        return subscribe.coach_id if subscribe else None


class CoachDetailSerializer(UserSerializer):
    items = serializers.SerializerMethodField()
    athletes = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        model = User
        fields = UserSerializer.Meta.fields + ['items',  'athletes']

    def get_items(self, obj):
        items = obj.collectibleitems.all()
        serializer = CollectibleItemSerializer(items, many=True)
        return serializer.data


    def get_athletes(self, obj):
        subscribe = Subscribe.objects.filter(coach_id=obj.id)
        return list(map(lambda x: x.athlete_id, subscribe)) if subscribe.exists() else None



class AthleteInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = AthleteInfo
        fields = ['goals', 'weight', 'user_id']
        read_only_fields = ['user_id']

    def validate_weight(self, value):
        if not 0 < value < 900 :
            raise serializers.ValidationError('not correct wiegth')

        return value

class ChallengeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Challenge
        fields = ['athlete', 'full_name']
        read_only_fields = ['athlete']

class PositionSerializer(serializers.ModelSerializer):
    date_time = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S.%f')
    speed = serializers.SerializerMethodField()
    distance = serializers.SerializerMethodField()

    class Meta:
        model = Position
        fields = ['id', 'run', 'latitude', 'longitude', 'date_time', 'speed', 'distance']

    def validate_run(self, value):
        try:
            run = Run.objects.get(id=value)
            if not run.status == 'in_progress':
                raise serializers.ValidationError('HTTP_400_BAD_REQUEST')
        except Run.DoesNotExist:
            raise serializers.ValidationError('HTTP_400_BAD_REQUEST')
        return value

    def validate_latitude(self, value):
        if not -90 <= value <= 90:
            raise serializers.ValidationError('HTTP_400_BAD_REQUEST')
        return value

    def validate_longitude(self, value):
        if not -180 <= value <= 180:
            raise serializers.ValidationError('HTTP_400_BAD_REQUEST')
        return value

    def get_speed(self, obj):
        return round(obj.speed, 2) if obj.speed else obj.speed

    def get_distance(self, obj):
        return round(obj.distance, 2) if obj.distance else obj.distance

class CollectibleItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectibleItem
        fields = ['name', 'uid', 'latitude', 'longitude', 'picture', 'value']

    def validate_longitude(self, value):
        try:
            float(value)
            return float(value)
        except:
            return value

    def validate_latitude(self, value):
        try:
            float(value)
            return float(value)
        except:
            return value

class SubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscribe
        fields = ['athlete', 'coach', 'rating']

    def validate_athlete(self, value):

        if value.is_staff:
            raise serializers.ValidationError()
        return value

    def validate_coach(self, value):

        if not value.is_staff:
            raise serializers.ValidationError()
        return value

class Analytics_for_coachSerializer(serializers.ModelSerializer):
    longest_run_value = serializers.FloatField()
    total_run_value = serializers.FloatField()
    speed_avg_value = serializers.FloatField()
    class Meta:
        model = Subscribe
        fields = ['athlete', 'longest_run_value', 'total_run_value', 'speed_avg_value']

    def get_longest_run_value(self, obj):
        return obj.is_longest_run_value if obj.is_longest_run_value != None else 0.0
