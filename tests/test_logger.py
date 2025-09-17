###############################################################################
##  `test_logging.py`                                                        ##
##                                                                           ##
##  Purpose: Unit tests for logger module                                    ##
###############################################################################


import unittest
import sys
from io import StringIO
from unittest.mock import patch

from src.logger import (
    log_info, log_debug, log_error, log_warning,
    log_section_start, log_section_end,
    log_original_text, log_nlp_clusters, log_cluster_mapping,
    log_validation_results, log_mention_info, force_flush
)


class MockMention:
    # Mock mention object for testing
    def __init__(self, name, pronouns, full_match):
        self.name = name
        self.pronouns = pronouns
        self.full_match = full_match


class TestLogger(unittest.TestCase):
    def setUp(self):
        # Set up test fixtures
        self.original_stdout = sys.stdout
        self.captured_output = StringIO()
        sys.stdout = self.captured_output
    
    def tearDown(self):
        # Clean up after tests
        sys.stdout = self.original_stdout
    
    def get_output(self):
        # Get captured output & reset buffer
        output = self.captured_output.getvalue()
        self.captured_output = StringIO()
        sys.stdout = self.captured_output
        return output
    
    def test_log_with_timestamps(self):
        # Test that log messages include timestamps
        log_info("Test message")
        output = self.get_output()
        
        self.assertIn("[INFO]", output)
        self.assertIn("Test message", output)
        # Check timestamp format (YYYY-MM-DD HH:MM:SS.mmm)
        self.assertRegex(output, r'\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}\]')
    
    def test_different_log_levels(self):
        # Test different log levels
        log_info("Info message")
        log_debug("Debug message")
        log_warning("Warning message")
        log_error("Error message")
        
        output = self.get_output()
        
        self.assertIn("[INFO] Info message", output)
        self.assertIn("[DEBUG] Debug message", output)
        self.assertIn("[WARN] Warning message", output)
        self.assertIn("[ERROR] Error message", output)
    
    def test_section_separators(self):
        # Test section start & end separators
        log_section_start("TEST SECTION")
        log_section_end("TEST SECTION")
        
        output = self.get_output()
        
        self.assertIn("START: TEST SECTION", output)
        self.assertIn("END: TEST SECTION", output)
        self.assertIn("=" * 20, output) # should contain separator chars
    
    def test_original_text_logging(self):
        # Test original text logging with truncation
        short_text = "Short text"
        long_text = "x" * 600 # longer than 500 char limit
        
        log_original_text(short_text)
        output1 = self.get_output()
        
        log_original_text(long_text)
        output2 = self.get_output()
        
        # Short text should appear in full
        self.assertIn("Short text", output1)
        self.assertIn("Length: 10 characters", output1)
        
        # Long text should be truncated
        self.assertIn("...", output2)
        self.assertIn("Length: 600 characters", output2)
    
    def test_cluster_logging(self):
        # Test NLP cluster logging
        clusters = [
            ["John", "he", "him"],
            ["Sarah", "she", "her"],
            ["they", "them", "everyone"]
        ]
        
        log_nlp_clusters(clusters)
        output = self.get_output()
        
        self.assertIn("Detected Coreference Clusters", output)
        self.assertIn("Cluster 1: John -> he -> him", output)
        self.assertIn("Cluster 2: Sarah -> she -> her", output)
        self.assertIn("Cluster 3: they -> them -> everyone", output)
    
    def test_cluster_mapping_logging(self):
        # Test cluster mapping logging
        mappings = {
            "John": ["he", "him"],
            "Sarah": ["she", "her"],
            "Alex": []
        }
        
        log_cluster_mapping(mappings)
        output = self.get_output()
        
        self.assertIn("Pronoun Cluster Mappings", output)
        self.assertIn("John: [he, him]", output)
        self.assertIn("Sarah: [she, her]", output)
        self.assertIn("Alex: [(no pronouns)]", output)
    
    def test_mention_info_logging(self):
        # Test mention information logging
        mention1 = MockMention("John Smith", ("he", "they"), "@**John Smith (he/they)**")
        mention2 = MockMention("Alex", (), "@**Alex**")
        
        log_mention_info(mention1)
        output1 = self.get_output()
        
        log_mention_info(mention2)
        output2 = self.get_output()
        
        self.assertIn("Mention Found: John Smith (he/they)", output1)
        self.assertIn("@**John Smith (he/they)**", output1)
        
        self.assertIn("Mention Found: Alex (None)", output2)
        self.assertIn("@**Alex**", output2)
    
    def test_validation_results_logging(self):
        # Test validation results logging
        results = [
            {"name": "John", "pronouns": "he/they", "pronouns_match": True},
            {"name": "Sarah", "pronouns": "she/her", "pronouns_match": False},
            {"name": "Alex", "pronouns": "None", "pronouns_match": True}
        ]
        
        log_validation_results(results, "Test")
        output = self.get_output()
        
        self.assertIn("Test Results", output)
        self.assertIn("John (he/they) - ✓ PASS", output)
        self.assertIn("Sarah (she/her) - ✗ FAIL", output)
        self.assertIn("Alex (None) - ✓ PASS", output)
    
    @patch('sys.stdout')
    @patch('sys.stderr')
    def test_force_flush(self, mock_stderr, mock_stdout):
        # Test force flush functionality
        force_flush()
        
        mock_stdout.flush.assert_called_once()
        mock_stderr.flush.assert_called_once()
    
    def test_flush_parameter(self):
        # Test that flush parameter is respected
        with patch('builtins.print') as mock_print:
            log_info("Test message", flush=True)
            log_info("Test message", flush=False)
            
            # Check that print was called with correct flush parameters
            calls = mock_print.call_args_list
            self.assertEqual(calls[0][1]['flush'], True)
            self.assertEqual(calls[1][1]['flush'], False)


if __name__ == '__main__':
    unittest.main()


