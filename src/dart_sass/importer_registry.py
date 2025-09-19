"""
Importer registry for custom Sass importers.

This module provides a Python implementation that matches the Node.js reference
implementation exactly.
"""

from typing import Dict, Callable, List, Union, Any, Optional, NamedTuple, Protocol
from pathlib import Path
from urllib.parse import urlparse
from .vendor import embedded_sass_pb2 as proto
from .exception import CompileException
from .canonicalize_context import CanonicalizeContext


class ImporterResult(NamedTuple):
    """Result of an import operation (matches Node.js ImporterResult)."""
    contents: str
    syntax: Optional[str] = None
    source_map_url: Optional[str] = None


class Importer(Protocol):
    """
    Regular importer interface (two-phase process).
    
    This matches the Node.js Importer interface exactly.
    """
    
    def canonicalize(self, url: str, context: CanonicalizeContext) -> Optional[str]:
        """
        Canonicalize a URL for this importer.
        
        Args:
            url: The URL to canonicalize
            context: Context about the canonicalization request
            
        Returns:
            Canonical URL string, or None if this importer can't handle the URL
        """
        ...
    
    def load(self, canonical_url: str) -> Optional[ImporterResult]:
        """
        Load the contents of a canonical URL.
        
        Args:
            canonical_url: The canonical URL returned by canonicalize()
            
        Returns:
            ImporterResult with contents and metadata, or None if loading failed
        """
        ...
    
    # Optional: schemes that are non-canonical for this importer
    non_canonical_scheme: Optional[Union[str, List[str]]] = None


class FileImporter(Protocol):
    """
    File importer interface (one-phase process).
    
    This matches the Node.js FileImporter interface exactly.
    """
    
    def find_file_url(self, url: str, context: CanonicalizeContext) -> Optional[str]:
        """
        Find a file URL for the given import.
        
        Args:
            url: The URL to find
            context: Context about the canonicalization request
            
        Returns:
            File URL string, or None if this importer can't handle the URL
        """
        ...


