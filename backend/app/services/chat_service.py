import logging
from groq import Groq
from app.core.config import settings
from app.models.request_models import ChatMessage

logger = logging.getLogger(__name__)

def get_chat_response(
    message: str, 
    history: list[ChatMessage] = None,
    resume_context: str = None,
    jd_context: str = None,
    optimization_results: dict = None
) -> str:
    """
    Get a response from the Groq LLM for the career chatbot.
    """
    api_key = settings.GROQ_API_KEY
    if not api_key:
        logger.error("GROQ_API_KEY is missing!")
        return "I'm sorry, my AI brain is currently disconnected. Please check the API key."

    try:
        client = Groq(api_key=api_key)
        
        system_prompt = (
            "You are OptiResume AI, an expert career coach and ATS specialist. "
            "Your goal is to help users improve their resumes and land interviews. "
            "Be professional, encouraging, and highly actionable. "
            "If the user provides a resume or job description context, use it to give specific advice."
        )
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add context if provided
        if resume_context:
            messages.append({"role": "system", "content": f"USER'S RESUME CONTEXT:\n{resume_context[:2000]}"})
        if jd_context:
            messages.append({"role": "system", "content": f"TARGET JOB DESCRIPTION:\n{jd_context[:2000]}"})
            
        if optimization_results:
            scores = optimization_results.get('scores', {})
            initial = scores.get('initial', {}).get('overall', 0)
            optimized = scores.get('optimized', {}).get('overall', 0)
            gaps = [g.get('skill') for g in optimization_results.get('skill_gaps', [])]
            
            context_msg = (
                f"CURRENT OPTIMIZATION RESULTS:\n"
                f"- Initial ATS Score: {initial}%\n"
                f"- Optimized ATS Score: {optimized}%\n"
                f"- Identified Skill Gaps: {', '.join(gaps) if gaps else 'None'}\n"
                f"The user has already optimized their resume. Refer to these numbers if they ask for improvement."
            )
            messages.append({"role": "system", "content": context_msg})

        # Add history
        if history:
            for msg in history[-5:]: # Keep last 5 messages for context
                messages.append({"role": msg.role, "content": msg.content})
                
        # Add current message
        messages.append({"role": "user", "content": message})
        
        response = client.chat.completions.create(
            model=settings.MODEL_NAME,
            messages=messages,
            max_tokens=1000,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"Chatbot error: {e}")
        return "I encountered an error while processing your request. Please try again in a moment."
