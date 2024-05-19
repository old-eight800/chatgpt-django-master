"""
Request工具类
"""
from loguru import logger
import requests


def get_request_ip(request):
    """
    获取请求IP
    :param request:
    :return:
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
        return ip
    ip = request.META.get('REMOTE_ADDR', '') or getattr(request, 'request_ip', None)
    return ip or 'unknown'


def get_ip_analysis(ip):
    """
    获取ip详细概略
    :param ip: ip地址
    :return:
    """
    data = {
        "continent": "",
        "country": "",
        "province": "",
        "city": "",
        "district": "",
        "isp": "",
        "area_code": "",
        "country_english": "",
        "country_code": "",
        "longitude": "",
        "latitude": ""
    }
    if ip != 'unknown' and ip:
      try:
          res = requests.get(url='https://ip.django-vue-admin.com/ip/analysis', params={"ip": ip}, timeout=5)
          if res.status_code == 200:
              res_data = res.json()
              if res_data.get('code') == 0:
                  data = res_data.get('data')
          return data
      except Exception as e:
          logger.error(e)
    return data

