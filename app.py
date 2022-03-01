from datetime import datetime
import os
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlmodel import create_engine, SQLModel, Field, select, Session

class BookModel(SQLModel, table=True):
    id: Optional[int]  = Field(default=None, primary_key=True)
    title: str
    author: str
    pages: int
    start: str
    end: Optional[str]
    score: Optional[int]

class BookBody(BaseModel):
    title: str
    author: str
    pages: int
    start: str = datetime.now().strftime('%d/%m/%Y')
    end: Optional[str]
    score: Optional[int]

class BookUpdate(BaseModel):
    title: Optional[str]
    author: Optional[str]
    pages: Optional[int]
    start: Optional[str]
    end: Optional[str] = datetime.now().strftime('%d/%m/%Y')
    score: Optional[int]

class BookUpdateFinish(BaseModel):
    end: Optional[str] = datetime.now().strftime('%d/%m/%Y')
    score: Optional[int]


app = FastAPI()
# criação do banco e das tabelas
engine = create_engine(url= "sqlite:///db.sqlite3")
if not os.path.isfile("db.sqlite3"):
    SQLModel.metadata.create_all(engine)

@app.get("/books")
def retrieve_books():
    with Session(engine) as session:
        query = select(BookModel)
        books = session.exec(query)
        books_list = [b for b in books]
    return {"books": books_list}

@app.get("/books/{title}")
def status_single_book(title: str):
    with Session(engine) as session:
        try:
            query = select(BookModel).where(BookModel.title == title)
            result = session.exec(query)
            book = result.first()
            assert book is not None, "Not on database"
        except Exception as e:
            raise HTTPException(status_code=404, detail="Book wasn't find. %s" % e)
    return book

@app.post('/addReading', status_code=201)
def add_reading(book: BookBody):
    with Session(engine) as session:
        bk = BookModel(
            title=book.title,
            author=book.author,
            pages=book.pages,
            start=book.start,
            end=book.end or "",
            score=book.score or -1
        )
        session.add(bk)
        session.commit()
    return "OK"

@app.delete("/books/{title}", status_code=204)
def leave_single_book(title: str):
    with Session(engine) as session:
        try:
            query = select(BookModel).where(BookModel.title == title)
            result = session.exec(query)
            book = result.first()
            assert book is not None, "Not on database"
        except Exception as e:
            raise HTTPException(status_code=404, detail="Book wasn't find. %s" % e)
        session.delete(book)
        session.commit()

@app.put("/books/finish/{title}", status_code=204)
def finish_single_reading(title: str, book: BookUpdateFinish):
    with Session(engine) as session:
        try:
            query = select(BookModel).where(BookModel.title == title)
            result = session.exec(query)
            old_book = result.first()
            assert book is not None, "Not on database"
        except Exception as e:
            raise HTTPException(status_code=404, detail="Book wasn't find. %s" % e)
    if book.end:
        old_book.end = book.end
    if book.score:
        old_book.score = book.score

    session.add(old_book)
    session.commit()

@app.put("/books/{title}", status_code=204)
def modify_single_reading(title:str, book:BookUpdate):
    with Session(engine) as session:
        try:
            query = select(BookModel).where(BookModel.title == title)
            result = session.exec(query)
            old_book = result.first()
            assert book is not None, "Not on database"
        except Exception as e:
            raise HTTPException(status_code=404, detail="Book wasn't find. %s" % e)
    if book.title:
        old_book.title = book.title
    if book.author:
        old_book.author = book.author
    if book.pages:
        old_book.pages = book.pages
    if book.start:
        old_book.start = book.start
    if book.end:
        old_book.end = book.end
    if book.score:
        old_book.score = book.score

    session.add(old_book)
    session.commit()