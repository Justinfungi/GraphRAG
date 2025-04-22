#!/bin/bash

# Run the 2Wiki-Multihop QA evaluation script

# Set the paths
DATA_FILE="/mnt/znzz/jus/code/self/GraphRAG/dataset/dev.json"
ALIAS_FILE="/mnt/znzz/jus/code/self/GraphRAG/dataset/id_aliases.json"
OUTPUT_FILE="/mnt/znzz/jus/code/self/GraphRAG/results/predictions.json"
RESULTS_DIR="/mnt/znzz/jus/code/self/GraphRAG/results"

# Create results directory if it doesn't exist
mkdir -p $RESULTS_DIR

# Set the number of examples to evaluate - using a very small number for testing
NUM_EXAMPLES=2

echo "Running 2Wiki-Multihop QA evaluation..."
echo "Data file: $DATA_FILE"
echo "Alias file: $ALIAS_FILE"
echo "Output file: $OUTPUT_FILE"
echo "Number of examples: $NUM_EXAMPLES"

# Make sure we have the necessary packages
pip install tqdm ujson

# Set Python path to include the project root
export PYTHONPATH="${PYTHONPATH}:/mnt/znzz/jus/code/self"

# Run the evaluation script with a timeout and direct output to a log file
cd /mnt/znzz/jus/code/self
LOG_FILE="${RESULTS_DIR}/eval_log_$(date +%Y%m%d_%H%M%S).log"

timeout 60 python GraphRAG/src/evaluation/eval_wiki.py \
    --data_file=$DATA_FILE \
    --alias_file=$ALIAS_FILE \
    --output_file=$OUTPUT_FILE \
    --generate \
    --limit=$NUM_EXAMPLES 2>&1 | tee $LOG_FILE

# Check if the script ran successfully
if [ $? -eq 124 ]; then
    echo "Evaluation script timed out after 60 seconds."
    echo "Check log file at $LOG_FILE for details."
    exit 1
elif [ $? -ne 0 ]; then
    echo "Evaluation script failed."
    echo "Check log file at $LOG_FILE for details."
    exit 1
else
    echo "Evaluation complete. Results saved to $RESULTS_DIR"
    echo "Log file saved to $LOG_FILE"
fi 