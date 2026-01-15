import os
from mimetypes import guess_type
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions


class FileUploadView(APIView):
    """
    Generic endpoint for uploading media files (images, videos, etc.)
    - Accepts multipart/form-data requests.
    - Optionally accepts a `folder` parameter to customize upload destination.
    - Returns a JSON response with file metadata.
    """
    permission_classes = [permissions.IsAdminUser]  # restrict to staff users

    def post(self, request):
        uploaded_file = request.FILES.get('file')
        folder = request.data.get('folder', 'uploads/')

        # Validate input
        if not uploaded_file:
            return Response(
                {"error": "No file uploaded."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Normalize folder path
        folder = folder.strip().rstrip('/') + '/'

        # Save file in default storage
        saved_path = default_storage.save(
            os.path.join(folder, uploaded_file.name),
            ContentFile(uploaded_file.read())
        )

        # Build full URL
        file_url = request.build_absolute_uri(
            settings.MEDIA_URL + saved_path
        )

        # Build response
        return Response({
            "url": file_url,
            "path": saved_path,
            "filename": uploaded_file.name,
            "size": uploaded_file.size,
            "mime_type": guess_type(uploaded_file.name)[0],
        }, status=status.HTTP_201_CREATED)
