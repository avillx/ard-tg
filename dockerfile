FROM python:3.13.14-alpine3.23

WORKDIR /opt/ard-tg

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    USER=runner \
    ARDTG_FILESTORAGE_PATH=/opt/ard-tg/data \
    ARDTG_AGENT_DATAPATH=/opt/ard-tg/agent-data

COPY --chmod=555 ./LICENSE ./README.md ./pyproject.toml ./
COPY --chmod=555 ./src ./
COPY --chmod=555 ./skills ./
COPY --chmod=555 ./scripts/entrypoint.sh ./

RUN adduser -D -H $USER

RUN mkdir -p $ARDTG_FILESTORAGE_PATH && chown -R $USER:$USER $ARDTG_FILESTORAGE_PATH
RUN mkdir -p $ARDTG_AGENT_DATAPATH  && chown -R $USER:$USER $ARDTG_AGENT_DATAPATH

RUN pip install --upgrade pip \
    && pip install .

USER $USER

ENTRYPOINT ["./entrypoint.sh"]
