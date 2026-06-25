from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Recording(Base):
    __tablename__ = "recordings"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    transcript = Column(Text, nullable=True)
    raw_metadata = Column(Text, nullable=True)  # JSON string for Grok STT metadata (diarization, timestamps)
    duration = Column(Integer, default=0)  # in seconds
    created_at = Column(DateTime, default=datetime.utcnow)
    
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="recordings")