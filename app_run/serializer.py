from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.status import HTTP_400_BAD_REQUEST

from .models import Run, AthleteInfo, Challenge, Position, CollectibleItem
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Max, Min, Count, Q

class AthleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'last_name', 'first_name']


class RunSerializer(serializers.ModelSerializer):
    athlete_data = AthleteSerializer(source='athlete', read_only=True)

    class Meta:
        model = Run
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    runs_finished = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'date_joined', 'username', 'last_name', 'first_name', 'type', 'runs_finished']

    def get_type(self, obj):
        return 'coach' if obj.is_staff else 'athlete'

    def get_runs_finished(self,obj):
    #     # run_finished_all = Run.objects.filter(status='finished')
    #     # return run_finished_all.filter(athlete__id=obj.id).count()
    #     # # user = User.objects.get(id=obj.id)
    #     # # return user.run_set.filter(status='finished').count()
    #     # return Run.objects.select_related('athlete').filter(status='finished', athlete__id=obj.id).count()
        return obj.__dict__['runs_finished']
        # return Run.objects.filter(status='finished', athlete__id=obj.id).count()

class UserDetailSerializer(UserSerializer):
    items = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        model = User
        fields = ['items']

    def get_items(self, obj):
        items = obj.collectibleitems.all()
        serializer = CollectibleItemSerializer(items, many=True)
        return serializer.data



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

    class Meta:
        model = Position
        fields = '__all__'

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