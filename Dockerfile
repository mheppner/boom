FROM python:2-onbuild
MAINTAINER Jonathan Meyer <jon@gisjedi.com>

sudo apt install git

EXPOSE 8000
CMD ["sh", "launch.sh"]
