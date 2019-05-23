from RecordParser.CommonParse import BytesStream


class ErrorEscapeException(Exception):
    """This Exception is use for escape err"""
    def __init__(self, err='Record msg escape err!'):
        super(__class__, self).__init__(err)


class ErrorHexStreamException(Exception):
    """This Exception is use for err hex stream"""
    def __init__(self, err='Record msg hex stream illegal!'):
        super(__class__, self).__init__(err)


class MsgProcess(object):
    """ 该类提供从文本中解析消息的功能"""

    msg_head_width = [8, 10, 2, 1, 32, 32, 32, 32, 16, 3]

    def __init__(self, raw_stream=str):
        self.t_atoutc = 0
        self.n_cycle = 0
        self.nid_modle = 0
        self.q_standby = 0
        self.t_ato = 0
        self.m_pos = 0
        self.v_speed = 0
        self.m_atomode = 0
        self.l_message = 0
        self.msg_content = raw_stream

    @staticmethod
    def escape_reverse(stream=str):
        """
        :param: stream 传入的记录板字符串字节流
        :return: 反转义后的字符串字节流,去掉头尾
        """
        # 当传入字节流非法，不是整字节个
        if len(stream) % 2 != 0:
            print(stream)
            raise ErrorHexStreamException()

        # 获取实际数据
        ori_bytes_str = stream[2:(len(stream)-2)]

        # 检查数据头尾是否为转义帧
        if stream[0:2] == '7E' and stream[-2:] == '7F':
            pass
        else:
            raise ErrorEscapeException('ErrorEscapeException! %s' % stream)

        # 检查字节流转义情况
        if '7E' in ori_bytes_str:
            idx1 = ori_bytes_str.index('7E')
            # 字节流内部整字节不应出现‘7E’
            if idx1 % 2 == 0:
                raise ErrorEscapeException('ErrorEscapeException! %s' % stream)
            else:
                pass
        if '7F' in ori_bytes_str:
            idx2 = ori_bytes_str.index('7F')
            # 字节流内部整字节不应出现‘7F’
            if idx2 % 2 == 0:
                raise ErrorEscapeException('ErrorEscapeException! %s' % stream)
            else:
                pass

        # 遍历内部数据反转义
        for idx in range(0, len(ori_bytes_str), 2):
            tmp = ori_bytes_str[idx:idx+2]
            if '7D' == tmp:
                ori_bytes_str = ori_bytes_str[:idx+1] + ori_bytes_str[idx+3:]
            else:
                pass
        return ori_bytes_str

    def msg_head_process(self):
        # 处理反转义
        self.msg_content = self.escape_reverse(self.msg_content)
        bs = BytesStream(self.msg_content)
        result = []
        for idx in range(len(self.msg_head_width)):
            result.append(bs.getSegmentByIndex(bs.curBitsIndex, self.msg_head_width[idx]))
        # update
        self.t_atoutc = result[6]
        self.n_cycle = result[4]
        self.nid_modle = result[2]
        self.q_standby = result[3]
        self.t_ato = result[5]
        self.m_pos = result[7]
        self.v_speed = result[8]
        self.m_atomode = result[9]
        self.l_message = result[1]
