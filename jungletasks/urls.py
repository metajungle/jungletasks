from django.conf.urls import patterns, include, url
from django.contrib.auth.views import login, logout 

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('tasks.views',

    url(r'^$', 'index', name='url_index'), 

    url(r'^tasks/$', 'tasks', name='url_tasks'), 
    url(r'^tasks/inbox/$', 'tasks_inbox', name='url_tasks_inbox'), 
    url(r'^tasks/all/$', 'tasks_all', name='url_tasks_all'), 
    url(r'^tasks/(?P<id>\d+)/$', 'tasks_label', name='url_tasks_label'), 

    url(r'^label/$', 'label', name='url_label'), 
    url(r'^label/add/$', 'label_add', name='url_label_add'), 
    url(r'^label/edit/(?P<id>\d+)/$', 'label_edit', name='url_label_edit'), 
    url(r'^label/delete/(?P<id>\d+)/$', 'label_delete', name='url_label_delete'), 
    
    url(r'^settings/$', 'settings', name='url_settings'), 
    url(r'^tools/$', 'tools', name='url_tools'), 
    url(r'^faq/$', 'faq', name='url_faq'), 

    url(r'^log/$', 'log', name='url_log'), 

    url(r'^form/task/add/$', 'form_task_add', name='url_form_task_add'), 
    url(r'^form/task/edit/$', 'form_task_edit', name='url_form_task_edit'), 
    (r'^b/task/add/$', 'bookmarklet_task_add'), 

    url(r'^api/task/add/$', 'api_task_add', name='url_task_add'), 
    url(r'^api/task/edit/$', 'api_task_edit', name='url_task_edit'), 
    url(r'^api/task/toggle/$', 'api_task_toggle', name='url_task_toggle'), 
    url(r'^api/task/labels/save/$', 'api_task_labels_save', 
        name='url_task_labels_save'), 
    url(r'^api/task/date/save/$', 'api_task_date_save', 
        name='url_task_date_save'), 

    url(r'^api/label/add/$', 'api_label_add', name='url_api_label_add'), 
    url(r'^api/label/rename/$', 'api_label_rename', name='url_label_rename'), 
    url(r'^api/label/del/$', 'api_label_delete', name='url_label_delete'), 
    url(r'^api/label/save/$', 'api_label_save', name='url_label_save'), 
    url(r'^api/labels/save/$', 'api_labels_save', name='url_labels_save'), 

    # admin and testing 
    (r'^robots.txt$', 'robots'), 
    # (r'^sitemap.xml$', 'googlesitemap'), 
                       
    (r'^test-ajax/$', 'ajax_response_test'), 
    (r'^test/$', 'test'), 

    # uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)

# account 
urlpatterns += patterns('account.views',
    url(r'^accounts/login/$', 'login', name='url_login'), 
    url(r'^accounts/signup/$', 'register', name='url_register'), 
    url(r'^confirm/$', 'confirm_email', name='url_email_confirmation'), 
    url(r'^accounts/pw/change/$', 'password_change', name='url_password_change'), 
    url(r'^accounts/pw/reset/$', 'password_reset', name='url_password_reset'), 
)

# import and export urls 
urlpatterns += patterns('tools.views',
    url(r'^tools/import/$', 'tasks_import', name='url_import'), 
    url(r'^tools/export/$', 'tasks_export', name='url_export'), 
)

# authentication 
urlpatterns += patterns('',
  # url(r'^accounts/signup/$', 'register', name='url_signup'), 
  #(r'^login/$',  login), 
  url(r'^logout/$', logout, name='url_logout', kwargs={ 'next_page': '/' }), 
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
