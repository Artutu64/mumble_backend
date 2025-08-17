FROM ubuntu:20.04

# Set non-interactive mode for apt
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update -y && apt-get upgrade -y

RUN apt-get install -y apt-utils

RUN apt-get install -y locales sudo python3 screen iproute2 python3-venv \
    nmap wget curl netcat netcat-openbsd build-essential gcc g++ python3-dev python3-pip \
    libssl-dev libbz2-dev mumble-server zeroc-ice-compilers python3-zeroc-ice

WORKDIR /app
COPY . /app

# Préparer la base de données mumble
RUN touch /var/lib/mumble-server/murmur.sqlite \
    && chown mumble-server:mumble-server /var/lib/mumble-server/murmur.sqlite

# Copier le fichier de configuration
RUN cp /app/etc/murmur.ini /etc/mumble-server.ini

# Générer mot de passe aléatoire et configurer mumble-server
RUN bash -c ' \
    PW=$(openssl rand -base64 16) && \
    echo "mumble-server mumble-server/password password $PW" | debconf-set-selections && \
    dpkg-reconfigure -f noninteractive mumble-server || true && \
    echo "Mumble password: $PW" \
'

# Installer Go
ENV GOLANG_VERSION=1.23.4
RUN wget https://go.dev/dl/go${GOLANG_VERSION}.linux-amd64.tar.gz -O /tmp/go.tgz \
    && tar -C /usr/local -xzf /tmp/go.tgz \
    && rm /tmp/go.tgz
ENV PATH="/usr/local/go/bin:$PATH"

RUN rm -rf /app/venv

RUN apt-get install -y python3-venv python3-pip

RUN python3 -m venv /app/venv

RUN /app/venv/bin/pip install --upgrade pip setuptools wheel
RUN /app/venv/bin/pip install zeroc-ice flask flask_classful flask_httpauth gevent greenlet gunicorn requests python-dotenv

RUN chmod +x entrypoint.sh

EXPOSE 80 443 20821 64739-64839/tcp 64739-64839/udp

CMD ["./entrypoint.sh"]
