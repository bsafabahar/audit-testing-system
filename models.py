"""
Simplified database models for testing with SQLite
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, Date, Numeric
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
    
    # Banking and Check Fields
    CheckNumber = Column(String(50), comment='شماره چک')
    CheckStatus = Column(String(50), comment='وضعیت چک (Issued, Outstanding, Pending, Cleared)')
    AccountNumber = Column(String(100), comment='شماره حساب بانکی')
    Payee = Column(String(700), comment='دریافت‌کننده وجه')
    
    # Transaction Identification Fields
    # Note: Id (line 80) is the internal database primary key
    # TransactionID is the business/external transaction identifier used in reports
    TransactionID = Column(String(100), comment='شناسه یکتای تراکنش - شناسه کسب‌وکار')
    # Note: DocumentDate (line 83) is for document-based transactions
    # TransactionDate is for general transaction timing used across different transaction types
    TransactionDate = Column(DateTime, comment='تاریخ تراکنش - تاریخ عمومی برای انواع تراکنش')
    TransactionType = Column(String(100), comment='نوع تراکنش (Purchase, Sale, Payment, Receipt, etc.)')
    ReferenceNumber = Column(String(100), comment='شماره مرجع')
    
    # Payroll Fields
    EmployeeID = Column(String(50), comment='شناسه کارمند')
    PayrollAmount = Column(Numeric(18, 2), comment='مبلغ حقوق و دستمزد')
    
    # Vendor Fields
    VendorID = Column(String(50), comment='شناسه فروشنده/تأمین‌کننده')
    VendorName = Column(String(700), comment='نام فروشنده/تأمین‌کننده')
    
    # Customer Fields
    CustomerID = Column(String(50), comment='شناسه مشتری')
    
    # Discount Fields
    OriginalAmount = Column(Numeric(18, 2), comment='مبلغ اصلی قبل از تخفیف')
    DiscountAmount = Column(Numeric(18, 2), comment='مبلغ تخفیف')
    
    # Inventory Fields
    ItemID = Column(String(50), comment='شناسه قلم کالا')
    Quantity = Column(Numeric(18, 2), comment='مقدار/تعداد')
    BeginningInventory = Column(Numeric(18, 2), comment='موجودی اول دوره')
    EndingInventory = Column(Numeric(18, 2), comment='موجودی پایان دوره')
    
    # Journal Entry Fields
    EntryType = Column(String(50), comment='نوع ثبت (Manual, Automatic)')
    EntryTime = Column(DateTime, comment='زمان ثبت')
    EnteredBy = Column(String(255), comment='ثبت‌کننده')
    
    def __repr__(self):
        return f"<Transaction(Id={self.Id}, DocumentNumber={self.DocumentNumber}, Amount={self.Debit or self.Credit})>"
