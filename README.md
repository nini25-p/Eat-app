# Eat?

A cozy FastAPI meal finder that suggests recipes from your ingredients, with built-in prep times, ingredient chips, favourites, and step-by-step cooking instructions.

## What It Does

- Search meals by ingredient keywords (ex: `chicken, rice, garlic`)
- Filter by meal type: Breakfast, Lunch, Dinner, or Snack
- Toggle gluten-free filtering
- Get a random suggestion with **Surprise Me**
- Save meals to favourites (stored in browser `localStorage`)
- Expand each meal to view cooking steps

## Tech Stack

- Python
- FastAPI
- Uvicorn
- Single-file HTML/CSS/JS UI rendered from `main.py`

## Project Files

- `main.py` - API endpoints, meal dataset, prep times, and embedded UI
- `meal_steps.py` - Generated step lists used at runtime (`MEAL_STEPS`)
- `build_meal_steps.py` - Regenerates `meal_steps.py`
- `lean_greenbean_snack_steps.py` - Curated snack steps for selected snack items

## Run Locally

1. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install fastapi uvicorn
```

3. Start the app:

```bash
uvicorn main:app --reload
```

4. Open:

- App: `http://127.0.0.1:8000/`
- Favourites page: `http://127.0.0.1:8000/favorites`
- API docs: `http://127.0.0.1:8000/docs`

## API Endpoints

- `GET /meal`
  - Query params:
    - `ingredients` (comma-separated string)
    - `meal_type` (`All`, `Breakfast`, `Lunch`, `Dinner`, `Snack`)
    - `gluten_free` (`true/false`)
- `GET /surprise`
  - Query params:
    - `meal_type`
    - `gluten_free`
- `GET /` - Main UI
- `GET /favorites` - Favourites UI

## Steps Data Workflow

Runtime uses `MEAL_STEPS` from `meal_steps.py`.

If you change meals, snack step overrides, or heuristic logic, regenerate steps:

```bash
python3 build_meal_steps.py
```

## Notes

- Snack ideas include a merged catalog from two sources (Lean Green Bean-inspired set + existing PureWow-derived set).
- Lean Green Bean snack inspiration reference:
  - https://www.theleangreenbean.com/homemade-snacks-to-make/
