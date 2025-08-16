FROM ubuntu:24.04

ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8
ENV PATH="/opt/venv/bin:$PATH"

# Installer les dépendances
RUN apt-get update && apt-get upgrade -y \
    && apt-get install -y \
        locales sudo apt-utils curl python3 screen python3-venv python3-pip \
        build-essential gcc g++ nmap libssl-dev libbz2-dev mumble-server wget \
    && locale-gen en_US.UTF-8

# Créer virtualenv
RUN python3 -m venv /opt/venv

# Copier fichiers
WORKDIR /app
COPY . /app

# Préparer Mumble
RUN touch /var/lib/mumble-server/murmur.sqlite \
    && chown mumble-server:mumble-server /var/lib/mumble-server/murmur.sqlite \
    && cp ./etc/murmur.ini /etc/mumble-server.ini

# Installation de Go
ENV GOLANG_VERSION=1.23.4
RUN wget https://go.dev/dl/go${GOLANG_VERSION}.linux-amd64.tar.gz -O /tmp/go.tgz \
    && tar -C /usr/local -xzf /tmp/go.tgz \
    && rm /tmp/go.tgz

ENV PATH="/usr/local/go/bin:$PATH"

# Exposer les ports
EXPOSE 80 443 20821 64739-64839/tcp 64739-64839/udp

RUN sh dep_collector.sh

RUN chmod +x entrypoint.sh

CMD ["./entrypoint.sh"]
