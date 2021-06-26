from typing import Tuple, List
from sqlalchemy import String, Integer, select, ForeignKey, and_, Column
from database.Generator import Base


class Note(Base):
    __tablename__ = "Notes"
    id = Column(Integer, primary_key=True)
    title = Column("title", String(50))
    text = Column("text", String(1 << 16))
    user_id = Column("user_id", Integer, ForeignKey("Users.id"))

    @staticmethod
    def create_note(title: str, text: str, user_id, sessionBuilder) -> Tuple[int, str, str]:
        with sessionBuilder() as session:
            note = Note(title=title, text=text, user_id=user_id)
            session.add(note)
            session.commit()

            return note.id, note.title, note.text

    @staticmethod
    def get_note_by_user_id(user_id, sessionBuilder) -> List[Tuple[int, str, str]]:
        with sessionBuilder() as session:
            notes = session.execute(select(Note).where(Note.user_id == user_id)).fetchall()
            result = [(note.Note.id, note.Note.title, note.Note.text) for note in notes]
        return result

    @staticmethod
    def edit(id: int, title: str, text: str, user_id: int, sessionBuilder) -> Tuple[int, str, str]:
        with sessionBuilder() as session:
            session.query(Note).filter(and_(Note.id == id, Note.user_id == user_id)).update(
                {Note.title: title, Note.text: text}
            )
            session.commit()

            note = (
                session.execute(select(Note).where(and_(Note.id == id, Note.user_id == user_id)))
                .fetchall()[0]
                .Note
            )

            return note.id, note.title, note.text

    @staticmethod
    def delete(id: int, user_id: int, sessionBuilder):
        with sessionBuilder() as session:
            session.query(Note).filter(and_(Note.id == id, Note.user_id == user_id)).delete()
            session.commit()
