from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..utils.database import Base
from sqlalchemy.dialects.postgresql import UUID  # ✅ SQLAlchemy's UUID type
from uuid import uuid4    

class UserProgress(Base):
    __tablename__ = "user_progress"
    
    # id = Column(Integer, primary_key=True, index=True)
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    total_xp = Column(Integer, default=0, nullable=False)
    level = Column(Integer, default=1, nullable=False)
    last_completed_node = Column(String(100), nullable=True)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationship
    user = relationship("User", back_populates="progress", uselist=False) 