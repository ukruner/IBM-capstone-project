FROM node:20-slim

WORKDIR /app

COPY package.json ./
RUN npm install

COPY get-dealership.js ./

ENV PORT=3000

EXPOSE 3000

CMD ["node", "get-dealership.js"]