class ImporterRegistry:
    """
    A registry of importers defined in the host that can be invoked by the compiler.
    
    This implementation matches the Node.js ImporterRegistry exactly.
    """
    
    def __init__(self, options=None):
        """
        Initialize the importer registry.
        
        Args:
            options: Options dict with 'importers' and 'load_paths' keys
                    (matches Node.js Options<sync> interface)
        """
        # Protocol buffer representations of the registered importers (like Node.js)
        self.importers: List[proto.InboundMessage.CompileRequest.Importer] = []
        
        # A map from importer IDs to their corresponding importers (like Node.js importersById)
        self._importers_by_id: Dict[int, Importer] = {}
        
        # A map from file importer IDs to their corresponding importers (like Node.js fileImportersById)
        self._file_importers_by_id: Dict[int, FileImporter] = {}
        
        # The next ID to use for an importer (like Node.js)
        self._next_id = 0
        
        # Process options exactly like Node.js constructor
        if options:
            # Register importers from options.importers (like Node.js)
            for importer in options.get('importers', []):
                proto_importer = self.register(importer)
                self.importers.append(proto_importer)
            
            # Register load paths from options.load_paths (like Node.js)
            for path in options.get('load_paths', []):
                resolved_path = str(Path(path).resolve())
                proto_importer = proto.InboundMessage.CompileRequest.Importer()
                proto_importer.path = resolved_path
                self.importers.append(proto_importer)
    
    def register(self, importer: Union[Importer, FileImporter]) -> proto.InboundMessage.CompileRequest.Importer:
        """
        Convert an importer to a proto without adding it to self.importers.
        
        This matches the Node.js register() method exactly.
        
        Args:
            importer: The importer to register
            
        Returns:
            Protocol buffer representation of the importer
            
        Raises:
            CompileException: If importer has invalid interface
        """
        # Create protobuf message (like Node.js)
        message = proto.InboundMessage.CompileRequest.Importer()
        
        # Check importer type exactly like Node.js
        if hasattr(importer, 'canonicalize'):
            if hasattr(importer, 'find_file_url'):
                raise CompileException(
                    f"Importer may not contain both canonicalize() and find_file_url(): {importer}"
                )
            
            # Regular importer (like Node.js)
            message.importer_id = self._next_id
            
            # Handle non-canonical schemes (like Node.js)
            if hasattr(importer, 'non_canonical_scheme') and importer.non_canonical_scheme:
                schemes = importer.non_canonical_scheme
                if isinstance(schemes, str):
                    schemes = [schemes]
                message.non_canonical_scheme.extend(schemes)
            
            self._importers_by_id[self._next_id] = importer
            
        elif hasattr(importer, 'find_file_url'):
            # File importer (like Node.js)
            message.file_importer_id = self._next_id
            self._file_importers_by_id[self._next_id] = importer
            
        else:
            raise CompileException(
                f"Importer must have either canonicalize() or find_file_url(): {importer}"
            )
        
        self._next_id += 1
        return message
    
    def canonicalize(self, request: proto.OutboundMessage.CanonicalizeRequest) -> proto.InboundMessage.CanonicalizeResponse:
        """
        Handle a canonicalization request.
        
        This matches the Node.js canonicalize() method exactly.
        
        Args:
            request: CanonicalizeRequest from the Sass compiler
            
        Returns:
            CanonicalizeResponse to send back to the compiler
        """
        from .utils import catch_or, then_or, compiler_error
        
        def execute_canonicalize():
            # Get importer by ID (like Node.js)
            importer = self._importers_by_id.get(request.importer_id)
            if not importer:
                raise compiler_error('Unknown CanonicalizeRequest.importer_id')
            
            # Create canonicalize context (like Node.js)
            canonicalize_context = CanonicalizeContext(
                request.containing_url if request.containing_url else None,
                request.from_import
            )
            
            # Call importer.canonicalize (might be async)
            result = importer.canonicalize(request.url, canonicalize_context)
            
            # Process result (like Node.js thenOr callback)
            def process_result(url):
                response = proto.InboundMessage.CanonicalizeResponse()
                if url is not None:
                    response.url = str(url)
                response.containing_url_unused = not canonicalize_context.containing_url_accessed
                return response
            
            return then_or(result, process_result)
        
        def handle_error(error):
            # Create error response (like Node.js error case)
            response = proto.InboundMessage.CanonicalizeResponse()
            response.error = str(error)
            return response
        
        # Use catchOr pattern exactly like Node.js
        return catch_or(execute_canonicalize, handle_error)
    
    def import_(self, request: proto.OutboundMessage.ImportRequest) -> proto.InboundMessage.ImportResponse:
        """
        Handle an import request.
        
        This matches the Node.js import() method exactly.
        Note: Named import_() to avoid Python keyword conflict.
        
        Args:
            request: ImportRequest from the Sass compiler
            
        Returns:
            ImportResponse to send back to the compiler
        """
        from .utils import catch_or, then_or, compiler_error, protofy_syntax
        
        def execute_import():
            # Get importer by ID (like Node.js)
            importer = self._importers_by_id.get(request.importer_id)
            if not importer:
                raise compiler_error('Unknown ImportRequest.importer_id')
            
            # Call importer.load (might be async)
            result = importer.load(request.url)
            
            # Process result (like Node.js thenOr callback)
            def process_result(import_result):
                response = proto.InboundMessage.ImportResponse()
                
                if not import_result:
                    # No result (like Node.js empty response)
                    return response
                
                # Validate contents (like Node.js)
                if not isinstance(import_result.contents, str):
                    raise CompileException(
                        f"Invalid argument (contents): must be a string but was: {type(import_result.contents).__name__}"
                    )
                
                # Validate sourceMapUrl (like Node.js)
                if import_result.source_map_url:
                    parsed = urlparse(import_result.source_map_url)
                    if not parsed.scheme:
                        raise CompileException(
                            f"Invalid argument (sourceMapUrl): must be absolute but was: {import_result.source_map_url}"
                        )
                
                # Create success response (like Node.js)
                success = proto.InboundMessage.ImportResponse.ImportSuccess()
                success.contents = import_result.contents
                success.syntax = protofy_syntax(import_result.syntax)
                if import_result.source_map_url:
                    success.source_map_url = import_result.source_map_url
                
                response.success.CopyFrom(success)
                return response
            
            return then_or(result, process_result)
        
        def handle_error(error):
            # Create error response (like Node.js error case)
            response = proto.InboundMessage.ImportResponse()
            response.error = str(error)
            return response
        
        # Use catchOr pattern exactly like Node.js
        return catch_or(execute_import, handle_error)
    
    def file_import(self, request: proto.OutboundMessage.FileImportRequest) -> proto.InboundMessage.FileImportResponse:
        """
        Handle a file import request.
        
        This matches the Node.js fileImport() method exactly.
        
        Args:
            request: FileImportRequest from the Sass compiler
            
        Returns:
            FileImportResponse to send back to the compiler
        """
        from .utils import catch_or, then_or, compiler_error
        
        def execute_file_import():
            # Get importer by ID (like Node.js)
            importer = self._file_importers_by_id.get(request.importer_id)
            if not importer:
                raise compiler_error('Unknown FileImportRequest.importer_id')
            
            # Create canonicalize context (like Node.js)
            canonicalize_context = CanonicalizeContext(
                request.containing_url if request.containing_url else None,
                request.from_import
            )
            
            # Call importer.find_file_url (might be async)
            result = importer.find_file_url(request.url, canonicalize_context)
            
            # Process result (like Node.js thenOr callback)
            def process_result(url):
                response = proto.InboundMessage.FileImportResponse()
                
                if not url:
                    # No result (like Node.js empty response)
                    response.containing_url_unused = not canonicalize_context.containing_url_accessed
                    return response
                
                # Validate file: URL (like Node.js)
                if not url.startswith('file:'):
                    raise CompileException(
                        f"FileImporter {importer} returned non-file: URL \"{url}\" for URL \"{request.url}\"."
                    )
                
                # Create success response (like Node.js)
                response.file_url = url
                response.containing_url_unused = not canonicalize_context.containing_url_accessed
                return response
            
            return then_or(result, process_result)
        
        def handle_error(error):
            # Create error response (like Node.js error case)
            response = proto.InboundMessage.FileImportResponse()
            response.error = str(error)
            return response
        
        # Use catchOr pattern exactly like Node.js
        return catch_or(execute_file_import, handle_error)
