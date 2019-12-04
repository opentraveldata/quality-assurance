# Quality Assurance (QA) dashboard for Open Travel Data (OPTD)
# References:
# * C++/Python base image:
#   + https://cloud.docker.com/u/cpppythondevelopment/repository/docker/cpppythondevelopment/base
#   + https://github.com/cpp-projects-showcase/docker-images
# * Docker images for this project:
#   + https://cloud.docker.com/u/opentraveldata/repository/docker/opentraveldata/quality-assurance
#   + https://github.com/opentraveldata/quality-assurance/tree/master/docker

#
FROM cpppythondevelopment/base:centos8
MAINTAINER Denis Arnaud <denis.arnaud_github at m4x dot org>
LABEL version="0.2"

# Docker build time environment variables
ENV container docker
ENV HOME /home/build
ENV LANGUAGE en_US:en
ENV LANG en_US.UTF-8
ENV LC_ALL ${LANG}
ENV OPTDQA_DIR ${HOME}/dev/geo/opentraveldata-qa

# Add a Shell alias for the OPTD QA project
USER root
ADD resources/bash_aliases ${HOME}/.bash_aliases
RUN chown build.build ${HOME}/.bash_aliases

# Switch to the `build` user
WORKDIR ${HOME}
USER build

# Clone the Open Travel Data (OPTD) Quality Assurance (QA) Git repository
RUN mkdir -p ${HOME}/dev/geo && \
  git clone https://github.com/opentraveldata/quality-assurance.git ${OPTDQA_DIR}
WORKDIR ${OPTDQA_DIR}
RUN ./mkLocalDir.sh
RUN source ${HOME}/.bashrc && pipenv install

# Add a Shell alias for the OPTD QA project
RUN cat >> ${HOME}/.bashrc < ${HOME}/.bash_aliases

# Run a few checkers
RUN source ${HOME}/.bashrc && make checkers && \
  for csvfile in results/*.csv; do wc -l ${csvfile}; done 

# Entry point
CMD ["/bin/bash"]

