FROM node:22.12-alpine AS builder

# Must be entire project because `prepare` script is run during `npm install` and requires all files.
COPY official-mcp-servers/servers/src/github /app
COPY official-mcp-servers/servers/tsconfig.json /tsconfig.json

WORKDIR /app

RUN --mount=type=cache,target=/root/.npm npm install

FROM node:22.12-alpine AS release

COPY --from=builder /app/dist /app/dist
COPY --from=builder /app/package.json /app/package.json
COPY --from=builder /app/package-lock.json /app/package-lock.json

ENV NODE_ENV=production
ENV GITHUB_PERSONAL_ACCESS_TOKEN=""

WORKDIR /app

RUN npm ci --ignore-scripts --omit-dev

ENTRYPOINT ["node", "dist/index.js"] 