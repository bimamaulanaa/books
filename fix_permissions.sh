#!/bin/bash

# Fix permissions
sudo chown -R ubuntu:www-data /home/ubuntu/books
sudo chmod -R 755 /home/ubuntu/books
sudo chmod -R g+w /home/ubuntu/books

# Check virtual environment
echo "Checking virtual environment..."
if [ -d "/home/ubuntu/books/venv" ]; then
    echo "Virtual environment exists"
    source /home/ubuntu/books/venv/bin/activate
    which python
    which gunicorn
    gunicorn --version
else
    echo "Virtual environment does not exist"
fi

# Check service status
echo "Checking service status..."
sudo systemctl status aitawfiq

# Check logs
echo "Checking logs..."
sudo journalctl -u aitawfiq -n 50

# Restart the service
echo "Restarting service..."
sudo systemctl restart aitawfiq

# Check status again
echo "Checking status after restart..."
sudo systemctl status aitawfiq 