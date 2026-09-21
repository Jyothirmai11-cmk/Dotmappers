# Stage 1: Build React app
FROM node:18-alpine as builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY public/ ./public/
COPY src/ ./src/

# Build React app
RUN npm run build

# Stage 2: Serve with nginx
FROM nginx:alpine

# Copy nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# Copy built app from builder stage
COPY --from=builder /app/build /usr/share/nginx/html

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:3000/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
