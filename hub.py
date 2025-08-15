import hashlib
import json
import logging
from datetime import timedelta, datetime
from typing import Any

from aiohttp import ContentTypeError

from .const import DOMAIN, BASE_URL
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import async_track_time_interval

_LOGGER = logging.getLogger(__name__)


def md5_hash(password: str):
    """Return an MD5 hash for the given password."""
    # 创建一个md5哈希对象
    hasher = hashlib.md5()
    # 更新哈希对象以添加待哈希的密码字符串, 需要先将字符串编码为字节
    hasher.update(password.encode('utf-8'))

    # 获取十六进制表示的哈希值
    return hasher.hexdigest()
langs = {
        'zh-hans': 'zh-CN',
        'zh-hant': 'zh-HK',
        # ar_QA
        'ar': 'ar-QA',
        # de_DE
        'de': 'de-DE',
        # en_US
        'en': 'en-US',
        # es_ES
        'es': 'es-ES',
        # fr_FR
        'fr': 'fr-FR',
        # it_IT
        'it': 'it-IT',
        # nl_NL
        'nl': 'nl-NL',
        # ru_RU
        'ru': 'ru-RU',
        # th_TH
        'th': 'th-TH',
        # vi_VN
        'vi': 'vi-VN'
    }

class MyIntegrationHub:
    def __init__(self, hass, username, password, senceId):

        self._entities = []
        self.senceId = senceId
        self.hass = hass
        self.devices_info: dict[str, list[Any]] = {}
        self._username = username
        self._password = password
        self._session = async_get_clientsession(self.hass)  # 存储登录后的会话
        self._unsub_polling = None  # 存储定时器取消函数
        self._unsub_login = None
        self.total_data = {}
        self.device_data: dict[str, Any] = {}
        self.plants = []
        self.home_control_devices=[]
        self.cur_ctl_devices = None
        self.lang=langs[hass.config.language.lower()]
        _LOGGER.error(f'lang : {self.lang}')
        if self.lang is None:
            self.lang='en-US'

    async def login(self, now=None):
        # 重新登录 并启动轮询
        """执行登录操作"""
        _LOGGER.warning("开始登录")
        await self._login(self._username, self._password)
        # 登录成功后启动轮询
        # await self.start_polling()

    async def _login(self, username, password):
        # 实现登录逻辑
        url = BASE_URL + "/user/login"
        self._session = async_get_clientsession(self.hass)
        headers = {'Content-Type': 'application/json'}
        hash_pwd = md5_hash(password)
        req = {"email": username, "password": hash_pwd, "phoneOs": 1, "phoneModel": "1.1", "appVersion": "V1.1"}
        json_data = json.dumps(req)
        resp = await self.post(headers, url, json_data)
        _LOGGER.info(f"登录响应：{resp}")
        if resp['result'] == 1:
            return True
        return False

    async def start_polling(self):
        """启动定时轮询"""
        # 先取消已有轮询（如果存在）
        await self.stop_polling()

        # 设置轮询间隔（示例：每15秒）
        update_interval = timedelta(seconds      =10)

        # 注册定时任务
        self._unsub_polling = async_track_time_interval(
            self.hass,
            self.async_update_data,  # 更新数据的回调函数
            update_interval
        )

        # 立即执行首次更新
        await self.async_update_data()

    async def stop_polling(self):
        """停止轮询"""
        if self._unsub_polling:
            self._unsub_polling()
            self._unsub_polling = None

    async def start_schedule_login(self):
        """启动定时轮询"""
        # 先取消已有轮询（如果存在）
        await self.stop_schedule_login()
        # 设置轮询间隔
        update_interval = timedelta(hours=8)
        # 注册定时任务
        self._unsub_login = async_track_time_interval(
            self.hass,
            self.login,  # 更新数据的回调函数
            update_interval
        )

    async def stop_schedule_login(self):
        """停止轮询"""
        if self._unsub_login:
            self._unsub_login()
            self._unsub_login = None

    def add_entity(self, entity):
        """添加需要更新的实体"""
        self._entities.append(entity)

    async def async_update_data(self, now=None):
        """执行数据更新操作"""
        _LOGGER.debug("开始更新数据")
        start_time = datetime.now()
        try:
            # 更新主页数据
            await self.getPlantVos()
            await self.get_home_control_devices()
            new_data = await self.getHomeCountData(self.cur_ctl_devices)
            devices_manager = self.hass.data[DOMAIN]['device_manager']
            # 按设备sn请求设备详细数据
            for device in devices_manager.devices:
                if device.type != -1:
                    _LOGGER.debug(f"开始更新设备：{device.type},{device.device_sn}")
                    res = await self.fetch_device_info(device.type, device.device_sn)
                    _LOGGER.debug(f"获取到设备信息：{res}")
                    # if res and res["datalogSn"]==device.device_sn:
                    self.devices_info[device.device_sn] = res["displayMap"]
            if new_data:
                # 更新设备所有关联实体
                # 检测更新用时 获取当前时间
                ai = await self.getAiSystemByPlantId()
                for entity in self._entities:
                    entity.update_data(new_data, self.devices_info, ai)

        except Exception as e:
            _LOGGER.error(f"发生异常的行号是: {e.__traceback__.tb_lineno}, 异常信息: {e}")
        end_time = datetime.now()
        _LOGGER.info(f"更新数据getHomeCountData完成，耗时：{end_time - start_time}")

    async def getHomeCountData(self, sn=""):
        url = BASE_URL + "/energy/getHomeCountData"
        resp = await self.post({}, url, params={
            "plantId": self.senceId,
            "deviceSn":sn
        })
        _LOGGER.info(f"获取到能流数据：{resp}")
        res = resp['obj']
        _LOGGER.debug(res)
        self.total_data = res
        return res

    # 获取用户下所有电站
    async def getPlantVos(self):
        url = BASE_URL + "/plant/getPlantVos"
        resp = await self.get({}, url, {})
        _LOGGER.debug(f"<UNK>{resp}")
        res = resp['obj']
        # _LOGGER.info(res)
        self.plants = res
        return res

    # AI能流详情
    async def getAiSystemByPlantId(self):
        # _LOGGER.info(self._session)
        url = BASE_URL + "/aiSystem/getAiSystemByPlantId"
        resp = await self.get({}, url, params={
            "plantId": self.senceId
        })
        _LOGGER.debug(f"ai模式响应：{resp}")
        res = resp['obj']
        _LOGGER.debug(f"res:{res}")
        return res

    # 获取设备数据详情
    async def fetch_device_info(self, device_type, device_sn):
        # _LOGGER.info(self._session)
        url = BASE_URL + "/device/getDeviceBySn"
        # 获取当前日期的yyyy-MM-dd格式字符串
        a = datetime.now().strftime("%Y-%m-%d")
        resp = await self.post({}, url, params={
            'deviceType': device_type,
            'time': a,
            'sn': device_sn,
        })
        _LOGGER.debug(f"设备数据详情响应：{resp}")
        res = resp['obj']
        _LOGGER.debug(res['chartMap'])
        if res is not None:
            # 置空
            res['chartMap'] = None
        # _LOGGER.debug(res)
        self.device_data[device_sn] = res
        return res

    # 开关
    async def switch_socket(self, sn, v):
        # _LOGGER.info(self._session)
        url = BASE_URL + "/device/setDeviceParam"
        resp = await self.post({'Content-Type': 'application/x-www-form-urlencoded'}, url, {
            'deviceSn': sn,
            'startAddr': 0x0000,
            'data': v,
        })
        _LOGGER.info(f"下发开关设置响应：{resp}")
        res = resp['msg']
        # _LOGGER.info(res)
        return res

    # 开关
    async def switch_charger(self, sn, v):
        url = BASE_URL + "/device/setDeviceParam"
        resp = await self.post({'Content-Type': 'application/x-www-form-urlencoded'}, url, {
            'deviceSn': sn,
            'startAddr': 0x00AF,
            'data': v,
        })
        _LOGGER.info(f"下发开关设置响应：{resp}")
        res = resp['msg']
        # _LOGGER.info(res)
        return res

    # 开关
    async def switch_product(self, sn, v):
        url = BASE_URL + "/energyProduct/setEnergyProductSwitch"
        resp = await self.post({}, url, params={
            "deviceSn": sn,
            "switchStatus": v
        })
        _LOGGER.info(f"下发开关设置响应：{resp}")
        res = resp['msg']
        # _LOGGER.info(res)
        return res

    # 电站日统计数据
    async def get_energy_data_day(self, plant_id, sn=""):
        url = BASE_URL + "/energy/getEnergyDataDay"
        a = datetime.now().strftime("%Y-%m-%d")
        resp = await self.post({}, url, params={
            'plantId':plant_id,
            'time': a,
            "deviceSn": sn
        })
        res = resp['obj']
        # _LOGGER.info(res)
        return res

    # 电站月统计数据
    async def get_energy_data_month(self, plant_id, sn=""):
        url = BASE_URL + "/energy/getEnergyDataMonth"
        a = datetime.now().strftime("%Y-%m")
        resp = await self.post({}, url, params={
            'plantId':plant_id,
            'time': a,
            "deviceSn": sn
        })
        res = resp['obj']
        # _LOGGER.info(res)
        return res
    # 电站年统计数据
    async def get_energy_data_year(self, plant_id, sn=""):
        url = BASE_URL + "/energy/getEnergyDataYear"
        a = datetime.now().strftime("%Y")
        resp = await self.post({}, url, params={
            'plantId':plant_id,
            'time': a,
            "deviceSn": sn
        })
        res = resp['obj']
        # _LOGGER.info(res)
        return res
    # 电站总计数据
    async def get_energy_data_total(self, plant_id, sn=""):
        url = BASE_URL + "/energy/getEnergyDataTotal"
        a = datetime.now().strftime("%Y")
        resp = await self.post({}, url, params={
            'plantId':plant_id,
            'time': a,
            "deviceSn": sn
        })
        res = resp['obj']
        # _LOGGER.info(res)
        return res
    async def get_home_control_devices(self):
        url = BASE_URL + "/energy/getHomeControlSn/"+self.senceId
        resp = await self.get({}, url)
        res = resp['obj']
        _LOGGER.info(res)
        self.home_control_devices=res
        self.cur_ctl_devices=res[0]['deviceSn']
        return res

    # 通用POST请求
    async def post(self, headers, url, data=None, params=None):
        # headers['Accept-Language'] =self.
        headers["Accept-Language"] = "en-US"
        async with self._session.post(url, headers=headers, params=params, data=data) as resp:
            if resp.status == 200:
                self._session.cookie_jar.update_cookies(resp.cookies)
                try:
                    resp_data = await resp.json()
                except json.JSONDecodeError:
                    resp_data = await resp.text()
                    _LOGGER.warning(resp_data)
                except ContentTypeError:
                    resp_data = await resp.text()
                    _LOGGER.warning(resp_data)
                if "请登录" in resp_data.values() or "Please login" in resp_data.values() or resp_data.get(
                        "result") == "10000":
                    _LOGGER.warning("需要登录")
                    await self.login()
                    return None
                return resp_data
            else:
                raise Exception(f"Failed to fetch data from {url}")

        # 通用Get请求

    # 通用GET请求
    async def get(self, headers, url, data=None, params=None):
        # headers['Accept-Language'] =self.lang
        headers['Accept-Language'] ='en-US'
        async with self._session.get(url, headers=headers, params=params, data=data) as resp:
            if resp.status == 200:
                self._session.cookie_jar.update_cookies(resp.cookies)
                try:
                    resp_data = await resp.json()
                except json.JSONDecodeError:
                    resp_data = await resp.text()
                if "请登录" in resp_data.values() or "Please login" in resp_data.values() or resp_data.get(
                        "result") == "10000":
                    _LOGGER.warning("需要登录")
                    _LOGGER.warning(resp_data)
                    await self.login()
                    return None
                return resp_data
            else:
                raise Exception(f"Failed to fetch data from {url}")

    # Battery Control API Methods
    async def set_ai_system_energy_mode(self, payload: dict):
        """Set AI system energy mode for battery control."""
        url = BASE_URL + "/aiSystem/setAiSystemTimesWithEnergyMode"
        
        # Use the existing authenticated session via post() method
        headers = {
            "Content-Type": "application/json;charset=UTF-8",
            "Accept": "application/json",
            "User-Agent": "okhttp/4.10.0"
        }
        
        # Convert payload to JSON string for data parameter
        import json
        json_data = json.dumps(payload)
        
        try:
            result = await self.post(headers, url, data=json_data)
            if result and result.get("result") == 0:
                _LOGGER.info(f"Successfully set AI system energy mode")
                return result
            elif result:
                _LOGGER.error(f"Failed to set AI system energy mode: {result.get('msg', 'Unknown error')}")
                raise Exception(f"API error: {result.get('msg', 'Unknown error')}")
            else:
                raise Exception("No response from API")
        except Exception as e:
            _LOGGER.error(f"Exception in set_ai_system_energy_mode: {e}")
            raise

    async def set_device_parameter(self, param_name: str, param_value: str):
        """Set a single device parameter using the existing authentication."""
        # Note: This method may require additional API credentials (companyCode, API key)
        # that are not available in the current config flow.
        # For now, we'll focus on the setAiSystemTimesWithEnergyMode API
        # which appears to work with the existing session authentication.
        
        _LOGGER.warning(f"set_device_parameter not yet implemented for {param_name}={param_value}")
        _LOGGER.warning("This requires additional API credentials not available in config flow")
        raise NotImplementedError("Device parameter setting requires additional API setup")
