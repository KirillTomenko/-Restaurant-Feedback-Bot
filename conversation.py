import logging
from datetime import datetime

logger = logging.getLogger(__name__)

SURVEY_STEPS = [
    {
        "step": 1,
        "question": "Welcome to our customer survey! Let's get started.\n\nWhat is your full name?",
        "field": "name"
    },
    {
        "step": 2,
        "question": "Thank you! What is your email address?",
        "field": "email"
    },
    {
        "step": 3,
        "question": "What is your phone number?",
        "field": "phone"
    },
    {
        "step": 4,
        "question": "Which company or organization do you represent?",
        "field": "company"
    },
    {
        "step": 5,
        "question": "How did you hear about us?\n(e.g., Social media, Friend, Advertisement, Search engine)",
        "field": "source"
    },
    {
        "step": 6,
        "question": "On a scale of 1-10, how satisfied are you with our service?",
        "field": "satisfaction_rating"
    },
    {
        "step": 7,
        "question": "What do you like most about our product/service?",
        "field": "likes"
    },
    {
        "step": 8,
        "question": "What improvements would you suggest?",
        "field": "improvements"
    },
    {
        "step": 9,
        "question": "Would you recommend us to others? (Yes/No/Maybe)",
        "field": "would_recommend"
    },
    {
        "step": 10,
        "question": "Any additional comments or feedback?",
        "field": "additional_comments"
    }
]

class ConversationHandler:
    def __init__(self):
        self.user_sessions = {}
    
    def get_session(self, user_id):
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {
                "current_step": 0,
                "responses": {},
                "started_at": datetime.now().isoformat()
            }
        return self.user_sessions[user_id]
    
    def reset_session(self, user_id):
        if user_id in self.user_sessions:
            del self.user_sessions[user_id]
    
    def handle_message(self, user_id, chat_id, text):
        text = text.strip()
        
        if text.lower() in ['/start', '/survey']:
            self.reset_session(user_id)
            session = self.get_session(user_id)
            session["user_id"] = user_id
            session["chat_id"] = chat_id
            session["current_step"] = 1
            first_question = SURVEY_STEPS[0]["question"]
            return first_question, False, None
        
        if text.lower() == '/cancel':
            self.reset_session(user_id)
            return "Survey cancelled. Type /start to begin a new survey.", False, None
        
        if text.lower() == '/help':
            return (
                "Available commands:\n"
                "/start - Start a new survey\n"
                "/cancel - Cancel current survey\n"
                "/help - Show this help message"
            ), False, None
        
        session = self.get_session(user_id)
        current_step = session["current_step"]
        
        if current_step == 0 and text.lower() not in ['/start', '/survey']:
            return "Please type /start to begin the survey.", False, None
        
        if current_step > 0 and current_step <= len(SURVEY_STEPS):
            step_info = SURVEY_STEPS[current_step - 1]
            session["responses"][step_info["field"]] = text
            logger.info(f"User {user_id} answered step {current_step}: {step_info['field']} = {text}")
        
        session["current_step"] += 1
        next_step = session["current_step"]
        
        if next_step <= len(SURVEY_STEPS):
            next_question = SURVEY_STEPS[next_step - 1]["question"]
            return next_question, False, None
        
        survey_data = self.compile_survey_data(session)
        self.reset_session(user_id)
        
        completion_message = (
            "Thank you for completing our survey!\n\n"
            "Your responses have been recorded. We appreciate your feedback!"
        )
        
        return completion_message, True, survey_data
    
    def compile_survey_data(self, session):
        return {
            "user_id": session.get("user_id"),
            "chat_id": session.get("chat_id"),
            "started_at": session.get("started_at"),
            "completed_at": datetime.now().isoformat(),
            "responses": session.get("responses", {})
        }
