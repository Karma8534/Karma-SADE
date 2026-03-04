FROM node:20-alpine

WORKDIR /app

# Install required dependencies
RUN npm install openai @anthropic-ai/sdk pdf-parse@1.1.1

# Copy application
COPY app/server.js ./
COPY app/public/ ./public/
COPY lib/ ./lib/

ENV NODE_ENV=production

EXPOSE 18090

CMD ["node", "server.js"]
