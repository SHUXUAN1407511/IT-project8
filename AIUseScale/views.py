from django.db import transaction
from rest_framework import viewsets, permissions, filters, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import AIUserScale, ScaleRecord, ScaleVersion, ScaleLevel
from .serializer import (
    AIUserScaleSerializer,
    ScaleRecordSerializer,
    SaveScaleVersionRequestSerializer,
)


# -------------------------
# 公共分页器
# -------------------------
class DefaultPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


# -------------------------
# 旧接口：/scales/（兼容 /aiusescale/）
# -------------------------
class AIUserScaleViewSet(viewsets.ModelViewSet):
    queryset = AIUserScale.objects.all()
    serializer_class = AIUserScaleSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = DefaultPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "notes"]
    ordering_fields = ["created_at", "updated_at", "name", "level"]
    ordering = ["-updated_at"]

    def get_queryset(self):
        qs = super().get_queryset()
        username = self.request.query_params.get("username")
        if username:
            qs = qs.filter(username=username)
        return qs

    def list(self, request, *args, **kwargs):
        no_page = request.query_params.get("nopage") in ("1", "true", "True")
        if request.query_params.get("page_size") == "0":
            no_page = True

        queryset = self.filter_queryset(self.get_queryset())
        if no_page or self.pagination_class is None:
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return super().update(request, *args, **kwargs)


class ScaleRecordViewSet(viewsets.ModelViewSet):
    """
    - GET /scale-records/?ownerType=&ownerId=&isPublic=1
    - POST /scale-records/
    - PUT/PATCH /scale-records/:id/
    - DELETE /scale-records/:id/
    - POST /scale-records/save_version   (SaveScaleVersionRequest)
    """
    queryset = ScaleRecord.objects.all().prefetch_related("versions__levels")
    serializer_class = ScaleRecordSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = DefaultPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["updated_at", "created_at", "name"]
    ordering = ["-updated_at"]

    def get_queryset(self):
        qs = super().get_queryset()
        owner_type = self.request.query_params.get("ownerType")
        owner_id = self.request.query_params.get("ownerId")
        is_public = self.request.query_params.get("isPublic")
        if owner_type:
            qs = qs.filter(owner_type=owner_type)
        if owner_id:
            qs = qs.filter(owner_id=owner_id)
        if is_public in ("1", "true", "True"):
            qs = qs.filter(is_public=True)
        return qs

    def list(self, request, *args, **kwargs):
        no_page = request.query_params.get("nopage") in ("1", "true", "True")
        if request.query_params.get("page_size") == "0":
            no_page = True

        queryset = self.filter_queryset(self.get_queryset())
        if no_page or self.pagination_class is None:
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=["post"], detail=False, url_path="save_version")
    def save_version(self, request, *args, **kwargs):
        """
        SaveScaleVersionRequest：
        {
          "scaleId": "uuid",
          "levels": [{ id,label,title?,description,aiUsage,instructions?,acknowledgement? }, ...],
          "notes": "optional",
          "updatedBy": "optional string"
        }
        """
        serializer = SaveScaleVersionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        record_id = data["scaleId"]
        notes = data.get("notes")
        levels = data["levels"]
        updated_by = data.get("updatedBy") or (
            getattr(getattr(request, "user", None), "username", None) or "system"
        )

        try:
            record = ScaleRecord.objects.get(pk=record_id)
        except ScaleRecord.DoesNotExist:
            return Response({"detail": "ScaleRecord not found"}, status=status.HTTP_404_NOT_FOUND)

        with transaction.atomic():
            last = record.versions.order_by("-version").first()
            next_version_num = (last.version + 1) if last else 1

            version = ScaleVersion.objects.create(
                record=record,
                version=next_version_num,
                updated_by=updated_by,
                notes=notes,
            )

            bulk_levels = []
            for idx, lv in enumerate(levels):
                bulk_levels.append(
                    ScaleLevel(
                        id=lv["id"],
                        version=version,
                        position=idx,
                        label=lv["label"],
                        title=lv.get("title") or None,
                        description=lv["description"],
                        ai_usage=lv["aiUsage"],
                        instructions=lv.get("instructions") or None,
                        acknowledgement=lv.get("acknowledgement") or None,
                    )
                )
            ScaleLevel.objects.bulk_create(bulk_levels)

        return Response(ScaleRecordSerializer(record).data, status=status.HTTP_201_CREATED)
