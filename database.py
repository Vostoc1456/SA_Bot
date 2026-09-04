import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()
engine = create_engine(os.getenv("DATABASE_URL", "sqlite:///sa_bot.db"))
SessionLocal = sessionmaker(bind=engine)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    
    # Progress
    current_session = Column(String, default="SA01_WELCOME")
    completed_sessions = Column(JSON, default=[])
    total_xp = Column(Integer, default=0)
    
    # Skills Scores (0-100)
    observation_score = Column(Float, default=0)
    awareness_score = Column(Float, default=0)
    threat_recognition_score = Column(Float, default=0)
    decision_making_score = Column(Float, default=0)
    deescalation_score = Column(Float, default=0)
    
    # Stats
    sessions_completed = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    wrong_answers = Column(Integer, default=0)
    total_questions = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SessionProgress(Base):
    __tablename__ = "session_progress"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    session_code = Column(String, nullable=False)
    current_node = Column(String, nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    score = Column(Integer, default=0)
    answers = Column(JSON, default=[])

class QuestionLog(Base):
    __tablename__ = "question_logs"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    question_id = Column(String, nullable=False)
    selected_answer = Column(String)
    is_correct = Column(Boolean)
    xp_earned = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(engine)