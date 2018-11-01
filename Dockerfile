# Quality Assurance (QA) dashboard for Open Travel Data (OPTD)
# Reference:
# * https://hub.docker.com/r/opentraveldata/quality-assurance/
# * https://github.com/opentraveldata/quality-assurance
#
FROM centos:centos7
MAINTAINER Denis Arnaud <denis.arnaud_github at m4x dot org>
LABEL version="0.1"

# Configuration
ENV HOME /root

# Import the Centos-7 GPG key to prevent warnings
RUN rpm --import http://mirror.centos.org/centos/RPM-GPG-KEY-CentOS-7

# Update of CentOS
RUN yum -y clean all
RUN yum -y upgrade

# EPEL
RUN yum -y install epel-release

# Base install
RUN yum -y install git-all bzip2 gzip tar wget curl which

# Web application
RUN yum -y install python34 python34-pip python34-devel python2-django mod_wsgi
RUN pip3 install -U pip
RUN pip3 install -U networkx

# Tell Docker that about the Web application
EXPOSE 8888

# Launch Django
CMD ["/bin/bash"]

