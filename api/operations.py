import base64
import os
import shutil
import subprocess
import tempfile
import urllib
import uuid
import zipfile


def get_random_file_name():
    return str(uuid.uuid4())

def base64_encode(file_name):
    """
    Base64 encode input file and replace input file
    :param file_name:
    :return:
    """
    
    temp_file = '%s.tmp' % (file_name,)
    with open(file_name, 'rb') as in_file:
        with open(temp_file, 'w') as out_file:
            base64.encode(in_file, out_file)

    os.remove(file_name)
    os.rename(temp_file, file_name)
    
def file_retrieve(remote, base64):
    """Support for retrieval of arbitrary files
    
    :param remote: Remote URL of file
    :param base64: Whether file should be base64 encoded
    """
    
    file_name = get_random_file_name()
    urllib.urlretrieve(remote, file_name)
    if base64:
        base64_encode(file_name)
        
    return file_name

def git_repo_retrieve(remote, base64, branches=False):
    """Support for retrieval of git repos, with associated tags and branches
    :param remote: HTTPS url of git repo
    :param base64: Whether file should be base64 encoded
    :param branches: Whether tags other than default should be retrieved
    """
    
    start_dir = os.path.abspath(os.getcwd())
    
    file_name = get_random_file_name()

    try:
        temp_path = tempfile.mkdtemp()
        
        # Retrieve via clone
        os.chdir(temp_path)
        
        print('Starting git clone of %s into %s...' % (remote, temp_path))
        
        proc = subprocess.Popen(['git', 'clone', remote], env={'GIT_TERMINAL_PROMPT': '0'}, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, err = proc.communicate()

        if proc.returncode != 0:
            raise Exception('Invalid return code of %s from git clone.\nOutput: %s\nError: %s' % (proc.returncode, output, err))
        git_dir = os.listdir(temp_path)[0]
        
        # If branches we need extra magic
        if branches:
            return_code = subprocess.call("cd %s && git branch -r | grep -v '\->' | while read remote; do git branch --track \"${remote#origin/}\" \"$remote\"; done" % git_dir, shell=True)
        
        # zip up repo
        with zipfile.ZipFile(os.path.join(start_dir, file_name), 'w') as my_zip:
            zip_dir(git_dir, my_zip)
            
        if base64:
            base64_encode(os.path.join(start_dir, file_name))
    except:
        raise
    finally:            
        os.chdir(start_dir)
        try:
            shutil.rmtree(temp_path)
        except:
            pass
    
    return file_name
    
        
def zip_dir(path, ziph):
    """Add an entire directory tree into a zip
    
    Courtesy of http://stackoverflow.com/questions/1855095/how-to-create-a-zip-archive-of-a-directory/
    """
    
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))