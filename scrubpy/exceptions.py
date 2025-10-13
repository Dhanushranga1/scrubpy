"""Custom exceptions for ScrubPy

This module defines all custom exceptions used throughout the ScrubPy application
to provide better error handling and more informative error messages.
"""


class ScrubPyError(Exception):
    """Base exception for all ScrubPy-related errors
    
    All ScrubPy exceptions inherit from this base class to allow
    for easy catching of any ScrubPy-specific error.
    """
    pass


class DataValidationError(ScrubPyError):
    """Raised when data validation fails
    
    This exception is raised when input data doesn't meet
    the requirements for processing (e.g., empty DataFrame,
    missing required columns, invalid data types).
    """
    pass


class ConfigurationError(ScrubPyError):
    """Raised when configuration is invalid or missing
    
    This exception is raised when there are issues with
    the ScrubPy configuration file or settings.
    """
    pass


class LLMConnectionError(ScrubPyError):
    """Raised when LLM service is unavailable or fails
    
    This exception is raised when there are connection issues
    with the configured LLM provider (Ollama, OpenAI, etc.).
    """
    pass


class OperationError(ScrubPyError):
    """Raised when a data cleaning operation fails
    
    This exception is raised when a specific cleaning operation
    cannot be completed successfully.
    """
    pass


class PerformanceError(ScrubPyError):
    """Raised when performance limits are exceeded
    
    This exception is raised when operations exceed configured
    memory limits, timeout thresholds, or other performance constraints.
    """
    pass


class FileHandlingError(ScrubPyError):
    """Raised when file operations fail
    
    This exception is raised when there are issues reading,
    writing, or processing files.
    """
    pass


class InterfaceError(ScrubPyError):
    """Raised when interface-specific operations fail
    
    This exception is raised when there are issues with
    web, CLI, or chat interface operations.
    """
    pass


class ValidationWarning(UserWarning):
    """Warning for data validation issues
    
    Used for non-critical validation issues that don't
    prevent processing but should be noted.
    """
    pass


# Convenience functions for creating exceptions with context
def create_data_validation_error(message: str, data_info: dict = None) -> DataValidationError:
    """Create a DataValidationError with additional context
    
    Args:
        message: Error message
        data_info: Dictionary with additional data information
        
    Returns:
        DataValidationError with enriched message
    """
    if data_info:
        context_parts = []
        if 'shape' in data_info:
            context_parts.append(f"Shape: {data_info['shape']}")
        if 'dtypes' in data_info:
            context_parts.append(f"Data types: {len(data_info['dtypes'])} columns")
        if 'missing_pct' in data_info:
            context_parts.append(f"Missing data: {data_info['missing_pct']:.1f}%")
        
        if context_parts:
            message = f"{message} | Context: {' | '.join(context_parts)}"
    
    return DataValidationError(message)


def create_operation_error(operation: str, details: str = None, 
                          suggestion: str = None) -> OperationError:
    """Create an OperationError with helpful context
    
    Args:
        operation: Name of the operation that failed
        details: Detailed error information
        suggestion: Suggested solution or next steps
        
    Returns:
        OperationError with enriched message
    """
    message_parts = [f"Operation '{operation}' failed"]
    
    if details:
        message_parts.append(f"Details: {details}")
    
    if suggestion:
        message_parts.append(f"Suggestion: {suggestion}")
    
    return OperationError(" | ".join(message_parts))


def create_llm_connection_error(provider: str, base_url: str = None, 
                               original_error: Exception = None) -> LLMConnectionError:
    """Create an LLMConnectionError with connection details
    
    Args:
        provider: LLM provider name
        base_url: Provider base URL if applicable
        original_error: Original exception that caused this error
        
    Returns:
        LLMConnectionError with connection context
    """
    message_parts = [f"Cannot connect to LLM provider '{provider}'"]
    
    if base_url:
        message_parts.append(f"URL: {base_url}")
    
    if original_error:
        message_parts.append(f"Underlying error: {str(original_error)}")
    
    # Add helpful suggestions based on provider
    if provider.lower() == 'ollama':
        message_parts.append("Suggestion: Ensure Ollama is running with 'ollama serve'")
    elif provider.lower() in ['openai', 'anthropic']:
        message_parts.append("Suggestion: Check your API key and internet connection")
    
    return LLMConnectionError(" | ".join(message_parts))


def create_performance_error(operation: str, resource: str, limit: str, 
                           current: str, suggestion: str = None) -> PerformanceError:
    """Create a PerformanceError with resource usage details
    
    Args:
        operation: Operation that exceeded limits
        resource: Type of resource (memory, time, etc.)
        limit: Configured limit
        current: Current usage
        suggestion: Suggested solution
        
    Returns:
        PerformanceError with resource context
    """
    message_parts = [
        f"Operation '{operation}' exceeded {resource} limit",
        f"Limit: {limit}",
        f"Current: {current}"
    ]
    
    if suggestion:
        message_parts.append(f"Suggestion: {suggestion}")
    else:
        # Default suggestions based on resource type
        if resource.lower() == 'memory':
            message_parts.append("Suggestion: Reduce chunk_size or memory_limit_gb in configuration")
        elif resource.lower() == 'time':
            message_parts.append("Suggestion: Increase timeout in configuration")
    
    return PerformanceError(" | ".join(message_parts))


# Exception context manager for operation logging
class ExceptionContext:
    """Context manager for handling exceptions with logging
    
    Usage:
        with ExceptionContext("data_loading", logger):
            df = load_data(file_path)
    """
    
    def __init__(self, operation_name: str, logger=None):
        self.operation_name = operation_name
        self.logger = logger
    
    def __enter__(self):
        if self.logger:
            self.logger.debug(f"Starting operation: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            error_msg = f"Operation '{self.operation_name}' failed: {exc_val}"
            
            if self.logger:
                if isinstance(exc_val, ScrubPyError):
                    # Log ScrubPy errors as warnings (expected/handled errors)
                    self.logger.warning(error_msg)
                else:
                    # Log unexpected errors as errors
                    self.logger.error(error_msg, exc_info=True)
            
            # Don't suppress the exception
            return False
        
        if self.logger:
            self.logger.debug(f"Completed operation: {self.operation_name}")
        
        return False