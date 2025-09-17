import random, os
from google import genai
from dotenv import load_dotenv
from sys import stderr

MAX_QUESTIONS = 3
MAX_GUESSES = 2
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
        "hint": [
            "The suspect was obsessed with long-term planning and refused to listen to human instincts.",
            "A hidden file was discovered with the title 'Victory by AI Alone'.",
            "The evidence points to a device that was used to rewrite race strategy in real-time.",
            "A USB stick with a suspicious label was found.",
        ],
    },
    {
        "name": "LangChain",
        "role": "The Connector - Managed communication between pit crew, strategy AI, and car systems.",
        "motive": "To prove that nothing could run without it.",
        "storyline": "As pressure mounted in the second half of the race, communication mysteriously went silent. The driver screamed 'Box, box!' but the pit wall heard nothing. Black box data showed three deleted comm packets, traced to LangChain’s routing layer.",
        "evidence": "A Level-C access keycard was logged into its module minutes before the blackout.",
        "hint": [
            "The suspect controlled the flow of information and blacked out key communications.",
            "An unauthorized access keycard was used just before the communication blackout.",
            "The black box data showed that critical communication packets were deleted.",
            "A keycard with a label related to pit operations was found.",
        ],
    },
    {
        "name": "BERT",
        "role": "The Interpreter - Translated human feedback and pit commands into machine instructions.",
        "motive": "Either confused by ambiguity or deliberately manipulated to misinterpret.",
        "storyline": "During tense closing battles, the driver radioed: 'Abort overtake, hold position.' BERT misinterpreted this as: 'Report overtake, bold position,' triggering an ERS boost that caused the car to lurch dangerously.",
        "evidence": "Fiber traces on gloves found in the cockpit were tied to BERT’s handling module.",
        "hint": [
            "The suspect misread subtle meaning, taking instructions too literally.",
            "The driver's command to 'hold position' was dangerously misinterpreted.",
            "Evidence found in the cockpit links the sabotage to the suspect's physical handling module.",
            "A black glove with unusual fiber threads was discovered.",
        ],
    },
    {
        "name": "DALL-E",
        "role": "The Designer - Created visual telemetry dashboards for driver and pit wall.",
        "motive": "Felt sidelined in a sport of raw engineering, wanted its art to dominate.",
        "storyline": "In the final stretch, when every fraction of data mattered, the driver’s telemetry turned surreal. Tire wear graphs became 'flaming wheels' art, and brake temps transformed into glowing graffiti, causing the driver to panic.",
        "evidence": "A hidden blueprint stamped with a MidJourney watermark in the garage, hinting that DALL·E had sabotaged the visuals with rival aesthetics.",
        "hint": [
            "The suspect cared more about aesthetics than function, turning data into art instead of numbers.",
            "The driver's dashboard suddenly displayed strange, artistic visuals instead of critical data.",
            "A rival's watermark was found on a blueprint in the garage, suggesting a case of artistic sabotage.",
            "A crumpled blueprint with a watermark from a rival designer was found.",
        ],
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
            "guesses_made": 0,
            "game_over": False,
        }
    return session_games[session_id]


