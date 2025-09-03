"""
Agent Router - Routes requests to appropriate worker agents
"""


from typing import Dict, Any
import logging


logger = logging.getLogger(__name__)


class AgentRouter:
  
  def __init__(self):
    self.agent_mapping = {
      "payment": "payment-agent-service",
      "search": "search-agent-service",
      "general": "general-agent-service"
    }
    
    
  
  def get_target_agent(self, analysis: Dict[str, Any]) -> str:
    """
    Get target agent service name based on analysis
    """
    
    intent = analysis.get("intent", "general")
    target_agent = self.agent_mapping.get(intent, "general-agent-service")
    
    logger.info(f"Routing intent '{intent}' to agent '{target_agent}'")
    
    return target_agent




