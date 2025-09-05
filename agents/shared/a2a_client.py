"""
Agent-to-Agent communication client
"""

import logging
import httpx
import pika
import json
from models import AgentRequest, AgentResponse
from typing import Dict, Any
from circuit_breaker import CircuitBreaker


logger = logging.getLogger(__name__)


class A2AClient:
  
  def __init__(self):
    self.http_client = httpx.AsyncClient(timeout=30.0)
    self.circuit_breakers = {} # Per-agent circuit breakers
    
    # RabbitMQ connection for async communication
    self.rabbitmq_url = "amqp://guest:guest@rabbitmq-service:5672"
    
    
  
  def get_circuit_breaker(self, agent_name: str) -> CircuitBreaker:
    """Get or create circuit breaker for specific agent"""
    if agent_name not in self.circuit_breakers:
      self.circuit_breakers[agent_name] = CircuitBreaker()
    return self.circuit_breakers[agent_name]
  
  
  async def send_sync_request(self, target_agent: str, request: AgentRequest) -> Dict[str, Any]:
    """
    Send synchronous HTTP request to target agent
    """
    circuite_breaker = self.get_circuit_breaker(target_agent)
    url = f"http://{target_agent}:8000/process"
    
    async def make_request():
      response = await self.http_client.post(url, json=request.model_dump(exclude_defaults=True))
      response.raise_for_status()
      return response.json()
    
    try:
      result = await circuite_breaker.call(make_request)
      logger.info(f"Sync request to {target_agent} successful")
      return result
    except Exception as e:
      logger.error(f"Sync request to {target_agent} failed: {str(e)}")
      raise
    
  
  async def send_async_request(self, target_agent: str, request: AgentRequest) -> Dict[str, Any]:
    """
    Send asynchronous request via message queue
    """
    
    try:
      connection = pika.BlockingConnection(pika.URLParameters(self.rabbitmq_url))
      channel = connection.channel()
      
      # Declare queue for target agent
      queue_name = f"{target_agent}_queue"
      channel.queue_declare(queue=queue_name, durable=True)
      
      # Publish message
      channel.basic_publish(
        exchange='',
        routing_key=queue_name,
        body=json.dumps(request.model_dump(exclude_defaults=True)),
        properties=pika.BasicProperties(delivery_mode=2) # Make  message persisitent
      )
      
      connection.close()
      logger.info(f"Async request sent to {target_agent} queue")
      
      return {
        "status": "queued",
        "queue": queue_name
      }
      
    except Exception as e:
      logger.error(f"Failed to send async request to {target_agent}: {str(e)}")
      raise
      

