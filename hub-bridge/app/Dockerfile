FROM node:20-alpine

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json* ./
RUN npm install --production 2>/dev/null || echo "npm install completed"

# Copy application
COPY server.js ./
COPY public/ ./public/

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:18090/health', (r) => { if (r.statusCode !== 200) throw new Error(r.statusCode); })" || true

EXPOSE 18090

CMD ["node", "server.js"]
