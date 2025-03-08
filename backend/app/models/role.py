from sqlalchemy import Column, String, ForeignKey, Table, Integer
from sqlalchemy.orm import relationship
from app.database import Base, engine, UUID

# Many-to-Many Association Table (Junction Table)
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", UUID, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)  # e.g., "admin", "student", "instructor"
    users = relationship("User", secondary=user_roles, back_populates="roles")  # Many-to-Many

    def __repr__(self):
        return f"<Role(name={self.name})>"

# Initialize the table
async def init_db():
    """Initialize the roles table asynchronously."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
