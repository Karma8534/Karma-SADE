FROM node:20-alpine

WORKDIR /app

# Sovereign proxy needs zero npm deps — Node 20 has fetch built-in
# No npm install — proxy.js uses only Node built-ins (http, fs, path, URL, fetch)

# Copy ONLY the sovereign proxy + public assets — nothing else
COPY app/proxy.js ./
COPY app/public/ ./public/

ENV NODE_ENV=production

EXPOSE 18090

# Sovereign proxy — thin door, CC is the brain
CMD ["node", "proxy.js"]
