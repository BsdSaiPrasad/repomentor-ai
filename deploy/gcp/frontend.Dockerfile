FROM node:20-slim

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=8080
ENV AUTH_SECRET=replace-me-in-cloud

WORKDIR /app

COPY frontend/package.json frontend/pnpm-lock.yaml ./
RUN corepack enable && pnpm install --frozen-lockfile

COPY frontend ./

RUN pnpm build

EXPOSE 8080

CMD ["sh", "-c", "pnpm start"]
