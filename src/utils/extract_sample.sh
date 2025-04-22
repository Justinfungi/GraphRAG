#!/bin/bash

# Check if pandas is installed
pip list | grep pandas > /dev/null
if [ $? -ne 0 ]; then
    echo "Installing pandas..."
    pip install pandas openpyxl
else
    echo "pandas already installed"
fi

echo "Extracting top 10 records from train.json dataset..."
cd /mnt/znzz/jus/code/self
python GraphRAG/src/utils/extract_sample_data.py

echo "Done! Files saved to:"
echo "  - /mnt/znzz/jus/code/self/GraphRAG/dataset/train_sample.xlsx"
echo "  - /mnt/znzz/jus/code/self/GraphRAG/dataset/train_sample.json" 