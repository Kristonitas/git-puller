import sys
import re
import os
from os import path
import git
import shutil

if len(sys.argv) != 2:
	print "Invalid number of arguments"
	exit(-1)

remoteUrl = sys.argv[1]
print remoteUrl

nameRe = re.compile(r'\/([^\/]+)\.git');
repoName = nameRe.search(remoteUrl).group(1)
print "Repository name: " + repoName

scriptPath = path.realpath(__file__)
scriptDir = path.dirname(scriptPath)
masterDir = path.join(scriptDir, "master")
tagDir = path.join(scriptDir, "tag")

if path.exists(masterDir):
	print "exists"
	repo = git.Repo(masterDir)
	repo.remote().pull()
else:
	print "cloning"
	repo = git.Repo.clone_from(remoteUrl, masterDir, branch='master')

masterLink = '<a href="master/">master</a>'

def onerror(func, path, exc_info):
    """
    Error handler for ``shutil.rmtree``.

    If the error is due to an access error (read only file)
    it attempts to add write permission and then retries.

    If the error is for another reason it re-raises the error.

    Usage : ``shutil.rmtree(path, onerror=onerror)``
    """
    import stat
    if not os.access(path, os.W_OK):
        # Is the error an access error ?
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise

if path.exists(tagDir):
	shutil.rmtree(tagDir, onerror=onerror)

tags = repo.tags
tagLinks = ''

for tag in tags:
	print "Tag: " + str(tag)
	tagSubDir = path.join(tagDir, str(tag))
	shutil.copytree(masterDir, tagSubDir)
	tagRepo = git.Repo(tagSubDir)
	tagRepo.git.checkout(str(tag))
	tagLinks += '      <li><a href="tag/{0}/">{0}</a></li>\n'.format(str(tag))

html = """
<!doctype html>
<html>
  <head>
  </head>
  <body>
  	<h1>{0}</h1>
    {1}

    <h4>Tags:</h4>
    <ul>
{2}    </ul>
  </body>
</html>
""".format(repoName.upper(), masterLink, tagLinks)

file = open(path.join(scriptDir, 'index.html'), 'w') 
file.write(html) 
file.close()
