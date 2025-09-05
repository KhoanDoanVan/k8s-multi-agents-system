"""
Circuit Breaker implementation for resilience
"""

import logging
from enum import Enum
from typing import Callable, Any
import time
import asyncio


logger = logging.getLogger(__name__)


class CircuitBreakerState(Enum):
  CLOSED = "closed"
  OPEN = "open"
  HALF_OPEN = "half_open"
  
  
  
class CircuiteBreaker:
  
  def __init__(
    self,
    failure_threshold: int = 5,
    timeout: int = 60,
    recovery_threshold: int = 3
  ):
    self.failure_threshold = failure_threshold
    self.timeout = timeout
    self.recovery_threshold = recovery_threshold
    self.failure_count = 0
    self.success_count = 0
    self.last_failure_time = None
    self.state = CircuitBreakerState.CLOSED
    
    
  
  async def call(self, func: Callable, *args, **kwargs) -> Any:
    """
    Execute function with circuit breaker protection
    """
    
    if self.state == CircuitBreakerState.OPEN:
      if time.time() - self.last_failure_time < self.timeout:
        raise Exception("Circuit breaker is OPEN")
      else:
        self.state = CircuitBreakerState.HALF_OPEN
        logger.info("Circuit breaker moving to HALF_OPEN")
        
    try:
      result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
      
      if self.state == CircuitBreakerState.HALF_OPEN:
        self.success_count += 1
        if self.success_count >= self.recovery_threshold:
          self.state = CircuitBreakerState.CLOSED
          self.failure_count = 0
          self.success_count = 0
          logger.info("Circuit breaker CLOSED - recovered")
          
      return result
    except Exception as e:
      self.failure_count += 1
      self.last_failure_time = time.time()
      
      if self.failure_count >= self.failure_threshold:
        self.state = CircuitBreakerState.OPEN
        logger.warning(f"Circuit breaker OPENED after {self.failure_count} failures")
        
      raise e