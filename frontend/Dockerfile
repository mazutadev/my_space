# Используем базовый образ Node.js для сборки
FROM node:18-slim AS build

WORKDIR /app

# Копируем package.json и package-lock.json для установки зависимостей
COPY package*.json ./

# Устанавливаем зависимости
RUN npm install

# Копируем остальные файлы и выполняем сборку
COPY . .

# Собираем фронтенд-приложение
RUN npm run build
