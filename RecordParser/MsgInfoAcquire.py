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
    """ 该类提供从文本中解析消息的功能,对接用于数据库存储记录 """

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
        self.msg_content = ""
        self.raw_record = raw_stream

    @staticmethod
    def escape_reverse(stream=str):
        """
        :param: stream 传入的记录板字符串字节流
        :return: 反转义后的原始记录字符串字节流,去掉头7E和尾7F
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
                raise ErrorEscapeException('ErrorEscapeException! 7E %s' % stream)
            else:
                pass
        if '7F' in ori_bytes_str:
            idx2 = ori_bytes_str.index('7F')
            # 字节流内部整字节不应出现‘7F’
            if idx2 % 2 == 0:
                raise ErrorEscapeException('ErrorEscapeException! 7F %s' % stream)
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
        """
        反转义并解析出消息头
        :return: 消息中的数据包列表
        """
        # 处理反转义
        self.msg_content = self.escape_reverse(self.raw_record)
        bs = BytesStream(self.msg_content)
        result = []
        for idx in range(len(self.msg_head_width)):
            result.append(bs.get_segment_by_index(bs.curBitsIndex, self.msg_head_width[idx]))
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

    def get_pkt_dic_from_record_msg(self):
        """

        :return: 消息中的数据包字典{包号:bit偏移}
        """
        pkt_dic = {}
        if self.msg_content:
            item = BytesStream(self.msg_content)
            bit_index_start = sum(self.msg_head_width)
            bit_index_end = len(item.hexStream)*4 - 1   # 十六进制字符串每4bit一个字符
            # 重置起始比特
            item.curBitsIndex = bit_index_start
            # 处理所有数据包
            while item.curBitsIndex <= bit_index_end:
                # 获取数据包
                pkt_id = item.get_segment_by_index(item.curBitsIndex, 8)
                pkt_len = item.get_segment_by_index(item.curBitsIndex, 13)
                if pkt_id in pkt_dic.keys():
                    print("Error:Exist the same pkt in msg !")
                else:
                    pkt_dic[pkt_id] = item.curBitsIndex - 21  # 21是每个包的包头 8+13
                    item.curBitsIndex = pkt_dic[pkt_id] + pkt_len

                # 考虑到一个数据包头至少有21bit
                if abs(item.curBitsIndex - bit_index_end) <= 21:
                    break
        else:
            print("Error:Reverse escape msg first !")

        return pkt_dic

    def get_atp_ato_dic_from_msg_pkt(self):
        """
        从记录板的原始通信数据包4（ATP->ATO）和5（ATO->ATP）中的消息（NID_STM=45）解析
        出来ATP-ATO通信的数据包信息
        :param pkt_offset: 在字节流中的比特偏移
        :return: 获取ATP-ATO数据包字典
        """
        atp_ato_dic = {}
        pkt_dic = {}
        pkt_len = 0
        if self.msg_content:
            item = BytesStream(self.msg_content)
            # 先解析原始记录消息
            pkt_dic = self.get_pkt_dic_from_record_msg()
            # 检查是否有ATP-ATO通信消息
            if 3 in pkt_dic.keys():
                # 处理消息45
                bit_index_start = pkt_dic[3] + 21  # 跳过记录包协议头，起点指向ATP-ATO原始消息
                bit_len = item.get_segment_by_index(bit_index_start + 24, 13)  # 先抽取ATP-ATO子包比特长度（不含消息结构）
                print('bit_len %d'%bit_len)
                bit_index_start = bit_index_start + 37  # 起点指向ATP-ATO子包数据头，ATP-ATO消息头尾37bit(8+8+8+13)
                bit_index_end = bit_index_start + bit_len  # 终点指向ATP-ATO自包尾

                while bit_index_start <= bit_index_end:

                    # 获取ATP-ATO数据包
                    pkt_id = item.get_segment_by_index(bit_index_start, 8)
                    if pkt_id == 0:
                        atp_ato_dic[pkt_id] = bit_index_start
                        pkt_len = ATPInfPktProcess.get_sp0_len(bit_index_start, self.msg_content)
                    elif pkt_id == 1:
                        atp_ato_dic[pkt_id] = bit_index_start
                        pkt_len = ATPInfPktProcess.get_sp1_len(bit_index_start, self.msg_content)
                    elif pkt_id == 2:
                        atp_ato_dic[pkt_id] = bit_index_start
                        pkt_len = ATPInfPktProcess.get_sp2_len()
                    elif pkt_id == 3:
                        atp_ato_dic[pkt_id] = bit_index_start
                        pkt_len = ATPInfPktProcess.get_sp3_len()
                    elif pkt_id == 4:
                        atp_ato_dic[pkt_id] = bit_index_start
                        pkt_len = ATPInfPktProcess.get_sp4_len()
                    elif pkt_id == 5:
                        atp_ato_dic[pkt_id] = bit_index_start
                        pkt_len = ATPInfPktProcess.get_sp5_len()
                    elif pkt_id == 6:
                        atp_ato_dic[pkt_id] = bit_index_start
                        pkt_len = ATPInfPktProcess.get_sp6_len()
                    elif pkt_id == 7:
                        atp_ato_dic[pkt_id] = bit_index_start
                        pkt_len = ATPInfPktProcess.get_sp7_len(bit_index_start, self.msg_content)
                    elif pkt_id == 8:
                        atp_ato_dic[pkt_id] = bit_index_start
                        ATPInfPktProcess.get_sp5_len()
                    elif pkt_id == 9:
                        atp_ato_dic[pkt_id] = bit_index_start
                        pkt_len = ATPInfPktProcess.get_sp9_len(bit_index_start, self.msg_content)

                    # 使用计算的长度更新偏移量
                    bit_index_start = bit_index_start + pkt_len
        else:
            print("Error:Reverse escape msg first !")

        return atp_ato_dic

class ATPInfPktProcess(object):
    def __init__(self):
        pass

    @staticmethod
    def get_sp0_len(bit_offset=int, stream=str):
        """
        由于sp0是不定长度的包，所以需要传入数据进行解析才能确定
        :param bit_offset: 是ATP-ATO数据包在记录消息中的偏移量，也就是CRSCD_GT_ATO_W_4056中的4包，5包比特偏移
        :param stream: 记录消息字节流字符串
        :return: SP0包的长度
        """
        item = BytesStream(stream)
        sp0_width_list_p1 = [8, 13, 2, 24, 15, 2, 2, 15, 15]
        ctrl_width = 2
        var_width = 15
        sp0_width_list_p2 = [7, 2, 4]

        ctrl_width_2 = 3
        var_width_2 = 8

        l_sp0 = sum(sp0_width_list_p1) + ctrl_width + ctrl_width_2 + sum(sp0_width_list_p2)

        ctrl_info = item.get_segment_by_index(bit_offset+sum(sp0_width_list_p1), ctrl_width)
        # 列车完整性保障
        if ctrl_info == 1 or ctrl_info == 2:
            l_sp0 = l_sp0 + var_width
        else:
            pass
        ctrl_info = item.get_segment_by_index(l_sp0, ctrl_width_2)
        # 等级
        if ctrl_info == 1:
            l_sp0 = l_sp0 + var_width_2
        else:
            pass
        return l_sp0

    @staticmethod
    def get_sp1_len(bit_offset=int, stream=str):
        """
        由于sp1是不定长度的包，所以需要传入数据进行解析才能确定
        :param bit_offset: 是ATP-ATO数据包在记录消息中的偏移量，也就是CRSCD_GT_ATO_W_4056中的4包，5包比特偏移
        :param stream: 记录消息字节流字符串
        :return: SP1包的长度
        """
        item = BytesStream(stream)
        sp1_width_list_p1 = [8, 13, 2, 24, 24, 15, 2, 2, 15, 15]
        ctrl_width = 2
        var_width = 15
        sp1_width_list_p2 = [7, 2, 4]

        ctrl_width_2 = 3
        var_width_2 = 8

        l_sp1 = sum(sp1_width_list_p1) + ctrl_width + sum(sp1_width_list_p2)

        ctrl_info = item.get_segment_by_index(bit_offset + sum(sp1_width_list_p1), ctrl_width)
        # 列车完整性保障
        if ctrl_info == 1 or ctrl_info == 2:
            l_sp1 = l_sp1 + var_width
        else:
            pass

        ctrl_info = item.get_segment_by_index(l_sp1, ctrl_width_2)
        # 等级
        if ctrl_info == 1:
            l_sp1 = l_sp1 + var_width_2
        else:
            pass

        return l_sp1

    @staticmethod
    def get_sp2_len():
        """
        sp2固定长度的包
        :return: SP2包的长度
        """
        sp2_width_list = [8, 2, 2, 2, 2, 2, 2, 16, 32, 3, 4, 32, 16, 16, 2, 16, 8, 4, 16, 32, 32, 32, 32, 2, 32, 2, 2]
        return sum(sp2_width_list)

    @staticmethod
    def get_sp3_len():
        """
        sp3固定长度的包
        :return: SP3包的长度
        """
        sp3_width_list = [8, 32]
        return sum(sp3_width_list)

    @staticmethod
    def get_sp4_len():
        """
        sp4固定长度的包
        :return: SP4包的长度
        """
        sp4_width_list = [8, 16, 32]
        return sum(sp4_width_list)

    @staticmethod
    def get_sp5_len():
        """
        sp5固定长度的包
        :return: SP5包的长度
        """
        sp5_width_list = [8, 8, 32, 32, 8, 16, 16, 16, 16, 24, 4]
        return sum(sp5_width_list)

    @staticmethod
    def get_sp6_len():
        """
        sp6固定长度的包
        :return: SP6包的长度
        """
        sp6_width_list = [8, 8, 8, 8, 8, 8, 8]
        return sum(sp6_width_list)

    @staticmethod
    def get_sp7_len(bit_offset=int, stream=str):
        """
        由于sp7是不定长度的包，所以需要传入数据进行解析才能确定
        :param bit_offset: 是ATP-ATO数据包在记录消息中的偏移量，也就是CRSCD_GT_ATO_W_4056中的4包，5包比特偏移
        :param stream: 记录消息字节流字符串
        :return: SP7包的长度
        """
        item = BytesStream(stream)
        sp7_width_list_p1 = [8, 24, 32, 32]
        ctrl_width = 9
        var_width_list = [2, 2, 2, 24, 15]

        l_sp7 = sum(sp7_width_list_p1) + ctrl_width

        ctrl_info = item.get_segment_by_index(bit_offset + sum(sp7_width_list_p1), ctrl_width)
        # 如果有C13包还包括后续长度
        if ctrl_info == 13:
            l_sp7 = l_sp7 + sum(var_width_list)
        else:
            pass
        return l_sp7

    @staticmethod
    def get_sp8_len():
        """
        sp8固定长度的包
        :return: SP8包的长度
        """
        sp8_width_list = [8, 1, 10, 14, 64, 1, 3]
        return sum(sp8_width_list)

    @staticmethod
    def get_sp9_len(bit_offset=int, stream=str):
        """
        由于sp9是不定长度的包，所以需要传入数据进行解析才能确定
        :param bit_offset: 是ATP-ATO数据包在记录消息中的偏移量，也就是CRSCD_GT_ATO_W_4056中的4包，5包比特偏移
        :param stream: 记录消息字节流字符串
        :return: SP9包的长度
        """
        item = BytesStream(stream)
        sp9_width_list_p1 = [8]
        ctrl_width = 5
        var_width_list = [32, 32, 4]

        l_sp9 = sum(sp9_width_list_p1) + ctrl_width

        ctrl_info = item.get_segment_by_index(bit_offset + sum(sp9_width_list_p1), ctrl_width)
        # 如果有隧道
        if ctrl_info != 0:
            l_sp9 = l_sp9 + sum(var_width_list)*ctrl_info
        else:
            pass
        return l_sp9

