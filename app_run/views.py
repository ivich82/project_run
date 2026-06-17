from wsgiref import headers

from django.contrib.sessions import serializers
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from .models import Run, AthleteInfo, Challenge, Position
from .serializer import RunSerializer, UserSerializer, AthleteInfoSerializer, ChallengeSerializer, PositionSerializer
from django.contrib.auth.models import User
from rest_framework.filters import  SearchFilter
from rest_framework.views import APIView
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Sum

@api_view(['GET'])
def company_details(request):
    details = {'company_name': settings.COMPANY_NAME,
               'slogan': settings.SLOGAN,
               'contacts': settings.CONTACTS}
    return Response(details)

class RunPagination(PageNumberPagination):
    page_size_query_param = 'size'
    max_page_size = 50

class RunViewSet(viewsets.ModelViewSet):
    queryset = Run.objects.select_related('athlete').all()
    serializer_class = RunSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status', 'athlete']
    ordering_fields = ['created_at']
    pagination_class = RunPagination


class UserPagination(PageNumberPagination):
    page_size_query_param = 'size'
    max_page_size = 50

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.filter(is_superuser=False)
    serializer_class = UserSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['first_name', 'last_name']
    ordering_fields = ['date_joined']
    pagination_class = UserPagination

    def get_queryset(self):
        qs = self.queryset
        type = self.request.query_params.get('type', None)
        if type == 'coach':
            qs = qs.filter(is_staff=True)
        elif type == 'athlete':
            qs = qs.filter(is_staff=False)
        return qs


class StartAPIView(APIView):
    def post(self, request, id):
        run = get_object_or_404(Run, id=id)
        if run.status == 'init':
            run.status = 'in_progress'
            run.save()
            data = {'status': 'in_progress'}
            return Response(data)
        return Response(status=400)


class StopAPIView(APIView):
    def post(self, request, id):
        run = get_object_or_404(Run, id=id)
        if run.status == 'in_progress':
            run.status = 'finished'
            run.save()
            athlete = get_object_or_404(User, id=run.athlete.id)
            serializer = UserSerializer(athlete)
            count_run = serializer.data.get('runs_finished')
            if int(count_run) == 10:
                object, created = Challenge.objects.update_or_create(
                    athlete=run.athlete,
                    full_name='Сделай 10 Забегов!')

            sum_distance =  Run.objects.filter(status='finished', athlete=athlete.id).aggregate(Sum('distance'))
            print(sum_distance)
            if sum_distance['distance__sum'] >= 50:
                print ('okey')
                object, created = Challenge.objects.update_or_create(
                    athlete=run.athlete,
                    full_name='Пробеги 50 километров!')
                print(object)
                print(created)
            return Response({'status': 'finished'})
        return Response(status=400)


class AthleteInfoAPIView(APIView):

    def get(self, request, pk, format=None):
        user_obj = get_object_or_404(User, id=pk)
        object, created = AthleteInfo.objects.get_or_create(user_id=user_obj)
        serializer = AthleteInfoSerializer(object)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        user_obj = get_object_or_404(User, id=pk)
        object, created = AthleteInfo.objects.update_or_create(user_id=user_obj)
        serializer = AthleteInfoSerializer(object, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

class ChallengeViewSet(viewsets.ModelViewSet):
    queryset = Challenge.objects.select_related('athlete').all()
    serializer_class = ChallengeSerializer

    def get_queryset(self):
        qs = self.queryset
        athlete = self.request.query_params.get('athlete', None)
        if athlete:
            qs = qs.filter(athlete=athlete)
        return  qs

class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer

    def get_queryset(self):
        qs = self.queryset
        run = self.request.query_params.get('run', None)
        if run:
            qs = qs.filter(run=run)
        return  qs

    # def destroy(self, request, pk=None):
    #     instance = self.get_object(id=pk)
    #     instance.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)

        