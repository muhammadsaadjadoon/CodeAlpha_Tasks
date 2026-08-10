from .database import Base, engine
from .ml.train import train_models

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("Database tables are ready.")
    result = train_models()
    print("Model training ready:", result["active_model"])
