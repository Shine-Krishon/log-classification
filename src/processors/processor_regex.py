import re
from src.utils.logger_config import get_logger
from src.core.constants import REGEX_PATTERNS
from src.services.cache_manager import cache_result

# Set up logging
logger = get_logger(__name__)

# Compile regex patterns for better performance
compiled_patterns = {}
for pattern, label in REGEX_PATTERNS.items():
    try:
        compiled_patterns[re.compile(pattern, re.IGNORECASE)] = label
    except re.error as e:
        logger.error(f"Invalid regex pattern '{pattern}': {e}")

logger.info(f"Compiled {len(compiled_patterns)} regex patterns for optimization")

@cache_result(ttl=3600)  # Cache regex results for 1 hour
def classify_with_regex(source, log_message):
    """
    Classify log message using precompiled regex patterns (optimized).
    
    Args:
        source (str): The log source (for compatibility with other processors)
        log_message (str): The log message to classify
        
    Returns:
        str: Classification label if pattern matches, "unclassified" otherwise
    """
    if not log_message or not isinstance(log_message, str):
        logger.warning(f"Invalid input received: {type(log_message)}")
        return "unclassified"
    
    try:
        logger.debug(f"Classifying log message from {source} with {len(compiled_patterns)} compiled patterns")
        
        # Use precompiled patterns for better performance
        for compiled_pattern, label in compiled_patterns.items():
            if compiled_pattern.search(log_message):
                logger.debug(f"Regex classification matched: {label}")
                return label
        
        logger.debug("No regex patterns matched")
        return "unclassified"
        
    except Exception as e:
        logger.error(f"Error in regex classification: {str(e)}", exc_info=True)
        return "unclassified"

if __name__ == "__main__":
    print(classify_with_regex("test", "Backup completed successfully."))
    print(classify_with_regex("test", "Account with ID 1234 created by User1."))
    print(classify_with_regex("test", "Hey Bro, chill ya!"))


