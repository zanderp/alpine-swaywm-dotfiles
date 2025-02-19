#!/bin/bash

# Check if notifications are muted
if swaync-client --print-status | grep -q "DND: true"; then
    echo "🔕"  # Muted (Do Not Disturb)
else
    echo "🔔"  # Active
fi
