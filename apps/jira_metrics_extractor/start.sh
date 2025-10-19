#!/bin/bash

DEBUG_FLAG=""
if [ "$DEBUG_MODE" = "true" ]; then
    DEBUG_FLAG="--d"
fi

# Build command arguments array
ARGS=("--insecure-http-parser" "dist/cli")

if [ -n "$JIRA_USERNAME" ] && [ -n "$JIRA_PASSWORD" ]; then
    ARGS+=("--u=$JIRA_USERNAME" "--p=$JIRA_PASSWORD")
fi
if [ -n "$OUTPUT_PATH" ]; then
    ARGS+=("--o=$OUTPUT_PATH")
fi
if [ -n "$CUSTOM_JQL" ]; then
    ARGS+=("--jql=$CUSTOM_JQL")
fi
if [ -n "$DEBUG_FLAG" ]; then
    ARGS+=("$DEBUG_FLAG")
fi

# Run the application
echo "node ${ARGS[*]}"
node "${ARGS[@]}"

# Upload to S3 if bucket is specified and output path exists
if [ -n "$S3_BUCKET_NAME" ] && [ -n "$OUTPUT_PATH" ]; then
    node upload.js "$OUTPUT_PATH" "$S3_BUCKET_NAME"
fi