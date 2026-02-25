FROM node:20-alpine

WORKDIR /app

# Install required dependencies
RUN npm install openai @anthropic-ai/sdk

# Copy application
COPY server.js ./

ENV NODE_ENV=production

EXPOSE 18090

CMD ["node", "server.js"]
