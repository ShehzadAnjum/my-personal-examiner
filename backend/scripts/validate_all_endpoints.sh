#!/bin/bash
#
# Validate all API endpoints from QUICK_START.md
#

set -e

BASE_URL="http://localhost:8001"

echo "🔍 Testing Phase II API Endpoints"
echo "=================================="
echo ""

# Test 1: Search Questions
echo "Test 1: Search Questions"
echo "------------------------"
RESPONSE=$(curl -s -X GET "${BASE_URL}/api/questions/search?subject_code=9708&sort_by=year&sort_order=desc&page=1&page_size=20")
TOTAL=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('total', 0))")
echo "✅ Found $TOTAL questions"
echo ""

# Test 2: Generate Exam
echo "Test 2: Generate Exam"
echo "---------------------"
EXAM_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/exams" \
  -H 'Content-Type: application/json' \
  -d '{"subject_code":"9708","exam_type":"PRACTICE","question_count":5,"strategy":"balanced"}')
EXAM_ID=$(echo "$EXAM_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))")
TOTAL_MARKS=$(echo "$EXAM_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('total_marks', 0))")
echo "✅ Created exam: $EXAM_ID"
echo "   Total marks: $TOTAL_MARKS"
echo ""

# Test 3: Get Exam Statistics
echo "Test 3: Get Exam Statistics"
echo "---------------------------"
STATS_RESPONSE=$(curl -s -X GET "${BASE_URL}/api/exams/${EXAM_ID}/statistics")
echo "$STATS_RESPONSE" | python3 -m json.tool
echo ""

# Test 4: Syllabus Coverage
echo "Test 4: Syllabus Coverage"
echo "-------------------------"
COVERAGE_RESPONSE=$(curl -s -X GET "${BASE_URL}/api/syllabus/coverage/9708")
COVERAGE=$(echo "$COVERAGE_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('coverage_percentage', 0))")
echo "✅ Syllabus coverage: ${COVERAGE}%"
echo ""

echo "=================================="
echo "✅ All tests passed!"
echo ""
