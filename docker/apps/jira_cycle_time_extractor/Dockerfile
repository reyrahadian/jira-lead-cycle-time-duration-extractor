# Use Node.js LTS version as the base image
FROM node:18-slim

# Set working directory
WORKDIR /app

# Copy package files
COPY apps/jira_cycle_time_extractor/package*.json ./

# Install dependencies
RUN npm install --production

# Copy application files
COPY apps/jira_cycle_time_extractor/ ./

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

# Command to run the application
CMD ["npm", "run", "extract"]
