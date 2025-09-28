import os
import uuid
from pathlib import Path
from typing import List
from abc import ABC, abstractmethod
import shutil
from fastapi import UploadFile, HTTPException
from PIL import Image
import io


class FileStorageStrategy(ABC):
    """Abstract base class for file storage strategies"""
    
    @abstractmethod
    async def save_file(self, file_content: bytes, filename: str) -> str:
        """Save file content and return the file path/URL"""
        pass
    
    @abstractmethod
    def delete_file(self, file_path: str) -> bool:
        """Delete a file and return success status"""
        pass
    
    @abstractmethod
    def get_file_url(self, file_path: str, base_url: str = None) -> str:
        """Generate accessible URL for a file"""
        pass


class LocalFileStorage(FileStorageStrategy):
    """Local file system storage strategy"""
    
    def __init__(self, upload_dir: str = "app/images"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(exist_ok=True, parents=True)
    
    async def save_file(self, file_content: bytes, filename: str) -> str:
        """Save file to local directory and return relative path"""
        try:
            file_path = self.upload_dir / filename
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            # Return relative path for database storage
            return f"images/{filename}"
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    def delete_file(self, file_path: str) -> bool:
        """Delete a file from the local upload directory"""
        try:
            # Handle both absolute and relative paths
            if file_path.startswith("images/"):
                # Relative path from database
                full_path = self.upload_dir / file_path.replace("images/", "")
            else:
                # Assume it's already a full path
                full_path = Path(file_path)
            
            if full_path.exists() and full_path.is_file():
                full_path.unlink()
                return True
            return False
        except Exception:
            return False
    
    def get_file_url(self, file_path: str, base_url: str = "http://localhost:8000") -> str:
        """Generate full URL for a local file"""
        return f"{base_url}/{file_path}"

class FileUploadManager:
    """Utility class for handling file uploads using pluggable storage strategies"""
    
    def __init__(self, storage_strategy: FileStorageStrategy):
        self.storage = storage_strategy
        
        # Allowed file extensions
        self.allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
        
        # Maximum file size (5MB)
        self.max_file_size = 5 * 1024 * 1024
        
        # Maximum image dimensions
        self.max_width = 2000
        self.max_height = 2000
    
    def validate_image_file(self, file: UploadFile) -> bool:
        """Validate if the uploaded file is a valid image"""
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Check file extension
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in self.allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid file extension. Allowed: {', '.join(self.allowed_extensions)}"
            )
        
        return True
    
    def validate_file_size(self, file: UploadFile) -> bool:
        """Validate file size"""
        if file.size and file.size > self.max_file_size:
            raise HTTPException(
                status_code=400, 
                detail=f"File too large. Maximum size: {self.max_file_size / (1024*1024):.1f}MB"
            )
        return True
    
    def resize_image_if_needed(self, image_data: bytes) -> bytes:
        """Resize image if it exceeds maximum dimensions"""
        try:
            image = Image.open(io.BytesIO(image_data))
            
            # Check if resizing is needed
            if image.width <= self.max_width and image.height <= self.max_height:
                return image_data
            
            # Calculate new dimensions maintaining aspect ratio
            ratio = min(self.max_width / image.width, self.max_height / image.height)
            new_width = int(image.width * ratio)
            new_height = int(image.height * ratio)
            
            # Resize image
            resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Save to bytes
            output = io.BytesIO()
            format_name = image.format or 'JPEG'
            resized_image.save(output, format=format_name, quality=85, optimize=True)
            
            return output.getvalue()
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")
    
    def generate_unique_filename(self, original_filename: str) -> str:
        """Generate a unique filename"""
        file_extension = Path(original_filename).suffix.lower()
        unique_id = str(uuid.uuid4())
        return f"{unique_id}{file_extension}"
    
    async def save_uploaded_file(self, file: UploadFile) -> str:
        """Save uploaded file and return the relative path"""
        # Validate file
        self.validate_image_file(file)
        
        # Read file content
        file_content = await file.read()
        
        # Validate file size (check actual content size)
        if len(file_content) > self.max_file_size:
            raise HTTPException(
                status_code=400, 
                detail=f"File too large. Maximum size: {self.max_file_size / (1024*1024):.1f}MB"
            )
        
        # Resize image if needed
        processed_content = self.resize_image_if_needed(file_content)
        
        # Generate unique filename
        unique_filename = self.generate_unique_filename(file.filename)
        
        # Use storage strategy to save file
        return await self.storage.save_file(processed_content, unique_filename)
    
    async def save_multiple_files(self, files: List[UploadFile]) -> List[str]:
        """Save multiple uploaded files and return list of relative paths"""
        if len(files) < 1:
            raise HTTPException(status_code=400, detail="At least 1 photo is required")
        
        if len(files) > 4:
            raise HTTPException(status_code=400, detail="Maximum 4 photos allowed")
        
        file_paths = []
        saved_files = []  # Track saved files for cleanup on error
        
        try:
            for file in files:
                if not file.filename:
                    continue  # Skip empty files
                
                file_path = await self.save_uploaded_file(file)
                file_paths.append(file_path)
                saved_files.append(file_path)
            
            if len(file_paths) < 1:
                raise HTTPException(status_code=400, detail="At least 1 valid photo is required")
            
            return file_paths
            
        except Exception as e:
            # Cleanup saved files on error using storage strategy
            for file_path in saved_files:
                try:
                    self.storage.delete_file(file_path)
                except:
                    pass  # Ignore cleanup errors
            raise e
    
    def delete_file(self, file_path: str) -> bool:
        """Delete a file using the storage strategy"""
        return self.storage.delete_file(file_path)
    
    def get_file_url(self, file_path: str, base_url: str = "http://localhost:8000") -> str:
        """Generate full URL for a file using the storage strategy"""
        return self.storage.get_file_url(file_path, base_url)


# Global instance with local storage strategy
local_storage = LocalFileStorage("app/images")
file_upload_manager = FileUploadManager(local_storage)