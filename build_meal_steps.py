"""Regenerate meal_steps.py from MEALS + curated overrides + built-in heuristics."""

from __future__ import annotations

import importlib.util
import pathlib

from lean_greenbean_snack_steps import LEAN_GREENBEAN_SNACK_STEPS


def _load_main():
    root = pathlib.Path(__file__).resolve().parent
    spec = importlib.util.spec_from_file_location("eat_app_main", root / "main.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod


# Hand-tuned steps (override generic heuristics). Keys must match meal["name"] exactly.
def _heuristic_steps(
    name: str,
    ingredients: list[str],
    meal_type: str,
    ingredient_blob,
) -> list[str]:
    """Former main.steps_for_meal logic — used only when regenerating meal_steps.py."""
    n = name.lower()
    blob = ingredient_blob(ingredients)
    ing_list = ", ".join(ingredients)

    def prep() -> str:
        return f"Gather and prep: {ing_list}. Wash produce, trim proteins, and chop or measure everything before you turn on the heat."

    if "smoothie" in n or "smoothie" in blob or "sorbet" in n:
        return [
            prep(),
            "Add liquids first, then soft fruit or veg, powders, and ice (if using) so the blender can move freely.",
            "Blend until silky, scraping down once if a chunk sticks. Thin with a splash of milk or water if needed.",
            "Taste and adjust sweetness, citrus, or salt; pour into a glass or bowl and enjoy right away.",
        ]

    if "soup" in n:
        return [
            prep(),
            "Warm a little oil or butter; soften aromatics (onion, celery, garlic) until fragrant.",
            "Add broth and main solids; simmer until tender. If using noodles, add them with enough time to cook through.",
            "Season to taste, then ladle hot bowls and finish with any fresh herbs or cheese on your list.",
        ]

    if "curry" in n or "stew" in n or "coconut" in blob and "curry" in blob:
        return [
            prep(),
            "Bloom spices or curry paste in oil until fragrant, then add sturdy vegetables or protein.",
            "Pour in coconut milk, tomatoes, or broth; simmer gently until flavors meld and ingredients are tender.",
            "Stir in quick-cook items (if any) at the end; taste, adjust salt/acid, and serve over rice or with bread.",
        ]

    if "stir" in n and "fry" in n or "stir-fry" in n or "stir fry" in n:
        return [
            prep(),
            "Heat a wok or large skillet until very hot; add oil and sear protein in batches if needed so it browns.",
            "Add vegetables from firmest to softest, tossing often; splash in gf soya sauce or other sauce ingredients to glaze.",
            "Return protein, toss everything, taste for balance, and serve immediately over rice or noodles.",
        ]

    if "pasta" in n or "noodle" in n or "spaghetti" in n or "fettuccine" in n or "linguine" in n:
        return [
            prep(),
            "Salt a pot of boiling water generously; cook pasta until just shy of al dente, reserving a mug of pasta water.",
            "In a wide pan, build your sauce (garlic, tomato, cream, or butter) and simmer until cohesive.",
            "Toss pasta with sauce, splashing in pasta water to loosen; finish with cheese or herbs and serve hot.",
        ]

    if "bake" in n or "baked" in n or "casserole" in n or "frittata" in n or "hash" in n:
        return [
            prep(),
            "Preheat the oven to the temperature that fits your dish (roughly 375–425°F / 190–220°C for many bakes).",
            "Par-cook or sear components on the stove if needed, then combine in your baking dish with sauces or eggs.",
            "Bake until set or golden and cooked through; rest a few minutes, then slice or scoop to serve.",
        ]

    if "salad" in n or "slaw" in n:
        return [
            prep(),
            "Whisk or shake dressing ingredients until emulsified; taste for salt and acid.",
            "Toss greens or chopped vegetables with most of the dressing, adding delicate herbs or cheese last.",
            "Plate and finish with any crunch (nuts, seeds) or extra drizzle; serve chilled or room temp.",
        ]

    if "taco" in n or "burrito" in n or "quesadilla" in n or "wrap" in n or "lettuce wrap" in n:
        return [
            prep(),
            "Cook fillings—seasoned meat, beans, or vegetables—until flavorful and any liquid has reduced.",
            "Warm tortillas or wraps briefly so they flex without cracking.",
            "Layer fillings, fold or roll tightly, slice if needed, and serve with salsa, lime, or extras on the side.",
        ]

    if "rice" in n and ("bowl" in n or "fried" in n or "pot" in n):
        return [
            prep(),
            "Cook rice (or use leftover) while you sear proteins and vegetables in a hot pan with oil.",
            "Push ingredients aside to scramble eggs if using, then fold everything together with gf soya sauce and seasonings.",
            "Pile over rice, top with fresh bits (herbs, avocado), and serve warm.",
        ]

    if "toast" in n or "sandwich" in n or "crostini" in n or "pinwheel" in n or "flauta" in n:
        return [
            prep(),
            "Toast or crisp bread/tortillas until golden where the recipe needs structure.",
            "Spread, layer, or fill with cheeses, proteins, and vegetables in even thickness.",
            "Finish (melt, press, broil, or roll), cut if needed, and serve while textures are at their best.",
        ]

    if "pancake" in n or "waffle" in n or "french toast" in n:
        return [
            prep(),
            "Mix wet and dry separately, then combine until *just* mixed—small lumps are fine for fluffy pancakes/waffles.",
            "Preheat griddle or waffle iron; grease lightly. Cook in batches until bubbles set on top and bottoms are golden.",
            "Stack and serve with toppings from your list while warm.",
        ]

    if "omelette" in n or "omelet" in n or "scramble" in n or "egg muffin" in n:
        return [
            prep(),
            "Whisk eggs with a pinch of salt until uniform; have fillings chopped and ready.",
            "Warm butter or oil in a nonstick pan; pour eggs and cook gently, lifting edges to let uncooked egg flow under.",
            "Add fillings, fold or roll, or bake in tins until just set; serve immediately.",
        ]

    if "oatmeal" in n or (
        "oat" in n
        and meal_type == "Breakfast"
        and "granola" not in n
        and "bar" not in n
        and "cinnamon roll" not in n
    ):
        return [
            prep(),
            "Simmer oats with liquid (water or milk) until creamy, stirring often so nothing sticks.",
            "Stir in spices, fruit, or sweeteners in the last few minutes to preserve texture.",
            "Spoon into bowls and finish with toppings from your list.",
        ]

    if "parfait" in n or "yogurt bowl" in n or "chia" in n and "pudding" in n:
        return [
            prep(),
            "Layer or soak components as the recipe suggests—chia often needs time in the fridge to thicken.",
            "Sweeten or spice to taste before final assembly.",
            "Top with fruit, granola, or nuts and serve chilled.",
        ]

    if meal_type == "Snack" and ("popcorn" in n or "chips" in n or "cracker" in n or "trail mix" in n):
        return [
            prep(),
            "Combine or season components while dry ingredients are still easy to toss evenly.",
            "Bake, toast, or pop according to the snack—watch closely so nuts and sugars don’t burn.",
            "Cool slightly if needed for crunch, then serve in a bowl for snacking.",
        ]

    if meal_type == "Snack" and ("bite" in n or "ball" in n or "cluster" in n or "truffle" in n or "energy" in n):
        return [
            prep(),
            "Mix binders (nut butter, honey, dates) with dry ingredients until the mixture holds when squeezed.",
            "Roll or press into portions; chill if the recipe needs them to firm up.",
            "Store airtight or serve straight from the fridge.",
        ]

    return [
        prep(),
        "Heat your main pan, pot, or oven to the right level for this dish before adding oil or butter.",
        "Cook in logical order—usually browning proteins or hardy veg first, then softer items—so everything finishes together.",
        "Combine, simmer, or toss as the recipe implies; taste and adjust salt, acid, or heat at the end.",
        "Plate while hot (or chill if meant cold) and enjoy!",
    ]


MEAL_STEP_OVERRIDES: dict[str, list[str]] = {
    "One Pot Chicken Rice": [
        "Cut chicken into even pieces; season with salt and black pepper.",
        "Dice onion, mince garlic, rinse rice until water runs clearer; drain.",
        "Heat vegetable oil in a heavy pot on medium-high; brown chicken; remove.",
        "Sauté onion until soft; add garlic 30 seconds; toast rice 1–2 minutes.",
        "Return chicken; add chicken broth and water to the ratio your rice needs; bring to a boil.",
        "Cover, simmer on low until rice is tender and liquid is absorbed (about 18–25 minutes).",
        "Rest off heat 5 minutes; fluff with a fork; adjust salt; serve.",
    ],
    "Chicken Lettuce Wrap": [
        "Mince garlic; slice green onions.",
        "Heat vegetable oil in a skillet on medium-high; cook ground chicken until no pink remains, breaking it up.",
        "Add garlic, most green onions, hoisin, gf soya sauce, sesame oil, and a splash of water; simmer until saucy, 3–5 minutes.",
        "Taste; adjust salt or gf soya sauce; cool slightly so lettuce does not wilt.",
        "Separate lettuce into cups; spoon filling in; top with remaining green onions; serve.",
    ],
    "Chicken Lettuce Wraps": [
        "Mince garlic; slice green onions; drain and finely dice water chestnuts.",
        "Heat vegetable oil in a skillet on medium-high; cook ground chicken until no pink remains, breaking it up.",
        "Add garlic, most green onions, hoisin, gf soya sauce, sesame oil, and a splash of water; simmer until saucy, 3–5 minutes.",
        "Taste; adjust salt or gf soya sauce; cool slightly so lettuce does not wilt.",
        "Separate lettuce into cups; spoon filling in; top with remaining green onions; serve.",
    ],
    "Chicken Wings": [
        "Pat wings very dry. Mix baking powder, garlic powder, paprika, salt, and pepper; toss to coat evenly.",
        "Optional: rest uncovered on a rack in the fridge 1–4 hours for drier skin.",
        "Bake at 425–450°F (220–230°C) on a rack until deeply golden and crisp, flipping once, 40–50 minutes.",
        "Toss with hot sauce mixed with a little melted butter or oil for a sauced wing.",
        "Rest 3 minutes; serve warm.",
    ],
    "Vegetable Stir-Fry": [
        "Prep vegetables; mince garlic and ginger. Mix cornstarch with cold water and gf soya sauce for a slurry.",
        "Heat vegetable oil in a wok on high until smoking-hot.",
        "Stir-fry carrots and broccoli first 2–3 minutes; add bell peppers; add garlic and ginger 30 seconds.",
        "Pour slurry around the pan; toss until glossy; adjust salt; drizzle sesame oil.",
        "Serve immediately over rice.",
    ],
    "Green Curry Chicken Thai": [
        "Cut chicken into bite-sized pieces; slice bell peppers; pick basil leaves.",
        "Heat oil; fry green curry paste 1–2 minutes until fragrant.",
        "Add chicken; cook until mostly opaque; pour in coconut milk; simmer until chicken is cooked through.",
        "Season with fish sauce, lime juice, and brown sugar to balance salty-sour-sweet.",
        "Add peppers until just tender; stir basil in off heat; serve with jasmine rice.",
    ],
    "Pasta": [
        "Boil salted water; cook pasta to al dente; reserve 1 cup pasta water.",
        "Sauté garlic in olive oil on medium-low until fragrant (do not brown).",
        "Add tomato sauce; simmer 8–12 minutes; season with salt, pepper, and red pepper flakes.",
        "Toss pasta with sauce and a splash of pasta water; emulsify by tossing vigorously.",
        "Off heat, add basil and parmesan; add more pasta water if needed; serve hot.",
    ],
    "Burrito Bowls": [
        "Cook rice; keep warm. Season chicken with cumin, chili powder, salt, and oil; grill or pan-sear to 165°F (74°C); rest and slice.",
        "Warm beans with a pinch of salt and cumin; warm or char corn briefly.",
        "Prep avocado, cilantro, lime, cheese, and sour cream.",
        "Layer rice, chicken, beans, corn, and toppings in bowls.",
        "Squeeze lime; sprinkle cilantro; serve.",
    ],
    "Chicken Burrito Bowl": [
        "Cook rice; keep warm. Season chicken; cook through; rest and slice.",
        "Warm black beans with cumin and salt; warm corn.",
        "Prep avocado, cilantro, lime, cheese, sour cream.",
        "Layer rice, chicken, beans, corn, and toppings.",
        "Finish with lime and cilantro.",
    ],
    "Tacos": [
        "Dice onion. Brown ground turkey in oil; drain excess fat if needed.",
        "Add cumin, chili powder, garlic powder, salt, and a splash of water; simmer until saucy.",
        "Warm tortillas on a dry skillet or in foil in the oven.",
        "Fill with turkey, lettuce, cheese, salsa, and lime.",
        "Serve immediately.",
    ],
}


def _write_meal_steps(path: pathlib.Path, steps: dict[str, list[str]]) -> None:
    lines = [
        '"""Recipe-style step lists for each meal (Eat? app). Used by main.meal_api_dict.',
        "",
        "Regenerate with: python3 build_meal_steps.py",
        '"""',
        "",
        "MEAL_STEPS: dict[str, list[str]] = {",
    ]
    for name in sorted(steps.keys()):
        lines.append(f"    {name!r}: [")
        for step in steps[name]:
            lines.append(f"        {step!r},")
        lines.append("    ],")
    lines.append("}")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    mod = _load_main()
    out: dict[str, list[str]] = {}
    for meal in mod.MEALS:
        name = meal["name"]
        if name in MEAL_STEP_OVERRIDES:
            out[name] = MEAL_STEP_OVERRIDES[name]
        elif name in LEAN_GREENBEAN_SNACK_STEPS:
            out[name] = LEAN_GREENBEAN_SNACK_STEPS[name]
        else:
            out[name] = _heuristic_steps(
                name, meal["ingredients"], meal["type"], mod._ingredient_blob
            )

    root = pathlib.Path(__file__).resolve().parent
    _write_meal_steps(root / "meal_steps.py", out)

    names = {m["name"] for m in mod.MEALS}
    assert set(out.keys()) == names, "MEAL_STEPS keys must match MEALS exactly"
    print(f"Wrote {len(out)} meals to meal_steps.py")


if __name__ == "__main__":
    main()
