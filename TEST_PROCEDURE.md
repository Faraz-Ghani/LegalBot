
LEGAL RAG CHATBOT - TESTING PROCEDURE
=====================================

1. TEST CATEGORIES (50 Tests divided into 5 sections):

   Section 1: Basic Retrieval Tests (Tests 1-10)
   - Validates core retrieval functionality
   - Tests section retrieval, chunk structure, source attribution
   - Verifies different document types are accessible

   Section 2: Query Expansion Tests (Tests 11-20)
   - Tests automatic keyword expansion for legal sections
   - Validates handling of alternative phrasings
   - Tests Islamic legal terminology
   - Checks case-insensitive and punctuation handling

   Section 3: Context Building Tests (Tests 21-30)
   - Validates context assembly for LLM consumption
   - Tests character limit enforcement
   - Tests formatting and truncation markers
   - Verifies metadata preservation

   Section 4: Cross-Document Retrieval Tests (Tests 31-40)
   - Tests retrieval across 13 different legal documents
   - Validates PPC/CRPC integration
   - Tests Evidence Act, Anti-Terrorism Act, Narcotics Act, etc.
   - Ensures substantive vs procedural law properly retrieved

   Section 5: Edge Cases & Scalability Tests (Tests 41-50)
   - Tests extreme query lengths and complexity
   - Tests numeric and special character handling
   - Validates performance with large k values
   - Tests caching effectiveness
   - Validates consistency and error handling


2. HOW TO RUN TESTS:

   a) From command line:
      $ cd /Users/faraz/RaveelChatbot
      $ source .venv/bin/activate
      $ python3 test_suite.py

   b) Interpretation:
      - ✓ PASS: Test condition met successfully
      - ✗ FAIL: Test condition not met, details provided
      - Summary shows: passed/total tests and list of failures


3. SUCCESS CRITERIA:

   Minimum: 45/50 tests passing (90%)
   Target:  48/50 tests passing (96%)
   Ideal:   50/50 tests passing (100%)

   Critical tests (must pass):
   - Tests 1, 2, 3, 4: Basic retrieval structure
   - Tests 31, 37: Cross-document and PPC prioritization
   - Tests 45, 46: Scalability to 200+ PDFs


4. KNOWN LIMITATIONS:

   - Test 50 (caching): Timing may vary based on system load
   - Tests 47-49: Edge cases may have different behavior on different systems
   - Performance tests (46) assume reasonable system resources


5. ADDING NEW TESTS:

   To add more tests, follow the pattern:
   
   ```python
   print("
Test N: Test name")
   # Perform test action
   results = retrieve_relevant_chunks("query", k=10)
   # Verify condition
   condition = (test_check)
   runner.test("Test name", condition, "Details about result")
   ```


6. CONTINUOUS TESTING:

   Run tests:
   - Before each deployment
   - After modifying retrieval.py or chat.py
   - After adding new documents
   - Weekly during active development


7. TRACKING RESULTS:

   Log test results:
   $ python3 test_suite.py > test_results_2026-03-19.txt
   
   Compare across time to detect regressions:
   $ diff test_results_2026-03-19.txt test_results_2026-03-20.txt
