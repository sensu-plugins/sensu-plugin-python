FROM python:3.6

COPY setup.sh /setup.sh

RUN chmod +x /setup.sh && \
    /setup.sh

ENTRYPOINT [ "/entrypoint.sh", "docker" ]
