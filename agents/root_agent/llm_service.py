"""
LLM Service for request analysis and categorization
"""

import os
from typing import Dict, Any
import json
from google import genai
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMService:
  
  def __init__(self):
    # In production, use proper secret management
    self.gemini_api_key = os.getenv("GEMINI_API_KEY")
    


  async def analyze_request(
    self, 
    message: str, 
    context: Dict[str, Any] = {}
  ) -> Dict[str, Any]:
    """
    Analyze request using LLM to determine intent and routing
    """
    try:
      if self.gemini_api_key:
        # Use Gemini for real analysis
        response = await self._analyze_with_gemini(message, context)
      else:
        # Fallback to rule-based analysis
        response = self._analyze_with_rules(message, context)
    except Exception as e:
      logger.error(f"LLM analysis error: {str(e)}")
      # Fallback to rule-based analysis
      return self._analyze_with_rules(message, context)
        
        
  
  async def _analyze_with_gemini(
    self,
    message: str,
    context: Dict[str, Any]
  ) -> Dict[str, Any]:
    """
    Use OpenAI GPT for request analysis
    """
    
    prompt = f"""
      Analyze the following user request and determine:
        1. Intent category (payment, search, general, support)
        2. Urgency level (urgent, normal, low)
        3. Required parameters
        4. Confidence score (0-1)

        User message: "{message}"
        Context: {json.dumps(context)}

        Respond in JSON format:
        {{
          "intent": "category",
          "urgency": "level",
          "urgent": boolean,
          "parameters": {{}},
          "confidence": 0.0-1.0,
          "reasoning": "explanation"
        }}
    """
    
    # Use Geminii for real analysis
    client = genai.Client(api_key=self.gemini_api_key)
    
    response = client.models.generate_content(
      model="gemini-2.5-flash", 
      contents=message
    )
    
    return json.loads(response.text)
    
    
    
  def _analyze_with_rules(
    self,
    message: str,
    context: Dict[str, Any]
  ) -> Dict[str, Any]:
    """Rule-based fallback analysis"""
    
    message_lower = message.lower()
    
    # Payment intent keywords
    if any(keyword in message_lower for keyword in ['pay', 'payment', 'charge', 'bill', 'invoice']):
      return {
        "intent": "payment",
        "urgency": "urgent",
        "urgent": True,
        "parameters": {"amount": None, "currency": "USD"},
        "confidence": 0.8,
        "reasoning": "Contains payment-related keywords"
      }
      
    
    # Search intent keywords
    elif any(keyword in message_lower for keyword in ['search', 'find', 'look for', 'query']):
      return {
        "intent": "search",
        "urgency": "normal",
        "urgent": False,
        "parameters": {"query": message},
        "confidence": 0.7,
        "reasoning": "Contains search-related keywords"
      }
      
    
    # Default to general intent
    else:
      return {
        "intent": "general",
        "urgency": "normal", 
        "urgent": False,
        "parameters": {},
        "confidence": 0.5,
        "reasoning": "No specific intent detected"
      }