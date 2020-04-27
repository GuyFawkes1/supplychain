from rest_framework import permissions

class IsAdmin(permissions.BasePermission):

	def has_permission(self,request,view):

		if request.user.groups.values_list('name',flat=True)[0] == "Admin":
			return True