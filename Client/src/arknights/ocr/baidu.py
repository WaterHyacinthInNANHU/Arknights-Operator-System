import base64
import time
from io import BytesIO
import requests
import config
from arknights.ocr.common import *
from PIL import Image

info = "baidu"
token_outdated = 2592000  # 1 month
token_timestamp = time.monotonic()

API_KEY = config.get('ocr/baidu_api/app_key', None)
SECRET_KEY = config.get('ocr/baidu_api/app_secret', None)


def _options(option):
    options = {}
    subtags = option.lower().split('-')
    if subtags[0] == 'en':
        options["language_type"] = "ENG"
    elif subtags[0] == 'zh':
        options["language_type"] = "CHN_ENG"
    return options


def _get_token():
    t = time.monotonic()
    tdiff = t - _get_token.last_time
    _get_token.last_time = t
    if tdiff == t or tdiff >= token_outdated:
        resp = requests.request('POST', 'https://aip.baidubce.com/oauth/2.0/token',
                                params={'grant_type': 'client_credentials', 'client_id': API_KEY,
                                        'client_secret': SECRET_KEY})
        resp.raise_for_status()  # raise exceptions if bad request
        resp = resp.json()
        res = resp['access_token']
        _get_token.cached_token = res
        return res
    else:
        return _get_token.cached_token


_get_token.last_time = 0
_get_token.cached_token = None


def _basic_general(image, options):
    data = {'image': base64.b64encode(image).decode()}
    data.update(options)
    t = time.monotonic()
    tdiff = t - _basic_general.last_call
    if tdiff < 0.4:
        # QPS limit
        time.sleep(0.4 - tdiff)
    resp = requests.post('https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic', data=data,
                         params={'access_token': _get_token()})
    resp.raise_for_status()
    resp = resp.json()
    if 'error_code' in resp:
        raise RuntimeError(resp['error_msg'])
    _basic_general.last_call = time.monotonic()
    return resp


_basic_general.last_call = 0


class BaiduOCR(OcrEngine):
    def recognize(self, image: Image) -> OcrResult:
        imgbytesio = BytesIO()
        if image.mode != 'RGB':
            image = image.convert('RGB')
        image.save(imgbytesio, format='JPEG', quality=95)
        result = _basic_general(imgbytesio.getvalue(), _options(self.lang))
        line = OcrLine([OcrWord(Rect(0, 0), x['words']) for x in result['words_result']])
        result = OcrResult([line])
        return result
