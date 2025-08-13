FROM europe-west3-docker.pkg.dev/rasa-releases/rasa-pro/rasa-pro:3.13.5

# Switch to root user to install packages
USER root

RUN . /opt/venv/bin/activate && \
    pip install tavily-python==0.7.10

# Switch back to the default user
USER 1001

RUN mkdir -p /app/models /app/actions

COPY endpoints.yml /app/
COPY credentials.yml /app/
COPY actions/ /app/actions/
COPY models/model.tar.gz /app/models/

EXPOSE 5005
WORKDIR /app

# Bind to all interfaces, not just localhost
CMD ["run", "--enable-api", "--cors", "*", "--debug", "--port", "5005"]
