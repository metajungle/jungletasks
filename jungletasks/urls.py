from django.conf.urls import patterns, include, url
from django.contrib.auth.views import login, logout 

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('tasks.views',

    url(r'^$', 'index', name='url_index'), 
    url(r'^about/$', 'about', name='url_about'), 

    url(r'^tasks/$', 'tasks', name='url_tasks'), 
    url(r'^tasks/inbox/$', 'tasks_inbox', name='url_tasks_inbox'), 
    url(r'^tasks/completed/$', 'tasks_completed', name='url_tasks_completed'), 
    url(r'^tasks/(?P<id>\d+)/$', 'tasks_by_label', name='url_tasks_label'), 

    url(r'^tasks/add/$', 'tasks_add_task', name='url_tasks_add'), 
    url(r'^tasks/edit/(?P<id>\d+)/$', 'tasks_edit', name='url_tasks_edit'), 
    url(r'^tasks/delete/(?P<id>\d+)/$', 'tasks_delete', name='url_tasks_delete'), 
    url(r'^tasks/mark/$', 'tasks_mark_done', name='url_tasks_mark_done'), 

    url(r'^label/$', 'label', name='url_label'), 
    url(r'^label/add/$', 'label_add', name='url_label_add'), 
    url(r'^label/edit/(?P<id>\d+)/$', 'label_edit', name='url_label_edit'), 
    url(r'^label/delete/(?P<id>\d+)/$', 'label_delete', name='url_label_delete'), 

    url(r'^label/assign/$', 'label_task_assign_json', name='url_task_assign_json'), 
    url(r'^label/hidden/$', 'label_set_hidden_json', name='url_label_set_hidden_json'), 

    # uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)

# account 
urlpatterns += patterns('account.views',
    url(r'^accounts/login/$', 'login', name='url_login'), 
    url(r'^accounts/signup/$', 'register', name='url_signup'), 
    url(r'^confirm/$', 'confirm_email', name='url_email_confirmation'), 
    url(r'^accounts/password-change/$', 'password_change', name='url_password_change'), 
    url(r'^accounts/password-reset/$', 'password_reset', name='url_password_reset'), 
)

# import and export urls 
urlpatterns += patterns('tools.views',
    url(r'^tools/$', 'tools', name='url_tools'), 
    url(r'^tools/export/preview/all/$', 'tasks_export_preview_all', name='url_export_preview_all'), 
    url(r'^tools/export/preview/(?P<id>\d+)/$', 'tasks_export_preview_label', name='url_export_preview_label'), 
    url(r'^tools/export/$', 'tasks_export', name='url_export'), 
    
    url(r'^tools/log/$', 'activity_log', name='url_log'), 
)

# authentication 
urlpatterns += patterns('',
  # url(r'^accounts/signup/$', 'register', name='url_signup'), 
  #(r'^login/$',  login), 
  url(r'^logout/$', logout, name='url_logout', kwargs={ 'next_page': '/' }), 
)

# for dev
urlpatterns += patterns('dev.views',
  url(r'^dev/login/$', 'dev_login', name='url_dev_login' ), 
)

# urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'jungletasks.views.home', name='home'),
    # url(r'^jungletasks/', include('jungletasks.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
# )
