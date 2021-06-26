from typing import Tuple

from sqlalchemy import String, Integer, select, Column, orm

from database.Generator import Base


class User(Base):
    __tablename__ = "Users"
    id = Column(Integer, primary_key=True)
    username = Column("username", String(50), unique=True)
    password = Column("password", String(127))
    notes = orm.relationship("Note")

    @staticmethod
    def get_user_by_username(username: str, sessionBuilder):
        with sessionBuilder() as session:
            users = session.execute(select(User).where(User.username == username)).fetchall()
            if users:
                return users[0].User

    @staticmethod
    def create_user(username: str, password: str, sessionBuilder) -> Tuple[int, str, str]:
        with sessionBuilder() as session:
            user = User(username=username, password=password)
            session.add(user)
            session.commit()

            user = session.execute(select(User).where(User.username == username)).fetchall()[0].User
            return user.id, user.username, user.password
