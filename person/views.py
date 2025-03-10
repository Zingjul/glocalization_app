from rest_framework import generics, permissions, serializers
from .models import Person
from .serializers import PersonSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named `user`.
        return obj.user == request.user

class PersonList(generics.ListCreateAPIView):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class PersonDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    permission_classes = [IsOwnerOrReadOnly]

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def toggle_business_name(request):
    profile = request.user.profile
    profile.use_business_name = not profile.use_business_name
    profile.save()
    serializer = PersonSerializer(profile)
    return Response(serializer.data)