FROM alpine:3.22
RUN apk add --no-cache tcpdump socat curl
CMD ["sh","-c","sleep infinity"]
