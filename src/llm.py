###############################################################################
##  `llm.py`                                                                 ##
##                                                                           ##
##  Purpose: Provides an extra layer of validation for pronoun scanning      ##
###############################################################################


import requests


BASE_URL = "https://text.pollinations.ai/"

PARAMS = {
    "model": "openai",
    "seed": 1,
    "private": "true",
}


def prompt_llm_via_api(prompt):
    try:
        # Use POST instead of GET for more reliability & security
        response = requests.post(
            BASE_URL, 
            json={
                "messages": [
                    {"role": "user", "content": prompt}
                ], 
                **PARAMS
            }, 
            timeout=10
        )
        response.raise_for_status()
        return response.text.strip()

    except requests.RequestException as e:
        raise RuntimeError(f"Error, failed to reach URL: {e}")


def validate_pronouns_with_llm(content, mentions):
    results = []

    for mention in mentions:
        first_name, pronouns = mention.first_name, mention.pronouns

        if not pronouns: 
            break
        
        # Format pronouns clearly for model to understand
        pronoun_options = ", ".join(pronouns)

        PROMPT = (f"""
            {first_name} uses the following pronouns: {pronoun_options}. 
            Any of these pronouns are valid for {first_name}.

            Check the text below. ONLY validate pronouns referring to {first_name}. 
            Ignore pronouns that refer to anyone else.

            Text:
            \"\"\"
            {content}
            \"\"\"

            Return 'true' if all pronouns referring to {first_name} are correct. 
            Return 'false' if any pronoun referring to {first_name} is incorrect. 
            Only return true or false.
            """
        )

        response = prompt_llm_via_api(PROMPT)

        if "true" in response:
            match = True
        elif "false" in response:
            match = False 

        pronouns_display = "/".join(pronouns) if pronouns else "None"
        results.append({
            "name": mention.name,
            "pronouns": pronouns_display,
            "pronouns_match": match
        })

    return results


