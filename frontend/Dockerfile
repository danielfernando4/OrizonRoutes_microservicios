FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 15173

# Correr en modo dev para que Vite funcione con Hot Module Replacement
CMD ["npm", "run", "dev", "--", "--host", "--port", "15173"]
