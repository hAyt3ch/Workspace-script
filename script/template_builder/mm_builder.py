import json
import string

import os
import errno

import logging
import logzero
from logzero import setup_logger

from arubafi import MMClient

class MMBuilder:
    """
    MobilityMaster Class to build a new Hierarchy and new profiles from JSON
    format. Hence, build multiple ap-group profiles extracted from a list using json files templates.
    * virtual-ap profiles
        ** aaa profile
        ** ssid profile
    * dot11 radio profiles
    * ap system profile
    * RD profile
    """
    __builder_logger = None
    __template_name = ''
    __md_config_path = ''
    __separator = ''
    __ap_group_name = ''
    __dot11a_filename = ''
    __dot11g_filename = ''
    __vap_corp_filename = ''
    __vap_public_filename = ''
    __ssid_corp_filename = ''
    __ssid_public_filename = ''
    __aaa_corp_filename = ''
    __aaa_corp_sg_filename = ''
    __aaa_corp_dot1x_filename = ''
    __aaa_radius_filename = ''
    __aaa_public_filename = ''
    __rd_filename = ''
    __ap_sys_filename = ''
    __ap_group_filename = ''
    __dot11a_radio_profile_name = ''
    __dot11g_radio_profile_name = ''
    __ap_sys_profile_name = ''
    __rd_profile_name = ''
    __vap_corp_profile_name = ''
    __vap_public_profile_name = ''
    __ssid_corp_profile_name = ''
    __ssid_public_profile_name = ''
    __aaa_corp_profile_name = ''
    __aaa_corp_sg_profile_name = ''
    __aaa_corp_dot1x_profile_name = ''
    __aaa_radius_profile_name = ''
    __aaa_public_profile_name = ''
    __ant_ext = False
    __md_config_data = {}
    __dot11a_data = {}
    __dot11g_data = {}
    __ap_sys_data = {}
    __rd_data = {}
    __ssid_corp_data = {}
    __ssid_public_data = {}
    __aaa_corp_data = {}
    __aaa_corp_sg_data = {}
    __aaa_corp_dot1x_data = {}
    __aaa_radius_data = {}
    __aaa_public_data = {}
    __vap_corp_data = {}
    __vap_public_data = {}
    __ap_group_data = {}
    mm_session_token = None
    
    def __init__(self, ap_group_name='', template_name='TEMPLATE', ant_ext=False, separator='-'):
        """
        MMbuilder constructor
        """
        self.__builder_logger = setup_logger(name="mm_builder_logger", logfile="mm_builder.log", level=logging.INFO)
        self.__template_name = template_name
        self.__md_config_path = '/md/'+template_name
        self.__md_config_data = {"node-path": template_name}
        self.__separator = separator
        self.__dot11a_filename = 'template-dot11a.json'
        self.__dot11g_filename = 'template-dot11g.json'
        self.__ssid_corp_filename = 'template-ssid_corp.json'
        self.__ssid_public_filename = 'template-ssid_public.json'
        self.__aaa_corp_filename = 'template-aaa_corp.json'
        self.__aaa_corp_sg_filename = 'template-aaa_corp-sg.json'
        self.__aaa_corp_dot1x_filename = 'template-aaa_corp-dot1x.json'
        self.__aaa_radius_filename = 'template-aaa-radius.json'
        self.__aaa_public_filename = 'template-aaa_public.json'
        self.__vap_corp_filename = 'template-vap_corp.json'
        self.__vap_public_filename = 'template-vap_public.json'
        self.__rd_filename = 'template-rd.json'
        self.__ap_sys_filename = 'template-ap_sys.json'
        self.__ap_group_filename = 'template-ap_group.json'
        self.__ant_ext = ant_ext

        const_name_id = ap_group_name[0:3]+self.__separator+template_name+self.__separator
        const_name_no_id = template_name+self.__separator

        self.__ap_group_name = ap_group_name.strip()
        self.__dot11a_radio_profile_name = const_name_id+('dot11a' if not self.__ant_ext else 'dot11a-ext')
        self.__dot11g_radio_profile_name = const_name_id+('dot11g' if not self.__ant_ext else 'dot11g-ext')
        self.__ap_sys_profile_name = const_name_id+'ap_sys'
        self.__rd_profile_name = const_name_id+'rd'
        self.__aaa_corp_profile_name = const_name_id+'aaa-corp'
        self.__aaa_corp_sg_profile_name = const_name_no_id+'aaa-sg-corp'
        self.__aaa_corp_dot1x_profile_name = const_name_no_id+'aaa-dot1x-corp'
        self.__aaa_radius_profile_name = const_name_no_id+'aaa-radius'
        self.__aaa_public_profile_name = const_name_no_id+'aaa-public'
        self.__ssid_corp_profile_name = const_name_id+'ssid-corp'
        self.__ssid_public_profile_name = const_name_id+'ssid-public'
        self.__vap_corp_profile_name = const_name_id+'vap-corp'
        self.__vap_public_profile_name = const_name_id+'vap-public'
        
        self.__dot11a_data = {}
        self.__dot11g_data = {}
        self.__ap_sys_data = {}
        self.__rd_data = {}
        self.__vap_corp_data = {}
        self.__vap_public_data = {}
        self.__ap_group_data = {}

        try:
           with (
               open(self.__dot11a_filename, 'r') as f_dot11a, 
               open(self.__dot11g_filename, 'r') as f_dot11g, 
               open(self.__ssid_corp_filename, 'r') as f_ssid_corp,
               open(self.__ssid_public_filename, 'r') as f_ssid_public,
               open(self.__aaa_radius_filename, 'r') as f_radius,
               open(self.__aaa_corp_dot1x_filename, 'r') as f_dot1x_corp,
               open(self.__aaa_corp_sg_filename, 'r') as f_sg_corp,
               open(self.__aaa_corp_filename, 'r') as f_aaa_corp,
               open(self.__vap_corp_filename, 'r') as f_vap_corp,
               open(self.__vap_public_filename, 'r') as f_vap_public,
               open(self.__rd_filename, 'r') as f_rd,
               open(self.__ap_sys_filename, 'r') as f_ap_sys,
               open(self.__ap_group_filename, 'r') as f_ap_group
           ):
                                   self.__dot11a_data = json.load(f_dot11a)
                                   self.__dot11g_data = json.load(f_dot11g)
                                   self.__ap_sys_data = json.load(f_ap_sys)
                                   self.__rd_data = json.load(f_rd)
                                   self.__ssid_corp_data = json.load(f_ssid_corp)
                                   self.__ssid_public_data = json.load(f_ssid_public)
                                   self.__aaa_corp_data = json.load(f_aaa_corp)
                                   self.__aaa_corp_sg_data = json.load(f_sg_corp)
                                   self.__aaa_corp_dot1x_data = json.load(f_dot1x_corp)
                                   self.__aaa_radius_data = json.load(f_radius)
                                   self.__vap_corp_data = json.load(f_vap_corp)
                                   self.__vap_public_data = json.load(f_vap_public)
                                   self.__ap_group_data = json.load(f_ap_group)
        except OSError as e:
            if e.errno == 2:
                self.__builder_logger.exception('Could not open json file: %s', e.filename)
                exit(0)
            else:
                raise
    
    @staticmethod
    def mm_login(mm_host, username):
        """
        docstring
        """
        MMBuilder.mm_session_token = MMClient(mm_host, username)
        MMBuilder.mm_session_token.login()

    @staticmethod
    def mm_logout():
        """
        docstring
        """
        MMBuilder.mm_session_token.logout()

    @staticmethod
    def mm_purge_config():
        """
        docstring
        """
        MMBuilder.mm_session_token.purge_pending_configuration()

    def __update_ssid_profile(self, **kwargs):
        """
        docstring
        """
        if kwargs['type'] == 'corp':
            self.__ssid_corp_data['profile-name'] = self.__ssid_corp_profile_name
            self.__ssid_corp_data['essid']['essid'] = self.__template_name
        elif kwargs['type'] == 'public':
            self.__ssid_public_data['profile-name'] = self.__ssid_public_profile_name
            self.__ssid_public_data['essid']['essid'] = self.__template_name+self.__separator+'PUBLIC'
        else:
            raise NotImplementedError

    def __update_aaa_radius(self):
        """
        docstring
        """
        self.__aaa_radius_data['rad_server_name'] = self.__aaa_radius_profile_name
        return True

    def __update_aaa_corp_sg_profile(self):
        """
        docstring
        """
        self.__aaa_corp_sg_data['sg_name'] = self.__aaa_corp_sg_profile_name
        dict_tmp = {}
        dict_tmp = self.__aaa_corp_sg_data['auth_server'][0]
        dict_tmp['name'] = self.__aaa_radius_profile_name
        return True

    def __update_aaa_corp_dot1x_profile(self):
        """
        docstring
        """
        self.__aaa_corp_dot1x_data['profile-name'] = self.__aaa_corp_dot1x_profile_name
        return True

    def __update_aaa_corp_profile(self, ):
        """
        docstring
        """
        self.__aaa_corp_data['profile-name'] = self.__aaa_corp_profile_name
        self.__aaa_corp_data['dot1x_auth_profile']['profile-name'] = self.__aaa_corp_dot1x_profile_name
        self.__aaa_corp_data['dot1x_server_group']['srv-group'] = self.__aaa_corp_sg_profile_name
        self.__aaa_corp_data['rad_acct_sg']['server_group_name'] = self.__aaa_corp_sg_profile_name
        return True

    def __update_rd_profile(self, parameter_list=None):
        """
        docstring
        """
        self.__rd_data['profile-name'] = self.__rd_profile_name
        return True

    def __update_ap_sys_profile(self, parameter_list=None):
        """
        docstring
        """
        self.__ap_sys_data['profile-name'] = self.__ap_sys_profile_name
        return True

    def __update_radio_profiles(self):
        """
        build radio profiles: a and g
        """
        self.__dot11g_data['profile-name'] = self.__dot11g_radio_profile_name
        self.__dot11a_data['profile-name'] = self.__dot11a_radio_profile_name
        return True
    
    def __get_ap_sys_profile(self, parameter_list=None):
        """
        docstring
        """
        return self.__ap_sys_data

    def __get_rd_profile(self, parameter_list=None):
        """
        docstring
        """
        return self.__rd_data

    def __get_dot11a_radio_profile(self):
        """
        get __dot11a_data member
        """
        return self.__dot11a_data

    def __get_dot11g_radio_profile(self):
        """
        get __dot11g_data member
        """
        return self.__dot11g_data

    def __get_ap_group_profile(self):
        """
        get __ap_group_data member
        """
        return self.__ap_group_data

    def __build_aaa_corp_profile(self):
        """
        docstring
        """
        data_http_post_sg_corp = {}
        data_http_post_dot1x_corp = {}
        data_http_post_aaa_radius = {}
        data_http_post_aaa = {}
        err_http_post_sg = err_http_post_dot1x = err_http_post_rad = err_http_post_aaa = None

        if (
            self.__update_aaa_radius()
            and self.__update_aaa_corp_sg_profile()
            and self.__update_aaa_corp_dot1x_profile()
        ):
            self.__update_aaa_corp_profile()

        data_http_post_aaa_radius = \
            MMBuilder.mm_session_token.rad_server(data=self.__aaa_radius_data, config_path=self.__md_config_path)
        err_http_post_rad = data_http_post_aaa_radius[0]['_global_result']['status_str'] 
        data_http_post_sg_corp = \
            MMBuilder.mm_session_token.server_group_prof(data=self.__aaa_corp_sg_data, config_path=self.__md_config_path)
        err_http_post_sg = data_http_post_sg_corp[0]['_global_result']['status_str']
        data_http_post_dot1x_corp = \
            MMBuilder.mm_session_token.dot1x_auth_prof(data=self.__aaa_corp_dot1x_data, config_path=self.__md_config_path)
        err_http_post_dot1x = data_http_post_dot1x_corp[0]['_global_result']['status_str']
        data_http_post_aaa = \
            MMBuilder.mm_session_token.aaa_prof(data=self.__aaa_corp_data, config_path=self.__md_config_path)
        err_http_post_aaa = data_http_post_aaa[0]['_global_result']['status_str']
        return True if (err_http_post_aaa == 'Success'
            and err_http_post_dot1x == 'Success'
            and err_http_post_rad == 'Success'
            and err_http_post_sg == 'Success'
            ) else False, err_http_post_sg, err_http_post_rad, err_http_post_dot1x, err_http_post_aaa
            
    def __build_ssid_profile(self, **kwargs):
        """
        docstring
        """
        err_http_post = None

        if (kwargs['type']=='corp'):
            data_http_post_ssid_corp = {}
            self.__update_ssid_profile(type='corp')
            data_http_post_ssid_corp = \
                MMBuilder.mm_session_token.wlan_ssid_profile(data=self.__ssid_corp_data, config_path=self.__md_config_path)
            err_http_post = data_http_post_ssid_corp[0]['_global_result']['status_str']
        elif (kwargs['type']=='corp'):
            data_http_post_ssid_public = {}
            self.__update_ssid_profile(type='public')
            data_http_post_ssid_public = \
                MMBuilder.mm_session_token.wlan_ssid_profile(data=self.__ssid_public_data, config_path=self.__md_config_path)
            err_http_post = data_http_post_ssid_public[0]['_global_result']['status_str']
        if err_http_post == 'Success':
            return True
        else:
            return False, err_http_post

    def __build_vap_corp_profile(self):
        """
        docstring
        """
        data_http_post_vap_corp = {}
        err_http_post = None  
        
        if self.__build_ssid_profile(type='corp') and self.__build_aaa_corp_profile():    
            self.__vap_corp_data['profile-name'] = self.__vap_corp_profile_name
            self.__vap_corp_data['aaa_prof']['profile-name'] = self.__aaa_corp_profile_name
            self.__vap_corp_data['ssid_prof']['profile-name'] = self.__ssid_corp_profile_name
            data_http_post_vap_corp = \
                MMBuilder.mm_session_token.virtual_ap(data=self.__vap_corp_data, config_path=self.__md_config_path)
            err_http_post = data_http_post_vap_corp[0]['_global_result']['status_str']
        else:
            return False
        return True if ( err_http_post == 'Success') else False, err_http_post

    def __build_vap_public_profile(self):
        """
        docstring
        """
        data_http_post_vap_public = {}
        data_http_post_ssid_public = {}

        self.__update_ssid_profile(type='public')
        data_http_post_ssid_public = \
            MMBuilder.mm_session_token.wlan_ssid_profile(data=self.__ssid_public_data, config_path=self.__md_config_path)
        self.__vap_public_data['profile-name'] = self.__vap_public_profile_name
        self.__vap_public_data['ssid_prof']['profile-name'] = self.__ssid_public_profile_name
        if data_http_post_ssid_public[0]['_global_result']['status'] == 0:    
            data_http_post_vap_public = \
                MMBuilder.mm_session_token.virtual_ap(data=self.__vap_public_data, config_path=self.__md_config_path)
        else:
            return False,data_http_post_ssid_public[0]['_global_result']['status']
        return True if data_http_post_vap_public[0]['_global_result']['status'] == 0 else False

    def build_ap_group_profile(self):
        """
        docstring
        """
        if not MMBuilder.mm_session_token:
            raise NotImplementedError

        data_http_post_dot11a = {}
        data_http_post_dot11g = {}
        data_http_post_rd = {}
        data_http_post_ap_sys = {}
        data_http_post_ap_group = {}

        node_data = MMBuilder.mm_session_token.add_node_hierarchy(data=self.__md_config_data, config_path='/md')
        self.__update_radio_profiles()
        self.__update_ap_sys_profile()
        self.__update_rd_profile()

        self.__ap_group_data['profile-name'] = self.__ap_group_name
        self.__ap_group_data['dot11a_prof']['profile-name'] = self.__dot11a_radio_profile_name
        self.__ap_group_data['dot11g_prof']['profile-name'] = self.__dot11g_radio_profile_name
        self.__ap_group_data['virtual_ap'][0]['profile-name'] = self.__vap_corp_profile_name
        self.__ap_group_data['virtual_ap'][1]['profile-name'] = self.__vap_public_profile_name
        self.__ap_group_data['ap_sys_prof']['profile-name'] = self.__ap_sys_profile_name
        self.__ap_group_data['reg_domain_prof']['profile-name'] = self.__rd_profile_name

        if self.__md_config_path and node_data[0]['_global_result']['status_str'] == 'Success' :
            data_http_post_dot11a = \
                MMBuilder.mm_session_token.ap_a_radio_prof(data=self.__dot11a_data, config_path=self.__md_config_path)
            data_http_post_dot11g = \
                MMBuilder.mm_session_token.ap_g_radio_prof(data=self.__dot11g_data, config_path=self.__md_config_path)
            data_http_post_rd = \
                MMBuilder.mm_session_token.reg_domain_prof(data=self.__rd_data, config_path=self.__md_config_path)
            data_http_post_ap_sys = \
                MMBuilder.mm_session_token.ap_sys_prof(data=self.__ap_sys_data, config_path=self.__md_config_path)
        else:
            return False
        if (self.__md_config_path 
        and data_http_post_dot11a[0]['_global_result']['status'] == 0
        and data_http_post_dot11g[0]['_global_result']['status'] == 0
        and data_http_post_ap_sys[0]['_global_result']['status'] == 0
        and data_http_post_rd[0]['_global_result']['status'] == 0
        and self.__build_vap_corp_profile()
        ):
            data_http_post_ap_group = \
                MMBuilder.mm_session_token.ap_group(data=self.__ap_group_data,config_path=self.__md_config_path)
        return True if data_http_post_ap_group else False