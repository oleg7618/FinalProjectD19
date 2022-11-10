from django import template
#from django.contrib.auth.models import Group
from BulletinBoard.models import *


register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    group = user.groups.filter(name='subscribe').exists()
    return  group