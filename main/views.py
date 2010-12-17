from django.conf import settings
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import Context, loader, RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse

from main.models import *

def project(request, client_slug, project_slug):
    """Show versions for a project"""
    client = get_object_or_404(Client, slug=client_slug)
    if not has_perm_for_client(request, client, "comment"):
	return HttpResponseForbidden()
    project = get_object_or_404(Project, slug=project_slug)
    if project.client != client:
        raise Http404
    pages = Page.objects.filter(project=project)

    return render_to_response('main/project.html', {
        'pages': pages,
        'client': client,
        'project': project,}, context_instance=RequestContext(request))

def page_version_comments(request, client_slug, project_slug, page_slug, version_no):
    """Show comments for a version of a page"""
    client = get_object_or_404(Client, slug=client_slug)
    if not has_perm_for_client(request, client, "comment"):
	return HttpResponseForbidden()
    project = get_object_or_404(Project, slug=project_slug)
    page = get_object_or_404(Page, slug=page_slug)
    if project.client != client and page.project != project:
        raise Http404
    page_version = get_object_or_404(PageVersion, page=page, number=version_no)
    next = reverse(page_version_comments, args=[client.slug, project.slug, page.slug, page_version.number])
    return render_to_response('main/page_comments.html', locals(),
	 context_instance=RequestContext(request))

def client(request, client_slug):
    """Shows all projects that belong to a client"""
    client = get_object_or_404(Client, slug=client_slug)
    if has_perm_for_client(request, client, "view"):
    	return render_to_response('main/client.html', {
        	'client': client
	        }, context_instance=RequestContext(request))
    else:
	return HttpResponseForbidden()

def has_perm_for_client(request, client, permission):
    if not request.user.is_authenticated:
        return false
    client_user = ClientUser.objects.get(user=request.user, client=client)
    if permission == "view":
	return client_user.can_view
    elif permission == "comment":
	return client_user.can_comment
    elif permission == "approve":
	return client_user.can_approve
    else:
	return False

def user_login(request):
    if "submit" not in request.POST:
	return render_to_response("main/login.html", context_instance=RequestContext(request))
    else:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
		return HttpResponseRedirect(reverse(client, args=["acme"]))
            else:
	        return render_to_response("main/login.html", 
                     {"error": "Account disabled"}, context_instance=RequestContext(request))
        else:
	    return render_to_response("main/login.html", 
                 {"error": "Invalid login credentials"}, context_instance=RequestContext(request))
