# Stage 1: Extract the packaged website from the war file
FROM alpine:latest AS extractor
RUN apk add --no-cache unzip
WORKDIR /app
COPY target/abc-technologies-devops-1.0.war /app/website.war
RUN unzip /app/website.war -d /app/extracted_web

# Stage 2: Serve the static files using Nginx
FROM nginx:alpine
COPY --from=extractor /app/extracted_web /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
