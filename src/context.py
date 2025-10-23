###############################################################################
##  `context.py`                                                             ##
##                                                                           ##
##  Purpose: Expands context window (previous messages) for NLP accuracy     ##
###############################################################################


from src.utils import fetch_latest_messages
from src.parser import validate_mentions_in_text
from src.logger import log_validation_results


def check_previous_messages(client, channel_stream_id, topic_subject_id, mentions):
    previous_msgs = fetch_latest_messages(
        client, 
        channel_stream_id, topic_subject_id, 
        count=5
    )

    msgs_content = [msg_obj["content"] for msg_obj in previous_msgs]
    full_str = "\n".join(msgs_content)

    results = validate_mentions_in_text(full_str, mentions)
    log_validation_results(results, "Final Validation")

    contextual_mismatches = [r for r in results if not r['pronouns_match']]
    return contextual_mismatches


def reconcile_context_window(original_mismatches, contextual_mismatches):
    # Create lookup for context results by name
    context_by_name = {r["name"]: r for r in contextual_mismatches}
    
    reconciled = []
    for orig in original_mismatches:
        name_key = orig["name"]

        # If name still in contextual list, then compare results
        if name_key in context_by_name:
            orig_mismatch_arr = orig["mismatches"]
            context_mismatch_arr = context_by_name[name_key]["mismatches"]

            intersection_arr = list(set(orig_mismatch_arr) & set(context_mismatch_arr))

            # All concern areas resolved (no intersection between them)
            if not intersection_arr:
                continue
            
            resolved = orig.copy()
            resolved["mismatches"] = intersection_arr
            reconciled.append(resolved)

        # Otherwise, name not found in context mismatches, so assume resolved
        else:
            continue
    
    return reconciled


