from app.database.database import Base
from app.database.database import engine

# Import all database models here
from app.database.models import Trade


def migrate():

    Base.metadata.create_all(
        bind=engine,
    )

    print("✅ Database initialized successfully.")