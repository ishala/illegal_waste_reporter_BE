from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from minio import Minio
from minio.error import S3Error
from fastapi import UploadFile, HTTPException, status
from typing import Optional
import uuid
from datetime import timedelta

from app.core.config import settings
from app.models.media import Media
from app.schemas.media import MediaCreate

class MinioService:
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        try:
            if not self.client.bucket_exists(settings.MINIO_BUCKET_NAME):
                self.client.make_bucket(settings.MINIO_BUCKET_NAME)
        except S3Error as e:
            print(f'Error creating bucket: {e}')
    
    def upload_file(
        self,
        file: UploadFile,
        folder: str = 'report_media'
    ) -> tuple[str, str]:
        try:
            content_type = file.content_type
            if not content_type.startswith(('image/', 'video/')):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Only images or video are allowed"
                )
            
            # Menentukan media type
            media_type = "image" if content_type.startswith("image/") else "video"
            # Ambil ekstensi file
            file_extension = file.filename.split('.')[-1]
            obj_name = f"{folder}{uuid.uuid4()}.{file_extension}"
            
            # Upload file
            file.file.seek(0)
            self.client.put_object(
                settings.MINIO_BUCKET_NAME,
                obj_name,
                file.file,
                length=-1,
                part_size=10*1024*1024, # 10MB
                content_type=content_type
            )
            
            return obj_name, media_type
        except S3Error as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'Failed to upload file: {str(e)}'
            )

    def get_file_url(
        self,
        obj_name: str,
        expires: int = 3600
    ) -> str:
        try:
            url = self.client.presigned_get_object(
                settings.MINIO_BUCKET_NAME,
                obj_name,
                expires=timedelta(seconds=expires)
            )
            return url
        except S3Error as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate file: {str(e)}"
            )
    
    def delete_file(
        self,
        obj_name:  str
    ) -> bool:
        try:
            self.client.remove_object(
                settings.MINIO_BUCKET_NAME,
                object_name=obj_name
            )
            return True
        except S3Error as e:
            print(f"Error deleting file: {e}")
            return False

minio_service = MinioService()

## CRUD ##
# Create
def create_media(
    db: Session,
    report_id: UUID,
    media_url: str,
    media_type: str
) -> Media:
    db_media = Media(
        report_id=report_id,
        media_url=media_url,
        media_type=media_type
    )
    db.add(db_media)
    db.commit()
    db.refresh(db_media)
    return db_media

def get_media_by_report(
    db: Session,
    report_id:  UUID
) -> List[Media]:
    return db.query(Media).filter(Media.report_id == report_id).first()

# Delete
def delete_media(
    db: Session,
    media_id: UUID
) -> bool:
    db_media = db.query(Media).filter(Media.id == media_id).first()
    if db_media is None:
        return False
    db.delete(db_media)
    db.commit()
    
    return True

def delete_media_by_report(
    db: Session,
    report_id: UUID
) -> bool:
    db_media = db.query(Media).filter(Media.report_id == report_id).all()
    if db_media is None:
        return False
    db.delete(db_media)
    db.commit()

    return True