FROM nginx:1.27-alpine

WORKDIR /app
COPY . /app

# Build static output in image so runtime is simple and deterministic.
RUN rm -rf /usr/share/nginx/html/* \
    && mkdir -p /usr/share/nginx/html \
    && cp -R /app/site/* /usr/share/nginx/html/ \
    && cp /app/README.md /usr/share/nginx/html/README.md \
    && cp /app/specification.md /usr/share/nginx/html/specification.md \
    && cp -R /app/registry /usr/share/nginx/html/registry-files \
    && find /usr/share/nginx/html -name '.DS_Store' -delete

COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]
