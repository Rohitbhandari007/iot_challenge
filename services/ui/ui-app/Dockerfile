FROM node:18-alpine AS builder

WORKDIR /app

RUN npm install

COPY .. .

RUN npm run build

# ---

FROM node:18-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production

COPY --from=builder /app/next.config.js ./
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000

# Start the Next.js application
CMD ["node", "server.js"]