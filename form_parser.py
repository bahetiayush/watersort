import re
from typing import Dict, Any, Optional

class MultipartFormParser:
    """Parser for multipart/form-data requests"""

    def __init__(self, content_type: str, data: bytes):
        self.content_type = content_type
        self.data = data
        self.boundary = self._get_boundary()

    def _get_boundary(self) -> bytes:
        """Extract boundary from content type header"""
        match = re.search(r'boundary=(.+)', self.content_type)
        if match:
            return match.group(1).encode()
        raise ValueError("Boundary not found in content type")

    def parse(self) -> Dict[str, Any]:
        """Parse the multipart form data and return a dictionary of fields"""
        result = {}

        # Split data by boundary
        parts = self.data.split(b'--' + self.boundary)

        # Skip the first and last parts (they're empty or just '--')
        for part in parts[1:-1]:
            # Skip the initial newline
            if part.startswith(b'\r\n'):
                part = part[2:]

            # Split headers and content
            headers_end = part.find(b'\r\n\r\n')
            if headers_end == -1:
                continue

            headers_raw = part[:headers_end]
            content = part[headers_end + 4:]  # +4 to skip '\r\n\r\n'

            # Parse headers
            headers = {}
            for header_line in headers_raw.split(b'\r\n'):
                if b':' in header_line:
                    header_name, header_value = header_line.split(b':', 1)
                    headers[header_name.strip().lower().decode()] = header_value.strip().decode()

            # Extract field name
            field_name = None
            if 'content-disposition' in headers:
                cd_parts = headers['content-disposition'].split(';')
                for cd_part in cd_parts:
                    if 'name=' in cd_part:
                        field_name = cd_part.split('=', 1)[1].strip('"\'')
                        break

            if not field_name:
                continue

            # Handle file fields
            if 'filename=' in headers.get('content-disposition', ''):
                filename = re.search(r'filename="([^"]*)"', headers['content-disposition'])
                if filename:
                    filename = filename.group(1)
                    # Remove the trailing \r\n from content if it exists
                    if content.endswith(b'\r\n'):
                        content = content[:-2]
                    # Store file data
                    result[field_name] = {
                        'filename': filename,
                        'content': content,
                        'content_type': headers.get('content-type', 'application/octet-stream')
                    }
            else:
                # Regular field
                # Remove the trailing \r\n from content if it exists
                if content.endswith(b'\r\n'):
                    content = content[:-2]
                result[field_name] = content.decode()

        return result
