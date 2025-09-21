import re
import time
import random
from groq import Groq
from src.utils.logger_config import get_logger
from src.core.config import config
from src.core.constants import LLM_CLASSIFICATION_PROMPT
from src.services.cache_manager import cache_result
from src.services.performance_monitor_simple import monitor_performance

# Set up logging
logger = get_logger(__name__)

# Global client for connection reuse
_groq_client = None

def get_groq_client():
    """Get or create Groq client with connection reuse."""
    global _groq_client
    
    if _groq_client is None:
        try:
            _groq_client = Groq(api_key=config.groq_api_key)
            logger.info("Groq client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Groq client: {str(e)}")
            return None
    
    return _groq_client

@cache_result(ttl=7200, use_file_cache=True)  # Cache LLM results for 2 hours
def classify_with_llm_batch(log_entries, task_id=None):
    """
    Classify multiple log messages using LLM in a single API call for better performance.
    
    Args:
        log_entries (list): List of tuples (source, log_message)
        task_id (str, optional): Task ID for cancellation support
        
    Returns:
        list: List of classification labels corresponding to input entries
    """
    if not log_entries:
        return []
    
    client = get_groq_client()
    if not client:
        logger.error("Groq client not available")
        return ["unclassified"] * len(log_entries)
    
    # Check for cancellation
    if task_id:
        from src.services.task_manager import task_manager
        if task_manager.is_cancelled(task_id):
            logger.info(f"Task {task_id} cancelled during LLM batch classification")
            return ["cancelled"] * len(log_entries)
    
    try:
        logger.debug(f"Batch classifying {len(log_entries)} log messages using LLM")
        
        # Create batch prompt for standard models
        batch_prompt = """Classify each log message into exactly one category: user_action, system_notification, workflow_error, deprecation_warning, or unclassified.

Log messages:
"""
        
        # Add each log with numbering
        for i, (source, log_message) in enumerate(log_entries, 1):
            batch_prompt += f"{i}. [{source}] {log_message}\n"
        
        batch_prompt += f"""\nRespond with ONLY a numbered list of exactly {len(log_entries)} classifications (no explanations or thinking):
1. category_name
2. category_name
... (continue for all {len(log_entries)} logs)

Valid categories ONLY: user_action, system_notification, workflow_error, deprecation_warning, security_alert, unclassified

Example response format:
1. workflow_error
2. user_action
3. system_notification"""
        
        # Make single API call for all logs
        response = client.chat.completions.create(
            model=config.llm_model_name,
            messages=[
                {
                    "role": "system", 
                    "content": "You are a precise log classifier. Output ONLY a numbered list with one category per line. No explanations, no thinking text, just the numbered classifications."
                },
                {
                    "role": "user", 
                    "content": batch_prompt
                }
            ],
            temperature=0.1,  # Lower temperature for more consistent formatting
            max_tokens=200,  # Reduce tokens since no reasoning needed
            timeout=30
        )
        
        # Parse batch response (handle reasoning models)
        response_content = response.choices[0].message.content.strip()
        logger.info(f"Raw LLM batch response: {response_content}")
        
        # Remove reasoning tokens and extract final answer
        # Handle <think>...</think> blocks by removing them
        import re
        
        original_content = response_content
        
        # Remove thinking blocks (handle incomplete blocks more carefully)
        import re
        
        original_content = response_content
        
        # First, remove complete thinking blocks
        response_content = re.sub(r'<think>.*?</think>', '', response_content, flags=re.DOTALL)
        
        # If no complete blocks were removed but we still have <think>, remove incomplete blocks
        if '<think>' in response_content:
            logger.warning("Found incomplete thinking block, removing everything after <think>")
            response_content = re.sub(r'<think>.*', '', response_content, flags=re.DOTALL)
        
        # If response is now empty or very short, extract from the original thinking content
        if len(response_content.strip()) < 10:
            logger.warning("Response mostly thinking text, extracting from original content")
            # Look for actual classifications mentioned in the thinking
            thinking_content = original_content.lower()
            
            # Extract the most likely classification based on content analysis
            if ('fail' in thinking_content or 'error' in thinking_content or 'abort' in thinking_content or 'escalation' in thinking_content) and ('process' in thinking_content or 'workflow' in thinking_content or 'case' in thinking_content or 'ticket' in thinking_content):
                response_content = "1. workflow_error"
                logger.info("Extracted workflow_error from failure/process keywords")
            elif 'security' in thinking_content or 'attack' in thinking_content or 'injection' in thinking_content or 'unauthorized' in thinking_content:
                response_content = "1. security_alert"
                logger.info("Extracted security_alert from security keywords")
            elif 'user' in thinking_content and ('login' in thinking_content or 'upload' in thinking_content or 'action' in thinking_content):
                response_content = "1. user_action"
                logger.info("Extracted user_action from user activity keywords")
            elif 'system' in thinking_content and ('start' in thinking_content or 'notification' in thinking_content or 'backup' in thinking_content):
                response_content = "1. system_notification"
                logger.info("Extracted system_notification from system keywords")
            elif 'deprecat' in thinking_content or 'legacy' in thinking_content or 'retired' in thinking_content or 'obsolete' in thinking_content:
                response_content = "1. deprecation_warning"
                logger.info("Extracted deprecation_warning from deprecation keywords")
            # Fallback: simple keyword-based classification
            elif 'fail' in thinking_content or 'error' in thinking_content:
                response_content = "1. workflow_error"
                logger.info("Fallback: extracted workflow_error from fail/error keywords")
            else:
                response_content = "1. unclassified"
                logger.info("No clear classification found in thinking text")
            
            logger.info(f"Extracted from thinking: {response_content}")
        else:
            # Remove any remaining incomplete thinking indicators
            response_content = response_content.replace('<think>', '').replace('</think>', '')
        
        # Clean up the response
        response_content = response_content.strip()
        
        logger.info(f"Cleaned LLM response: {response_content}")
        
        # Split response into lines and extract classifications
        lines = [line.strip() for line in response_content.split('\n') if line.strip()]
        logger.info(f"Response lines: {lines}")
        
        classifications = []
        
        # Valid classifications (including security_alert)
        valid_classifications = {'user_action', 'system_notification', 'workflow_error', 'deprecation_warning', 'security_alert', 'unclassified'}
        
        # First try: Parse numbered classifications (e.g., "1. user_action", "2. system_notification")
        for line in lines[:len(log_entries)]:  # Only process up to the number of log entries
            line_clean = line.strip()
            
            # Remove numbering (1., 2., etc.)
            line_clean = re.sub(r'^\d+\.\s*', '', line_clean)
            line_clean = line_clean.strip()
            
            # Check if it's a valid classification
            if line_clean in valid_classifications:
                classifications.append(line_clean)
                logger.info(f"Found valid classification: {line_clean}")
            else:
                # Try to find a valid classification within the line
                found_classification = None
                for valid_class in valid_classifications:
                    if valid_class in line_clean.lower():
                        found_classification = valid_class
                        break
                
                if found_classification:
                    classifications.append(found_classification)
                    logger.info(f"Found classification in text: {found_classification}")
                else:
                    # For escalation/failure cases, default to workflow_error
                    if any(keyword in line_clean.lower() for keyword in ['fail', 'error', 'escalation', 'abort', 'timeout']):
                        classifications.append("workflow_error")
                        logger.info(f"Keyword-based classification: workflow_error")
                    else:
                        logger.warning(f"Could not parse classification from line: '{line_clean}' - will handle in fallback")
                        break  # Stop processing and use fallback
        
        # If we have enough good classifications, use them
        if len(classifications) >= len(log_entries):
            logger.info(f"Successfully parsed {len(classifications)} classifications from numbered list")
            return classifications[:len(log_entries)]
        
        # If we have very few lines or no valid classifications, try a simpler approach
        if len(lines) < len(log_entries):
            logger.warning(f"Not enough classification lines ({len(lines)}) for {len(log_entries)} log entries. Trying fallback parsing.")
            
            # Try to extract from original content, excluding the thinking block
            all_text = response_content.lower()
            
            # First, try to use the partial classifications we got
            for line in lines:
                line_lower = line.lower().strip()
                line_lower = line_lower.replace(f"{len(classifications)+1}.", "").replace("-", "").replace("*", "").strip()
                
                # Check for partial matches that could be completed
                if line_lower == "de" or line_lower == "deprec":
                    classifications.append("deprecation_warning")
                elif line_lower == "sys" or line_lower == "system":
                    classifications.append("system_notification")
                elif line_lower == "work" or line_lower == "workflow":
                    classifications.append("workflow_error")
                elif line_lower == "user":
                    classifications.append("user_action")
                elif line_lower in valid_classifications:
                    classifications.append(line_lower)
                else:
                    # Try to find any valid classification in the line
                    found = False
                    for valid_class in valid_classifications:
                        if valid_class in line_lower:
                            classifications.append(valid_class)
                            found = True
                            break
                    if not found:
                        classifications.append("unclassified")
            
            # Fill remaining with pattern matching from the remaining content
            remaining_needed = len(log_entries) - len(classifications)
            for i in range(remaining_needed):
                found_classification = None
                for valid_class in valid_classifications:
                    if valid_class in all_text:
                        found_classification = valid_class
                        # Remove this classification from text to avoid duplicates
                        all_text = all_text.replace(valid_class, '', 1)
                        break
                
                classifications.append(found_classification or "unclassified")
        else:
            # Filter out non-classification lines
            classification_lines = []
            for line in lines:
                line_lower = line.lower().strip()
                # Skip explanatory text, keep only lines that look like classifications
                if any(valid_class in line_lower for valid_class in valid_classifications):
                    classification_lines.append(line_lower)
                elif line_lower in valid_classifications:
                    classification_lines.append(line_lower)
            
            logger.info(f"Classification lines: {classification_lines}")
            
            # Process classification lines
            for i, line in enumerate(classification_lines):
                if i >= len(log_entries):
                    break
                
                # Clean the line
                line = line.lower().strip()
                
                # Remove common prefixes/suffixes
                line = line.replace(f"{i+1}.", "").replace("-", "").replace("*", "").strip()
                
                # Check if it's a valid classification
                if line in valid_classifications:
                    classifications.append(line)
                else:
                    # Try to extract classification from longer text
                    found_classification = None
                    for valid_class in valid_classifications:
                        if valid_class in line:
                            found_classification = valid_class
                            break
                    
                    if found_classification:
                        classifications.append(found_classification)
                    else:
                        logger.warning(f"Could not parse classification from line: '{line}'")
                        classifications.append("unclassified")
        
        # Ensure we have the right number of classifications with intelligent fallback
        while len(classifications) < len(log_entries):
            missing_index = len(classifications)
            logger.warning(f"Adding intelligent classification for missing entry {missing_index + 1}, currently have {len(classifications)}, need {len(log_entries)}")
            
            # Get the log message for intelligent classification
            if missing_index < len(log_entries):
                _, log_message = log_entries[missing_index]
                log_lower = log_message.lower()
                
                # Intelligent classification based on keywords
                if any(keyword in log_lower for keyword in ['fail', 'error', 'abort', 'escalation', 'timeout', 'invalid']):
                    classifications.append("workflow_error")
                    logger.info(f"Intelligent classification: workflow_error (keywords: fail/error/abort)")
                elif any(keyword in log_lower for keyword in ['deprecat', 'legacy', 'retired', 'no longer supported', 'obsolete']):
                    classifications.append("deprecation_warning")
                    logger.info(f"Intelligent classification: deprecation_warning (keywords: deprecat/legacy)")
                elif any(keyword in log_lower for keyword in ['user', 'login', 'upload', 'creat', 'register']):
                    classifications.append("user_action")
                    logger.info(f"Intelligent classification: user_action (keywords: user/login)")
                elif any(keyword in log_lower for keyword in ['security', 'attack', 'blocked', 'unauthorized', 'injection']):
                    classifications.append("security_alert")
                    logger.info(f"Intelligent classification: security_alert (keywords: security/attack)")
                elif any(keyword in log_lower for keyword in ['backup', 'start', 'complet', 'http', 'get', 'post']):
                    classifications.append("system_notification")
                    logger.info(f"Intelligent classification: system_notification (keywords: backup/start/http)")
                else:
                    classifications.append("unclassified")
                    logger.info(f"Intelligent classification: unclassified (no matching keywords)")
            else:
                classifications.append("unclassified")
        
        logger.info(f"Final classifications: {classifications}")
        logger.debug(f"LLM batch classification successful: {len(classifications)} results")
        return classifications[:len(log_entries)]  # Trim to exact size
        
    except Exception as e:
        logger.error(f"Error in LLM batch classification: {str(e)}")
        return ["unclassified"] * len(log_entries)

