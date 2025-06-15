FROM alpine:3.21 AS builder
RUN apk add --no-cache py3-virtualenv
RUN virtualenv venv
ENV PATH="/venv/bin:$PATH"
RUN pip install nicegui

FROM alpine:3.21
RUN apk add --no-cache bash wget uuidgen python3 git tmux
COPY --from=builder /venv /venv
ENV PATH="/venv/bin:$PATH"

ENV VERSION=v2.1.1b3
ENV BASE_URL=https://github.com/heidrich76/megacmd-alpine/releases/download/${VERSION}
RUN wget "${BASE_URL}/megacmd_alpine_${VERSION}_$(uname -m).apk" -O /tmp/megacmd.apk && \
    apk add --no-cache --allow-untrusted /tmp/megacmd.apk && rm /tmp/megacmd.apk

ENV CONFIG_HOME=/root
ENV NICEGUI_STORAGE_PATH="$CONFIG_HOME/.nicegui"
COPY app /opt/megacmd-gui
WORKDIR /opt/megacmd-gui
RUN chmod -R -x * && chmod +x *.sh && ./prepare.sh
ENTRYPOINT ["/opt/megacmd-gui/run.sh"]
