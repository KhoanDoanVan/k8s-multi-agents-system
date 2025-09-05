"""
Shared data models for inter-agent communication
"""

from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime



class AgentRequest(BaseModel):
  id: str
  message: str
  user_id: Optional[str] = None
  context: Dict[str, Any] = {}
  analysis: Dict[str, Any] = {}
  timestamp: datetime = datetime.utcnow()
  
  
  
class AgentResponse(BaseModel):
  request_id: str
  agent_id: str
  status: str
  data: Dict[str, Any] = {}
  error: Optional[str] = None
  timestamp: datetime = datetime.utcnow()

