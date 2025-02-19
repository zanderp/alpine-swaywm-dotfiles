#!/bin/bash

# Check if notifications are muted
if swaync-client -D; then
    echo "🔕"  # Muted
else
    echo "🔔"  # Active
fi
