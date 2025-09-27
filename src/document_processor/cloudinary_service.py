"""
Cloudinary Image Service
Downloads and processes images from Cloudinary URLs
"""

import os
import tempfile
import logging
from pathlib import Path
from typing import Optional
import aiohttp
import asyncio
from PIL import Image

logger = logging.getLogger(__name__)

class CloudinaryService:
    """Service for handling Cloudinary image operations"""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
    
    async def download_image(self, cloudinary_url: str) -> str:
        """
        Download image from Cloudinary URL to temporary file
        
        Args:
            cloudinary_url: Cloudinary image URL
            
        Returns:
            Path to downloaded temporary file
            
        Raises:
            Exception: If download fails or image is invalid
        """
        try:
            # Validate URL format
            if not cloudinary_url.startswith('https://res.cloudinary.com'):
                raise ValueError("Invalid Cloudinary URL format")
            
            # Create session with timeout and SSL settings
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            
            # Create SSL context that's more permissive for demo purposes
            import ssl
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            
            async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
                logger.info(f"Downloading image from: {cloudinary_url}")
                
                async with session.get(cloudinary_url) as response:
                    # Check if request was successful
                    if response.status != 200:
                        raise Exception(f"Failed to download image: HTTP {response.status}")
                    
                    # Check content type
                    content_type = response.headers.get('content-type', '')
                    if not content_type.startswith('image/'):
                        raise Exception(f"Invalid content type: {content_type}")
                    
                    # Read image data
                    image_data = await response.read()
                    
                    if not image_data:
                        raise Exception("Empty image data received")
                    
                    # Determine file extension from URL or content type
                    file_extension = self._get_file_extension(cloudinary_url, content_type)
                    
                    # Create temporary file
                    temp_file = tempfile.NamedTemporaryFile(
                        delete=False, 
                        suffix=file_extension,
                        prefix='cloudinary_'
                    )
                    
                    # Write image data to temporary file
                    temp_file.write(image_data)
                    temp_file.flush()
                    temp_file.close()
                    
                    # Validate image using PIL
                    await self._validate_image(temp_file.name)
                    
                    logger.info(f"Image downloaded successfully: {temp_file.name}")
                    return temp_file.name
        
        except Exception as e:
            logger.error(f"Failed to download image from {cloudinary_url}: {e}")
            raise Exception(f"Image download failed: {str(e)}")
    
    async def _validate_image(self, file_path: str):
        """Validate downloaded image file"""
        try:
            # Run image validation in thread pool to avoid blocking
            await asyncio.get_event_loop().run_in_executor(
                None, self._validate_image_sync, file_path
            )
        except Exception as e:
            # Clean up invalid file
            Path(file_path).unlink(missing_ok=True)
            raise Exception(f"Invalid image file: {str(e)}")
    
    def _validate_image_sync(self, file_path: str):
        """Synchronous image validation using PIL"""
        try:
            with Image.open(file_path) as img:
                # Verify the image
                img.verify()
                
                # Check file size (max 50MB)
                file_size = Path(file_path).stat().st_size
                max_size = 50 * 1024 * 1024  # 50MB
                
                if file_size > max_size:
                    raise Exception(f"Image too large: {file_size / (1024*1024):.1f}MB (max 50MB)")
                
                # Check image dimensions (reasonable limits)
                img_check = Image.open(file_path)
                width, height = img_check.size
                
                if width > 10000 or height > 10000:
                    raise Exception(f"Image dimensions too large: {width}x{height}")
                
                if width < 100 or height < 100:
                    logger.warning(f"Image dimensions quite small: {width}x{height}")
                
                logger.info(f"Image validation passed: {width}x{height}, {file_size / 1024:.1f}KB")
                
        except Exception as e:
            raise Exception(f"Image validation failed: {str(e)}")
    
    def _get_file_extension(self, url: str, content_type: str) -> str:
        """Determine appropriate file extension"""
        # Try to get extension from URL
        path = url.split('?')[0]  # Remove query parameters
        url_ext = Path(path).suffix.lower()
        
        if url_ext in self.supported_formats:
            return url_ext
        
        # Fallback to content type
        content_type_map = {
            'image/jpeg': '.jpg',
            'image/jpg': '.jpg',
            'image/png': '.png',
            'image/bmp': '.bmp',
            'image/tiff': '.tiff',
            'image/webp': '.webp',
        }
        
        return content_type_map.get(content_type.lower(), '.jpg')
    
    @staticmethod
    def cleanup_temp_file(file_path: str):
        """Clean up temporary file"""
        try:
            if file_path and Path(file_path).exists():
                Path(file_path).unlink()
                logger.debug(f"Cleaned up temporary file: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to cleanup temp file {file_path}: {e}")
    
    async def get_image_info(self, cloudinary_url: str) -> dict:
        """
        Get basic information about image without downloading
        
        Args:
            cloudinary_url: Cloudinary image URL
            
        Returns:
            Dictionary with image metadata
        """
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            
            # Create SSL context that's more permissive
            import ssl
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            
            async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
                # Use HEAD request to get headers only
                async with session.head(cloudinary_url) as response:
                    if response.status != 200:
                        raise Exception(f"Image not accessible: HTTP {response.status}")
                    
                    headers = response.headers
                    
                    return {
                        'content_type': headers.get('content-type', ''),
                        'content_length': int(headers.get('content-length', 0)),
                        'last_modified': headers.get('last-modified', ''),
                        'url': cloudinary_url,
                        'accessible': True
                    }
        
        except Exception as e:
            logger.error(f"Failed to get image info for {cloudinary_url}: {e}")
            return {
                'url': cloudinary_url,
                'accessible': False,
                'error': str(e)
            }

# Global service instance
cloudinary_service = CloudinaryService()

async def download_image_from_url(url: str) -> str:
    """Convenience function to download image from Cloudinary URL"""
    return await cloudinary_service.download_image(url)