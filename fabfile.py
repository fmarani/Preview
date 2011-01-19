import datetime
from fabric.api import *

tmp_time = datetime.datetime.now()
env.time = tmp_time.strftime("%Y-%m-%d_%H-%M")
env.project_name = "preview"

def production():
    """
    Live environment details
    """
    env.hosts = ['']
    env.environment = 'production'
    env.user = ''
    env.path = '/var/www/preview/'
    env.apache = 'preview-production-httpd.conf'
    env.wsgi = 'preview-production.wsgi'
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
    env.path = '/var/www/preview/'
    env.apache = 'preview-test-httpd.conf'
    env.wsgi = 'preview-test.wsgi'
    env.mysql_user = env.prefix
    env.mysql_pass = env.prefix
    env.mysql_name = env.prefix

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
    with cd(env.path):
        sudo('git checkout %s' % git_tag)
        print green("Deployment process completed.")

def restart():
    """
    Touches the wsgi file to 'restart' the app.
    """
    sudo('touch %(path)s../conf/%(wsgi)s' % env )

def clean():
    """
    Remove pyc files from the server. DO not forget to restart the server
    """
    run('find %s -iname \*pyc -delete' % env.path)

def sync_media():
    """
    Tar up the remote non-static media, download and install locally.
    """
    local('rsync -avz %(alias)s:%(path)smedia/uploads/ %(local_media_root)suploads/' % env)


