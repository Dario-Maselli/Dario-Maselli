# Use Ubuntu as the base image
FROM ubuntu:latest

ARG DEBIAN_FRONTEND=noninteractive

# Install necessary packages
RUN apt-get update && apt-get install -y \
    curl \
    sudo \
    unzip \
    git \
    libicu-dev \
    apt-transport-https \
    ca-certificates \
    gnupg2 \
    software-properties-common

# Install Docker
RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add - \
    && add-apt-repository \
    "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
    && apt-get update \
    && apt-get install -y docker-ce docker-ce-cli containerd.io

# Define user and group
ARG USERNAME=myuser

# Create a user and group dynamically with home directory
RUN groupadd -r $USERNAME && useradd -r -g $USERNAME -m -s /bin/bash $USERNAME \
    && usermod -aG docker $USERNAME \
    && usermod -aG sudo $USERNAME

# Give 'myuser' sudo privileges
RUN echo "$USERNAME ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/$USERNAME

# Set proper permissions for the necessary directories
RUN mkdir -p /actions-runner/_diag && chown -R $USERNAME:$USERNAME /actions-runner /home/$USERNAME

# Download and extract actions-runner
WORKDIR /actions-runner
RUN curl -o actions-runner.tar.gz -L https://github.com/actions/runner/releases/download/v2.314.1/actions-runner-linux-x64-2.314.1.tar.gz \
    && tar xzf actions-runner.tar.gz \
    && chown -R $USERNAME:$USERNAME /actions-runner

# Switch to the non-root user
USER $USERNAME

# Install additional packages as non-root user
RUN sudo apt-get update && sudo apt-get install -y \
    xz-utils \
    jq

# Configure the GitHub Actions local runner with the provided token
ARG GITHUB_ACCESS_TOKEN
ARG RUNNER_NAME
RUN ./config.sh --url https://github.com/Dario-Maselli/Dario-Maselli --token $GITHUB_ACCESS_TOKEN --name $RUNNER_NAME

# Specify the full path to the run.sh script
CMD ["./run.sh"]

# docker build -t private_runner --build-arg USERNAME=myuser --build-arg RUNNER_NAME=DARIO_MASELLI_RUNNER --build-arg GITHUB_ACCESS_TOKEN=A355TUGXHJAYHRVAEA4YIITGKS44G .
#  And run
# docker run --privileged -d private_runner