@cache_result(ttl=7200, use_file_cache=True)  # Cache LLM results for 2 hours
def classify_with_llm(source, log_message, task_id=None):
    """
    Classify log message using Groq LLM with caching, optimization, and rate limiting.
    
    Args:
        source (str): Log source
        log_message (str): Log message to classify
        task_id (str, optional): Task ID for cancellation support
        
    Returns:
        str: Classification label or "unclassified"
    """
    if not log_message or not isinstance(log_message, str):
        logger.warning("Invalid log message provided to LLM classifier")
        return "unclassified"
    
    client = get_groq_client()
    if client is None:
        logger.error("Groq client not available")
        return "unclassified"
    
    # Rate limiting parameters
    max_retries = 3
    base_delay = 1.0
    max_delay = 60.0
    
    for attempt in range(max_retries):
        try:
            # Check for cancellation
            if task_id:
                from src.services.task_manager import task_manager
                if task_manager.is_cancelled(task_id):
                    logger.info(f"Task {task_id} cancelled during LLM classification")
                    return "cancelled"
            
            logger.debug(f"Classifying log message from {source} using LLM (attempt {attempt + 1})")
            
            # Format the prompt
            prompt = LLM_CLASSIFICATION_PROMPT.format(log_message=log_message)
            
            # Make API call with timeout and optimization
            response = client.chat.completions.create(
                model=config.llm_model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=config.llm_temperature,
                max_tokens=100,  # Limit tokens for faster response
                timeout=30  # 30 second timeout
            )
            
            # Extract response content
            response_content = response.choices[0].message.content.strip()
            logger.debug(f"LLM response: {response_content}")
            
            # Extract classification from response
            classification = extract_classification_from_response(response_content)
            
            if classification:
                logger.debug(f"LLM classification successful: {classification}")
                return classification
            else:
                logger.warning(f"Could not extract classification from LLM response: {response_content}")
                return "unclassified"
                
        except Exception as e:
            error_str = str(e)
            
            # Handle rate limiting specifically
            if "429" in error_str or "rate limit" in error_str.lower():
                if attempt < max_retries - 1:
                    # Exponential backoff with jitter
                    delay = min(base_delay * (2 ** attempt) + random.uniform(0, 1), max_delay)
                    logger.warning(f"Rate limit hit, retrying in {delay:.2f}s (attempt {attempt + 1}/{max_retries})")
                    time.sleep(delay)
                    continue
                else:
                    logger.error(f"Rate limit exceeded after {max_retries} attempts, falling back to unclassified")
                    return "unclassified"
            
            # For other errors, don't retry
            logger.error(f"Error in LLM classification: {error_str}", exc_info=True)
            return "unclassified"
    
    return "unclassified"

