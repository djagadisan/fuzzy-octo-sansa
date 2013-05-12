import os
import sys
import argparse
import numpy as np
import unicodedata
from numpy import *
from keystoneclient.v2_0 import client as client_keystone
from novaclient.v1_1 import client as client_nova
from keystoneclient import utils
from ConfigParser import SafeConfigParser

parser = SafeConfigParser()
config_file='/home/deven/scripts/nova/keystone/config.ini'
parser.read(config_file)

def process_config(section,option):
    for section_name in parser.sections():
        try:
            if section_name == section:
                list_items = parser.get(section_name,option)
        except:
            list_items=None
    return list_items


def create_client(_user,_pass,_t_name,_a_url,args=None,_id=None,_tenant_args=None,description=None,roles=None):
    keystone = client_keystone.Client(username=_user,password=_pass,tenant_name=_t_name,auth_url=_a_url)
    if args is "list":
        _out = array(keystone.users.list())
    elif args is "user":
        _out = array(keystone.users.get(_id))
    elif args is "tenant":
        _out = array(keystone.tenants.list())
    elif args is "add_tenant":
        _out = keystone.tenants.create(_tenant_args,description)
    elif args is "rm_tenant":
        _out = keystone.tenants.delete(_id)
    elif args is "add_role":
        _out = keystone.tenants.add_user(_tenant_args,_id,roles)
    elif args is "roles":
        _out = keystone.users.list_roles(_id,_tenant_args)

    return _out

def create_user_list(conn):
    users = array(conn.users.list())
    return users

def _search(_info,_search_var,_var):
    _var = unicode(_var)
    for x in range(len(_info)):
        if isinstance(getattr(_info[x],_search_var),unicode) and getattr(_info[x],_search_var).strip().lower()==_var.lower():
            _user_uuid=getattr(_info[x],'id')
            break
        else:
            _user_uuid=None

    return _user_uuid


def user_input(**kwargs):
    for key in kwargs:
       return kwargs[key]
    
        
def _arg_parse():
    parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS)
    parser.add_argument('create_tenant',help='Create tenant with quota from allocation request')
    parser.add_argument('-t','-tenant_name',action='store',required=True,help='Tenant Name')
    parser.add_argument('-e','-user_email',action='store',required=True,help='User email')
    parser.add_argument('-c','-cores',action="store",type=int,required=True,help='Number or cores')
    parser.add_argument('-i','-instances',action='store',required=True,type=int,help='Number of instances')
    parser.add_argument('-d','-tenant_desc',action='store',nargs=1,default=None,help='Tenant description')

    _return = parser.parse_args()

     

    return _return

infra="production"
_user=process_config(infra,'user')
_passwd=process_config(infra,'passwd')
_name=process_config(infra,'name')
_url=process_config(infra,'url')

#_email = _arg_parse()
results=_arg_parse()
args_type = results.create_tenant
args_tname = results.t
args_uemail = results.e
args_cores = results.c
args_i = results.i
args_tdesc = results.d
args_memory = (args_i * (1024*4))

print "Adding Tenant with following input"
print "Tenant Name: %s" % args_tname
print "Tenant Manager: %s"% args_uemail
print "Number of Cores allocated: %d" % args_cores
print "Memory allocated: %d" % args_memory
print "Number of instances allocated: %d \n" % args_i

#ram_='81096'
#cores_='4'
#instances_='2'
#t_id='f1fef9e57fd34ff48cffe6987b5da40f'
#t_id='3f782066c60b45beab3eeefa493101e1'
#t_id='57032e044c7f42e2be842bcd4b208594'
#t_id='220dd9b55f5244e9b81c63e8ec760623'
role_admin='14'
role_member='2'
#role_admin='75fc2fd3a6004c37bbd6c518c25cdaaa'
#role_member='f5ef8c03b88f4bc98b2b2a3856f8ad1c'
#create_client(_user,_passwd,_name,_url,args="rm_tenant",_id=t_id)
#keystone = client_keystone.Client(username=_user,password=_passwd,tenant_name=_name,auth_url=_url)
#keystone.tenants.delete(t_id)
#quota_ = client.Client(username=_user,api_key=_passwd,project_id=_name,auth_url=_url)
#quota_.quotas.update(t_id,ram=ram_,instances=instances_,cores=cores_)
#print quota_.quotas.get(t_id)
#print "Cores: %s, Memory: %s, Instances: %s" % (getattr(quota_.quotas.get(t_id),'cores'),getattr(quota_.quotas.get(t_id),'ram'),getattr(quota_.quotas.get(t_id),'instances'))


_list = create_client(_user,_passwd,_name,_url,args="tenant")
_res_t = _search(_list,'name',args_tname)
_list = create_client(_user,_passwd,_name,_url,args="list")
_res_id = _search(_list,'email',args_uemail)


if _res_t == None :
    if _res_id != None:
        print "Add Tenant"
        create_client(_user,_passwd,_name,_url,args="add_tenant",_tenant_args=args_tname,description=args_tdesc)
        _list = create_client(_user,_passwd,_name,_url,args="tenant")
        t_id = _search(_list,'name',args_tname)
        create_client(_user,_passwd,_name,_url,args="add_role",_tenant_args=t_id,_id=_res_id,roles=role_admin)
        create_client(_user,_passwd,_name,_url,args="add_role",_tenant_args=t_id,_id=_res_id,roles=role_member)
        _list = create_client(_user,_passwd,_name,_url,args="tenant",_tenant_args=t_id,_id=_res_id,roles=role_member)
        _t_id = _search(_list,'name',args_tname)
        quota_ = client_nova.Client(username=_user,api_key=_passwd,project_id=_name,auth_url=_url)
        quota_.quotas.update(_t_id,ram=args_memory,instances=args_i,cores=args_cores)
        _list = create_client(_user,_passwd,_name,_url,args="tenant")
        args_tid = _search(_list,'name',args_tname)

        print "Adding Tenant Succesfull"
        print "Tenant Name: %s" % args_tname
        print "Tenant Manager: %s"% args_uemail
        print "Tenant ID: %s" % args_tid
        print "Number of Cores allocated: %d" % args_cores
        print "Memory allocated: %d" % args_memory
        print "Number of instances allocated: %d \n" % args_i

        
    else:
        print "Adding Tenant failed ! User does not exits!"
        exit(0)    
else:
    print "Adding Tenant failed ! Tenant %s with id %r exists!" %(args_tname,_res_t)
    exit(0)
