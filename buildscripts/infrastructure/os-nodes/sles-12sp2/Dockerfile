ARG DOCKER_REGISTRY
FROM ${DOCKER_REGISTRY}/sles-12sp2-base

SHELL ["/bin/bash", "-c"]

ARG ARTIFACT_STORAGE
ARG PACKAGES

RUN zypper addrepo -G ${ARTIFACT_STORAGE}/repository/sles12sp2 sles12sp2 \
    && zypper addrepo -G ${ARTIFACT_STORAGE}/repository/sles12spx-web-scripting web-scripting \
    && zypper -n --no-gpg-checks in --replacefiles --force-resolution \
    curl \
    cyrus-sasl-devel \
    enchant-devel \
    git \
    krb5-devel \
    libmysqlclient-devel \
    make \
    nodejs10 \
    npm10 \
    openldap2-devel \
    python \
    python-devel \
    python-pyOpenSSL \
    python-xml \
    rrdtool-devel \
    sudo \
    && zypper clean -a
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py \
    && python get-pip.py
RUN pip install --upgrade setuptools \
    && pip install git+https://github.com/svenpanne/pipenv.git@41f30d7ac848fdfe3eb548ddd19b731bfa8c331a \
    && zypper -n --no-gpg-checks in --replacefiles \
    $PACKAGES \
    && zypper clean -a
