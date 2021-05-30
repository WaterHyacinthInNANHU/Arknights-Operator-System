from PIL import Image
import config
from .common import *


class OCREngine(OcrEngine):
    def __init__(self, lang: str):
        super().__init__(lang)
        engine = config.get('ocr/engine')
        assert engine in ['baidu']  # TODO: add more engines
        if engine == 'baidu':
            from arknights.ocr.baidu import BaiduOCR
            self.engine = BaiduOCR(self.lang)

        #   TODO: add more engines

    def recognize(self, image: Image) -> OcrResult:
        return self.engine.recognize(image)

    # def baidu_ocr(self, image: Image) -> dict:
    #     client = AipOcr(self.app_id, self.app_key, self.app_secret)
    #     result = {}
    #
    #     # # debug
    #     # with open(resource, 'rb') as file:
    #     #     img = file.read()
    #     #     message = client.basicGeneral(img)  # 通用文字识别，每天 50 000 次免费
    #     # message = client.basicAccurate(img)   # 通用文字高精度识别，每天 800 次免费
    #
    #     target_bytes = self._pil_image_to_bytes(image)
    #     message = client.basicGeneral(target_bytes)
    #
    #     if len(message.get('words_result')) == 0:
    #         raise Exception("can't find any words")
    #     # return message.get('words_result')[0].get('words')
    #     for msg in message.get('words_result'):
    #         result[msg['words']] = msg['location']
    #     return result

