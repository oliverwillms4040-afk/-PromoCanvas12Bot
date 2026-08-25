#!/bin/bash
echo "=== Starting PromoCanvas Bot ==="
echo "Python version: $(python --version)"
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "Starting bot..."
python bot.py
