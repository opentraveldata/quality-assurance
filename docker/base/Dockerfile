# Quality Assurance (QA) dashboard for Open Travel Data (OPTD)
# Reference:
# * https://hub.docker.com/r/opentraveldata/quality-assurance/
# * https://github.com/opentraveldata/quality-assurance/tree/master/docker
#
FROM centos:centos7
MAINTAINER Denis Arnaud <denis.arnaud_github at m4x dot org>
LABEL version="0.1"

# Docker build time environment variables
ENV HOME /root
ENV OPTDQA_DIR ${HOME}/dev/geo/opentraveldata-qa
ENV LANG en_US.UTF-8
ENV LC_ALL ${LANG}

# Set up of the user environment
ADD resources/bashrc ${HOME}/.bashrc
ADD resources/gitconfig ${HOME}/.gitconfig

# Import the Centos-7 GPG key to prevent warnings
RUN rpm --import http://mirror.centos.org/centos/RPM-GPG-KEY-CentOS-7

# Update of CentOS
RUN yum -y clean all && \
    yum -y upgrade && \
    yum -y install epel-release

# Supplementary software packages
RUN yum -y install git-all zlib-devel bzip2-devel gzip tar wget curl which \
	           gcc readline-devel sqlite-devel openssl-devel libffi-devel \
	           python34 python34-pip python34-devel \
                   python2-django mod_wsgi \
	           geos-devel geos-python

# Python Pyenv and pipenv
RUN git clone https://github.com/pyenv/pyenv.git ${HOME}/.pyenv
ENV PATH ${HOME}/.pyenv/bin:${HOME}/.pyenv/shims:${PATH}
RUN source ${HOME}/.bashrc && pyenv install 3.7.2
RUN pyenv global 3.7.2 && pip install -U pip pipenv && pyenv global system

# Clone the Open Travel Data (OPTD) Quality Assurance (QA) Git repository
RUN mkdir -p ${HOME}/dev/geo && \
	git clone https://github.com/opentraveldata/quality-assurance.git \
	${HOME}/dev/geo/opentraveldata-qa
WORKDIR ${OPTDQA_DIR}
RUN ./mkLocalDir.sh
RUN source ${HOME}/.bashrc && \
  pipenv install cython && \
  pipenv install git+https://github.com/jswhit/pyproj.git#egg=pyproj && \
  pipenv install git+https://github.com/matplotlib/basemap.git#egg=basemap && \
  pipenv install


# Launch a Bash Shell
CMD ["bash"]

