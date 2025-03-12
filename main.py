from fastapi import FastAPI, Depends
from pydantic import BaseModel
from typing import List, Annotated, Optional
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session

app = FastAPI()
@app.get("/")
async def read_root():
    return {"message": "Welcome to FastAPI with PostgreSQL!"}

models.Base.metadata.create_all(bind=engine)

class ChoiceBase(BaseModel):
    choice_text: str
    is_correct: bool

class QuestionBase(BaseModel):
    question_text: str
    choices: List[ChoiceBase]

class ChoiceUpdate(BaseModel):
    id : Optional[int]
    choice_text: str
    is_correct: bool

class QuestionUpdateRequest(BaseModel):
    updated_question_text: str
    updated_choices: List[ChoiceUpdate]  # Danh sách các lựa chọn

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
db_dependency = Annotated[Session, Depends(get_db)]

@app.put("/edit/{question_id}")
async def edit_question(
    question_id: int, 
    request: QuestionUpdateRequest,  
    db: db_dependency 
):
    question = db.query(models.Questions).filter(models.Questions.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found!")
    
    question.question_text = request.updated_question_text
    db.commit()
    existing_choices = {c.id: c for c in db.query(models.Choices).filter(models.Choices.question_id == question_id)} 
    for new_choice in request.updated_choices:
        if new_choice.id and new_choice.id in existing_choices:
            existing_choice = existing_choices[new_choice.id]
            existing_choice.choice_text = new_choice.choice_text
            existing_choice.is_correct = new_choice.is_correct
        else:
            db_choice = models.Choices(
                choice_text=new_choice.choice_text,
                is_correct=new_choice.is_correct,
                question_id=question.id 
            )
            db.add(db_choice)
        # Xóa choice không có trong request
    updated_ids = {choice.id for choice in request.updated_choices if choice.id}
    for choice_id in existing_choices:
        if choice_id not in updated_ids:
            db.delete(existing_choices[choice_id])
    db.commit()
    return {"message": "Question and choice eidt successfully!"}  # Trả về phản hồi

    return 

@app.get("/delete/{question_id}")
async def delete_question(question_id: int, db: db_dependency):
    question = db.query(models.Questions).filter(models.Questions.id == question_id).first()
    choices = db.query(models.Choices).filter(models.Questions.id == question_id).all()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found!")
    if not choices:
        raise HTTPException(status_code=404, detail="Choices not found!")
    db.delete(question)
    db.delete(choices)
    # for choice in choices:
    #     db.delete(choice)
    db.commit()
    return {"message": "Question deteled successfully!"} 

@app.get("/questions/{question_id}")
async def read_questions(question_id: int, db: db_dependency):
    result = db.query(models.Questions).filter(models.Questions.id == question_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Question not found!")
    return result

@app.get("/choices/{question_id}")
async def read_choices(question_id: int, db: db_dependency):
    result = db.query(models.Choices).filter(models.Choices.id == question_id).all()
    if not result:
        raise HTTPException(status_code=404, detail="Choices not found!")
    return result

@app.post("/questions/")
async def create_questions(question: QuestionBase, db: db_dependency):
    db_question = models.Questions(question_text=question.question_text)
    db.add(db_question)
    db.commit()
    db.refresh(db_question)

    for choice in question.choices:
        db_choice = models.Choices(
            choice_text=choice.choice_text,
            is_correct=choice.is_correct,
            question_id=db_question.id 
        )
        db.add(db_choice)

    db.commit()
    return {"message": "Question created successfully!"}  # Trả về phản hồi
