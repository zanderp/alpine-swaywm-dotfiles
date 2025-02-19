#!/bin/bash

# Check if notifications are muted
if swaync-client --print-status | grep -q "DND: true"; then
    echo "[M]"  # Muted
else
    echo "[N]"  # Active
fi