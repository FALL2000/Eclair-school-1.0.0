# ÉTAPE 1 : Build de l'application
FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install --ignore-scripts
COPY . .
RUN npm run build --configuration=production

FROM nginxinc/nginx-unprivileged:stable-alpine
COPY --from=build /app/dist/frontend/browser /usr/share/nginx/html

# Le port par défaut de cette image est 8080 au lieu de 80
EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]