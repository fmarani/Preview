import datetime
from fabric.api import *

tmp_time = datetime.datetime.now()
env.time = tmp_time.strftime("%Y-%m-%d_%H-%M")
env.project_name = "preview"
env.project_repo = "git://github.com/fmarani/Preview.git"
env.virtualenv_path = '/usr/local/django/virtualenvs/'

def production():
    """
    Live environment details
    """
    env.hosts = ['']
    env.environment = 'production'
    env.user = ''
    env.path = '/usr/local/django/preview/'
    env.apache = 'preview-production.conf'
    env.wsgi = 'preview.wsgi'
    env.mysql_user = env.prefix
    env.mysql_pass = env.prefix
    env.mysql_name = env.prefix

def test():
    """
    Test environment details
    """
    env.hosts = ['localhost']
    env.environment = 'test'
    env.user = 'maranif'
    env.path = '/usr/local/django/preview/'
    env.apache = 'preview-test.conf'
    env.wsgi = 'preview.wsgi'
    env.mysql_user = env.prefix
    env.mysql_pass = env.prefix
    env.mysql_name = env.prefix

def bootstrap():
    """
    Bootstrap target environment, only do this once
    """
    print green("Bootstrapping %s on %s.." % (env.project_name, env.environment))
    require('root', provided_by=('production', 'test'))
    run("git clone %s %s" % (env.project_repo, env.path))
    with cd(env.path):
        run("mkvirtualenv --no-site-packages %s" % env.project_name)
        run("source %(virtualenv_path)s%(project_name)s/bin/activate && pip install -r requirements.txt")

def deploy():
    """
    Update the checkout with git.
    """
    print green("Starting the deployment process for %s on %s.." % (env.project_name, env.environment))
    require('root', provided_by=('production', 'test'))
    if env.environment == 'production':
        if not console.confirm('Are you sure you want to deploy PRODUCTION?',
                               default=False):
            utils.abort('Production deployment aborted.')
    git_tag = prompt("Which git tag?")
    if not git_tag:
        utils.abort('Please specify tag')
    with cd(env.path):
        sudo('git checkout %s' % git_tag)
        print green("Deployment process completed.")

def restart():
    """
    Touches the wsgi file to 'restart' the app.
    """
    sudo('touch %(path)s../apache/%(wsgi)s' % env )

def clean():
    """
    Remove pyc files from the server. DO not forget to restart the server
    """
    run('find %s -iname \*.pyc -delete' % env.path)

def sync_media():
    """
    Tar up the remote non-static media, download and install locally.
    """
    pass
    #local('rsync -avz %(alias)s:%(path)smedia/uploads/ %(local_media_root)suploads/' % env)


