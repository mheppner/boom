import os
import traceback

from api.models import Download
from api.forms import StreamForm
from api.operations import file_retrieve, git_repo_retrieve

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods


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

def view_file_retrieve(remote, file_name, do_base64_encode, client_ip):
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
        output_file = file_retrieve(remote, do_base64_encode)
        
        with FileCleaner(output_file, 'rb') as fp:

            response = HttpResponse(fp)
            response["Content-Disposition"] = "attachment; filename=%s" % (file_name,)
            model.status = 'SUCCESS'
            return response
    except Exception, ex:
        model.status = 'FAILED'
        ex_str = traceback.format_exc()
        model.error = ex_str
        return HttpResponse(ex_str, status=400)
    finally:
        model.save()

def view_git_repo_retrieve(remote, file_name, do_base64_encode, client_ip, branches=False):
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
    model.git_branches = branches
    
    try:
        print('Starting retrieve...')
        output_file = git_repo_retrieve(remote, do_base64_encode, branches)
        with FileCleaner(output_file, 'rb') as fp:

            response = HttpResponse(fp)
            response["Content-Disposition"] = "attachment; filename=%s" % (file_name,)
            model.status = 'SUCCESS'
            return response
    except Exception, ex:
        model.status = 'FAILED'
        ex_str = traceback.format_exc()
        model.error = ex_str
        return HttpResponse(ex_str, status=400)
    finally:
        model.save()

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
            retrieve_type = form.cleaned_data['retrieve_type'].lower()
            do_base64_encode = False
            if 'base64_encode' in form.cleaned_data:
                do_base64_encode = form.cleaned_data['base64_encode'].lower() == 'true'
            
            if retrieve_type == 'git':
                return view_git_repo_retrieve(remote, file_name, do_base64_encode, get_client_ip(request))
            elif retrieve_type == 'git-all':
                return view_git_repo_retrieve(remote, file_name, do_base64_encode, get_client_ip(request), branches=True)
            elif retrieve_type == 'file':
                return view_file_retrieve(remote, file_name, do_base64_encode, get_client_ip(request))

        return HttpResponse('Invalid form request', status=400)
