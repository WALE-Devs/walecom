from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, AllowAny
from .models import Content, ContentBlock
from .serializers import ContentSerializer, ContentBlockSerializer


class ContentViewSet(viewsets.ModelViewSet):
    """Public + Admin API for main content entries"""

    queryset = Content.objects.prefetch_related("blocks").order_by(
        "identifier", "language"
    )
    serializer_class = ContentSerializer
    lookup_field = "identifier"

    def get_permissions(self):
        # Allow public GET, restrict POST/PUT/PATCH/DELETE to staff
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAdminUser()]

    def get_queryset(self):
        """Supports ?lang=xx filtering for language"""
        lang = self.request.query_params.get("lang")
        qs = super().get_queryset()
        if lang:
            qs = qs.filter(language=lang)
        return qs


class ContentBlockViewSet(viewsets.ModelViewSet):
    """Admin-only API for managing blocks"""

    queryset = ContentBlock.objects.select_related("content").order_by("order")
    serializer_class = ContentBlockSerializer
    permission_classes = [IsAdminUser]
