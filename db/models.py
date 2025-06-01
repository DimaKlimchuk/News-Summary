from sqlalchemy import Column, Integer, String, Date, Text as SQLText, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    Source = Column(String)
    Title = Column(String)
    Text = Column(SQLText)
    Date = Column(Date)
    Cluster = Column(String)
    Theme = Column(String)
    Sentiment = Column(String)
    Summary = Column(SQLText)
    Category = Column(String)
    Verificated = Column(Boolean, default=False)
    Sources = Column(String)
    Link = Column(String)

