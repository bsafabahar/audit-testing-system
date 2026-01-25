"""
Database models module.
Define your SQL Server tables here as SQLAlchemy models.

Instructions:
1. Import necessary column types from sqlalchemy
2. Create classes that inherit from Base
3. Map your existing SQL Server tables to these classes
4. Run query_runner.py to query your data
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, Date, BigInteger, Numeric, event
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy.orm import relationship, Query
from database import Base


# Soft Delete Mixin
# ===========================

class SoftDeleteMixin:
    """
    Mixin to add soft delete functionality.
    Automatically filters out records where IsDeleted = True
    """
    
    @classmethod
    def query_active(cls, session):
        """
        Get query with soft delete filter applied (only non-deleted records)
        
        Usage:
            # Get only active (non-deleted) records
            results = Transaction.query_active(session).filter(...).all()
            
            # To include deleted records, use regular query
            all_results = session.query(Transaction).all()
        """
        return session.query(cls).filter(cls.IsDeleted == False)


# Configure automatic soft delete filtering for all queries
# This event listener will automatically add IsDeleted = False filter to all queries
@event.listens_for(Query, "before_compile", retval=True)
def filter_soft_deletes(query):
    """
    Automatically filter out soft-deleted records from all queries.
    To include deleted records, use query.execution_options(include_deleted=True)
    
    Usage:
        # Normal query - excludes deleted records automatically
        results = session.query(Transaction).all()
        
        # To include deleted records explicitly
        all_results = session.query(Transaction).execution_options(include_deleted=True).all()
    """
    # Check if we should include deleted records
    for entity in query.column_descriptions:
        entity_class = entity['entity']
        if entity_class is not None and hasattr(entity_class, 'IsDeleted'):
            # Check execution options
            if not query._execution_options.get('include_deleted', False):
                # Add filter for non-deleted records
                query = query.enable_assertions(False).filter(entity_class.IsDeleted == False)
    
    return query


# Your Database Models
# ===========================

class Transaction(Base, SoftDeleteMixin):
    """
    af.Transactions table mapping
    Financial transactions with detailed accounting information
    """
    __tablename__ = 'Transactions'
    __table_args__ = {'schema': 'af'}
    
    # Primary Key
    Id = Column(BigInteger, primary_key=True, autoincrement=True)
    
    # Document Information
    DocumentDate = Column(DateTime)
    DocumentNumber = Column(BigInteger)
    DocumentDescription = Column(String(700))
    
    # Account Codes
    AccountCode = Column(String(700))
    TotalCode = Column(String(50))
    SubsidiaryCode = Column(String(50))
    Detail1Code = Column(String(50))
    Detail2Code = Column(String(50))
    Detail3Code = Column(String(50))
    
    # Financial Amounts
    Debit = Column(Numeric(18, 2))
    Credit = Column(Numeric(18, 2))
    TotalBalance = Column(Numeric(18, 2))
    SubsidiaryBalance = Column(Numeric(18, 2))
    Detail1Balance = Column(Numeric(18, 2))
    Detail2Balance = Column(Numeric(18, 2))
    Detail3Balance = Column(Numeric(18, 2))
    
    # Balance Per Line
    TotalBalancePerLine = Column(Numeric(18, 2), nullable=False, default=0.0)
    SubsidiaryBalancePerLine = Column(Numeric(18, 2), nullable=False, default=0.0)
    Detail1BalancePerLine = Column(Numeric(18, 2), nullable=False, default=0.0)
    Detail2BalancePerLine = Column(Numeric(18, 2), nullable=False, default=0.0)
    Detail3BalancePerLine = Column(Numeric(18, 2), nullable=False, default=0.0)
    
    # Previous Values
    CreditPrevious = Column(Numeric(18, 2))
    DebitPrevious = Column(Numeric(18, 2))
    DescriptionPrevious = Column(Text)
    DocumentDescriptionPrevious = Column(String(700))
    DocumentNumberPrevious = Column(BigInteger)
    PreviousId = Column(BigInteger)
    
    # Titles and Descriptions
    Detail1Title = Column(String(700))
    Detail2Title = Column(String(700))
    Detail3Title = Column(String(700))
    SubsidiaryTitle = Column(String(700))
    Description = Column(String(700), nullable=False, default='')
    CounterPartyDescription = Column(String(700), nullable=False, default='')
    
    # File and Group Information
    FileIndex = Column(Integer)
    TransactionGroup = Column(String(1024))
    RecordIndex = Column(Integer, nullable=False, default=0)
    
    # Flags and Status
    IsCalculated = Column(Boolean, nullable=False)
    IsClosing = Column(Boolean, nullable=False, default=False)
    IsOpening = Column(Boolean, nullable=False, default=False)
    IsDeleted = Column(Boolean, nullable=False)
    IsArchived = Column(Boolean, nullable=False, default=False)
    WithoutAttachment = Column(Boolean, nullable=False, default=False)
    IsResidualItemsAudit = Column(Boolean, nullable=False, default=False)
    
    # Importance and Assertions
    TransactionImportant = Column(Integer, nullable=False, default=0)
    TransActionAssertionEnum = Column(Integer, nullable=False, default=0)
    CounterPartyAssertion = Column(Integer, nullable=False, default=0)
    EntityState = Column(Integer, nullable=False, default=0)
    
    # Audit Trail
    CreationTime = Column(DateTime, nullable=False)
    CreatorUserId = Column(BigInteger)
    LastModificationTime = Column(DateTime)
    LastModifierUserId = Column(BigInteger)
    DeleterUserId = Column(BigInteger)
    DeletionTime = Column(DateTime)
    
    # Attachments and Comments
    AttachmentCount = Column(Integer, nullable=False, default=0)
    CommentCount = Column(Integer, nullable=False, default=0)
    
    # Unique Identifiers and References
    Uuid = Column(UNIQUEIDENTIFIER, nullable=False)
    SamplingSectionId = Column(UNIQUEIDENTIFIER)
    AuditHeadingId = Column(BigInteger)
    
    # Additional Data
    AdditionalData = Column(Text)
    
    def __repr__(self):
        return (f"<Transaction(Id={self.Id}, DocumentNumber={self.DocumentNumber}, "
                f"AccountCode='{self.AccountCode}', Debit={self.Debit}, Credit={self.Credit})>")


class CheckPayables(Base, SoftDeleteMixin):
    """
    af.CheckPayables table mapping
    Payable checks information
    """
    __tablename__ = 'CheckPayables'
    __table_args__ = {'schema': 'af'}
    
    Id = Column(BigInteger, primary_key=True, autoincrement=True)
    Uuid = Column(UNIQUEIDENTIFIER, nullable=False)
    DocumentPaymentNumber = Column(String, comment='شماره برگه پرداخت اسناد')
    DocumentPaymentDate = Column(DateTime, nullable=False, comment='تاریخ برگه پرداخت اسناد')
    CheckNumber = Column(String, comment='شماره چک')
    CheckAmount = Column(Numeric(18, 2), nullable=False, comment='مبلغ چک')
    CheckDate = Column(DateTime, nullable=False, comment='تاریخ چک')
    PayeeCode = Column(String, comment='کد دریافتکننده چک')
    PayeeName = Column(String, comment='نام دریافتکننده چک')
    CreationTime = Column(DateTime, nullable=False)
    CreatorUserId = Column(BigInteger)
    LastModificationTime = Column(DateTime)
    LastModifierUserId = Column(BigInteger)
    IsDeleted = Column(Boolean, nullable=False)
    DeleterUserId = Column(BigInteger)
    DeletionTime = Column(DateTime)
    
    def __repr__(self):
        return f"<CheckPayables(Id={self.Id}, CheckNumber='{self.CheckNumber}', CheckAmount={self.CheckAmount})>"


class CheckReceivables(Base, SoftDeleteMixin):
    """
    af.CheckReceivables table mapping
    Receivable checks information
    """
    __tablename__ = 'CheckReceivables'
    __table_args__ = {'schema': 'af'}
    
    Id = Column(BigInteger, primary_key=True, autoincrement=True)
    Uuid = Column(UNIQUEIDENTIFIER, nullable=False)
    DocumentReceiptNumber = Column(String, comment='شماره برگه دریافت اسناد')
    DocumentReceiptDate = Column(DateTime, nullable=False, comment='تاریخ برگه دریافت اسناد')
    CheckNumber = Column(String, comment='شماره چک')
    CheckAmount = Column(Numeric(18, 2), nullable=False, comment='مبلغ چک')
    CheckDate = Column(DateTime, nullable=False, comment='تاریخ چک')
    DrawerCode = Column(String, comment='کد واگذارکننده چک')
    DrawerName = Column(String, comment='نام واگذارکننده چک')
    CreationTime = Column(DateTime, nullable=False)
    CreatorUserId = Column(BigInteger)
    LastModificationTime = Column(DateTime)
    LastModifierUserId = Column(BigInteger)
    IsDeleted = Column(Boolean, nullable=False)
    DeleterUserId = Column(BigInteger)
    DeletionTime = Column(DateTime)
    
    def __repr__(self):
        return f"<CheckReceivables(Id={self.Id}, CheckNumber='{self.CheckNumber}', CheckAmount={self.CheckAmount})>"


class AssetAdditions(Base, SoftDeleteMixin):
    """
    af.AssetAdditions table mapping
    Asset addition transactions
    """
    __tablename__ = 'AssetAdditions'
    __table_args__ = {'schema': 'af'}
    
    Id = Column(BigInteger, primary_key=True, autoincrement=True)
    Uuid = Column(UNIQUEIDENTIFIER, nullable=False)
    FormNumber = Column(String, comment='شماره برگه')
    FormDate = Column(DateTime, nullable=False, comment='تاریخ برگه')
    AssetCode = Column(String, comment='کد اموال')
    AssetName = Column(String, comment='نام اموال')
    UtilizationDate = Column(DateTime, nullable=False, comment='تاریخ بهرهبرداری')
    DepreciationMethod = Column(String, comment='روش استهلاک')
    DepreciationRate = Column(Numeric(18, 2), nullable=False, comment='نرخ استهلاک')
    TotalCost = Column(Numeric(18, 2), nullable=False, comment='بهای تمامشده')
    CreationTime = Column(DateTime, nullable=False)
    CreatorUserId = Column(BigInteger)
    LastModificationTime = Column(DateTime)
    LastModifierUserId = Column(BigInteger)
    IsDeleted = Column(Boolean, nullable=False)
    DeleterUserId = Column(BigInteger)
    DeletionTime = Column(DateTime)
    
    def __repr__(self):
        return f"<AssetAdditions(Id={self.Id}, AssetCode='{self.AssetCode}', TotalCost={self.TotalCost})>"


class AssetDisposals(Base, SoftDeleteMixin):
    """
    af.AssetDisposals table mapping
    Asset disposal transactions
    """
    __tablename__ = 'AssetDisposals'
    __table_args__ = {'schema': 'af'}
    
    Id = Column(BigInteger, primary_key=True, autoincrement=True)
    Uuid = Column(UNIQUEIDENTIFIER, nullable=False)
    FormNumber = Column(String, comment='شماره برگه')
    FormDate = Column(DateTime, nullable=False, comment='تاریخ برگه')
    AssetCode = Column(String, comment='کد اموال')
    AssetName = Column(String, comment='نام اموال')
    UtilizationDate = Column(DateTime, nullable=False, comment='تاریخ بهرهبرداری')
    DepreciationMethod = Column(String, comment='روش استهلاک')
    DepreciationRate = Column(Numeric(18, 2), nullable=False, comment='نرخ استهلاک')
    TotalCost = Column(Numeric(18, 2), nullable=False, comment='بهای تمامشده')
    AccumulatedDepreciationBeginning = Column(Numeric(18, 2), nullable=False, comment='استهلاک انباشته ابتدای دوره')
    DepreciationDuringPeriod = Column(Numeric(18, 2), nullable=False, comment='استهلاک طی دوره')
    CreationTime = Column(DateTime, nullable=False)
    CreatorUserId = Column(BigInteger)
    LastModificationTime = Column(DateTime)
    LastModifierUserId = Column(BigInteger)
    IsDeleted = Column(Boolean, nullable=False)
    DeleterUserId = Column(BigInteger)
    DeletionTime = Column(DateTime)
    
    def __repr__(self):
        return f"<AssetDisposals(Id={self.Id}, AssetCode='{self.AssetCode}', FormDate={self.FormDate})>"


class AssetEndOfPeriods(Base, SoftDeleteMixin):
    """
    af.AssetEndOfPeriods table mapping
    Asset end of period balances
    """
    __tablename__ = 'AssetEndOfPeriods'
    __table_args__ = {'schema': 'af'}
    
    Id = Column(BigInteger, primary_key=True, autoincrement=True)
    Uuid = Column(UNIQUEIDENTIFIER, nullable=False)
    AssetCode = Column(String, comment='کد اموال')
    AssetName = Column(String, comment='نام اموال')
    UtilizationDate = Column(DateTime, nullable=False, comment='تاریخ بهرهبرداری')
    DepreciationMethod = Column(String, comment='روش استهلاک')
    DepreciationRate = Column(Numeric(18, 2), nullable=False, comment='نرخ استهلاک')
    TotalCost = Column(Numeric(18, 2), nullable=False, comment='بهای تمامشده')
    AccumulatedDepreciationBeginning = Column(Numeric(18, 2), nullable=False, comment='استهلاک انباشته ابتدای دوره')
    DepreciationDuringPeriod = Column(Numeric(18, 2), nullable=False, comment='استهلاک طی دوره')
    AccumulatedDepreciationEnding = Column(Numeric(18, 2), nullable=False, comment='استهلاک انباشته پایان دوره')
    CreationTime = Column(DateTime, nullable=False)
    CreatorUserId = Column(BigInteger)
    LastModificationTime = Column(DateTime)
    LastModifierUserId = Column(BigInteger)
    IsDeleted = Column(Boolean, nullable=False)
    DeleterUserId = Column(BigInteger)
    DeletionTime = Column(DateTime)
    
    def __repr__(self):
        return f"<AssetEndOfPeriods(Id={self.Id}, AssetCode='{self.AssetCode}', TotalCost={self.TotalCost})>"


class InventoryIssues(Base, SoftDeleteMixin):
    """
    af.InventoryIssues table mapping
    Inventory issue/consumption transactions
    """
    __tablename__ = 'InventoryIssues'
    __table_args__ = {'schema': 'af'}
    
    Id = Column(BigInteger, primary_key=True, autoincrement=True)
    Uuid = Column(UNIQUEIDENTIFIER, nullable=False)
    IssueNumber = Column(String, comment='شماره حواله انبار')
    IssueDate = Column(DateTime, nullable=False, comment='تاریخ حواله انبار')
    ItemCode = Column(String, comment='کد کالا')
    ItemName = Column(String, comment='نام کالا')
    Quantity = Column(Numeric(18, 2), nullable=False, comment='مقدار')
    UnitPrice = Column(Numeric(18, 2), nullable=False, comment='نرخ')
    Amount = Column(Numeric(18, 2), nullable=False, comment='مبلغ')
    CostCenterCode = Column(String, comment='کد مرکز هزینه')
    CostCenterName = Column(String, comment='نام مرکز هزینه')
    CreationTime = Column(DateTime, nullable=False)
    CreatorUserId = Column(BigInteger)
    LastModificationTime = Column(DateTime)
    LastModifierUserId = Column(BigInteger)
    IsDeleted = Column(Boolean, nullable=False)
    DeleterUserId = Column(BigInteger)
    DeletionTime = Column(DateTime)
    
    def __repr__(self):
        return f"<InventoryIssues(Id={self.Id}, IssueNumber='{self.IssueNumber}', Amount={self.Amount})>"


class PurchaseReceipts(Base, SoftDeleteMixin):
    """
    af.PurchaseReceipts table mapping
    Purchase receipt transactions
    """
    __tablename__ = 'PurchaseReceipts'
    __table_args__ = {'schema': 'af'}
    
    Id = Column(BigInteger, primary_key=True, autoincrement=True)
    Uuid = Column(UNIQUEIDENTIFIER, nullable=False)
    ReceiptNumber = Column(String, comment='شماره رسید انبار')
    ReceiptDate = Column(DateTime, nullable=False, comment='تاریخ رسید انبار')
    ItemCode = Column(String, comment='کد کالا')
    ItemName = Column(String, comment='نام کالا')
    Quantity = Column(Numeric(18, 2), nullable=False, comment='مقدار')
    UnitPrice = Column(Numeric(18, 2), nullable=False, comment='نرخ')
    Amount = Column(Numeric(18, 2), nullable=False, comment='مبلغ')
    SupplierCode = Column(String, comment='کد تأمینکننده (بستانکاران)')
    SupplierName = Column(String, comment='نام تأمینکننده (بستانکاران)')
    CreationTime = Column(DateTime, nullable=False)
    CreatorUserId = Column(BigInteger)
    LastModificationTime = Column(DateTime)
    LastModifierUserId = Column(BigInteger)
    IsDeleted = Column(Boolean, nullable=False)
    DeleterUserId = Column(BigInteger)
    DeletionTime = Column(DateTime)
    
    def __repr__(self):
        return f"<PurchaseReceipts(Id={self.Id}, ReceiptNumber='{self.ReceiptNumber}', Amount={self.Amount})>"


class PayrollTransactions(Base, SoftDeleteMixin):
    """
    af.PayrollTransactions table mapping
    Employee payroll transactions
    """
    __tablename__ = 'PayrollTransactions'
    __table_args__ = {'schema': 'af'}
    
    Id = Column(BigInteger, primary_key=True, autoincrement=True)
    Uuid = Column(UNIQUEIDENTIFIER, nullable=False)
    VoucherNumber = Column(String, comment='شماره سند')
    VoucherDate = Column(DateTime, nullable=False, comment='تاریخ سند')
    Month = Column(String, comment='ماه')
    EmployeeCode = Column(String, comment='کد کارمند')
    EmployeeFullName = Column(String, comment='نام و نام خانوادگی کارمند')
    WorkedDays = Column(Integer, nullable=False, comment='کارکرد (روز)')
    MissionDays = Column(Integer, nullable=False, comment='مأموریت (روز)')
    OvertimeHours = Column(Numeric(18, 2), nullable=False, comment='اضافهکار (ساعت)')
    BaseSalary = Column(Numeric(18, 2), nullable=False, comment='حقوق پایه')
    AttractionAllowance = Column(Numeric(18, 2), nullable=False, comment='حق جذب')
    RegularBenefits = Column(Numeric(18, 2), nullable=False, comment='سایر مزایای مستمر')
    OvertimePay = Column(Numeric(18, 2), nullable=False, comment='اضافهکاری')
    NightShiftPay = Column(Numeric(18, 2), nullable=False, comment='شبکاری')
    ShiftPay = Column(Numeric(18, 2), nullable=False, comment='نوبتکاری')
    IrregularBenefits = Column(Numeric(18, 2), nullable=False, comment='سایر مزایای غیرمستمر')
    InsuranceDeduction = Column(Numeric(18, 2), nullable=False, comment='بیمه مکسوره')
    TaxDeduction = Column(Numeric(18, 2), nullable=False, comment='مالیات مکسوره')
    OtherDeductions = Column(Numeric(18, 2), nullable=False, comment='سایر کسورات')
    NetPayment = Column(Numeric(18, 2), nullable=False, comment='خالص پرداختی')
    CreationTime = Column(DateTime, nullable=False)
    CreatorUserId = Column(BigInteger)
    LastModificationTime = Column(DateTime)
    LastModifierUserId = Column(BigInteger)
    IsDeleted = Column(Boolean, nullable=False)
    DeleterUserId = Column(BigInteger)
    DeletionTime = Column(DateTime)
    
    def __repr__(self):
        return f"<PayrollTransactions(Id={self.Id}, EmployeeCode='{self.EmployeeCode}', NetPayment={self.NetPayment})>"


class SalesReturns(Base, SoftDeleteMixin):
    """
    af.SalesReturns table mapping
    Sales return transactions
    """
    __tablename__ = 'SalesReturns'
    __table_args__ = {'schema': 'af'}
    
    Id = Column(BigInteger, primary_key=True, autoincrement=True)
    Uuid = Column(UNIQUEIDENTIFIER, nullable=False)
    ReturnNumber = Column(String, comment='شماره برگشت از فروش')
    ReturnDate = Column(DateTime, nullable=False, comment='تاریخ برگشت از فروش')
    CustomerCode = Column(String, comment='کد مشتری')
    CustomerName = Column(String, comment='نام مشتری')
    ItemCode = Column(String, comment='کد کالا')
    ItemName = Column(String, comment='نام کالا')
    Quantity = Column(Numeric(18, 2), nullable=False, comment='مقدار')
    UnitPrice = Column(Numeric(18, 2), nullable=False, comment='نرخ')
    Amount = Column(Numeric(18, 2), nullable=False, comment='مبلغ')
    CreationTime = Column(DateTime, nullable=False)
    CreatorUserId = Column(BigInteger)
    LastModificationTime = Column(DateTime)
    LastModifierUserId = Column(BigInteger)
    IsDeleted = Column(Boolean, nullable=False)
    DeleterUserId = Column(BigInteger)
    DeletionTime = Column(DateTime)
    
    def __repr__(self):
        return f"<SalesReturns(Id={self.Id}, ReturnNumber='{self.ReturnNumber}', Amount={self.Amount})>"


class SalesTransactions(Base, SoftDeleteMixin):
    """
    af.SalesTransactions table mapping
    Sales invoice transactions
    """
    __tablename__ = 'SalesTransactions'
    __table_args__ = {'schema': 'af'}
    
    Id = Column(BigInteger, primary_key=True, autoincrement=True)
    Uuid = Column(UNIQUEIDENTIFIER, nullable=False)
    InvoiceNumber = Column(String, comment='شماره فاکتور فروش')
    InvoiceDate = Column(DateTime, nullable=False, comment='تاریخ فاکتور فروش')
    CustomerCode = Column(String, comment='کد مشتری')
    CustomerName = Column(String, comment='نام مشتری')
    ItemCode = Column(String, comment='کد کالا')
    ItemName = Column(String, comment='نام کالا')
    Quantity = Column(Numeric(18, 2), nullable=False, comment='مقدار')
    UnitPrice = Column(Numeric(18, 2), nullable=False, comment='نرخ')
    Amount = Column(Numeric(18, 2), nullable=False, comment='مبلغ')
    CreationTime = Column(DateTime, nullable=False)
    CreatorUserId = Column(BigInteger)
    LastModificationTime = Column(DateTime)
    LastModifierUserId = Column(BigInteger)
    IsDeleted = Column(Boolean, nullable=False)
    DeleterUserId = Column(BigInteger)
    DeletionTime = Column(DateTime)
    
    def __repr__(self):
        return f"<SalesTransactions(Id={self.Id}, InvoiceNumber='{self.InvoiceNumber}', Amount={self.Amount})>"
