import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

def setup_logging(config_settings=None) -> logging.Logger:
    """Setup centralized logging system
    
    Args:
        config_settings: Configuration settings object (optional)
        
    Returns:
        Configured logger instance
    """
    
    # Handle missing config gracefully during initial setup
    if config_settings is None:
        try:
            from scrubpy.config.settings import settings
            config_settings = settings
        except ImportError:
            # Fallback to basic logging if config not available
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[logging.StreamHandler(sys.stdout)]
            )
            return logging.getLogger('scrubpy')
    
    # Get log level
    log_level_str = config_settings.get('logging.level', 'INFO')
    log_level = getattr(logging, log_level_str.upper(), logging.INFO)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    )
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(simple_formatter)
    console_handler.setLevel(log_level)
    
    # Prepare handlers list
    handlers = [console_handler]
    
    # File handler (if enabled)
    if config_settings.get('logging.file_logging', True):
        try:
            log_dir = Path(config_settings.get('logging.log_dir', Path.home() / '.scrubpy' / 'logs'))
            log_dir.mkdir(parents=True, exist_ok=True)
            
            # Create rotating file handler
            from logging.handlers import RotatingFileHandler
            
            log_file = log_dir / f"scrubpy_{datetime.now().strftime('%Y%m%d')}.log"
            max_bytes = config_settings.get('logging.max_file_size_mb', 10) * 1024 * 1024
            backup_count = config_settings.get('logging.backup_count', 5)
            
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=backup_count
            )
            file_handler.setFormatter(detailed_formatter)
            file_handler.setLevel(log_level)
            handlers.append(file_handler)
            
        except Exception as e:
            # If file logging fails, continue with console only
            print(f"Warning: Could not set up file logging: {e}")
    
    # Configure root logger
    # Remove existing handlers to avoid duplicates
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Configure with new settings
    logging.basicConfig(
        level=log_level,
        handlers=handlers,
        force=True
    )
    
    # Return ScrubPy-specific logger
    scrubpy_logger = logging.getLogger('scrubpy')
    scrubpy_logger.info("Logging system initialized successfully")
    
    return scrubpy_logger

def get_logger(name: str) -> logging.Logger:
    """Get a logger with ScrubPy namespace
    
    Args:
        name: Logger name (will be prefixed with 'scrubpy.')
        
    Returns:
        Logger instance
    """
    return logging.getLogger(f'scrubpy.{name}')

def set_log_level(level: str):
    """Set logging level for all ScrubPy loggers
    
    Args:
        level: Log level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    logging.getLogger('scrubpy').setLevel(log_level)
    
    # Update all existing ScrubPy loggers
    for name in logging.Logger.manager.loggerDict:
        if name.startswith('scrubpy'):
            logging.getLogger(name).setLevel(log_level)

def log_performance(func_name: str, duration: float, operation_type: str = "operation"):
    """Log performance metrics
    
    Args:
        func_name: Function or operation name
        duration: Duration in seconds
        operation_type: Type of operation
    """
    logger = get_logger('performance')
    
    if duration > 10:
        log_level = logging.WARNING
        status = "SLOW"
    elif duration > 1:
        log_level = logging.INFO
        status = "NORMAL"
    else:
        log_level = logging.DEBUG
        status = "FAST"
    
    logger.log(log_level, f"{operation_type.upper()} [{status}] {func_name}: {duration:.2f}s")

def log_data_operation(operation: str, before_shape: tuple, after_shape: tuple, 
                      details: Optional[str] = None):
    """Log data cleaning operations
    
    Args:
        operation: Name of the operation
        before_shape: Shape before operation (rows, cols)
        after_shape: Shape after operation (rows, cols)
        details: Additional details about the operation
    """
    logger = get_logger('operations')
    
    rows_changed = before_shape[0] - after_shape[0]
    cols_changed = before_shape[1] - after_shape[1]
    
    message_parts = [
        f"OPERATION: {operation}",
        f"Before: {before_shape[0]:,} rows × {before_shape[1]} cols",
        f"After: {after_shape[0]:,} rows × {after_shape[1]} cols"
    ]
    
    if rows_changed != 0:
        message_parts.append(f"Rows changed: {rows_changed:+,}")
    
    if cols_changed != 0:
        message_parts.append(f"Columns changed: {cols_changed:+}")
    
    if details:
        message_parts.append(f"Details: {details}")
    
    logger.info(" | ".join(message_parts))

def log_memory_usage():
    """Log current memory usage"""
    try:
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        
        logger = get_logger('memory')
        logger.debug(f"Memory usage: {memory_mb:.1f} MB")
        
        # Warn if memory usage is high
        if memory_mb > 1000:  # 1GB
            logger.warning(f"High memory usage detected: {memory_mb:.1f} MB")
            
    except ImportError:
        # psutil not available
        pass
    except Exception as e:
        logger = get_logger('memory')
        logger.debug(f"Could not check memory usage: {e}")

# Initialize global logger
try:
    logger = setup_logging()
except Exception as e:
    # Fallback to basic logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger('scrubpy')
    logger.warning(f"Could not initialize advanced logging: {e}")

# Convenience function for timing operations
def log_timing(operation_name: str):
    """Decorator to log operation timing
    
    Args:
        operation_name: Name of the operation to log
    
    Usage:
        @log_timing("data_cleaning")
        def clean_data(df):
            # cleaning operations
            return cleaned_df
    """
    def decorator(func):
        import functools
        import time
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                log_performance(operation_name, duration)
                return result
            except Exception as e:
                duration = time.time() - start_time
                get_logger('errors').error(
                    f"Operation {operation_name} failed after {duration:.2f}s: {e}"
                )
                raise
        
        return wrapper
    return decorator

def performance_monitor(operation_type: str = "operation"):
    """
    Simple decorator to monitor and log function performance.
    
    Args:
        operation_type: Type of operation for categorization
        
    Usage:
        @performance_monitor("data_cleaning")
        def clean_data():
            pass
    """
    def decorator(func):
        import functools
        import time
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                log_performance(func.__name__, duration, operation_type)
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"Performance: {func.__name__} ({operation_type}) failed after {duration:.3f}s: {e}")
                raise
        return wrapper
    return decorator