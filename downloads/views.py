from django.core.urlresolvers import reverse
from django.views.generic import DetailView, TemplateView, ListView, RedirectView
from django.http import Http404

from .models import OS, Release


class DownloadLatestPython2(RedirectView):
    """ Redirec to latest Python 2 release """
    permanent = False

    def get_redirect_url(self, **kwargs):
        try:
            latest_python2 = Release.objects.released().python2().latest()
        except Release.DoesNotExist:
            latest_python2 = None

        if latest_python2:
            return latest_python2.get_absolute_url()
        else:
            return reverse('download')

class DownloadLatestPython3(RedirectView):
    """ Redirec to latest Python 3 release """
    permanent = False

    def get_redirect_url(self, **kwargs):
        try:
            latest_python3 = Release.objects.released().python3().latest()
        except Release.DoesNotExist:
            latest_python3 = None

        if latest_python3:
            return latest_python3.get_absolute_url()
        else:
            return reverse('download')


class DownloadBase(object):
    """ Include latest releases in all views """
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'latest_python2': Release.objects.released().python2().latest(),
            'latest_python3': Release.objects.released().python3().latest(),
        })
        return context


class DownloadHome(DownloadBase, TemplateView):
    template_name = 'downloads/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            latest_python2 = Release.objects.released().python2().latest()
        except Release.DoesNotExist:
            latest_python2 = None

        try:
            latest_python3 = Release.objects.released().python3().latest()
        except Release.DoesNotExist:
            latest_python3 = None

        python_files = []
        for o in OS.objects.all():
            data = {
                'os': o,
                'python2': latest_python2.download_file_for_os(o.slug),
                'python3': latest_python3.download_file_for_os(o.slug),
            }
            python_files.append(data)

        context.update({
            'releases': Release.objects.downloads(),
            'latest_python2': latest_python2,
            'latest_python3': latest_python3,
            'python_files': python_files,
        })

        return context


class DownloadFullOSList(DownloadBase, ListView):
    template_name = 'downloads/full_os_list.html'
    context_object_name = 'os_list'
    model = OS


class DownloadOSList(DownloadBase, DetailView):
    template_name = 'downloads/os_list.html'
    context_object_name = 'os'
    model = OS

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'os_slug': self.object.slug,
            'releases': Release.objects.filter(files__os__slug=self.object.slug).select_related().distinct().order_by('-release_date')
        })
        return context


class DownloadReleaseDetail(DownloadBase, DetailView):
    template_name = 'downloads/release_detail.html'
    model = Release
    context_object_name = 'release'

    def get_object(self):
        try:
            return self.get_queryset().select_related().get(slug=self.kwargs['release_slug'])
        except self.model.DoesNotExist:
            raise Http404
