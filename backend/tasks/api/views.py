import binascii

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from poap.core.api import CustomPagination
from poap.tasks.api.serializers import (
    TasksSerializer, TasksCreateSerializer,
    VerificationClassSerializer, TaskTagSerializer,
    TaskUserSerializer,
)
from poap.tasks.check import get_checker, function_checker
from poap.tasks.models import Task, TaskClass, TaskTag, TaskUser
from poap.utils.contract import contract


class TaskClassListView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = TaskClass.objects.all()
    serializer_class = VerificationClassSerializer


class TaskTagListView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = TaskTag.objects.all()
    serializer_class = TaskTagSerializer


class TaskListView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Task.objects.all()
    serializer_class = TasksSerializer
    pagination_class = CustomPagination
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ["name", "created_by__address", "users__address"]
    ordering_fields = ["created_at", "name"]
    parser_classes = (MultiPartParser,)

    def get_permissions(self):
        if self.request.method in ("GET", "HEAD", "OPTIONS"):
            return []
        return super().get_permissions()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"user": self.request.user})
        return context

    def post(self, request, *args, **kwargs):
        serializer = TasksCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data["created_by"] = request.user
        task = serializer.save()
        return Response(
            status=status.HTTP_201_CREATED,
            data=self.serializer_class(task, context={"user": self.request.user}).data,
        )


class TaskDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Task.objects.all()
    serializer_class = TasksCreateSerializer
    lookup_url_kwarg = "task_id"

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return Response(status=status.HTTP_200_OK, data=TasksSerializer(self.get_object()).data)

    def perform_destroy(self, instance):
        # set is_active to False
        instance.is_active = False
        instance.save()


class TaskUserJoinView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = TaskUser.objects.all()
    serializer_class = TaskUserSerializer
    pagination_class = CustomPagination
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    ordering_fields = ["created_at", "owned"]
    filterset_fields = ["owned"]

    def get_permissions(self):
        if self.request.method in ("GET", "HEAD", "OPTIONS"):
            return []
        return super().get_permissions()

    def post(self, request, task_id: int, *args, **kwargs):
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if task.mode == Task.MODE_APPROVE and "verify_address" not in request.data:
            return Response(status=400)

        if not task.users.contains(request.user):
            task_user = TaskUser.objects.create(
                user=request.user,
                task=task,
                verify_address=request.data.get("verify_address"),
            )
            task.users.add(request.user)
            request.user.joined_count += 1
            request.user.save()
            task.joined_count += 1
            task.save()
        else:
            return Response(status=status.HTTP_409_CONFLICT)

        return Response(status=status.HTTP_200_OK)


class TaskUserApproveView(APIView):
    permission_classes = (IsAuthenticated,)
    
    def post(self, request, task_id, *args, **kwargs):
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.user.address != task.created_by.address:
            return Response(status=403)

        for address in request.data:
            task_user = TaskUser.objects.filter(user__address=address, task=task, owned=False)
            if not task_user:
                continue

            task_user = task_user.first()
            tx_hash, _ = contract.mint(task.id, task_user.user.address)
            print("tx_hash:", tx_hash)
            request.user.owned_count += 1
            request.user.save()
            task_user.owned = True
            task_user.save()
        return Response(status=status.HTTP_200_OK, data={"token_id": task.id})


class EligibilityCheckView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        response = []
        # TODO: Check joined tasks within 3 months
        for task_user in TaskUser.objects.prefetch_related("user", "task").filter(
            user=request.user, owned=False,
        ).order_by("-task__created_by"):
            task = task_user.task
            eligibility = get_checker(task_user)
            task_data = TasksSerializer(task, context={"user": self.request.user}).data
            task_data["eligibility"] = eligibility
            response.append(task_data)
        return Response(status=status.HTTP_200_OK, data=response)


class FunctionsCheckView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, task_id: int, *args, **kwargs):
        try:
            task = Task.objects.get(id=task_id)
            task_user = TaskUser.objects.get(user=request.user, task=task)
        except (Task.DoesNotExist, TaskUser.DoesNotExist):
            return Response(status=status.HTTP_404_NOT_FOUND)

        if task_user.owned:
            task_user.owned = False
            task_user.save()
            return Response(status=status.HTTP_400_BAD_REQUEST)

        user_balance = contract.balance(task.id, task_user.user.address)
        if user_balance != 0:
            task_user.owned = True
            task_user.save()
            return Response(status=status.HTTP_400_BAD_REQUEST)

        request_hash, tx_hash, _ = function_checker(task_user)

        task_user.request_hash = binascii.hexlify(request_hash).decode()
        task_user.save()

        return Response(status=status.HTTP_200_OK, data={"token_id": task.id, "tx_hash": tx_hash})


class TaskClaimView(ListAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, task_id: int, *args, **kwargs):
        try:
            task = Task.objects.get(id=task_id)
            task_user = TaskUser.objects.get(user=request.user, task=task)
        except (Task.DoesNotExist, TaskUser.DoesNotExist):
            return Response(status=status.HTTP_404_NOT_FOUND)

        if task_user.owned:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        user_balance = contract.balance(task.id, task_user.user.address)
        if user_balance != 0:
            task_user.owned = True
            task_user.save()
            return Response(status=status.HTTP_400_BAD_REQUEST)

        eligibility = get_checker(task_user)
        if not eligibility:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        tx_hash, _ = contract.mint(task.id, task_user.user.address)
        print("tx_hash:", tx_hash)
        request.user.owned_count += 1
        request.user.save()
        task_user.owned = True
        task_user.save()

        return Response(status=status.HTTP_200_OK, data={"token_id": task.id, "tx_hash": tx_hash})
