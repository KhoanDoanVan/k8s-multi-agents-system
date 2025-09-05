"""
FastAPI Application for Root Agent
"""

import logging
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import uuid
from llm_service import LLMService
from agent_router import AgentRouter
from shared.a2a_client import A2AClient
from shared.models import AgentRequest


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI(title="Root Agent", version="1.0.0")

# Inititialize services
llm_service = LLMService()
agent_router = AgentRouter()
a2a_client = A2AClient()


class RequestPayload(BaseModel):
  message: str
  user_id: str = None
  context: Dict[str, Any] = {}
  
  

@app.post("/process")
async def process_request(payload: RequestPayload):
  """
  Main endpoint to process incoming requests
  """
  
  try:
    request_id = str(uuid.uuid4())
    logger.info(f"Processing request {request_id}: {payload.message}")
    
    # Step 1: Use LLM to analyze and categorize the request
    analysis = await llm_service.analyze_request(payload.message, payload.context)
    
    # Step 2: Route tot appropriate agent based on analysis
    target_agent = agent_router.get_target_agent(analysis)
    
    # Step 3: Forward to target agent
    agent_request = AgentRequest(
      id=request_id,
      message=payload.message,
      user_id=payload.user_id,
      context=payload.context,
      analysis=analysis
    )
    
    # Use appropriate communcation method based on urgency
    if analysis.get("urgent", False):
      # Synchronous HTTP for urgent requests
      response = await a2a_client.send_sync_request(target_agent, agent_request)
    else:
      # Asynchronous message queue for non-urgent requests
      response = await a2a_client.send_async_request(target_agent, agent_request)
      
    return {
      "status": "success",
      "data": response,
      "request_id": request_id
    }
    
  except Exception as e:
    logger.error(f"Error processing request: {str(e)}")
    raise HTTPException(status_code=500, detail=str(e))
  
  
@app.get("/health")
async def health_check():
  return {
    "status": "healthy",
    "service": "root-agent"
  }
  
  