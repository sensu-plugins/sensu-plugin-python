FROM python:2.7

ADD ./setup.sh /setup.sh

RUN chmod +x /setup.sh && \
    bash -c /setup.sh

ENTRYPOINT [ "/entrypoint.sh", "docker" ]
