from typing import Optional, Dict
from fastapi import FastAPI, HTTPException, Query


app = FastAPI()


def normalize_message(message: Optional[str]) -> str:
    if message is None:
        raise HTTPException(
            status_code=400,
            detail="message query parameter is required",
        )

    normalized_message = message.strip()
    if not normalized_message:
        raise HTTPException(
            status_code=400,
            detail="message query parameter cannot be empty",
        )
    return normalized_message


def build_response(input_value: str, output_value: str) -> Dict[str, object]:
    return {
        "success": True,
        "input": input_value,
        "output": output_value,
    }


@app.get("/")
def read_root() -> Dict[str, object]:
    """Return a basic welcome message."""
    return build_response("", "Hello World")


@app.get("/echo")
def echo(message: Optional[str] = Query(None, max_length=200)) -> Dict[str, object]:
    """Return the same message that was provided."""
    try:
        normalized_message = normalize_message(message)
        return build_response(normalized_message, normalized_message)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="internal error while processing message",
        ) from exc


@app.get("/shout")
def shout(message: Optional[str] = Query(None, max_length=200)) -> Dict[str, object]:
    """Return the provided message converted to uppercase."""
    try:
        normalized_message = normalize_message(message)
        return build_response(normalized_message, normalized_message.upper())
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="internal error while processing message",
        ) from exc


@app.get("/reverse")
def reverse(message: Optional[str] = Query(None, max_length=200)) -> Dict[str, object]:
    """Return the provided message with characters reversed."""
    try:
        normalized_message = normalize_message(message)
        return build_response(normalized_message, normalized_message[::-1])
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="internal error while processing message",
        ) from exc


@app.get("/length")
def length(message: Optional[str] = Query(None, max_length=200)) -> Dict[str, object]:
    """Return the character count of the provided message."""
    try:
        normalized_message = normalize_message(message)
        return build_response(normalized_message, str(len(normalized_message)))
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="internal error while processing message",
        ) from exc
