"""
Asynchronous compiler for embedded Sass.
"""

import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, Set
import reactivex as rx
from reactivex import operators as ops

from ..compiler_path import get_compiler_command
from ..message_transformer import MessageTransformer
from ..packet_transformer import PacketTransformer
from ..vendor import embedded_sass_pb2 as proto
from ..types import CompileResult
from ..exception import CompileException
from ..utils import compiler_error
from ..function_registry import FunctionRegistry
from ..importer_registry import ImporterRegistry
from ..deprecations import active_deprecation_options
from .utils import (
    create_dispatcher, 
    handle_compile_response, 
    handle_log_event,
    new_compile_path_request,
    new_compile_string_request
)


# Flag allowing the constructor passed by init_async_compiler
_INIT_FLAG = object()


class AsyncCompiler:
    """Asynchronous wrapper for the embedded Sass compiler."""
    
    def __init__(self, flag: object = None):
        """Initialize the async compiler. Use init_async_compiler() instead."""
        if flag is not _INIT_FLAG:
            raise compiler_error(
                'AsyncCompiler cannot be directly constructed. '
                'Please use `init_async_compiler()` instead.'
            )
        
        self._disposed = False
        self._compilation_id = 1
        self._compilations: Set[asyncio.Future] = set()
        
        # Get the compiler command
        try:
            self._compiler_command = get_compiler_command()
        except RuntimeError as e:
            raise CompileException(f"Sass compiler not found: {e}") from e
        
        # These will be set up in the async init
        self._process = None
        self._stdout_observable = None
        self._stderr_observable = None
        self._exit_future = None
        self._packet_transformer = None
        self._message_transformer = None
    
    async def _initialize_if_needed(self):
        """Initialize the compiler if not already done."""
        if self._process is None:
            await self._start_process()
            self._setup_message_handling()
    
    async def _start_process(self) -> None:
        """Start the compiler subprocess using asyncio."""
        try:
            # Use the compiler's directory as working directory
            cwd = str(Path(self._compiler_command[0]).parent)
            
            # Start the process with asyncio (proper async streams)
            self._process = await asyncio.create_subprocess_exec(
                *self._compiler_command, '--embedded',
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd
            )
            
            # Create exit future (like Node.js exit$ promise)
            self._exit_future = asyncio.create_task(self._process.wait())
            
        except Exception as e:
            raise CompileException(f"Failed to start compiler process: {e}") from e
    
    def _setup_message_handling(self) -> None:
        """Set up message handling following Node.js pattern exactly."""
        # Create a subject for exit events instead of using the future directly
        self._exit_subject = rx.Subject()
        
        # Create RxPY Observables that wrap the asyncio streams (like Node.js)
        self._stdout_observable = rx.create(self._stdout_observer_factory).pipe(
            ops.take_until(self._exit_subject)
        )
        
        self._stderr_observable = rx.create(self._stderr_observer_factory).pipe(
            ops.take_until(self._exit_subject)
        )
        
        # Set up stderr logging (like Node.js)
        self._stderr_observable.subscribe(
            on_next=lambda data: print(f"Sass compiler stderr: {data.decode('utf-8', errors='replace').strip()}")
        )
        
        # Set up the packet transformer (like Node.js)
        self._packet_transformer = PacketTransformer(
            self._stdout_observable,
            lambda buffer: self._write_stdin(buffer)
        )
        
        # Set up the message transformer (like Node.js)
        self._message_transformer = MessageTransformer(
            self._packet_transformer.outbound_protobufs,
            lambda packet: self._packet_transformer.write_inbound_protobuf(packet)
        )
    
    def _stream_observer_factory(self, stream, observer, scheduler):
        """Generic factory for stream observables."""
        async def read_stream():
            try:
                while not self._disposed and self._process.returncode is None:
                    data = await stream.read(8192)
                    if data:
                        observer.on_next(data)
                    else:
                        break  # EOF
                observer.on_completed()
            except Exception as e:
                observer.on_error(e)
        
        # Start the async task
        asyncio.create_task(read_stream())
        
        # Return disposable
        return lambda: None
    
    def _stdout_observer_factory(self, observer, scheduler):
        """Factory for stdout observable - delegates to generic factory."""
        return self._stream_observer_factory(self._process.stdout, observer, scheduler)
    
    def _stderr_observer_factory(self, observer, scheduler):
        """Factory for stderr observable - delegates to generic factory."""
        return self._stream_observer_factory(self._process.stderr, observer, scheduler)
    
    def _write_stdin(self, buffer: bytes) -> None:
        """Write buffer to the process stdin (like Node.js writeStdin)."""
        if self._process and self._process.stdin:
            self._process.stdin.write(buffer)
    
    def _throw_if_disposed(self) -> None:
        """Guard against using a disposed compiler."""
        if self._disposed:
            raise compiler_error('Async compiler has already been disposed.')
    
    async def compile_string_async(self, source: str, options: Optional[Dict[str, Any]] = None) -> CompileResult:
        """
        Asynchronously compile a Sass string to CSS.
        
        Args:
            source: The Sass source code to compile
            options: Compilation options
            
        Returns:
            CompileResult containing the compiled CSS and metadata
        """
        self._throw_if_disposed()
        await self._initialize_if_needed()
        
        # Use ImporterRegistry and utility functions like Node.js
        importers = ImporterRegistry(options)
        
        # Use our utility function instead of custom method
        request = new_compile_string_request(source, importers, options)
        
        return await self._compile_request_async(request, importers, options)
    
    async def compile_async(self, path: str, options: Optional[Dict[str, Any]] = None) -> CompileResult:
        """
        Asynchronously compile a Sass file to CSS.
        
        Args:
            path: The path to the Sass file to compile
            options: Compilation options
            
        Returns:
            CompileResult containing the compiled CSS and metadata
        """
        self._throw_if_disposed()
        await self._initialize_if_needed()
        
        # Use ImporterRegistry and utility functions like Node.js
        importers = ImporterRegistry(options)
        
        # Use our utility function instead of custom method
        request = new_compile_path_request(path, importers, options)
        
        return await self._compile_request_async(request, importers, options)
    
    async def _compile_request_async(self, request: proto.InboundMessage.CompileRequest, importers: ImporterRegistry, options: Optional[Dict[str, Any]] = None) -> CompileResult:
        """
        Send a compile request to the child process and return a Promise that
        resolves with the CompileResult. Follows the Node.js reference implementation.
        """
        options_key = object()
        active_deprecation_options[options_key] = options or {}
        dispatcher = None
        try:
            compilation_id = self._compilation_id
            self._compilation_id += 1
            
            # Create function registry from options (like Node.js)
            functions = FunctionRegistry(options.get('functions') if options else None)
            
            # No additional register() calls needed - constructor handles everything (like Node.js)
            
            # Create dispatcher with callback handlers (like Node.js)
            dispatcher = create_dispatcher(
                compilation_id,
                self._message_transformer,
                {
                    'handleFunctionCallRequest': lambda request: functions.call(request),
                    'handleImportRequest': lambda request: importers.import_(request),
                    'handleFileImportRequest': lambda request: importers.file_import(request),
                    'handleCanonicalizeRequest': lambda request: importers.canonicalize(request),
                }
            )
            
            # Subscribe to log events (like Node.js)
            dispatcher.log_events.subscribe(
                on_next=lambda event: handle_log_event(options, event),
                on_error=lambda e: None,  # Handle errors silently like Node.js
                on_completed=lambda: None
            )
            
            # Create a future for this compilation (like Node.js Promise)
            compilation_future = asyncio.Future()
            
            def callback(err, resp):
                """Callback to handle compilation result (like Node.js)."""
                self._compilations.discard(compilation_future)
                
                # Reset compilation ID when idle (like Node.js)
                if len(self._compilations) == 0:
                    self._compilation_id = 1
                
                if err:
                    if not compilation_future.done():
                        compilation_future.set_exception(err)
                else:
                    if not compilation_future.done():
                        compilation_future.set_result(resp)
            
            # Add to active compilations (like Node.js)
            self._compilations.add(compilation_future)
            
            # Send the compile request using dispatcher (like Node.js)
            # The utility functions return CompileRequest directly, not InboundMessage
            dispatcher.send_compile_request(request, callback)
            
            # Wait for the compilation to complete
            response = await compilation_future
            
            # Use utility function instead of custom conversion
            return handle_compile_response(response)
            
        except Exception as e:
            # Clean up on error
            self._compilations.discard(compilation_future)
            if len(self._compilations) == 0:
                self._compilation_id = 1
            raise
        finally:
            # Clean up activeDeprecationOptions (like Node.js)
            active_deprecation_options.pop(options_key, None)
            # Clean up dispatcher if it was created (like sync compiler)
            if dispatcher:
                dispatcher.dispose()
    
    async def dispose(self) -> None:
        """Dispose of the compiler and clean up resources."""
        if self._disposed:
            return
        
        self._disposed = True
        
        # Wait for all active compilations to complete (like Node.js)
        if self._compilations:
            await asyncio.gather(*self._compilations, return_exceptions=True)
        
        # Clean up transformers
        if hasattr(self, '_packet_transformer') and self._packet_transformer:
            try:
                self._packet_transformer.dispose()
            except Exception:
                pass
        
        # Note: MessageTransformer doesn't have dispose() method in Node.js reference
        # The observables will be cleaned up automatically when the process ends
        
        # Signal exit to RxPY streams
        if hasattr(self, '_exit_subject') and self._exit_subject:
            try:
                self._exit_subject.on_next(True)
                self._exit_subject.on_completed()
            except Exception:
                pass
        
        # Terminate the process
        if self._process:
            try:
                # Close stdin to signal exit (like Node.js)
                if self._process.stdin:
                    try:
                        self._process.stdin.close()
                        await self._process.stdin.wait_closed()
                    except Exception:
                        pass  # Already closed or other error
                
                # Wait for process to exit gracefully
                try:
                    await asyncio.wait_for(self._process.wait(), timeout=2.0)
                except asyncio.TimeoutError:
                    # Force terminate if it doesn't exit gracefully
                    self._process.terminate()
                    try:
                        await asyncio.wait_for(self._process.wait(), timeout=1.0)
                    except asyncio.TimeoutError:
                        # Kill it if terminate doesn't work
                        self._process.kill()
                        try:
                            await asyncio.wait_for(self._process.wait(), timeout=1.0)
                        except asyncio.TimeoutError:
                            print(f"Warning: Could not kill Sass compiler process {self._process.pid}")
                
                # Close remaining streams (asyncio streams don't have 'closed' attribute)
                if self._process.stdout:
                    try:
                        self._process.stdout.close()
                    except Exception:
                        pass
                if self._process.stderr:
                    try:
                        self._process.stderr.close()
                    except Exception:
                        pass
                    
            except Exception as e:
                print(f"Warning: Error during async process cleanup: {e}")
            finally:
                self._process = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.dispose()


async def init_async_compiler() -> AsyncCompiler:
    """Initialize an asynchronous compiler."""
    return AsyncCompiler(_INIT_FLAG)
