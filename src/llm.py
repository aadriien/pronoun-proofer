###############################################################################
##  `llm.py`                                                                 ##
##                                                                           ##
##  Purpose: Provides an extra layer of validation for pronoun scanning      ##
###############################################################################


import requests
import time


BASE_URL = "https://text.pollinations.ai/"

PARAMS = {
    "model": "openai",
    "seed": 1,
    "private": "true",
}


def prompt_llm_via_api(prompt, max_retries=3):
    # Call LLM API with retry logic for resilience
    for attempt in range(max_retries):
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
                timeout=15
            )
            response.raise_for_status()
            return response.text.strip()

        except requests.exceptions.Timeout as e:
            if attempt == max_retries - 1:
                raise RuntimeError(f"LLM API timeout after {max_retries} attempts: {e}")
            time.sleep(2 ** attempt)  # Exponential backoff
            continue
            
        except requests.exceptions.ConnectionError as e:
            if attempt == max_retries - 1:
                raise RuntimeError(f"LLM API connection failed after {max_retries} attempts: {e}")
            time.sleep(2 ** attempt)
            continue
            
        except requests.exceptions.HTTPError as e:
            # Don't retry HTTP errors (4xx/5xx)
            raise RuntimeError(f"LLM API HTTP error {response.status_code}: {e}")
            
        except requests.RequestException as e:
            if attempt == max_retries - 1:
                raise RuntimeError(f"LLM API request failed after {max_retries} attempts: {e}")
            time.sleep(2 ** attempt)
            continue


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


