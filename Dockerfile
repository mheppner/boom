FROM python:2-onbuild
MAINTAINER Jonathan Meyer <jon@gisjedi.com>

EXPOSE 8000
CMD ["sh", "launch.sh"]
