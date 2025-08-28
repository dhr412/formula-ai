import uuid
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from game_infer import ask_question, get_hint

app = FastAPI(
    title="Formula.AI Grand Prix Investigation API",
    description="An API to play a detective game to find the AI saboteur.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QuestionRequest(BaseModel):
    question: str


class AnswerResponse(BaseModel):
    answer: str
    game_over: bool = False
    session_id: str


class HintResponse(BaseModel):
    hint: str
    session_id: str


@app.post("/ask", response_model=AnswerResponse)
async def ask_investigation_question(request: QuestionRequest, http_request: Request):
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="Question must not be empty.")

    session_id = http_request.headers.get("X-Session-ID")
    if not session_id:
        session_id = str(uuid.uuid4())

    try:
        answer = ask_question(request.question, session_id)

        answer_lower = answer.lower()
        game_over = "case solved" in answer_lower or "game over" in answer_lower

        return {"answer": answer, "game_over": game_over, "session_id": session_id}
    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while processing the question.",
        )


@app.get("/hint", response_model=HintResponse)
async def get_investigation_hint(http_request: Request):
    session_id = http_request.headers.get("X-Session-ID")
    if not session_id:
        session_id = str(uuid.uuid4())

    try:
        hint = get_hint(session_id)
        return {"hint": hint, "session_id": session_id}
    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while generating a hint.",
        )


@app.get(
    "/",
    summary="Root Endpoint",
    description="A simple root endpoint to confirm the API is running.",
)
async def read_root():
    return {
        "message": "Welcome to the Grand Prix Investigation API. Use the /ask and /hint endpoints to play."
    }
