# Use Node.js LTS version as the base image
FROM node:18-slim

# Set working directory
WORKDIR /app

# Copy package files
COPY apps/jira_metrics_extractor/package*.json ./

# Install dependencies
RUN npm install --production

# Copy application files
COPY apps/jira_metrics_extractor/ ./

RUN npm run build

# Remove development files that are in .npmignore
RUN rm -rf \
    .gitignore \
    tsconfig.json \
    tslint.json \
    .vscode \
    regression \
    tmp \
    build

# Create config directory
RUN mkdir -p /config

# Set environment variables
ENV NODE_ENV=production
ENV CONFIG_PATH=/config/config.yaml
ENV OUTPUT_PATH=""
ENV JIRA_USERNAME=""
ENV JIRA_PASSWORD=""
ENV CUSTOM_JQL=""

# Command to run the application
CMD if [ -n "$JIRA_USERNAME" ] && [ -n "$JIRA_PASSWORD" ]; then \
    if [ -n "$OUTPUT_PATH" ]; then \
        if [ -n "$CUSTOM_JQL" ]; then \
            node --insecure-http-parser dist/cli --u="$JIRA_USERNAME" --p="$JIRA_PASSWORD" --o="$OUTPUT_PATH" --jql="$CUSTOM_JQL" --d; \
        else \
            node --insecure-http-parser dist/cli --u="$JIRA_USERNAME" --p="$JIRA_PASSWORD" --o="$OUTPUT_PATH" --d; \
        fi; \
    else \
        if [ -n "$CUSTOM_JQL" ]; then \
            node --insecure-http-parser dist/cli --u="$JIRA_USERNAME" --p="$JIRA_PASSWORD" --jql="$CUSTOM_JQL" --d; \
        else \
            node --insecure-http-parser dist/cli --u="$JIRA_USERNAME" --p="$JIRA_PASSWORD" --d; \
        fi; \
    fi; \
    else \
    if [ -n "$OUTPUT_PATH" ]; then \
        if [ -n "$CUSTOM_JQL" ]; then \
            node --insecure-http-parser dist/cli --o="$OUTPUT_PATH" --jql="$CUSTOM_JQL" --d; \
        else \
            node --insecure-http-parser dist/cli --o="$OUTPUT_PATH" --d; \
        fi; \
    else \
        if [ -n "$CUSTOM_JQL" ]; then \
            node --insecure-http-parser dist/cli --jql="$CUSTOM_JQL" --d; \
        else \
            node --insecure-http-parser dist/cli --d; \
        fi; \
    fi; \
    fi
