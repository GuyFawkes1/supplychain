from django.conf.urls import url
from . import views
from rest_framework.urlpatterns import format_suffix_patterns


urlpatterns = [
	url('create/',views.profile_create.as_view()),
	url('test/',views.test.as_view())
#	url('api-auth/',include('rest_framework.urls'))
#	url('delete/',views.profile_delete.as_view()),
#	url('pub_key/',key_finder.as_view()),
#	url('edit/',views.profile_edit.as_view()),

]

urlpatterns = format_suffix_patterns(urlpatterns)