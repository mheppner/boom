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
    
def chunk_data(file_name, target_name, base64, chunk_size):
    files = [file_name]
    
    start_dir = os.path.abspath(os.getcwd())

    try:
        temp_path = tempfile.mkdtemp()
        
        # Retrieve via clone
        os.chdir(temp_path)
          
        # Track all files from chunking
        if chunk_size > 0:
            files = split_file(os.path.join(start_dir, files[0]), chunk_size)
            
        if base64:
            for file in files:
                base64_encode(file)
        
        # if we have more than one file, zip it up for download
        if len(files) > 1:
            
            random_name = os.path.join(start_dir, get_random_file_name() + '.zip')
            
            helper_name = get_random_file_name() + '.sh'
            # Write a helper file to rebuild from chunks
            with open(helper_name, 'w') as helper:
                helper.write('cat %s.??? %s> %s' % (target_name, '| base64 -d ' if base64 else '', target_name))
            
            with zipfile.ZipFile(random_name, 'w') as my_zip:
                for file in files:
                    arc_name = '%s.%s' % (target_name, file.split('.')[1])
                    my_zip.write(file, arc_name)
                my_zip.write(helper_name, 'reconstitute.sh')
            
            # Now that all files are packed into zip assign name to return
            file_name = random_name
    except:
        raise
    finally:            
        os.chdir(start_dir)
        try:
            shutil.rmtree(temp_path)
        except:
            pass

        
    return file_name
    
def file_retrieve(remote, target_name, base64, chunk_size=0):
    """Support for retrieval of arbitrary files
    
    :param remote: Remote URL of file
    :param target_name: chosen name for file to download
    :param base64: Whether file should be base64 encoded
    :param chunk_size: 0 for no chunking, otherwise max size in MiBs
    """
    
    file_name = get_random_file_name()
    urllib.urlretrieve(remote, file_name)
        
    output_file = chunk_data(file_name, target_name, base64, chunk_size)
    
    # if data was chunked, clean up source file
    if file_name != output_file:
        os.remove(file_name)
        
    return output_file

def git_repo_retrieve(remote, target_name, base64, branches=False, chunk_size=0):
    """Support for retrieval of git repos, with associated tags and branches
    :param remote: HTTPS url of git repo
    :param target_name: chosen name for file to download
    :param base64: Whether file should be base64 encoded
    :param branches: Whether tags other than default should be retrieved
    :param chunk_size: 0 for no chunking, otherwise max size in MiBs
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
    except:
        raise
    finally:            
        os.chdir(start_dir)
        try:
            shutil.rmtree(temp_path)
        except:
            pass
        
    output_file = chunk_data(file_name, target_name, base64, chunk_size)
    
    # if data was chunked, clean up source file
    if file_name != output_file:
        os.remove(file_name)
        
    return output_file
    
def split_file(path, size_mb):
    MAX  = size_mb*1024*1024 # max chapter size
    BUF  = 1*1024*1024  # 1GB   - memory buffer size
    
    file_names = []
    chapters = 0
    uglybuf  = ''
    with open(path, 'rb') as src:
      while True:
        file_name = os.path.basename(path + '.%03d' % chapters)
        with open(file_name, 'wb') as tgt:
            file_names.append(file_name)
            written = 0
            while written < MAX:
              tgt.write(uglybuf)
              tgt.write(src.read(min(BUF, MAX-written)))
              written += min(BUF, MAX-written)
              uglybuf = src.read(1)
              if len(uglybuf) == 0:
                break
        if len(uglybuf) == 0:
          break
        chapters += 1
        
    return file_names

def zip_dir(path, ziph):
    """Add an entire directory tree into a zip
    
    Courtesy of http://stackoverflow.com/questions/1855095/how-to-create-a-zip-archive-of-a-directory/
    """
    
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))