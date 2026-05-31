from rest_framework import serializers
from .models import Run
from django.contrib.auth.models import User


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

        run_finished_all = Run.objects.filter(status='finished')
        return run_finished_all.filter(athlete__id=obj.id).count()
        # user = User.objects.get(id=obj.id)
        # return user.run_set.filter(status='finished').count()
        # return Run.objects.filter(status='finished', athlete__id=obj.id).count()