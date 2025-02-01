from sqlalchemy import create_engine
from app.core.config import settings
from app.db.base_class import Base
from app.models import Paper, RelationType, PaperRelation

def init_db():
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URL)
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("数据库表创建成功！") 