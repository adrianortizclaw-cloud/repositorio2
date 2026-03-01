FROM node:20-alpine AS builder

WORKDIR /app

# Dependencias definidas manualmente para mantener la estructura limpia.
COPY package.json package-lock.json ./
RUN npm ci --only=production

COPY . .

CMD ["npm", "start"]
