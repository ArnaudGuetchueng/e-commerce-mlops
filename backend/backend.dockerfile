FROM python:3 as base

ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=.

COPY ./requirements.txt /backend/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /backend/requirements.txt
RUN rm /backend/requirements.txt

COPY ./ /backend

RUN chmod +x /backend/start-reload.sh

WORKDIR /backend

# Should be used for production image

FROM base as dev
CMD [ "./start-reload.sh" ]

FROM base as prod
CMD [ "./start-with-telemetry.sh" ]

# [Optional] If your requirements rarely change, uncomment this section to add them to the image.
# COPY requirements.txt /tmp/pip-tmp/
# RUN pip3 --disable-pip-version-check --no-cache-dir install -r /tmp/pip-tmp/requirements.txt \
#    && rm -rf /tmp/pip-tmp

# [Optional] Uncomment this section to install additional OS packages.
# RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
#     && apt-get -y install --no-install-recommends <your-package-list-here>



