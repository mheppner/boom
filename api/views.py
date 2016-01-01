import base64
import os
import urllib

from api.models import Download
from api.forms import StreamForm

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods


def get_client_ip(request):
    """
    Identify the remote IP of the user
    :param request:
    :return:
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

class FileCleaner:
    """
    Special context handler to remove file on context exit
    """
    def __init__(self, file_name, open_flags):
        self.fp = open(file_name, open_flags)
        self.file_name = file_name

    def __enter__(self):
        return self.fp

    def __exit__(self, exc_type, exc_value, traceback):
        self.fp.close()
        os.remove(self.file_name)
        print 'Cleanup complete for file: %s' % (self.file_name,)


def streaming_retrieve(remote, file_name, do_base64_encode, client_ip):
    """
    Code for retrieval and relay of either unmodified or base64_encoded content
    :param remote:
    :param file_name:
    :param do_base64_encode:
    :param client_ip:
    :return:
    """

    model = Download()
    model.base64encode = do_base64_encode
    model.remote = remote
    model.file_name = file_name
    model.client_ip = client_ip

    try:
        urllib.urlretrieve(remote, file_name)
        if do_base64_encode:
            base64_encode(file_name)

        with FileCleaner(file_name, 'rb') as fp:

            response = HttpResponse(fp)
            response["Content-Disposition"] = "attachment; filename=%s" % (file_name,)
            model.status = 'SUCCESS'
            return response
    except Exception, ex:
        model.status = 'FAILED'
        model.error = ex.message
    finally:
        model.save()


def base64_encode(file_name):
    """
    Base64 encode input file and replace input file
    :param file_name:
    :param chunk_size:
    :return:
    """
    temp_file = 'temp_%s' % (file_name,)
    with open(file_name, 'rb') as in_file:
        with open(temp_file, 'w') as out_file:
            base64.encode(in_file, out_file)

    os.remove(file_name)
    os.rename(temp_file, file_name)


@require_http_methods(["GET", "POST"])
def stream_view(request):
    """Support retrieval of a remote resource with optional base64 encoding

    :param request:
    :return:
    """
    if request.method == 'GET':
        return render(request, 'stream.html', {'form': StreamForm()})

    if request.method == 'POST':
        form = StreamForm(request.POST)
        if form.is_valid():
            file_name = form.cleaned_data['file_name']
            remote = form.cleaned_data['remote']
            do_base64_encode = False
            if 'base64_encode' in form.cleaned_data:
                do_base64_encode = form.cleaned_data['base64_encode'].lower() == 'true'

            return streaming_retrieve(remote, file_name, do_base64_encode, get_client_ip(request))

        return HttpResponse('Invalid form request', status=400)
