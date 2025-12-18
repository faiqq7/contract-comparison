#!/bin/bash
# Contract Comparison Agent - Demo Script
# Run this for a quick demo

echo "=============================================="
echo "🔍 CONTRACT COMPARISON AGENT - DEMO"
echo "=============================================="
echo ""

# Check if virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "⚠️  Activating virtual environment..."
    source contract_agent_env/bin/activate
fi

echo "📄 Input Files:"
echo "   Original:  data/test_contracts/service_agreement_original.jpg"
echo "   Amendment: data/test_contracts/service_agreement_amendment_1.jpg"
echo ""
echo "🚀 Starting analysis..."
echo "----------------------------------------------"
echo ""

# Run the analysis
python src/main.py \
    --original data/test_contracts/service_agreement_original.jpg \
    --amendment data/test_contracts/service_agreement_amendment_1.jpg \
    --format summary

echo ""
echo "=============================================="
echo "✅ Demo Complete!"
echo "=============================================="

