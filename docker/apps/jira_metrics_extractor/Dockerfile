# Use Node.js LTS version as the base image
FROM node:22-slim

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
ENV S3_BUCKET_NAME=""
ENV DEBUG_MODE=false


# Command to run the application
CMD ["/app/start.sh"]
