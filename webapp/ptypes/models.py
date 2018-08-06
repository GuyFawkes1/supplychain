from django.db import models

# Create your models here.
class Ptype(object):
    def __init__(self, ptype_name, dept, role):
        self.name = ptype_name
        self.dept = dept
        self.role = role

class history_object(object):
    def __init__(self, name, ptype, dept, role, check, action, timestamp):
        self.name = name
        self.ptype = ptype
        self.dept = dept
        self.role = role
        self.check = check
        self.action = action
        self.timestamp = timestamp

class ProductTypeCreation(models.Model):
    ptype_name = models.CharField(max_length = 30)
    role_name = models.CharField(max_length = 30)
    check_assign = models.CharField(max_length = 100)

    
