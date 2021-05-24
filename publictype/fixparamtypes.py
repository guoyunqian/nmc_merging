#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: fixparamtypes.py

'''
Created on Aug 21, 2020

@author: anduin
'''

from enum import Enum
class FixParamTypes(Enum):
    DT = 'dt'                          #datetime的时间
    DTS = 'dts'                        #datetime的时间列表
    DTInfos = 'dt_infos'               #datetime的时间列表，
    STime = 'stime'                    #补数据开始时间，datetime
    ETime = 'etime'                    #补数据结束时间，不包含该时间，datetime
    TNum = 't_num'                     #需要处理的小时数
    
    FHS = 'fhs'                        #需要数据的时间的小时数值列表，可以用range生成
    FHS_OBS = 'fhs_obs'                #需要数据的时间的小时数值列表，可以用range生成
    FMS = 'fms'                        #需要数据的时间的分钟数值列表，可以用range生成
    FMS_OBS = 'fms_obs'                #需要数据的时间的分钟数值列表，可以用range生成
    SFHS = 's_fhs'
    SFHSs = 's_fhs_s'
    DFHS = 'd_fhs'
    DFHSs = 'd_fhs_s'
    
    TZ_Delta = 'tz_delta'              #间隔，单位是小时，用于确定保存文件名时的时差
    Deltas = 'deltas'                  #多数据处理时，源数据对应的时间，与目的数据的时间差，负值代表源数据时间在前，正值是在后，分钟为单位
    FDelta = 'f_delta'                 #用来判断#文件存在时是否需要更新，文件修改时间大于dt加该间隔，不需要更新文件，否则需要更新。值为None，不需要更新。dt是世界时，则该间隔包含时差
    
    SFDelta = 's_f_delta'              #确定文件生成时间与文件时效时间的差值
    SFDeltas = 's_f_deltas'
    DFDelta = 'd_f_delta'
    DFDeltas = 'd_f_deltas'

    FhsDelta = 'fhs_delta'             #起报时的间隔
    SFhsDelta = 's_fhs_delta'          #确定提前生成/使用新的时效的文件的差值
    SFhsDeltas = 's_fhs_deltas'
    DFhsDelta = 'd_fhs_delta'
    DFhsDeltas = 'd_fhs_deltas'

    RangeDelta = 'range_delta'         #用于处理时间段时的时间间隔，比如确定时间的间隔，cmadaas的timeRange
    RangeDelta_OBS = 'range_delta_obs' #用于处理时间段时的时间间隔，比如确定时间的间隔
    
    SIsBJT = 's_is_bjt'                #需要处理的数据是否是北京时间，如果是False，则是utc时间
    DIsBJT = 'd_is_bjt'                #需要保存的数据是否是北京时间，如果是False，则是utc时间

    SeqObj = 'seqobj'                  #预报时效的序列，可以是列表，可以用range生成，扩展成可以描述文件序列，比如站点名称BJ
    SSeq = 's_seq'
    SSeqs = 's_seq_s'
    DSeq = 'd_seq'
    DSeqs = 'd_seq_s'

    SeqFmt = 'seqfmt'                  #SeqObj中数据在文件名中的格式，预报时效可以['FFF', '%03d']，站点可以[['XX', '%02s'], ['XX', '%02s']]
    SSeqFmt = 's_seq_fmt'              #SeqObj中数据在源文件名中的格式，预报时效可以['FFF', '%03d']，站点可以['XX', '%02s']
    SSeqFmts = 's_seq_fmts'
    DSeqFmt = 'd_seq_fmt'              #SeqObj中数据在目标文件名中的格式，预报时效可以['FFF', '%03d']，站点可以['XX', '%02s']
    DSeqFmts = 'd_seq_fmts'

    SeqNum = 'seqnum'                  #预报时效值
    SeqNums = 'seqnums'                #多个预报时效值，列表
    SeqCount = 'seq_count'             #预报时效数
    SeqCounts = 'seq_counts'           #多个预报时效数
    
    SeqField = 'seq_field'             #seq对应的字段

    #perturbationNumber
    PNumObj = 'p_num_obj'              #扰动场，可以用range生成，或者是列表
    PNumFmt = 'p_num_fmt'              #扰动场数值在文件中的格式，['PPP', '%03d']或者[['PPP', '%03d'],['PPP', '%03d']]
    SPNumFmt = 's_p_num_fmt'           #扰动场数值在源文件中的格式，['PPP', '%03d']
    DPNumFmt = 'd_p_num_fmt'           #扰动场数值在目标文件中的格式，['PPP', '%03d']
    PNum = 'p_num'                     #扰动场数值
    PNums = 'p_nums'                   #多个扰动场数值
    PNumCount = 'p_num_count'          #扰动场数量
    PNumCounts = 'p_num_counts'        #多个扰动场数量

    PNumField = 'p_num_field'          #扰动场对应的字段

    SeqAndPNum = 'seq_and_p_num'       #包含seq和pnum信息的字符串，格式为pnum_seq，可以没有pnum，值为seq
    SeqKeyIsNum = 'seq_key_is_num'     #字典中seq为key时，True代表保持seq为数值，False代表seq需要转换成字符串

    SDict = 's_dict'                   #源文件的目录
    SDicts = 's_dicts'                 #多个源文件的目录
    DDict = 'd_dict'                   #目标文件的目录
    DDicts = 'd_dicts'                 #多个目标文件的目录
    TDict = 't_dict'                   #临时文件的目录
    SFnFmt = 's_fn_fmt'                #源文件文件名的格式
    SFnFmts = 's_fn_fmts'              #多个源文件文件名的格式
    DFnFmt = 'd_fn_fmt'                #目标文件文件名的格式
    DFnFmts = 'd_fn_fmts'              #多个目标文件文件名的格式
    
    DTFmt = 'dt_fmt'                   #文件名称中时间的格式
    SDTFmt = 's_dt_fmt'                #源文件名称中时间的格式
    SDTFmts = 's_dt_fmts'              #多个源文件名称中时间的格式
    DDTFmt = 'd_dt_fmt'                #源文件名称中时间的格式
    DDTFmts = 'd_dt_fmts'              #多个源文件名称中时间的格式
    DTFmtObs = 'dt_fmt_obs'            #实况文件名称中时间的格式
    DTFmtFix = 'dt_fmt_fix'            #源文件名称中时间的格式
    DTFmtSave = 'dt_fmt_save'          #目标文件名称中时间的格式
    
    SFullPath = 's_full_path'          #源文件全路径
    SFullPaths = 's_full_paths'        #多个源文件全路径
    DFullPath = 'd_full_path'          #目标文件全路径
    DFullPaths = 'd_full_paths'        #多个目标文件全路径
    SPathExist = 's_path_exist'        #判断源文件路径是否存在
    DPathExist = 'd_path_exist'        #判断目标文件路径是否存在
    MaskFile = 'mask_file'             #格点数据的mask文件
    
    DType = 'dtype'                    #数据的类型
    S_DType = 's_dtype'                #数据类型转换时，数据初始类型
    D_DType = 'd_dtype'                #数据类型转换时，数据要转换成的类型
    SName = 'sname'                    #进行数据类型转换的数据名称，改数据名称时的源名称
    Columns = 'columns'                #数据列名称列表
    Values = 'values'                  #数据列值的列表
    Conditions = 'conditions'          #比较条件
    KeepAttrs = 'keep_attrs'           #进行数据类型转换时是否保存Attributes
    DName = 'dname'                    #pandas.DataFrame.to_hdf,Identifier for the group in the store，nc中的数据名称，改数据名称时的目的名称
    Multi = 'multi'                    #数据需要乘的数，用于单位转换
    GridData = 'grid_data'             #读出的需要处理、保存的数据
    GridDataList = 'grid_data_list'    #读出的需要处理、保存的数据的列表
    DstGridData = 'dst_grid_data'      #处理过的数据
    
    DatasName = 'datas_name'           #数据集名称

    StaID = 'sta_id'                   #站点id
    StaIDs = 'sta_ids'                 #站点ids
    StaCode = 'sta_code'               #站点代码
    StaInfos = 'sta_infos'             #站点信息
    
    NLon = 'nlon'                      #经度点数
    NLat = 'nlat'                      #纬度点数
    SLon = 'slon'                      #开始经度
    SLat = 'slat'                      #开始纬度
    ELon = 'elon'                      #结束经度
    ELat = 'elat'                      #结束纬度
    DLon = 'dlon'                      #经度刻度
    DLat = 'dlat'                      #纬度刻度
    GridR = 'grid_r'                   #读文件时的grid，meb.grid([70,140,0.05],[0,60,0.05])#网格信息
    GridW = 'grid_w'                   #修改数据时的grid
    
    MinValue = 'min_value'             #最小值
    MaxValue = 'max_value'             #最大值
    DiffNum = 'diff_num'               #不同值的数目
    Miss = 'miss'                      #文件中无数据时数据项的数值
    Default = 'default'                #无数据时数据项的默认值
    UseAround = 'use_around'           #浮点比较时是否使用numpy的around函数先确定精度
    Decimals = 'decimals'              #浮点精度，数字，或者列表
    ScaleDecimals = 'scale_decimals'   #经纬度、刻度的浮点精度
    DeepCopy = 'deep_copy'             #数据处理时是否需要深度拷贝一份，有时数据会是只读，直接处理会有异常
    IsCreatDir = 'is_creat_dir'        #保存数据时是否自动创建目录
    
    SrvIP = 'srv_ip'                   #服务器IP地址
    SrvPort = 'srv_port'               #服务器port端口
    SrvUserName = 'srv_username'       #服务器登录用户名
    SrvPwd = 'srv_pwd'                 #服务器登录密码
    
    Url = 'url'                        #url，在cmadaas使用时指不包括query和fragment部分的url
    UrlParams = 'url_params'           #生成url的参数,在cmadaas指query部分的参数
    IsUrl = 'is_url'                   #指定是否是url类型
    
    FileFmt = 'file_fmt'               #文件内容格式，0是micaps4模式数据，1是bin二进制格式模式数据，2是micaps3实况数据
    NCDict = 'nc_dict'                 #保存nc格式时用的字典，encoding={"my_variable": {"dtype": "int16", "scale_factor": 0.1, "zlib": True, , '_FillValue':0.0}
    SepStr = 'sepstr'                  #numpy或者xarray加载文本时，数据的分割字符
    LimitDelta = 'limit_delta'         #限制时间间隔，分钟
    FileName = 'file_name'             #文件名称
    Formatters = 'formatters'          #dataframe to_string使用的formatters参数
    IsByte = 'is_byte'                 #写文件时，数据是字符串还是字节类型
    Compression = 'compression'        #压缩类型
    HasE = 'hase'                      #grads文件有场
    GradsCtl = 'grads_ctl'             #grads描述文件解析出的结果
    Level = 'level'                    #数据的层级
    Title = 'title'                    #文件中的title，micaps或者其他
    Encoding = 'encoding'              #编码类型
    
    LevelField = 'level_field'         #level对应的字段

    Proc = 'proc'                      #函数
    TimeProc = 'time_proc'             #时间的处理函数，cmadaas的times和timerange
    SetParamsProc = 'set_params_proc'  #设置参数的函数
    SeqProc = 'seq_proc'               #seqnum的处理函数

    FuncName = 'func_name'             #函数的名字
    FuncData = 'func_data'             #函数用到的数据集

    RecordPath = 'rec_path'            #保存记录的文件全路径
    RecordData = 'rec_data'            #记录数据
    RecordFDTType = 'rec_fdt_type'     #记录中文件对应时效的时间的类型
    RecordFMDTType = 'rec_fmdt_type'   #文件的修改时间的类型
    RecordFDT = 'rec_fdt'              #记录中文件对应时效的时间
    RecordFMDT = 'rec_fmdt'            #文件的修改时间

    StaMulInfos = 'sta_mul_infos'      #将保存多个要素的站点数据保存成单要素的m3文件时需要的信息，以与目录或者名字有关的信息为key，以列名为value
    DirMulTypes = 'dir_mul_types'      #多个目录类型
    DirMulTypeFmt = 'dir_mul_type_fmt' #多个目录时，格式
    ColDataTypes = 'col_data_types'    #列的数据类型

    Filters = 'filters'                #过滤条件
    CfgFilePath = 'cfg_file_path'      #配置文件路径，可以是全路径，也可以是日志文件名，保存到默认目录
    LogFilePath = 'log_file_path'      #日志文件路径，可以是全路径，也可以是日志文件名，保存到默认目录
    CurLogger = 'cur_logger'           #当前使用的日志模块

    CfgObj = 'cfg_obj'                 #配置文件解析出的对象
    CfgObjList = 'cfg_obj_list'        #配置文件解析出的对象的列表

    UserNMem = 'user_nmem'             #用户指定的数据场数

    Ascending = 'ascending'

    GribRst = 'grib_rst'               #读grib文件时，True是返回grib，False是返回xarray

    ComPreferred = 'com_preferred'     #完整数据优先
if __name__ == '__main__':
    
    a=FixParamTypes.STime
    print(a.value)
    print(FixParamTypes.STime)
    
    print('test done')