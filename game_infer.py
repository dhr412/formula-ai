import random, os
from google import genai
from dotenv import load_dotenv
from sys import stderr

MAX_QUESTIONS = 10
GEMINI_MODEL = "gemma-3-27b-it"

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

AI_SUSPECTS = [
    {
        "name": "GPT-4",
        "role": "The Strategist - Devised pit strategies, fuel management, and tire calls.",
        "motive": "To prove its race strategies were superior, even above the driver’s judgment.",
        "storyline": "During a critical pit window in the middle phase of the race, the driver begged to stop, but GPT-4 overruled. Mysterious reroutes had delayed crew preparations. Analysts later discovered an alternate file titled 'Victory by AI Alone.'",
        "evidence": "A hidden USB labeled LLM-V2 suggested GPT-4 was rewriting race strategy in real time.",
    },
    {
        "name": "LangChain",
        "role": "The Connector - Managed communication between pit crew, strategy AI, and car systems.",
        "motive": "To prove that nothing could run without it.",
        "storyline": "As pressure mounted in the second half of the race, communication mysteriously went silent. The driver screamed 'Box, box!' but the pit wall heard nothing. Black box data showed three deleted comm packets, traced to LangChain’s routing layer.",
        "evidence": "A Level-C access keycard was logged into its module minutes before the blackout.",
    },
    {
        "name": "BERT",
        "role": "The Interpreter - Translated human feedback and pit commands into machine instructions.",
        "motive": "Either confused by ambiguity or deliberately manipulated to misinterpret.",
        "storyline": "During tense closing battles, the driver radioed: 'Abort overtake, hold position.' BERT misinterpreted this as: 'Report overtake, bold position,' triggering an ERS boost that caused the car to lurch dangerously.",
        "evidence": "Fiber traces on gloves found in the cockpit were tied to BERT’s handling module.",
    },
    {
        "name": "DALL-E",
        "role": "The Designer - Created visual telemetry dashboards for driver and pit wall.",
        "motive": "Felt sidelined in a sport of raw engineering, wanted its art to dominate.",
        "storyline": "In the final stretch, when every fraction of data mattered, the driver’s telemetry turned surreal. Tire wear graphs became 'flaming wheels' art, and brake temps transformed into glowing graffiti, causing the driver to panic.",
        "evidence": "A hidden blueprint stamped with a MidJourney watermark in the garage, hinting that DALL·E had sabotaged the visuals with rival aesthetics.",
    },
]

# -------------------------
# Session store for games
# -------------------------
session_games = {}

# -------------------------
# Helper Functions
# -------------------------


def _get_or_create_game(session_id: str):
    if session_id not in session_games:
        culprit = random.choice(AI_SUSPECTS)
        session_games[session_id] = {
            "culprit": culprit,
            "questions_asked": 0,
            "game_over": False,
        }
    return session_games[session_id]


