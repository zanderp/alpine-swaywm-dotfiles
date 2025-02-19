#!/bin/bash

# Check if notifications are muted
if swaync-client --print-status | grep -q "DND: true"; then
    echo "🔕"  # Muted (Safe alternative: "M" or "X")
else
    echo "🔔"  # Active (Safe alternative: "N" or "!")
fi
