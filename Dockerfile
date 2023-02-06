FROM public.ecr.aws/docker/library/python:3.9.5-slim-buster AS requirements_builder

WORKDIR /app
COPY ./deployment/.ssh/ /root/.ssh/
RUN chmod 400 /root/.ssh/id_rsa

COPY --chown=1000:1000 docker-entrypoint.sh .
COPY requirements/requirements.txt /tmp/requirements.txt

ENV BUILD_DEPENDENCIES="\
    gcc \
    make \
    libsasl2-dev \
    git \
    openssh-client"

RUN set -ex \
    && apt-get update \
    && apt-get install -y --no-install-recommends ${BUILD_DEPENDENCIES} libldap2-dev libmariadbclient-dev curl iputils-ping vim-tiny chromium-driver \
    && python -m venv /venv \
    && . /venv/bin/activate \
    && pip install -U pip \
    && pip install --no-deps -r /tmp/requirements.txt \
    && apt-get remove -y ${BUILD_DEPENDENCIES} \
    && apt-get autoremove -y

ENTRYPOINT [ "/app/docker-entrypoint.sh" ]


FROM requirements_builder AS dev

COPY requirements/requirements_test.txt /tmp/requirements_test.txt

RUN set -ex \
    && apt-get update \
    && apt-get install -y --no-install-recommends ${BUILD_DEPENDENCIES}

RUN . /venv/bin/activate \
    && pip install --no-deps -r /tmp/requirements_test.txt

ENV PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE="pdf_gen_poc.settings"

COPY . .

EXPOSE 8000

# collect static
RUN /venv/bin/python manage.py collectstatic --noinput

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]


FROM requirements_builder AS production

ARG USER=pdf_gen_poc

ENV UID=1000 \
    GID=1000

RUN set -ex \
    && addgroup --gid ${GID} --system ${USER} \
    && adduser --system --gecos ${USER} --gid ${GID} -u ${UID} ${USER}

ENV PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE="pdf_gen_poc.settings"


RUN chown 1000:1000 .
COPY --chown=1000:1000 . .

RUN set -ex \
    && find /app -depth \( -name '*.pyo' -o -name '*.pyc' -o -name 'test' -o -name 'tests' \) -exec rm -rf '{}' +

# collect static
RUN . /venv/bin/activate \
    && /venv/bin/python manage.py collectstatic --noinput

# Switch to non-root user
USER ${USER}

EXPOSE 8000

CMD ["uwsgi", "pdf_gen_poc/uwsgi.ini"]
