from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import get_user_model
from decimal import Decimal, InvalidOperation
from .models import Product
from .serializers import (
    UserSerializer, RegisterSerializer, ProductSerializer
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)

class ProfileView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def top_up_balance(request):
    try:
        amount = Decimal(str(request.data.get('amount', 0)))
        if amount <= 0:
            return Response({'error': 'Сумма должна быть больше нуля'}, status=status.HTTP_400_BAD_REQUEST)
    except InvalidOperation:
        return Response({'error': 'Неверный формат суммы'}, status=status.HTTP_400_BAD_REQUEST)

    user = request.user
    user.balance += amount
    user.save()
    return Response({'status': 'success', 'new_balance': user.balance})


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]