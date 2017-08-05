from django.conf.urls import url, handler400, handler403, handler404, handler500

from . import views


handler400 = 'views.handler400'
handler403 = 'views.handler403'
handler404 = 'views.handler404'
handler500 = 'views.handler500'

urlpatterns = [
    url(r'login$', views.login, name='login'),
    url(r'logout$', views.logout, name='logout'),
    # ex: /
    url(r'^$', views.index, name='index'),
    url(r'address1/$',views.address1,name="address1"),
    url(r'address2/$',views.address2,name="address2"),

    # ex: /register/
    # url(r'^register', views.register, name='register'),
    url(r'(?P<roll_no>\w+)/basic$', views.GetInfo.basic, name='get-user-basic'),
    url(r'(?P<roll_no>\w+)/social$', views.GetInfo.social, name='get-user-social'),
    url(r'(?P<roll_no>\w+)/misc$', views.GetInfo.misc, name='get-user-misc'),

    url(r'(?P<roll_no>\w+)/basic/edit', views.PostInfo.basic, name='edit-user-basic'),
    url(r'(?P<roll_no>\w+)/social/edit', views.PostInfo.social, name='edit-user-social'),
    url(r'(?P<roll_no>\w+)/misc/edit', views.PostInfo.misc, name='edit-user-misc'),
    # url(r'(?P<roll_no>\w+)/address/current/edit', views.edit_current_address),
    # url(r'(?P<roll_no>\w+)/address/permanent/edit', views.edit_permanent_address),
    # url(r'(?P<roll_no>\w+)/qualification/(?P<qual_id>\w+)/edit', views.edit_qualification),
    # url(r'(?P<roll_no>\w+)/experience/(?P<exp_id>\w+)/edit', views.edit_work_experience),
]