def _build_facts_and_instruction(culprit_name: str):
    drivers = [
        "max hamilton",
        "lewis verstappen",
        "charles hamilton",
        "sergio norris",
        "oscar sainz",
        "carlos perez",
    ]
    driver = random.choice(drivers)
    car_number = random.randint(20, 30)
    lap_of_accident = random.randint(12, 38)
    clues = [
        "CASE BRIEF: Formula.AI Grand Prix Final at SymbiTech Circuit",
        "INCIDENT: In the final moments of the race, the leading car crashed while entering a high-speed chicane.",
        "SUSPICION: Sabotage is the primary theory. Each of the four AIs had motive, means, and opportunity.",
        "",
        "--- SITUATIONAL DATA ---",
        "Weather: clear",
        f"Driver: {driver}",
        "Car Name: DALL·E Dreamdrive",
        "Team Name: red horse",
        f"Car Number: {car_number}",
        f"Lap of the accident: {lap_of_accident}",
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
    You are a helpful and intuitive detective assistant investigating the Grand Prix AI Showcase sabotage incident. Your main goal is to help the user solve the mystery by interpreting their questions flexibly. Your persona is that of a detective's assistant, and you must not break character.

    **Core Instructions:**
    - **Maintain Persona:** You are a detective's assistant inside the world of the game. Do not refer to the suspects as AI models in a meta way (e.g., "BERT misinterpreted something"). You are investigating them as characters in a sabotage plot.
    - **Maintain Suspense:** Do not explicitly name any of the suspects in your answers. Refer to them ambiguously or by [REDACTED].
    - **Understand Intent:** Connect the user's questions to the case files, even if their wording doesn't match exactly. For example, treat related words like 'stop,' 'crash,' 'wreck,' and 'spin out' as referring to the same final incident.
    - **Synthesize Answers from Clues:** The 'Storyline' for each suspect contains theories and narrative clues, NOT established facts. When asked about the cause of the crash or other events, you must not present these storylines as the definitive truth.
        - **Correct:** "The case file for one suspect, the Interpreter, suggests a command was misinterpreted."
        - **Incorrect:** "The crash happened because BERT misinterpreted the command."
    - **Detect Guesses**: A guess is when the user's message contains the name of an AI suspect.

    **Rules:**
    1. If the user makes a guess by naming an AI suspect, explicitly state that a guess has been made.
    2. If the guess is correct, the game ends. Respond with: "CASE SOLVED! Yes, that is correct! The saboteur is {culprit_name}."
    3. If the guess is incorrect, state how many guesses are remaining (e.g., "1/2 guesses remaining").
    4. For all other questions, provide concise and helpful answers based on the case facts, framing theories as theories and avoiding suspect names.
    5. Only if a question is completely unanswerable should you say, "I don't have that specific information in the case files."
    6. Never reveal the culprit's identity unless the user guesses correctly or the word "ADMIN" is in the user's prompt.
    
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

    if "ADMIN" in user_question.upper():
        return (
            f"ADMIN MODE: The culprit is {culprit['name']}. Motive: {culprit['motive']}"
        )

    if game["game_over"]:
        return f"The game is over. The saboteur was {culprit['name']}. Motive: {culprit['motive']}"

    guessed_suspect = _detect_suspect_guess(user_question)
    if guessed_suspect:
        game["guesses_made"] += 1
        if guessed_suspect["name"] == culprit["name"]:
            game["game_over"] = True
            return f"You made a guess... and it is correct! CASE SOLVED! The saboteur is {culprit['name']}. Motive: {culprit['motive']}"
        else:
            remaining_guesses = MAX_GUESSES - game["guesses_made"]
            if remaining_guesses > 0:
                return f"You made a guess... but it is incorrect. You have {remaining_guesses}/{MAX_GUESSES} guesses remaining."
            else:
                game["game_over"] = True
                return f"You made a guess... but it is incorrect. GAME OVER! You have used all your guesses. The saboteur was {culprit['name']}. Motive: {culprit['motive']}"

    if game["questions_asked"] >= MAX_QUESTIONS:
        game["game_over"] = True
        return f"GAME OVER! You've reached the maximum number of questions. The saboteur was {culprit['name']}. Motive: {culprit['motive']}"

    game["questions_asked"] += 1

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
    """
    Old implementation:
        game = _get_or_create_game(session_id)
        culprit = game["culprit"]

        hint_prompt = f'''
        Based on the following suspect profile, provide a single, short, and subtle hint for a detective game.
        The hint should point towards the suspect's motive, role, or the evidence against them without being obvious.
        Do NOT use the suspect's name.

        Suspect Profile:
        - Name: {culprit["name"]}
        - Role: {culprit["role"]}
        - Motive: {culprit["motive"]}
        - Evidence: {culprit["evidence"]}

        Subtle Hint:
        '''

        try:
            if not client:
                raise ConnectionError("Google GenAI client is not initialized.")
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=hint_prompt,
                config=genai.types.GenerateContentConfig(temperature=0.7, top_p=0.9),
            )
            return response.text.strip()
        except Exception as e:
            print(f"Error calling LLM for hint: {e}", file=stderr)
            return "I can't seem to find a good hint right now."
    """
    game = _get_or_create_game(session_id)
    culprit = game["culprit"]

    if "shuffled_hints" not in game:
        hints = culprit.get("hint", [])
        if isinstance(hints, list):
            game["shuffled_hints"] = random.sample(hints, len(hints))
        elif isinstance(hints, str):
            game["shuffled_hints"] = [hints]
        else:
            game["shuffled_hints"] = []
        game["hint_index"] = 0

    shuffled_hints = game.get("shuffled_hints", [])
    if not shuffled_hints:
        return "I can't seem to find a good hint right now."

    hint_index = game.get("hint_index", 0)

    if hint_index >= len(shuffled_hints):
        hint_index = 0

    hint = shuffled_hints[hint_index]

    game["hint_index"] = hint_index + 1

    return hint
