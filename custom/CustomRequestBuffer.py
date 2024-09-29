from feapder.buffer.request_buffer import RequestBuffer

from feapder.utils.log import log
from feapder.utils import tools
class CustomRequestBufferNoEffort(RequestBuffer):
    def __init__(self, redis_key):
        super(CustomRequestBufferNoEffort, self).__init__(redis_key)


    def is_exist_request(self, request):
        '''
        在request白名单中不需要去重，否则全部去重
        :param request: 在
        :return:
        '''
        import feapder.setting as setting
        white_list = request.white_list or []
        for white in white_list:
            if white in request.url:
                return False

        if (
                request.filter_repeat
                and setting.REQUEST_FILTER_ENABLE
                and not self.__class__.dedup.add(request.fingerprint)
        ):
            log.debug("request已存在  url = %s" % request.url)
            return True
        return False

