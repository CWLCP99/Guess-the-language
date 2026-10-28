"""Guess the Language: the backend (Stage 2).

The browser never sees the answers. It asks the server for a sentence,
sends back a guess, and the server checks it and keeps the score.

Run locally:   uvicorn app.main:app --reload
API docs:      http://localhost:8000/docs
"""

import json
import random
import time
import uuid
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Settings and data
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
SENTENCES: list[dict] = json.loads((ROOT / "app" / "sentences.json").read_text(encoding="utf-8"))
ROUNDS = 10
GAME_TTL_SECONDS = 60 * 60  # unfinished games are forgotten after an hour

Lang = Literal["en", "de", "es"]

app = FastAPI(title="Guess the Language", version="2.0.0")

# Games live in memory: game_id -> game state.
# This is lost whenever the server restarts or the free instance goes to sleep.
# Stage 3 moves it into a real database.
GAMES: dict[str, dict] = {}


# ---------------------------------------------------------------------------
# Request and response shapes (Pydantic checks these automatically)
# ---------------------------------------------------------------------------

class NewGame(BaseModel):
    game_id: str
    round: int
    total: int
    sentence: str          # just the text, never the language


class Guess(BaseModel):
    guess: Lang            # anything other than "en", "de" or "es" gets a 422 error


class AnswerResult(BaseModel):
    correct: bool
    answer: Lang
    meaning: str | None
    score: int
    streak: int
    round: int             # the round that was just answered
    total: int
    finished: bool
    next_sentence: str | None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def forget_old_games() -> None:
    """Drop games nobody has touched in a while, so memory doesn't grow forever."""
    cutoff = time.time() - GAME_TTL_SECONDS
    for game_id in [gid for gid, g in GAMES.items() if g["updated_at"] < cutoff]:
        del GAMES[game_id]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    """Serve the game page."""
    return FileResponse(ROOT / "static" / "index.html")


@app.get("/health")
def health() -> dict:
    """A cheap endpoint the host can call to check the app is alive."""
    return {"status": "ok", "sentences": len(SENTENCES), "active_games": len(GAMES)}


@app.post("/api/games", response_model=NewGame)
def create_game() -> NewGame:
    """Start a game: pick 10 random sentences and send back the first one."""
    forget_old_games()
    game_id = uuid.uuid4().hex
    GAMES[game_id] = {
        "deck": random.sample(SENTENCES, ROUNDS),
        "round": 0,            # index of the sentence waiting for an answer
        "score": 0,
        "streak": 0,
        "updated_at": time.time(),
    }
    first = GAMES[game_id]["deck"][0]
    return NewGame(game_id=game_id, round=1, total=ROUNDS, sentence=first["text"])


@app.post("/api/games/{game_id}/answers", response_model=AnswerResult)
def answer(game_id: str, body: Guess) -> AnswerResult:
    """Check a guess for the current sentence and move the game forward."""
    game = GAMES.get(game_id)
    if game is None:
        raise HTTPException(status_code=404, detail="Game not found. It may have expired, so start a new one.")
    if game["round"] >= ROUNDS:
        raise HTTPException(status_code=409, detail="This game is already finished.")

    item = game["deck"][game["round"]]
    correct = body.guess == item["lang"]
    if correct:
        game["score"] += 1
        game["streak"] += 1
    else:
        game["streak"] = 0

    game["round"] += 1
    game["updated_at"] = time.time()
    finished = game["round"] >= ROUNDS
    next_sentence = None if finished else game["deck"][game["round"]]["text"]

    return AnswerResult(
        correct=correct,
        answer=item["lang"],
        meaning=item.get("meaning"),
        score=game["score"],
        streak=game["streak"],
        round=game["round"],
        total=ROUNDS,
        finished=finished,
        next_sentence=next_sentence,
    )
