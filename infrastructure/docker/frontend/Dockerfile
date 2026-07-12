# ─── Development stage ────────────────────────────────────────────────────────
FROM node:20-alpine AS development

WORKDIR /app
COPY package*.json ./
RUN npm install --legacy-peer-deps && npm install ajv@8.12.0 --legacy-peer-deps
COPY . .

EXPOSE 3000
ENV CHOKIDAR_USEPOLLING=true
CMD ["npm", "start"]

# ─── Build stage ──────────────────────────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app
COPY frontend/web/package*.json ./
RUN npm install --legacy-peer-deps && npm install ajv@8.12.0 --legacy-peer-deps

COPY frontend/web/ ./
ARG REACT_APP_API_URL
ARG REACT_APP_WS_URL
ENV REACT_APP_API_URL=$REACT_APP_API_URL
ENV REACT_APP_WS_URL=$REACT_APP_WS_URL

RUN npm run build

# ─── Production stage (Nginx) ─────────────────────────────────────────────────
FROM nginx:1.25-alpine AS production

# Remove default config
RUN rm /etc/nginx/conf.d/default.conf

# Nginx config for SPA
COPY infrastructure/docker/frontend/nginx.conf /etc/nginx/conf.d/app.conf

# Copy built assets
COPY --from=builder /app/build /usr/share/nginx/html

EXPOSE 80

# Runtime env substitution for API URL
COPY infrastructure/docker/frontend/docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]
