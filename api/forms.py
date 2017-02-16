from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit


class StreamForm(forms.Form):
    remote = forms.URLField(help_text='Remote URI of object to retrieve')
    file_name = forms.CharField(help_text='File name including extension to name download. (Ignored with git clones)')
    chunk_size = forms.IntegerField(help_text='Maximum file chunk in MiBs. 0 will skip chunking. Base64 encoding will grow chunks by roughly 4/3s.',
                                initial=0)
    retrieve_type = forms.ChoiceField(
        choices=(
            ('file', "URL to publicly available file"),
            ('git', "HTTP/HTTPS endpoint to git repo, default branch only"),
            ('git-all', "HTTP/HTTPS endpoint to git repo, with all branches")
        ),
        widget=forms.RadioSelect,
        initial='file')
    base64_encode = forms.ChoiceField(
        choices=(
            (True, "Base64 encode download"),
            (False, "Leave download unaltered")
        ),
        widget=forms.RadioSelect,
        initial=False)

    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-lg-2'
    helper.field_class = 'col-lg-8'
    helper.layout = Layout(
        'remote',
        'file_name',
        'chunk_size',
        'retrieve_type',
        'base64_encode',
        Submit('submit', 'Download', css_class='btn-primary'),
    )

class EmailForm(forms.Form):
    remote = forms.URLField(label='Remote URI of file to retrieve')
    file_name = forms.CharField(label='Valid file name with extension to name download')
    email = forms.EmailField(label='Email to send file')
    base64_encode = forms.BooleanField(label='Should it be base64 encoded', required=False)
