FROM node:20

WORKDIR /usr/src/app

# Install deps
COPY package.json tsconfig.json ./
RUN npm install && npm cache clean --force

# Copy source
COPY src ./src

EXPOSE 4000

CMD ["npx", "ts-node", "src/server.ts"] 