# Etapa 1: compilar la app de React a archivos estáticos (HTML, JS, CSS)
FROM node:26-alpine AS build

WORKDIR /app

# Primero solo las dependencias, para que Docker las cachee si no cambian
COPY package.json package-lock.json ./
RUN npm ci

# Después el resto del código, y compilamos (el resultado queda en /app/dist)
COPY . .
RUN npm run build

# Etapa 2: Nginx sirve esos archivos y reenvía /api al backend.
# Node no llega a la imagen final: solo hacía falta para compilar.
FROM nginx:stable-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
