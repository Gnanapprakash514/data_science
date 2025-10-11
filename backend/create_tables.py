from database import engine, Base
from models import Dataset, DatasetCleaned, DatasetInsights

# Create all tables
Base.metadata.create_all(bind=engine)
print("Tables created successfully!")