"""
Search Agent - Handles search requests
"""
from fastapi import FastAPI, HTTPException
from typing import Dict, Any
import logging

from search_service import SearchService
from shared.models import AgentRequest, AgentResponse

logger = logging.getLogger(__name__)
app = FastAPI(title="Search Agent", version="1.0.0")

search_service = SearchService()

@app.post("/process")
async def process_search_request(request: AgentRequest):
  """
  Process search-related requests
  """
  try:
    logger.info(f"Search agent processing request: {request.id}")
    
    result = await search_service.perform_search(
      request.message,
      request.analysis.get("parameters", {})
    )
    
    response = AgentResponse(
      request_id=request.id,
      agent_id="search-agent",
      status="success", 
      data=result
    )
    
    return response.dict()
    
  except Exception as e:
      logger.error(f"Search processing error: {str(e)}")
      response = AgentResponse(
        request_id=request.id,
        agent_id="search-agent",
        status="error",
        error=str(e)
      )
      return response.dict()



@app.get("/health")
async def health_check():
  return {"status": "healthy", "service": "search-agent"}