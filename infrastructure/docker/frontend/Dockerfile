# ─── Development stage ────────────────────────────────────────────────────────
FROM node:20-alpine AS development

WORKDIR /app
COPY frontend/web/package*.json ./
RUN npm install && npm install ajv@8.12.0
COPY frontend/web/ ./

EXPOSE 5173
CMD ["npm", "run", "dev"]

# ─── Build stage ──────────────────────────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app
COPY frontend/web/package*.json ./
RUN npm install && npm install ajv@8.12.0

COPY frontend/web/ ./
ARG VITE_API_URL
ARG VITE_WS_URL
ENV VITE_API_URL=$VITE_API_URL
ENV VITE_WS_URL=$VITE_WS_URL

RUN npm run build

# ─── Production stage (Nginx) ─────────────────────────────────────────────────
FROM nginx:1.25-alpine AS production

# Remove default config
RUN rm /etc/nginx/conf.d/default.conf

# Nginx config for SPA
COPY infrastructure/docker/frontend/nginx.conf /etc/nginx/conf.d/app.conf

# Copy built assets
COPY --from=builder /app/build /usr/share/nginx/html

# Fail the image build on nginx config errors (also confirms the sub_filter
# module is present in the image) instead of shipping a broken frontend.
RUN nginx -t

EXPOSE 80

# Runtime env substitution for API URL
COPY infrastructure/docker/frontend/docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]
