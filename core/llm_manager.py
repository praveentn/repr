# core/llm_manager.py
import asyncio
import json
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from openai import AsyncAzureOpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class LLMResponse:
    content: str
    usage: Dict[str, int]
    model: str
    response_time: float
    timestamp: str

class LLMManager:
    def __init__(self):
        self.client = None
        self.config = {
            "api_key": os.getenv("AZURE_OPENAI_API_KEY"),
            "endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
            "deployment": os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4.1-nano"),
            "api_version": os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
            "temperature": float(os.getenv("TEMPERATURE", "0.7")),
            "max_tokens": int(os.getenv("MAX_TOKENS", "2000")),
            "top_p": float(os.getenv("TOP_P", "1.0"))
        }
        
        # Representation-specific prompts
        self.representation_prompts = {
            "plain_text": "Provide a clear, well-structured response to the user's query.",
            "color_coded": "Provide a response with clear sections for facts (blue), assumptions (yellow), examples (green), and risks/warnings (red). Mark each section clearly.",
            "knowledge_graph": "Structure your response as interconnected concepts with clear relationships. Identify main entities, their properties, and connections.",
            "analogical": "Explain the concepts using creative analogies and metaphors that make complex ideas accessible.",
            "eli5": "Explain this in very simple terms that a 5-year-old could understand, using everyday examples.",
            "expert": "Provide a comprehensive, technical explanation with detailed analysis and professional insights.",
            "persona_layman": "Explain this in conversational, accessible language for a general audience.",
            "collapsible_concepts": "Structure the response with main concepts and expandable sub-topics. Organize hierarchically.",
            "interactive": "Create an engaging explanation with hypothetical scenarios and 'what-if' questions.",
            "cinematic": "Present the information as a compelling narrative with story elements and dramatic pacing.",
            "timeline": "Structure the response chronologically, showing how concepts evolved over time.",
            "comparison": "Present multiple perspectives or approaches, highlighting similarities and differences.",
            "summary": "Provide a concise overview focusing on key points and takeaways.",
            "detailed": "Give a comprehensive, in-depth analysis covering all aspects thoroughly."
        }
    
    async def initialize(self):
        """Initialize the Azure OpenAI client"""
        try:
            if not self.config["api_key"] or not self.config["endpoint"]:
                raise ValueError("Azure OpenAI credentials not properly configured")
            
            self.client = AsyncAzureOpenAI(
                api_key=self.config["api_key"],
                azure_endpoint=self.config["endpoint"],
                api_version=self.config["api_version"]
            )
            
            print("✅ LLM Manager initialized successfully")
            
        except Exception as e:
            print(f"❌ Failed to initialize LLM Manager: {e}")
            raise
    
    async def generate_response(
        self, 
        query: str, 
        context: Optional[Dict] = None,
        representation_mode: str = "plain_text",
        custom_prompt: Optional[str] = None
    ) -> LLMResponse:
        """Generate response using Azure OpenAI"""
        start_time = time.time()
        
        try:
            # Build messages
            messages = self._build_messages(query, context, representation_mode, custom_prompt)
            
            # Make API call
            response = await self.client.chat.completions.create(
                model=self.config["deployment"],
                messages=messages,
                temperature=self.config["temperature"],
                max_tokens=self.config["max_tokens"],
                top_p=self.config["top_p"]
            )
            
            response_time = time.time() - start_time
            
            return LLMResponse(
                content=response.choices[0].message.content,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                model=self.config["deployment"],
                response_time=round(response_time, 3),
                timestamp=str(time.time())
            )
            
        except Exception as e:
            print(f"Error generating LLM response: {e}")
            raise
    
    def _build_messages(
        self, 
        query: str, 
        context: Optional[Dict],
        representation_mode: str,
        custom_prompt: Optional[str]
    ) -> List[Dict[str, str]]:
        """Build message array for OpenAI API"""
        
        # Base system prompt
        system_prompt = self._get_system_prompt(representation_mode, custom_prompt)
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add context if provided
        if context:
            context_text = self._format_context(context)
            if context_text:
                messages.append({
                    "role": "user", 
                    "content": f"Context: {context_text}"
                })
        
        # Add main query
        messages.append({"role": "user", "content": query})
        
        return messages
    
    def _get_system_prompt(self, representation_mode: str, custom_prompt: Optional[str]) -> str:
        """Get system prompt based on representation mode"""
        base_prompt = """You are an intelligent knowledge representation assistant. 
Your goal is to provide helpful, accurate, and well-structured information based on the user's query and preferred representation mode.

Always maintain clarity, accuracy, and appropriate depth for the chosen representation style."""
        
        if custom_prompt:
            return f"{base_prompt}\n\nSpecial Instructions: {custom_prompt}"
        
        mode_prompt = self.representation_prompts.get(
            representation_mode, 
            self.representation_prompts["plain_text"]
        )
        
        return f"{base_prompt}\n\nRepresentation Mode: {mode_prompt}"
    
    def _format_context(self, context: Dict) -> str:
        """Format context information"""
        context_parts = []
        
        if context.get("chat_history"):
            context_parts.append(f"Previous conversation: {context['chat_history']}")
        
        if context.get("user_profile"):
            context_parts.append(f"User profile: {context['user_profile']}")
        
        if context.get("preferences"):
            context_parts.append(f"User preferences: {context['preferences']}")
        
        if context.get("metadata"):
            context_parts.append(f"Additional context: {context['metadata']}")
        
        return " | ".join(context_parts)
    
    async def generate_representation_optimized_response(
        self,
        content: str,
        target_mode: str,
        user_preferences: Optional[Dict] = None
    ) -> LLMResponse:
        """Generate a response specifically optimized for a representation mode"""
        
        optimization_prompts = {
            "knowledge_graph": "Transform this content into structured nodes and relationships. Identify: 1) Main entities/concepts, 2) Properties of each entity, 3) Relationships between entities, 4) Hierarchical organization.",
            "color_coded": "Reorganize this content with clear color-coded sections: FACTS (key information), ASSUMPTIONS (uncertain elements), EXAMPLES (concrete instances), WARNINGS (potential issues).",
            "analogical": "Rewrite this content using powerful analogies and metaphors. Find real-world comparisons that make complex concepts intuitive.",
            "timeline": "Restructure this content chronologically, showing the progression and evolution of ideas, events, or concepts over time.",
            "comparison": "Present this content as a comparative analysis, highlighting different approaches, perspectives, or alternatives."
        }
        
        if target_mode in optimization_prompts:
            optimization_query = f"{optimization_prompts[target_mode]}\n\nContent to transform:\n{content}"
            
            return await self.generate_response(
                query=optimization_query,
                representation_mode=target_mode
            )
        else:
            # For other modes, return the content as-is
            return LLMResponse(
                content=content,
                usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
                model=self.config["deployment"],
                response_time=0.0,
                timestamp=str(time.time())
            )
    
    def get_current_config(self) -> Dict[str, Any]:
        """Get current LLM configuration"""
        return {
            "model": self.config["deployment"],
            "temperature": self.config["temperature"],
            "max_tokens": self.config["max_tokens"],
            "top_p": self.config["top_p"],
            "api_version": self.config["api_version"]
        }
    
    def update_config(self, new_config: Dict[str, Any]):
        """Update LLM configuration"""
        for key, value in new_config.items():
            if key in self.config:
                self.config[key] = value
        print("✅ LLM configuration updated")
    
    async def health_check(self) -> bool:
        """Check if LLM service is healthy"""
        try:
            if not self.client:
                return False
            
            # Simple test call
            response = await self.client.chat.completions.create(
                model=self.config["deployment"],
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=5
            )
            return True
        except Exception:
            return False
    
    def get_available_models(self) -> List[str]:
        """Get list of available models (would need to be configured)"""
        return [
            "gpt-4.1-nano",
            "gpt-4",
            "gpt-4-32k",
            "gpt-35-turbo",
            "gpt-35-turbo-16k"
        ]
    
    async def estimate_tokens(self, text: str) -> int:
        """Rough token estimation (4 characters ≈ 1 token)"""
        return len(text) // 4
    
    async def validate_api_key(self) -> bool:
        """Validate API key configuration"""
        try:
            await self.health_check()
            return True
        except Exception:
            return False
