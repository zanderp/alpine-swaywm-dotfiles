#!/bin/bash

# Check if notifications are muted
if swaync-client -D > /dev/null; then
    echo "  "  # Muted (DND On)
else
    echo "󰂚  "  # Active (DND Off)
fi
