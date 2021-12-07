
import threading
from sqlalchemy import Column, String
from VEXERA.modules.sql import BASE, SESSION
class SnehabhiChats(BASE):
    __tablename__ = "snehabhi_chats"
    chat_id = Column(String(14), primary_key=True)

    def __init__(self, chat_id):
        self.chat_id = chat_id

SnehabhiChats.__table__.create(checkfirst=True)
INSERTION_LOCK = threading.RLock()


def is_snehabhi(chat_id):
    try:
        chat = SESSION.query(SnehabhiChats).get(str(chat_id))
        return bool(chat)
    finally:
        SESSION.close()

def set_snehabhi(chat_id):
    with INSERTION_LOCK:
        snehabhichat = SESSION.query(SnehabhiChats).get(str(chat_id))
        if not snehabhichat:
            snehabhichat = SnehabhiChats(str(chat_id))
        SESSION.add(Snehabhichat)
        SESSION.commit()

def rem_snehabhi(chat_id):
    with INSERTION_LOCK:
        snehabhichat = SESSION.query(SnehabhiChats).get(str(chat_id))
        if kukichat:
            SESSION.delete(snehabhichat)
        SESSION.commit()


def get_all_snehabhi_chats():
    try:
        return SESSION.query(SnehabhiChats.chat_id).all()
    finally:
        SESSION.close()
