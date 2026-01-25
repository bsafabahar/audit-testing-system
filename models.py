"""
Simplified database models for testing with SQLite
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, Date
from database import Base


class Transaction(Base):
    """Transaction model for audit testing"""
    __tablename__ = 'transactions'
    
    Id = Column(Integer, primary_key=True, autoincrement=True)
    DocumentDate = Column(Date, nullable=True)
    DocumentNumber = Column(Integer, nullable=True)
    AccountCode = Column(String(50), nullable=True)
    Debit = Column(Float, nullable=True, default=0.0)
    Credit = Column(Float, nullable=True, default=0.0)
    Description = Column(String(500), nullable=True)
    
    def __repr__(self):
        return f"<Transaction(Id={self.Id}, DocumentNumber={self.DocumentNumber}, Amount={self.Debit or self.Credit})>"
