from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
from rest_framework import viewsets
from .models import Run
from .serializer import RunSerializer, UserSerializer
from django.contrib.auth.models import User
from rest_framework.filters import  SearchFilter
from rest_framework.views import APIView
from rest_framework import status
from django.shortcuts import get_object_or_404

@api_view(['GET'])
def company_details(request):
    details = {'company_name': settings.COMPANY_NAME,
               'slogan': settings.SLOGAN,
               'contacts': settings.CONTACTS}
    return Response(details)

class RunViewSet(viewsets.ModelViewSet):
    queryset = Run.objects.select_related('athlete').all()
    serializer_class = RunSerializer

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.filter(is_superuser=False)
    serializer_class = UserSerializer
    filter_backends = [SearchFilter]
    search_fields = ['first_name', 'last_name']

    def get_queryset(self):
        qs = self.queryset
        type = self.request.query_params.get('type', None)
        if type == 'coach':
            qs = qs.filter(is_staff=True)
        elif type == 'athlete':
            qs = qs.filter(is_staff=False)
        return qs


class StartAPIView(APIView):

    # def get(self, request, id):
    #     run = get_object_or_404(Run, id=id)
    #     serializer = RunSerializer(run)
    #     return Response(serializer.data.get("status"))

    def post(self, request, id):
        run = get_object_or_404(Run, id=id)
        if run.status == 'init':
            run.status = 'in_progress'
            run.save()
            data = {'status': 'in_progress'}
            return Response(data)
        return Response()


class StopAPIView(APIView):
    def post(self, request, id):
        run = get_object_or_404(Run, id=id)
        if run.status == 'in_progress':
            run.status = 'finished'
            run.save(status=400)
            return Response({'status': 'finished'})
        return Response(status=400)


