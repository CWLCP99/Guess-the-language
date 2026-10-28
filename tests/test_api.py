"""Tests for the backend. Run them with:  pytest

In Stage 4, GitHub Actions runs these on every push and blocks the deploy if one fails.
"""

from fastapi.testclient import TestClient

from app.main import GAMES, ROUNDS, app

client = TestClient(app)


def start_game() -> dict:
    res = client.post("/api/games")
    assert res.status_code == 200
    return res.json()


def right_answer(game_id: str) -> str:
    """Peek at the server's memory to find the correct answer (only tests may do this)."""
    game = GAMES[game_id]
    return game["deck"][game["round"]]["lang"]


def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_page_is_served():
    res = client.get("/")
    assert res.status_code == 200
    assert "Guess the Language" in res.text


def test_page_does_not_contain_answers():
    # The whole point of Stage 2: the page source no longer contains the sentences or their languages.
    page = client.get("/").text
    assert "Ich verstehe nur Bahnhof" not in page
    assert "sentences.json" not in page


def test_new_game_hides_the_language():
    game = start_game()
    assert set(game) == {"game_id", "round", "total", "sentence"}
    assert game["round"] == 1 and game["total"] == ROUNDS


def test_perfect_game_scores_ten():
    game = start_game()
    gid = game["game_id"]
    for i in range(ROUNDS):
        res = client.post(f"/api/games/{gid}/answers", json={"guess": right_answer(gid)})
        body = res.json()
        assert body["correct"] is True
        assert body["score"] == i + 1
        assert body["streak"] == i + 1
    assert body["finished"] is True
    assert body["next_sentence"] is None


def test_wrong_guess_resets_streak():
    gid = start_game()["game_id"]
    wrong = next(lang for lang in ("en", "de", "es") if lang != right_answer(gid))
    body = client.post(f"/api/games/{gid}/answers", json={"guess": wrong}).json()
    assert body["correct"] is False
    assert body["score"] == 0 and body["streak"] == 0
    assert body["next_sentence"]


def test_invalid_guess_is_rejected():
    gid = start_game()["game_id"]
    res = client.post(f"/api/games/{gid}/answers", json={"guess": "fr"})
    assert res.status_code == 422


def test_unknown_game_returns_404():
    res = client.post("/api/games/does-not-exist/answers", json={"guess": "en"})
    assert res.status_code == 404


def test_no_answers_after_the_game_ends():
    gid = start_game()["game_id"]
    for _ in range(ROUNDS):
        client.post(f"/api/games/{gid}/answers", json={"guess": "en"})
    res = client.post(f"/api/games/{gid}/answers", json={"guess": "en"})
    assert res.status_code == 409