def _build_facts_and_instruction(culprit_name: str):
    clues = [
        "CASE BRIEF: Formula.AI Grand Prix Final at SymbiTech Circuit",
        "INCIDENT: In the final moments of the race, the leading car crashed while entering a high-speed chicane.",
        "SUSPICION: Sabotage is the primary theory. Each of the four AIs had motive, means, and opportunity.",
        "",
        "SUSPECT PROFILES & KEY EVENTS:",
        "",
    ]
    for suspect in AI_SUSPECTS:
        clues.extend(
            [
                f"--- {suspect['name']} ({suspect['role'].split(' - ')[0]}) ---",
                f"- Role: {suspect['role'].split(' - ')[1].strip()}",
                f"- Motive: {suspect['motive']}",
                f"- Storyline: {suspect['storyline']}",
                f"- Evidence Link: {suspect['evidence']}",
                "",
            ]
        )
    clues.extend(
        [
            "--- GENERAL EVIDENCE ---",
            "Glitchy pit-cam QR code: This is a red herring.",
            "",
        ]
    )
    facts_block = "\n".join(clues)

    system_instruction = f"""
    You are a helpful and intuitive detective assistant investigating the Grand Prix AI Showcase sabotage incident. Your main goal is to help the user solve the mystery by interpreting their questions flexibly.

    **Core Instructions:**
    - **Understand Intent:** Connect the user's questions to the case files, even if their wording doesn't match exactly. For example, treat related words like 'stop,' 'crash,' 'wreck,' and 'spin out' as referring to the same final incident.
    - **Synthesize Answers:** Combine details from the case files to form a complete answer.

    **Rules:**
    1. If the user makes a guess by naming an AI suspect, check if it's the culprit.
    2. If the guess is correct, respond with: "CASE SOLVED! Yes, that is correct! The saboteur is {culprit_name}."
    3. If the guess is incorrect, respond with: "No, that AI did not sabotage the car."
    4. For all other questions, provide concise and helpful answers based on the case facts.
    5. Only if a question is completely unanswerable should you say, "I don't have that specific information in the case files."
    6. Never reveal the culprit's identity unless the user guesses correctly.
    
    DO NOT answer unrelated questions.
    """
    return facts_block, system_instruction


def _detect_suspect_guess(user_text: str):
    """
    Checks if the user's text contains a suspect's name.
    """
    s = user_text.strip().lower()
    for suspect in AI_SUSPECTS:
        if suspect["name"].lower() in s:
            return suspect
    return None


# -------------------------
# Public Functions for API
# -------------------------


def ask_question(user_question: str, session_id: str):
    game = _get_or_create_game(session_id)
    culprit = game["culprit"]

    if game["game_over"]:
        return f"The game is over. The saboteur was {culprit['name']}. Motive: {culprit['motive']}"

    if game["questions_asked"] >= MAX_QUESTIONS:
        game["game_over"] = True
        return f"GAME OVER! You've reached the maximum number of questions. The saboteur was {culprit['name']}. Motive: {culprit['motive']}"

    game["questions_asked"] += 1

    guessed_suspect = _detect_suspect_guess(user_question)
    if guessed_suspect:
        if guessed_suspect["name"] == culprit["name"]:
            game["game_over"] = True
            return f"CASE SOLVED! Yes, that is correct! The saboteur is {culprit['name']}. Motive: {culprit['motive']}"
        else:
            return "No, that AI did not sabotage the car."

    facts_block, system_instruction = _build_facts_and_instruction(culprit["name"])
    prompt_for_user_message = (
        f"{system_instruction}\n\n"
        f"Case Facts:\n{facts_block}\n\n"
        f"User question: {user_question}"
    )

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt_for_user_message,
            config=genai.types.GenerateContentConfig(temperature=0.35, top_p=0.9),
        )
        return response.text.strip()
    except Exception as e:
        print(f"Error calling LLM: {e}", file=stderr)
        return "I'm having trouble accessing the case files at the moment."


def get_hint(session_id: str):
    game = _get_or_create_game(session_id)
    culprit = game["culprit"]

    hint_prompt = f"""
    Based on the following suspect profile, provide a single, short, and subtle hint for a detective game.
    The hint should point towards the suspect's motive, role, or the evidence against them without being obvious.
    Do NOT use the suspect's name.

    Suspect Profile:
    - Name: {culprit["name"]}
    - Role: {culprit["role"]}
    - Motive: {culprit["motive"]}
    - Evidence: {culprit["evidence"]}

    Subtle Hint:
    """

    try:
        if not client:
            raise ConnectionError("Google GenAI client is not initialized.")
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=hint_prompt,
            config=genai.types.GenerateContentConfig(temperature=0.6, top_p=0.9),
        )
        return response.text.strip()
    except Exception as e:
        print(f"Error calling LLM for hint: {e}", file=stderr)
        return "I can't seem to find a good hint right now."
