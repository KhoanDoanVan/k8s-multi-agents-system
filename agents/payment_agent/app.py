"""
Payment Agent - Handles payment processing
"""


import logging
from fastapi import FastAPI
from payment_service import PaymentService
from shared.models import AgentRequest, AgentResponse



logger = logging.getLogger(__name__)
app = FastAPI(title="Payment Agent", version="1.0.0")


payment_service = PaymentService()


@app.post("/process")
async def process_payment_request(request: AgentRequest):
  """
  Process payment-related requests
  """
  try:
    logger.info(f"Payment agent processing request: {request.id}")
    
    result = await payment_service.process_payment(
      request.message, 
      request.analysis.get("parameters", {})
    )
    
    response = AgentResponse(
      request_id=request.id,
      agent_id="payment-agent",
      status="success",
      data=result
    )
    
    return response.dict()
      
  except Exception as e:
    logger.error(f"Payment processing error: {str(e)}")
    response = AgentResponse(
      request_id=request.id,
      agent_id="payment-agent", 
      status="error",
      error=str(e)
    )
    return response.dict()
    
    

@app.get("/health")
async def health_check():
  return {"status": "healthy", "service": "payment-agent"}



