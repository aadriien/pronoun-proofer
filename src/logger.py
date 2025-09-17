###############################################################################
##  `logger.py`                                                             ##
##                                                                           ##
##  Purpose: Provides clean logging functionality with timestamps           ##
###############################################################################


import sys
from datetime import datetime
from typing import Any, Dict, List


def log_with_timestamp(message: str, level: str = "INFO", flush: bool = True) -> None:
    # Log a message with timestamp & level
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    formatted_message = f"[{timestamp}] [{level}] {message}"
    print(formatted_message, flush=flush)


def log_info(message: str, flush: bool = True) -> None:
    # Log an info message
    log_with_timestamp(message, "INFO", flush)


def log_debug(message: str, flush: bool = True) -> None:
    # Log a debug message
    log_with_timestamp(message, "DEBUG", flush)


def log_error(message: str, flush: bool = True) -> None:
    # Log an error message
    log_with_timestamp(message, "ERROR", flush)


def log_warning(message: str, flush: bool = True) -> None:
    # Log a warning message
    log_with_timestamp(message, "WARN", flush)


def log_separator(title: str = None, flush: bool = True) -> None:
    # Log a visual separator with optional title
    separator = "=" * 80
    if title:
        title_line = f" {title} "
        padding = (80 - len(title_line)) // 2
        separator = "=" * padding + title_line + "=" * (80 - padding - len(title_line))
    print(separator, flush=flush)


def log_section_start(title: str, flush: bool = True) -> None:
    # Log the start of a processing section
    log_separator(f"START: {title}", flush)


def log_section_end(title: str, flush: bool = True) -> None:
    # Log the end of a processing section
    log_separator(f"END: {title}", flush)


def log_mention_info(mention, flush: bool = True) -> None:
    # Log mention information in a clean format
    pronouns_display = "/".join(mention.pronouns) if mention.pronouns else "None"
    log_info(f"Mention Found: {mention.name} ({pronouns_display}) - Full: {mention.full_match}", flush)


def log_validation_results(results: List[Dict[str, Any]], title: str, flush: bool = True) -> None:
    # Log validation results in a clean format
    log_info(f"{title} Results:", flush)
    for result in results:
        status = "✓ PASS" if result["pronouns_match"] else "✗ FAIL"
        log_info(f"  {result['name']} ({result['pronouns']}) - {status}", flush)


def log_cluster_mapping(mappings: Dict[str, List[str]], flush: bool = True) -> None:
    # Log cluster mappings in a clean format
    log_info("Pronoun Cluster Mappings:", flush)
    for name, pronouns in mappings.items():
        pronouns_str = ", ".join(pronouns) if pronouns else "(no pronouns)"
        log_info(f"  {name}: [{pronouns_str}]", flush)


def log_nlp_clusters(clusters: List[List[str]], flush: bool = True) -> None:
    # Log NLP clusters in a clean format
    log_info("Detected Coreference Clusters:", flush)
    for i, cluster in enumerate(clusters, 1):
        cluster_str = " -> ".join(cluster)
        log_info(f"  Cluster {i}: {cluster_str}", flush)


def log_original_text(text: str, flush: bool = True) -> None:
    # Log the original text input
    log_section_start("PROCESSING TEXT INPUT")
    # Truncate very long text for readability
    display_text = text[:500] + "..." if len(text) > 500 else text
    log_info(f"Text: {display_text}", flush)
    log_info(f"Length: {len(text)} characters", flush)


def force_flush() -> None:
    # Force flush stdout & stderr buffers
    sys.stdout.flush()
    sys.stderr.flush()