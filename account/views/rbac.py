from rest_framework.views import APIView
from rest_framework.response import Response
from ..permissions import IsSuperAdmin, IsBusinessman

class SuperAdminOnlyView(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        return Response({'message': 'Hello SuperAdmin!'})
    

class BusinessmanOnlyView(APIView):
    permission_classes = [IsBusinessman]

    def get(self, request):
        return Response({'message': 'Hello Businessman!'})