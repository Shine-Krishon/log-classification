from processor_regex import classify_with_regex
from processor_bert import classify_with_bert
from processor_llm import classify_with_llm
from logger_config import get_logger
from config import config

# Set up logging
logger = get_logger(__name__)

def classify(logs):
    """
    Classify a list of log entries using the hybrid classification system.
    
    Args:
        logs (list): List of tuples containing (source, log_message)
        
    Returns:
        list: List of classification labels
    """
    if not logs or not isinstance(logs, list):
        logger.error("Invalid logs input: must be a non-empty list")
        raise ValueError("logs must be a non-empty list")
    
    logger.info(f"Starting classification of {len(logs)} log entries")
    labels = []
    
    for i, (source, log_msg) in enumerate(logs):
        try:
            logger.debug(f"Processing log {i+1}/{len(logs)} from source: {source}")
            label = classify_log(source, log_msg)
            labels.append(label)
            logger.debug(f"Log {i+1} classified as: {label}")
        except Exception as e:
            logger.error(f"Error classifying log {i+1}: {str(e)}", exc_info=True)
            labels.append(config.classification_categories["unclassified"])
    
    # Log classification statistics
    label_counts = {}
    for label in labels:
        label_counts[label] = label_counts.get(label, 0) + 1
    
    logger.info(f"Classification completed. Results: {label_counts}")
    return labels


def classify_log(source, log_msg):
    """
    Classify a single log entry using the hybrid approach.
    
    Args:
        source (str): The source system of the log
        log_msg (str): The log message to classify
        
    Returns:
        str: Classification label
    """
    if not source or not log_msg:
        logger.warning("Empty source or log message provided")
        return config.classification_categories["unclassified"]
    
    logger.debug(f"Classifying log from {source}: {log_msg[:50]}...")
    
    try:
        # Use LLM for legacy sources
        if source in config.legacy_sources:
            logger.debug(f"Using LLM classification for legacy source: {source}")
            label = classify_with_llm(log_msg)
        else:
            # Try regex first, then BERT for other sources
            logger.debug("Using regex classification first")
            label = classify_with_regex(log_msg)
            if not label:
                logger.debug("Regex failed, trying BERT classification")
                label = classify_with_bert(log_msg)
        
        logger.info(f"Log classified as: {label}")
        return label
        
    except Exception as e:
        logger.error(f"Error in classify_log: {str(e)}", exc_info=True)
        return config.classification_categories["unclassified"]

def classify_csv(input_file):
    import pandas as pd
    df = pd.read_csv(input_file)

    # Perform classification
    df["target_label"] = classify(list(zip(df["source"], df["log_message"])))

    # Save the modified file
    output_file = "output.csv"
    df.to_csv(output_file, index=False)

    return output_file

if __name__ == '__main__':
    classify_csv("test.csv")
    # logs = [
    #     ("ModernCRM", "IP 192.168.133.114 blocked due to potential attack"),
    #     ("BillingSystem", "User 12345 logged in."),
    #     ("AnalyticsEngine", "File data_6957.csv uploaded successfully by user User265."),
    #     ("AnalyticsEngine", "Backup completed successfully."),
    #     ("ModernHR", "GET /v2/54fadb412c4e40cdbaed9335e4c35a9e/servers/detail HTTP/1.1 RCODE  200 len: 1583 time: 0.1878400"),
    #     ("ModernHR", "Admin access escalation detected for user 9429"),
    #     ("LegacyCRM", "Case escalation for ticket ID 7324 failed because the assigned support agent is no longer active."),
    #     ("LegacyCRM", "Invoice generation process aborted for order ID 8910 due to invalid tax calculation module."),
    #     ("LegacyCRM", "The 'BulkEmailSender' feature is no longer supported. Use 'EmailCampaignManager' for improved functionality."),
    #     ("LegacyCRM", " The 'ReportGenerator' module will be retired in version 4.0. Please migrate to the 'AdvancedAnalyticsSuite' by Dec 2025")
    # ]
    # labels = classify(logs)
    #
    # for log, label in zip(logs, labels):
    #     print(log[0], "->", label)


