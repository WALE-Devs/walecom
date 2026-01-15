import os
from mimetypes import guess_type
from datetime import datetime
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils.timezone import get_current_timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions


class FileUploadView(APIView):
    """
    Generic endpoint for uploading and listing media files (images, videos, etc.).
    Compatible with local and remote storage (S3, GCS...).
    """
    permission_classes = [permissions.IsAdminUser]  # Restrict access to staff users.

    def post(self, request):
        """Handle file upload."""
        uploaded_file = request.FILES.get('file')
        folder = request.data.get('folder', 'uploads/')

        if not uploaded_file:
            return Response(
                {"error": "No file uploaded."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        folder = folder.strip().rstrip('/') + '/'

        # Save file using the configured storage backend.
        saved_path = default_storage.save(
            os.path.join(folder, uploaded_file.name),
            ContentFile(uploaded_file.read())
        )

        # Build absolute URL (works for local or S3 backends).
        file_url = (
            default_storage.url(saved_path)
            if hasattr(default_storage, "url")
            else request.build_absolute_uri(settings.MEDIA_URL + saved_path)
        )

        return Response({
            "url": file_url,
            "path": saved_path,
            "filename": uploaded_file.name,
            "size": uploaded_file.size,
            "mime_type": guess_type(uploaded_file.name)[0],
        }, status=status.HTTP_201_CREATED)

    def get(self, request):
        """List recently uploaded files (works with local or S3 storage)."""
        folder = request.query_params.get('folder', 'uploads/')
        limit = int(request.query_params.get('limit', 10))

        folder = folder.strip().rstrip('/') + '/'

        files = []

        try:
            # Use storage backend to list files (works for S3 & local).
            dirs, file_list = default_storage.listdir(folder)
        except Exception:
            return Response([], status=status.HTTP_200_OK)

        # Sort by modification time if possible (local only)
        if hasattr(default_storage, "path"):
            folder_path = default_storage.path(folder)
            file_list = sorted(
                file_list,
                key=lambda f: os.path.getmtime(os.path.join(folder_path, f)),
                reverse=True
            )[:limit]
        else:
            file_list = file_list[:limit]

        for filename in file_list:
            path = os.path.join(folder, filename)
            url = (
                default_storage.url(path)
                if hasattr(default_storage, "url")
                else request.build_absolute_uri(settings.MEDIA_URL + path)
            )

            file_info = {
                "url": url,
                "path": path,
                "filename": filename,
                "mime_type": guess_type(filename)[0],
                "modified": None,  # Modification time available only for local storage
            }

            # Add last modified timestamp if storage supports it (local only)
            if hasattr(default_storage, "path"):
                file_info["modified"] = datetime.fromtimestamp(
                    os.path.getmtime(default_storage.path(path)),
                    tz=get_current_timezone()
                ).isoformat()

            files.append(file_info)

        return Response(files, status=status.HTTP_200_OK)