def extract_classification_from_response(response_content):
    """
    Extract classification label from LLM response with improved parsing.
    
    Args:
        response_content (str): LLM response content
        
    Returns:
        str: Extracted classification label or None
    """
    if not response_content:
        return None
    
    try:
        # Try to extract from <category> tags first
        category_match = re.search(r'<category>\s*(.+?)\s*</category>', response_content, re.IGNORECASE)
        if category_match:
            category = category_match.group(1).strip().lower()
            return normalize_classification_label(category)
        
        # Fallback: look for known classification terms
        response_lower = response_content.lower()
        
        classification_mappings = {
            'workflow error': 'workflow_error',
            'deprecation warning': 'deprecation_warning', 
            'user action': 'user_action',
            'system notification': 'system_notification',
            'unclassified': 'unclassified'
        }
        
        for term, label in classification_mappings.items():
            if term in response_lower:
                logger.debug(f"Found classification term: {term} -> {label}")
                return label
        
        logger.warning(f"No classification found in response: {response_content}")
        return None
        
    except Exception as e:
        logger.error(f"Error extracting classification: {str(e)}")
        return None

def normalize_classification_label(label):
    """
    Normalize classification label to standard format.
    
    Args:
        label (str): Raw classification label
        
    Returns:
        str: Normalized label
    """
    if not label:
        return "unclassified"
    
    label = label.strip().lower()
    
    # Mapping of various label formats to standard ones
    label_mappings = {
        'workflow error': 'workflow_error',
        'workflow_error': 'workflow_error',
        'error': 'workflow_error',
        
        'deprecation warning': 'deprecation_warning',
        'deprecation_warning': 'deprecation_warning',
        'warning': 'deprecation_warning',
        'deprecated': 'deprecation_warning',
        
        'user action': 'user_action',
        'user_action': 'user_action',
        'user': 'user_action',
        
        'system notification': 'system_notification',
        'system_notification': 'system_notification',
        'notification': 'system_notification',
        'system': 'system_notification',
        
        'unclassified': 'unclassified',
        'unknown': 'unclassified',
        'other': 'unclassified'
    }
    
    return label_mappings.get(label, "unclassified")

def get_llm_info():
    """Get information about LLM configuration."""
    return {
        'model_name': config.llm_model_name,
        'temperature': config.llm_temperature,
        'api_key_configured': bool(config.groq_api_key),
        'client_initialized': _groq_client is not None
    }


if __name__ == "__main__":
    print(classify_with_llm(
        "Case escalation for ticket ID 7324 failed because the assigned support agent is no longer active."))
    print(classify_with_llm(
        "The 'ReportGenerator' module will be retired in version 4.0. Please migrate to the 'AdvancedAnalyticsSuite' by Dec 2025"))
    print(classify_with_llm("System reboot initiated by user 12345."))