import logging
from pathlib import Path
from functools import wraps
from mcp.server.fastmcp import Context

LOG_CONFIG = {
  'dir': 'logs/',
  'file_name': 'sweetpotatobase_mcp.log',
  'default_log_level': 'debug',
  'format': '%(asctime)s [%(levelname)s] %(message)s',
}

def string_to_log_level(level: str):
  return logging._nameToLevel.get(level.upper(), logging.INFO)

log_dir = Path(LOG_CONFIG['dir'])
log_dir.mkdir(exist_ok=True)

log_file = log_dir / LOG_CONFIG['file_name']

default_log_level = string_to_log_level(LOG_CONFIG['default_log_level'])

log_format = LOG_CONFIG['format']

logging.basicConfig(
  filename=log_file,
  level=default_log_level,
  format=log_format,
)

def with_logging(level: str = 'info'):
  """
  Decorator to log entry, exit, and errors for MCP tools at a given level.
  Works with both sync and async functions.
  """

  def decorator(func):
    # is_async = inspect.iscoroutinefunction(func)
    # needs 'inspect' module to know if a function is sync/async
    # setting is_async false for now
    is_async = False

    @wraps(func)
    async def async_wrapper(*args, **kwargs):
      ctx = None
      if args and hasattr(args[0], 'log'):
        ctx = args[0]
      func_name = func.__name__
      level_num = string_to_log_level(level)
      start_msg = f'Starting tool: {func_name}'
      end_msg = f'Completed tool: {func_name} successfully'

      # Entry log
      if ctx:
        ctx.log(level.lower(), start_msg)
      logging.log(level_num, start_msg)

      try:
        result = await func(*args, **kwargs)
        # Exit log
        if ctx:
          ctx.log(level.lower(), end_msg)
        logging.log(level_num, end_msg)
        return result
      except Exception as e:
        err_msg = f'Error in tool {func_name}: {e}'
        if ctx:
          ctx.log('error', err_msg)
        logging.exception(err_msg)
        raise

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
      ctx = None
      # check if context has log method
      if args and hasattr(args[0], 'log'):
        ctx = args[0]
      func_name = func.__name__
      level_num = string_to_log_level(level)
      start_msg = f'Starting tool: {func_name}'
      end_msg = f'Completed tool: {func_name} successfully'

      # Entry log
      if ctx:
        ctx.log(level.lower(), start_msg)
      logging.log(level_num, start_msg)

      try:
        result = func(*args, **kwargs)
        # Exit log
        if ctx:
          ctx.log(level.lower(), end_msg)
        logging.log(level_num, end_msg)
        return result
      except Exception as e:
        err_msg = f'Error in tool {func_name}: {e}'
        if ctx:
          ctx.log('error', err_msg)
        logging.exception(err_msg)
        raise

    return async_wrapper if is_async else sync_wrapper

  return decorator


async def log(ctx, level: str, message: str):
  """Send logs to both MCP context and file."""
  level_lower = level.lower()

  # Send to MCP context
  if ctx:
    await ctx.log(level_lower, message)

  # Send to Python logging
  if level_lower == 'debug':
    logging.debug(message)
  elif level_lower == 'warning':
    logging.warning(message)
  elif level_lower == 'error':
    logging.error(message)
  else:
    logging.info(message)


async def log_server_tool(ctx: Context, func_name: str, func, *args, **kwargs):
  """Helper to log tool execution"""
  log_level = LOG_CONFIG['default_log_level']
  await log(ctx, log_level, f'Starting tool: {func_name}')
  try:
    result = await func(*args, **kwargs)
    await log(ctx, log_level, f'Completed tool: {func_name} successfully')
    return result
  except Exception as e:
    await log(ctx, 'error', f'Error in tool {func_name}: {e}')
    raise
