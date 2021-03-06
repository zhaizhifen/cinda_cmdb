# -*- coding: utf-8 -*-
from openerp import fields
from openerp import models, api
import datetime, time
from email.utils import formataddr
from email.header import Header



class base_class(models.Model):
    _name = "cinda_cmdb.base_class"
    _rec_name = 'class_name'
    _description = '总类编码表'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _mail_post_access = 'read'

    class_number = fields.Char(string="总类编号")
    class_name = fields.Char(string="总类名称")
    comment = fields.Char(string="备注")


class base_type(models.Model):
    _name = "cinda_cmdb.base_type"
    _rec_name = 'type_name'
    _description = '细类编码表'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _mail_post_access = 'read'

    type_number = fields.Char(string="细类编号")
    type_name = fields.Char(string="细类名称")
    class_id = fields.Many2one("cinda_cmdb.base_class", string="所属父类")
    comment = fields.Char(string="备注")


class base_data(models.Model):
    _name = "cinda_cmdb.base_data"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _mail_post_access = 'read'

    base_data_id = fields.Char(string="基础数据ID")
    value = fields.Char(string="值")
    pare_id = fields.Char(string="父id")
    pare_lnk_mod = fields.Integer(string="父节点连接类型")
    pare_val = fields.Char(string="父值")
    last_id = fields.Integer(string="前节点id")
    last_lnk_mod = fields.Integer(string="前节点连接类型")
    last_val = fields.Char(string="前节点值")
    next_id = fields.Integer(string="后节点id")
    next_lnk_mod = fields.Integer(string="后节点连接类型")
    next_val = fields.Char(string="后节点值")
    chld_id = fields.Integer(string="子节点id")
    chld_lnk_mod = fields.Integer(string="子节点连接类型")
    chld_val = fields.Char(string="子节点值")
    comment = fields.Char(string="备注")
    last_upd = fields.Datetime(default=fields.datetime.now(), require=True)


class device(models.Model):
    _name = "cinda_cmdb.device"
    _rec_name = "sn"
    _description = '硬件设备表'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _mail_post_access = 'read'
    # _track = {
    #     'stage_id': {
    #         'project.mt_task_new': lambda self, cr, uid, obj, ctx=None: obj.stage_id and obj.stage_id.sequence <= 1,
    #         'project.mt_task_stage': lambda self, cr, uid, obj, ctx=None: obj.stage_id.sequence > 1,
    #     },
    #     'user_id': {
    #         'project.mt_task_assigned': lambda self, cr, uid, obj, ctx=None: obj.user_id and obj.user_id.id,
    #     },
    # }

    device_id = fields.Char(string="硬件ID")
    lab_id = fields.Many2one("cinda_cmdb.base_type", string='机房', domain=[('class_id', 'ilike', "机房")])
    cab = fields.Many2one("cinda_cmdb.cabinet", string="机柜")
    pos_seq = fields.Integer(string="位置序号")
    u_pos = fields.Many2one("cinda_cmdb.base_type", string="位置U", domain=[('class_id', 'ilike', "位置代号")])
    u_space = fields.Integer(string="占位U")
    env_id = fields.Many2one("cinda_cmdb.base_type", string="环境", domain=[('class_id', 'ilike', "环境")])
    use_mode = fields.Selection([('using', '使用中'), ('un_use', '未使用'),], default="", Require="False", string="使用状态")
    dev_start = fields.Selection([('start up', '开机'), ('shut down', '关机'),], default="", Require="False", string="设备状态")
    type_id = fields.Many2one("cinda_cmdb.base_type", string="设备类型", domain=[('class_id', 'ilike', "设备类型")])
    brand_id = fields.Many2one("cinda_cmdb.base_type", string="品牌", domain=[('class_id', 'ilike', "设备品牌")])
    product_name = fields.Char(string="产品型号")
    host_name = fields.Char(string="设备命名")
    model = fields.Char(string="Model")
    asset_num_old = fields.Char(string="旧资产编号")
    asset_num = fields.Char(string="资产编号")
    sn = fields.Char(string="序列号")
    purpose = fields.Char(string="用途")
    accept_date = fields.Char(string="初验日期", compute='min_contract_date', store=True)
    reject_date = fields.Char(string="过保日期", compute='max_contract_date', store=True)
    owner_id = fields.Many2one("cinda_cmdb.base_type", string="资产所有人", domain=[('class_id', 'ilike', "资产所有者")])
    user = fields.Many2one("cinda_cmdb.member_list", string="使用人")
    srve_prvd = fields.Many2one("cinda_cmdb.vendor_list", string="服务商")
    admin = fields.Many2one("cinda_cmdb.member_list", string="管理人")
    comment = fields.Char(string="备注")
    last_upd = fields.Datetime(default=fields.datetime.now(), require=True, string="最后修改日期")
    contract_ids = fields.Many2many("cinda_cmdb.contract_purchase","device_contract_ref", "device_id", "contract_id", string="采购合同编号")
    interface_ids = fields.One2many('cinda_cmdb.interface', 'device_id', string="接口")
    #以下是server表中引用过来的字段
    # server_ids = fields.One2many('cinda_cmdb.server','dev_id', string="服务器信息1")
    # server_ids_a = fields.Many2one('cinda_cmdb.server', string="服务器信息2", compute='_get_record_id', store=True)
    # app_sys = fields.Char(related="server_ids_a.app_sys", string="所属系统")
    # os = fields.Char(related="server_ids_a.os", string="底层操作系统")
    # last_upd_a = fields.Datetime(related="server_ids_a.last_upd_a", require=True, string="最后截止日期")

    # 将设备所对应的多个合同的初验日期的最早那天选出来
    @api.multi
    @api.depends('contract_ids.accept_date')
    def min_contract_date(self):
        # print '#'*80
        datas=[]
        for r in self:
            for contract in r.contract_ids:
                if contract.accept_date:
                    datas.append(contract.accept_date)
            if datas:
                r.accept_date=min(datas)

    # 将设备所对应的多个合同的初验日期的最晚那天选出来
    @api.multi
    @api.depends('contract_ids.reject_date')
    def max_contract_date(self):
        # print '#'*80
        datas=[]
        for r in self:
            for contract in r.contract_ids:
                if contract.reject_date:
                    datas.append(contract.reject_date)
            if datas:
                r.reject_date=max(datas)

    # 在device表中新建一条数据，然后根据设备类型，在相对应的表里面创建一条数据，并且将刚才数据的id赋给新数据的dev_id
    def create(self, cr, uid, vals, context=None):
        vals['device_id'] = self.pool.get('ir.sequence').get(cr, uid, 'cinda_cmdb.device')
        id = super(device, self).create(cr, uid, vals, context=context)
        if self.browse(cr, uid, id, context=context)[0].type_id:
            record = self.browse(cr, uid, id, context=context)[0].type_id.type_name
            if record == "小型计算机":
                self.pool.get('cinda_cmdb.mini_pc').create(cr, uid, {'dev_id':id}, context=context)
            elif record in ["存储",   "磁盘阵列",  "存储扩展柜"]:
                self.pool.get('cinda_cmdb.st_dev').create(cr, uid, {'dev_id':id}, context=context)
            elif record == "PC服务器":
                self.pool.get('cinda_cmdb.server').create(cr, uid, {'dev_id':id}, context=context)
            elif record in ["光纤交换机", "光纤连接器"]:
                self.pool.get('cinda_cmdb.fc_switch').create(cr, uid, {'dev_id':id}, context=context)
            elif record in ["磁带机", "磁带库"]:
                self.pool.get('cinda_cmdb.tape_station').create(cr, uid, {'dev_id':id}, context=context)
        return id

    #修改作为外键时的显示
    @api.multi
    @api.depends('sn', 'host_name')
    def name_get(self):
        datas=[]
        for r in self:
            if r.host_name:
                datas.append((r.id, (r.sn + '(' + (r.host_name) + ')')))
            else:
                datas.append((r.id, (r.sn)))
        return datas

    # 将sever表里的字段引用到device表里面。。。(将)
    # @api.one
    # @api.depends('server_ids')
    # def _get_record_id(self):
    #     for r in self:
    #         r.server_ids_a = r.server_ids




class server(models.Model):
    _name = "cinda_cmdb.server"
    _description = 'PC服务器表'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _mail_post_access = 'read'
    _rec_name = "sn_id"

    vm_ids = fields.One2many("cinda_cmdb.vm", "server_ids", string="虚拟机信息")
    dev_id = fields.Many2one("cinda_cmdb.device", string="设备资产id", domain=[('type_id.type_name', 'ilike', "PC服务器")])
    sn_id = fields.Char(related="dev_id.sn", string="所属设备序列号")
    interface_ids_a = fields.One2many('cinda_cmdb.interface', 'server_id', string="HBA卡接口", domain=[('type', '=', "hba")])
    interface_ids_b = fields.One2many('cinda_cmdb.interface', 'server_id', string="网卡接口",  domain=[('type', 'in', ['ethernet_electricity', 'ethernet_fiber'])])
    # server_info_ids_a = fields.Char(related="server_info_ids", string="服务器信息合同")
    server_id = fields.Char(string="服务器id")
    app_sys = fields.Char(string="所属系统")
    buss_ip_addr = fields.Char(string="业务网IP地址")
    stor_ip_addr = fields.Char(string="存储网IP地址")
    bck_ip_addr = fields.Char(string="备份网IP地址")
    mng_ip_addr = fields.Char(string="管理网IP地址")
    admin_ip = fields.Char(string="管理口IP")
    admin_info = fields.Char(string="管理口信息点")
    # os_id = fields.Char(string="底层操作系统id")
    os = fields.Char(string="底层操作系统")
    cpu_num = fields.Integer(string="CPU数量")
    single_cpu_num = fields.Integer(string="单CPU核数")
    cpu_sum = fields.Integer(string="CPU总核数", compute="_cpu_sum", store="True")
    cpu_spec = fields.Char(string="CPU规格")
    mem_num = fields.Integer(string="内存条数")
    single_mem_size = fields.Float(string="单条内存容量")
    mem_sum = fields.Float(string="内存总容量", compute="_mem_sum", store="True")
    mem_spec = fields.Char(string="内存规格")
    disk_size = fields.Integer(string="硬盘数量")
    single_disk_size = fields.Float(string="单硬盘容量")
    disk_sum = fields.Float(string="硬盘总容量", compute="_disk_sum", store="True")
    disk_spec = fields.Char(string="硬盘规格")
    ext_st_size = fields.Float(string="外接存储容量(TB)")
    hba_config = fields.Char(string="HBA卡配置")
    hba_used = fields.Char(string="HBA卡已用情况")
    g_netcard_config = fields.Char(string="千兆网卡配置")
    g_netcard_used = fields.Char(string="千兆网卡已用情况")
    t_netcard_config = fields.Char(string="万兆网卡配置")
    t_netcard_used = fields.Char(string="万兆网卡已用情况")
    netcard_band = fields.Char(string="网卡绑定")
    exten_mod = fields.Char(string="扩展模块")
    vir_mark = fields.Many2one("cinda_cmdb.cluster", string="虚拟化标志")
    comment1 = fields.Char(string="备注1")
    comment2 = fields.Char(string="备注2")
    last_upd = fields.Datetime(default=fields.datetime.now(), require=True)
    san_wwn = fields.Char(string="san网络wwn号")
    ha_mode = fields.Char(string="主备状态")
    four_g_hba_num = fields.Integer(string="4G HBA卡数量")
    four_g_hba_used_num = fields.Integer(string="4G HBA卡已用数量")
    eight_g_hba_num = fields.Integer(string="8G HBA卡数量")
    eight_g_hba_used_num = fields.Integer(string="8G HBA卡已用数量")
    sixteen_g_hba_num = fields.Integer(string="16G HBA卡数量")
    sixteen_g_hba_used_num = fields.Integer(string="16G HBA卡已用数量")
    thirty_two_g_hba_num = fields.Integer(string="32G HBA卡数量")
    thirty_two_g_hba_used_num = fields.Integer(string="32G HBA卡已用数量")
    g_netcard_num = fields.Integer(string="千兆网口数量")
    g_netcard_used_num = fields.Integer(string="千兆网口已用数量")
    t_netcard_num = fields.Integer(string="万兆网口数量")
    t_netcard_used_num = fields.Integer(string="万兆网口已用数量")
    #以下是device表中引用过来用来展示的字段
    host_name = fields.Char(related="dev_id.host_name", string="设备命名")
    type_id = fields.Many2one(related="dev_id.type_id", string="设备类型", domain=[('type_name', 'ilike', "PC服务器")], store="Ture")
    brand_id = fields.Many2one(related="dev_id.brand_id", string="品牌")
    product_name = fields.Char(related="dev_id.product_name", string="产品型号")
    # sn = fields.Char(related="dev_id.sn", string="序列号")
    model = fields.Char(related="dev_id.model", string="Model")
    use_mode = fields.Selection(related="dev_id.use_mode", string="使用状态")
    dev_start = fields.Selection(related="dev_id.dev_start", string="设备状态")
    asset_num_old = fields.Char(related="dev_id.asset_num_old", string="旧资产编号")
    asset_num = fields.Char(related="dev_id.asset_num", string="资产编号")
    purpose = fields.Char(related="dev_id.purpose", string="用途")
    owner_id = fields.Many2one(related="dev_id.owner_id", string="资产所有人")
    user = fields.Many2one(related="dev_id.user",  string="使用人")
    admin = fields.Many2one(related="dev_id.admin", string="管理人")
    comment = fields.Char(related="dev_id.comment", string="备注")
    lab_id = fields.Many2one(related="dev_id.lab_id", string="机房")
    cab = fields.Many2one(related="dev_id.cab", string="机柜")
    pos_seq = fields.Integer(related="dev_id.pos_seq", string="位置序号")
    u_pos = fields.Many2one(related="dev_id.u_pos", string="位置U")
    u_space = fields.Integer(related="dev_id.u_space", string="占位U")
    env_id = fields.Many2one(related="dev_id.env_id", string="环境")
    srve_prvd = fields.Many2one(related="dev_id.srve_prvd", string="服务商")
    contract_ids = fields.Many2many(related="dev_id.contract_ids", string="采购合同编号")
    accept_date = fields.Char(related="dev_id.accept_date", string="初验日期")
    reject_date = fields.Char(related="dev_id.reject_date", string="过保日期")



    # 计算内存总容量
    @api.multi
    @api.depends('mem_num', 'single_mem_size')
    def _mem_sum(self):
        for r in self:
            r.mem_sum = r.mem_num * r.single_mem_size

    # 计算硬盘总容量
    @api.multi
    @api.depends('disk_size', 'single_disk_size')
    def _disk_sum(self):
        for r in self:
            r.disk_sum = r.disk_size * r.single_disk_size

    #计算CPU核数量
    @api.multi
    @api.depends('cpu_num', 'single_cpu_num')
    def _cpu_sum(self):
        for r in self:
            r.cpu_sum = r.single_cpu_num * r.cpu_num

    #
    @api.multi
    def action_to_confirm(self):
        import patter
        patter.patter()


class net_dev(models.Model):
    _name = "cinda_cmdb.net_dev"
    _description = '网络信息表'
    _rec_name = "host_name"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _mail_post_access = 'read'

    # name = fields.Char(string="设备命名")
    # area = fields.Selection([('east_ring', '东环'), ('yi_zh', '亦庄'), ('money_center', '金融中心'), ('fen_firm', '分公司'), ('son_firm', '子公司')], default="", Require="False", string="物理位置")
    area = fields.Char( string="物理位置")
    region = fields.Char( string="所属区域")
    version = fields.Char(string="软件版本")
    admin_ip = fields.Char(string="管理口IP")
    account = fields.Char(string="账号")
    comment = fields.Char(string="备注")
    online_time = fields.Date(string="上线日期")
    offline_time = fields.Date(string="下线日期")
    scrap_time = fields.Date(string="报废日期")
    fixed_assets_project = fields.Char(string="固定资产项目名称")
    config_backup_method = fields.Selection([('auto', '自动备份'), ('manual', '手动')], default='manual', string="配置备份方式")
    config_backup_frequency = fields.Selection(
        [('per_day', '每天'),
         ('per_week', '每周'),
         ('per_month', '每月'),
         ('per_year', '每年')],
        string="配置备份频率"
    )
    interface_ids = fields.One2many(related='dev_id.interface_ids', string="接口")
    last_upd = fields.Datetime(default=fields.datetime.now(), require=True, string="最后修改日期")
    dev_id = fields.Many2one("cinda_cmdb.device", string="序列号", domain=['|','|','|','|','|','|','|','|','|','|','|','|','|',
                                                                                    ('type_id.type_name','ilike',"网络设备"),
                                                                                    ('type_id.type_name','ilike',"交换机"),
                                                                                    ('type_id.type_name','ilike',"路由器"),
                                                                                    ('type_id.type_name','ilike',"安全设备"),
                                                                                    ('type_id.type_name','ilike',"防火墙"),
                                                                                    ('type_id.type_name','ilike',"负载均衡"),
                                                                                    ('type_id.type_name','ilike',"邮件网关"),
                                                                                    ('type_id.type_name','ilike',"PIX"),
                                                                                    ('type_id.type_name','ilike',"IDS探针"),
                                                                                    ('type_id.type_name','ilike',"SG"),
                                                                                    ('type_id.type_name','ilike',"SSL_VPN"),
                                                                                    ('type_id.type_name','ilike',"IPSEC_VPN"),
                                                                                    ('type_id.type_name','ilike',"CITRIX"),
                                                                                    ('type_id.type_name','ilike',"备邮数据中心"),
                                                                                    ])
    sn_id = fields.Char(related="dev_id.sn", string="所属设备序列号")
    #以下是device表中引用过来用来展示的字段
    host_name = fields.Char(related="dev_id.host_name", string="设备命名")
    brand_id = fields.Many2one(related="dev_id.brand_id", string="品牌")
    type_id = fields.Many2one(related="dev_id.type_id", string="设备类型", domain=['|','|','|','|','|','|','|','|','|','|','|','|','|',
                                                                                        ('type_name','ilike',"网络设备"),
                                                                                        ('type_name','ilike',"交换机"),
                                                                                        ('type_name','ilike',"路由器"),
                                                                                        ('type_name','ilike',"安全设备"),
                                                                                        ('type_name','ilike',"防火墙"),
                                                                                        ('type_name','ilike',"负载均衡"),
                                                                                        ('type_name','ilike',"邮件网关"),
                                                                                        ('type_name','ilike',"PIX"),
                                                                                        ('type_name','ilike',"IDS探针"),
                                                                                        ('type_name','ilike',"SG"),
                                                                                        ('type_name','ilike',"SSL_VPN"),
                                                                                        ('type_name','ilike',"IPSEC_VPN"),
                                                                                        ('type_name','ilike',"CITRIX"),
                                                                                        ('type_name','ilike',"备邮数据中心"),
                                                                                        ], store="Ture")
    product_name = fields.Char(related="dev_id.product_name", string="产品型号")
    # sn = fields.Char(related="dev_id.sn", string="序列号")
    model = fields.Char(related="dev_id.model", string="Model")
    use_mode = fields.Selection(related="dev_id.use_mode", string="使用状态")
    dev_start = fields.Selection(related="dev_id.dev_start", string="设备状态")
    asset_num_old = fields.Char(related="dev_id.asset_num_old", string="旧资产编号")
    asset_num = fields.Char(related="dev_id.asset_num", string="资产编号")
    purpose = fields.Char(related="dev_id.purpose", string="用途")
    owner_id = fields.Many2one(related="dev_id.owner_id", string="资产所有人")
    user = fields.Many2one(related="dev_id.user",  string="使用人")
    admin = fields.Many2one(related="dev_id.admin", string="管理人")
    comment = fields.Char(related="dev_id.comment", string="备注")
    lab_id = fields.Many2one(related="dev_id.lab_id", string="机房")
    cab = fields.Many2one(related="dev_id.cab", string="机柜")
    pos_seq = fields.Integer(related="dev_id.pos_seq", string="位置序号")
    u_pos = fields.Many2one(related="dev_id.u_pos", string="位置U")
    u_space = fields.Integer(related="dev_id.u_space", string="占位U")
    env_id = fields.Many2one(related="dev_id.env_id", string="环境")
    srve_prvd = fields.Many2one(related="dev_id.srve_prvd", string="服务商")
    contract_ids = fields.Many2many(related="dev_id.contract_ids", string="采购合同编号")
    accept_date = fields.Char(related="dev_id.accept_date", string="初验日期")
    reject_date = fields.Char(related="dev_id.reject_date", string="过保日期")
    # net_dev_id = fields.Char(string="网络设备id")
    # area_id = fields.Integer(string="区域id")
    # root_acc = fields.Char(string="根用户")
    # chg_acc = fields.Char(string="变更用户")
    # mon_acc = fields.Char(string="监控用户")
    # ha_mode = fields.Char(string="主备状态")
    # dev_id = fields.Integer(string="设备资产id")


class board(models.Model):
    _name = "cinda_cmdb.board"
    _description = 'net_board'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _mail_post_access = 'read'

    board_id = fields.Char(string="板卡id")
    area_id = fields.Integer(string="区域id")
    area = fields.Char(string="区域")
    dev_id = fields.Integer(string="设备资产id")
    net_dev_id = fields.Integer(string="网络设备id")
    srv_dev_id = fields.Integer(string="服务器设备id")
    card_type = fields.Char(string="板卡类型")
    card_sn = fields.Char(string="板卡序列号")
    slot = fields.Char(string="槽位")
    comment1 = fields.Char(string="备注")
    comment2 = fields.Char(string="备注2")
    last_upd = fields.Datetime(default=fields.datetime.now(), require=True)


class st_dev(models.Model):
    _name = "cinda_cmdb.st_dev"
    _description = 'storage'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _mail_post_access = 'read'

    st_dev_id = fields.Char(string="存储id")
    interface_ids = fields.One2many(related='dev_id.interface_ids', string="接口")
    st_part_ids = fields.One2many('cinda_cmdb.st_part', 'st_id', string="存储组件")
    st_part_ids_a = fields.One2many(related='st_part_ids', string="组件磁盘")
    st_part_ids_b = fields.One2many(related='st_part_ids', string="组件容量")
    interface_ids = fields.One2many('cinda_cmdb.interface', 'st_dev_id', string="光口", domain=[('type', 'in', ["ethernet_fiber", "hba"])])
    interface_ids_a = fields.One2many('cinda_cmdb.interface', 'st_dev_id', string="电口", domain=[('type', '=', "ethernet_electricity")])
    dev_id = fields.Many2one("cinda_cmdb.device", string="设备资产id",
                             domain=['|','|','|','|','|',
                                     ('type_id.type_name', 'ilike', "磁带机"),
                                     ('type_id.type_name', 'ilike', "磁带库"),
                                     ('type_id.type_name', 'ilike', "磁盘阵列"),
                                     ('type_id.type_name', 'ilike', "存储扩展柜"),
                                     ('type_id.type_name', 'ilike', "光纤连接器"),
                                     ('type_id.type_name', 'ilike', "光纤交换机")])
    type = fields.Many2one("cinda_cmdb.base_type", string="存储类型", domain=[('class_id.class_name', 'ilike', '存储类型')])
    pc_control_num = fields.Integer(string="整机控制器数")
    pc_cage_num = fields.Integer(string="整机笼子数")
    each_cage_disk_num = fields.Integer(string="每个笼子可容纳磁盘数")
    pc_all_size = fields.Float(string="整机裸容量(T)")
    pc_enable_size = fields.Float(string="整机总可使用容量(T)")
    pc_used_size = fields.Float(string="整机已经分配容量(T)")
    pc_remain_size = fields.Float(string="整机剩余可使用容量(T)")
    ip = fields.Char(string="IP")
    app_sys = fields.Char(string="所属系统")
    # type_id_a = fields.Many2one("cinda_cmdb.base_type", domain=[('class_id', 'ilike', "设备类型")])
    #以下是device表中引用过来用来展示的字段
    host_name = fields.Char(related="dev_id.host_name", string="设备命名")
    type_id = fields.Many2one(related="dev_id.type_id", string="设备类型", domain=['|','|','|','|','|',
                                     ('type_name', 'ilike', "磁带机"),
                                     ('type_name', 'ilike', "磁带库"),
                                     ('type_name', 'ilike', "磁盘阵列"),
                                     ('type_name', 'ilike', "存储扩展柜"),
                                     ('type_name', 'ilike', "光纤交换机"),
                                     ('type_name', 'ilike', "光纤连接器")], store="Ture")
    brand_id = fields.Many2one(related="dev_id.brand_id", string="品牌")
    product_name = fields.Char(related="dev_id.product_name", string="产品型号")
    sn = fields.Char(related="dev_id.sn", string="序列号")
    model = fields.Char(related="dev_id.model", string="Model")
    use_mode = fields.Selection(related="dev_id.use_mode", string="使用状态")
    dev_start = fields.Selection(related="dev_id.dev_start", string="设备状态")
    asset_num_old = fields.Char(related="dev_id.asset_num_old", string="旧资产编号")
    asset_num = fields.Char(related="dev_id.asset_num", string="资产编号")
    purpose = fields.Char(related="dev_id.purpose", string="用途")
    owner_id = fields.Many2one(related="dev_id.owner_id", string="资产所有人")
    user = fields.Many2one(related="dev_id.user",  string="使用人")
    admin = fields.Many2one(related="dev_id.admin", string="管理人")
    comment = fields.Char(related="dev_id.comment", string="备注")
    lab_id = fields.Many2one(related="dev_id.lab_id", string="机房")
    cab = fields.Many2one(related="dev_id.cab", string="机柜")
    pos_seq = fields.Integer(related="dev_id.pos_seq", string="位置序号")
    u_pos = fields.Many2one(related="dev_id.u_pos", string="位置U")
    u_space = fields.Integer(related="dev_id.u_space", string="占位U")
    env_id = fields.Many2one(related="dev_id.env_id", string="环境")
    srve_prvd = fields.Many2one(related="dev_id.srve_prvd", string="服务商")
    contract_ids = fields.Many2many(related="dev_id.contract_ids", string="采购合同编号")
    accept_date = fields.Char(related="dev_id.accept_date", string="初验日期")
    reject_date = fields.Char(related="dev_id.reject_date", string="过保日期")



class srv_room_dev(models.Model):
    _name = "cinda_cmdb.srv_room_dev"
    _description = '机房设备表'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _mail_post_access = 'read'

    srv_room_dev_id = fields.Char(string="机房设备id")
    asset_type = fields.Char(string="资产大类")
    num = fields.Integer(string="数量")
    start_date = fields.Date(string="启用日期")
    elec_power = fields.Integer(string="总功率")
    ampere = fields.Integer(string="电流")
    comment = fields.Char(string="备注")
    last_upd = fields.Datetime(default=fields.datetime.now(), require=True)
    dev_id = fields.Integer(string="设备资产id")


class san_port(models.Model):
    _name = "cinda_cmdb.san_port"
    _description = 'SAN端口表'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _mail_post_access = 'read'

    san_port_id = fields.Char(string="SAN端口id")
    dev_id = fields.Integer(string="设备资产id")
    type_id = fields.Integer(string="设备类型")
    port = fields.Char(string="端口号")
    module = fields.Char(string="模块")
    # port = fields.Char(string="本端端口号")
    end_port_id = fields.Integer(string="对端端口ID")
    end_on_port = fields.Char(string="对端的端口号")
    end_on_wwn = fields.Char(string="对端的WWN")
    protocl = fields.Char(string="使用协议")
    device_code = fields.Char(string="设备编号")
    end_on_dev_id = fields.Integer(string="对端设备id")
    wwn = fields.Char(string="本端WWN")
    speed = fields.Char(string="速率")
    fc_card_name = fields.Char(string="光纤卡名")
    slot = fields.Char(string="槽位")
    alias = fields.Char(string="别名")
    captain = fields.Char(string="说明")
    comment = fields.Char(string="备注")
    last_upd = fields.Datetime(default=fields.datetime.now(), require=True, string='最后截止日期')


class ip_port(models.Model):
    _name = "cinda_cmdb.ip_port"
    _description = 'ip端口表'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _mail_post_access = 'read'

    ip_port_id = fields.Char(string="IP端口ID")
    dev_id = fields.Integer(string="设备id")
    net_dev_id = fields.Integer(string="网络设备id")
    card_id = fields.Integer(string="板卡id")
    port = fields.Char(string="本端物理端口号")
    port_num = fields.Char(string="本端端口名")
    port_mac = fields.Char(string="本端MAC")
    port_ip = fields.Char(string="本端IP地址")
    port_type = fields.Char(string="本端端口类型")
    end_on_dev_id = fields.Integer(string="对端设备id")
    end_on_card_id = fields.Integer(string="对端板卡id")
    end_on_port = fields.Char(string="对端物理端口号")
    end_on_nam = fields.Char(string="对端端口名")
    end_on_port_mac = fields.Char(string="对端MAC")
    end_on_port_ip = fields.Char(string="对端ip地址")
    end_on_port_type = fields.Char(string="对端端口类型")
    port_status = fields.Char(string="端口状态")
    port_speed = fields.Char(string="端口速率")
    port_info = fields.Char(string="端口描述")
    mod_type = fields.Char(string="模块类型")
    mod_sn = fields.Char(string="模块序列号")
    last_upd = fields.Datetime(default=fields.datetime.now(), require=True)


class cabinet(models.Model):
    _name = "cinda_cmdb.cabinet"
    _description = '机柜表'
    _rec_name = "cab_num"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _mail_post_access = 'read'

    cab_num = fields.Char(string="机柜号", require=True)
    lab = fields.Many2one("cinda_cmdb.base_type", string="机房", domain=[('class_id', 'ilike', "机房")])
    pdu_num = fields.Integer(string="PDU数目")
    elec_power = fields.Integer(string="电源功率")
    ampere = fields.Integer(string="电流")
    u_num = fields.Integer(string="U位数目")
    purpose = fields.Char(string="用途")
    comment = fields.Char(string="备注")
    last_upd = fields.Datetime(default=fields.datetime.now(), require=True)


class soft(models.Model):
    _name = "cinda_cmdb.soft"
    _description = '软件总表'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _mail_post_access = 'read'
    _rec_name = 'soft_code'

    soft_id = fields.Char(string="软件总id")
    total_class = fields.Char(string="总类别", require=True)
    subclass = fields.Char(string="明细类别", require=True)
    soft_code = fields.Char(string="软件编号", require=True)
    soft_name = fields.Char(string="全称")
    purpose = fields.Char(string="用途")
    license_type = fields.Char(string="许可类型")
    license_company = fields.Char(string="许可单位")
    num = fields.Integer(string="数量")
    developer = fields.Char(string="开发商")
    status = fields.Char(string="状态")
    media_type = fields.Char(string="介质类型")
    reject_date = fields.Datetime(string="支持到期时间")
    contact_info = fields.Char(string="支持联系方式")
    license_pos = fields.Char(string="许可证位置")
    comment = fields.Char(string="备注")
    last_upd = fields.Datetime(default=fields.datetime.now(), require=True)



class soft_detail(models.Model):
    _name = "cinda_cmdb.soft_detail"
    _description = '软件明细表'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _mail_post_access = 'read'

    soft_detail_id = fields.Char(string="软件明细id")
    soft_code_id = fields.Many2one("cinda_cmdb.soft", string="软件编号", required="True")
    detail_code = fields.Char(string="明细编号")
    detail_name = fields.Char(string="细项名称")
    version = fields.Char(string="版本号")
    num = fields.Integer(string="购买数量")
    auth_info = fields.Char(string="授权信息")
    buy_date = fields.Date(string="购买时间")
    over_date = fields.Date(string="服务截止时间")
    vendor = fields.Char(string="供应商")
    buyer = fields.Char(string="购买单位")
    owner = fields.Char(string="资产所有人")
    user = fields.Char(string="使用人")
    media_type = fields.Char(string="介质类型")
    license_key = fields.Char(string="许可密钥")
    license_path = fields.Char(string="许可保存路径")
    comment = fields.Char(string="备注")
    last_upd = fields.Datetime(default=fields.datetime.now(), require=True)


class vendor_list(models.Model):
    _name = "cinda_cmdb.vendor_list"
    _description = '厂商信息表'
    _rec_name = "vendor"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _mail_post_access = 'read'

    vendor_list_id = fields.Char(string="服务商ID")
    vendor = fields.Char(string="名称", require=True)
    attr = fields.Char(string="性质")
    address = fields.Char(string="地址")
    contact = fields.One2many("cinda_cmdb.member_list", "address", string="联系人")
    # position = fields.Char(string="职位")
    fixed_phone = fields.Char(string="电话")
    mobile_phone = fields.Char(string="手机")
    mail = fields.Char(string="邮件")
    comment = fields.Char(string="备注")
    last_upd = fields.Datetime(default=fields.datetime.now(), require=True)


class member_list(models.Model):
    _name = "cinda_cmdb.member_list"
    _description = '人员表'
    _rec_name = "name"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _mail_post_access = 'read'

    member_list_id = fields.Char(string="人员表ID")
    name = fields.Char(string="名称", require=True)
    attr = fields.Char(string="性质")
    address = fields.Many2one("cinda_cmdb.vendor_list", string="公司")
    position = fields.Char(string="职位")
    fixed_phone = fields.Char(string="电话")
    mobile_phone = fields.Char(string="手机")
    mail = fields.Char(string="邮件")
    comment = fields.Char(string="备注")
    last_upd = fields.Datetime(default=fields.datetime.now(), require=True)


class chg_log(models.Model):
    _name = "cinda_cmdb.chg_log"
    _description = '变更记录表'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _mail_post_access = 'read'

    exe_date = fields.Date(string="日期")
    executor = fields.Many2one("cinda_cmdb.member_list", string="实施人", require=True)
    chg_dev_id = fields.Many2one('cinda_cmdb.device', string="设备")
    chg_type = fields.Char(string="类型")
    action = fields.Char(string="动作", require=True)


class device_chg_log(models.Model):
    _name = "cinda_cmdb.device_chg_log"
    _description = '硬件变更记录表'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _mail_post_access = 'read'

    exe_date = fields.Date(string="日期")
    executor = fields.Many2one("cinda_cmdb.member_list", string="实施人", require=True)
    chg_dev_id = fields.Many2one('cinda_cmdb.device', string="设备")
    chg_type = fields.Char(string="类型")
    action = fields.Char(string="动作", require=True)


class soft_chg_log(models.Model):
    _name = "cinda_cmdb.soft_chg_log"
    _description = '软件变更记录表'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _mail_post_access = 'read'

    exe_date = fields.Date(string="日期")
    executor = fields.Many2one("cinda_cmdb.member_list", string="实施人", require=True)
    chg_dev_id = fields.Many2one('cinda_cmdb.device', string="设备")
    chg_type = fields.Char(string="类型")
    action = fields.Char(string="动作", require=True)


class vm_chg_log(models.Model):
    _name = "cinda_cmdb.vm_chg_log"
    _description = '虚拟资源变更记录表'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _mail_post_access = 'read'

    exe_date = fields.Date(string="日期")
    executor = fields.Many2one("cinda_cmdb.member_list", string="实施人", require=True)
    chg_dev_id = fields.Many2one('cinda_cmdb.device', string="设备")
    chg_type = fields.Char(string="类型")
    action = fields.Char(string="动作", require=True)


class auth_chg_log(models.Model):
    _name = "cinda_cmdb.auth_chg_log"
    _description = '授权变更记录表'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _mail_post_access = 'read'

    exe_date = fields.Date(string="日期")
    executor = fields.Many2one("cinda_cmdb.member_list", string="实施人", require=True)
    chg_dev_id = fields.Many2one('cinda_cmdb.device', string="设备")
    chg_type = fields.Char(string="类型")
    action = fields.Char(string="动作", require=True)

class net_config(models.Model):
    _name = "cinda_cmdb.net_config"
    _description = '网络配置表'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _mail_post_access = 'read'

    net_config_id = fields.Char(string="网络配置管理id")
    logic_area = fields.Char(string="逻辑区域")
    admin_ip = fields.Char(string="管理IP")
    version = fields.Char(string="软件版本")
    license_date = fields.Date(string="许可证日期")
    port_num = fields.Integer(string="端口数量")
    port_info = fields.Char(string="端口信息")
    vlan_info = fields.Char(string="VLAN信息")
    fw_policy1 = fields.Char(string="防火墙策略1")
    fw_policy2 = fields.Char(string="防火墙策略2")
    mail_gw_policy = fields.Char(string="邮件网关策略")


class st_zone_lun(models.Model):
    _name = "cinda_cmdb.st_zone_lun"
    _description = 'LUN信息表'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _mail_post_access = 'read'

    st_zone_lun_id = fields.Char(string="存储zone_lun划分id")
    zone_lun_id = fields.Char(string="ZONE_LUN_ID")
    lun_id = fields.Char(string="lun号")
    ioport = fields.Char(string="ioport")
    total_size = fields.Float(string="总容量")
    used_size = fields.Float(string="使用容量")
    free_size = fields.Float(string="剩余容量")
    host_name = fields.Char(string="使用的主机")
    system = fields.Char(string="业务系统")
    raid_type = fields.Char(string="RAID类型")
    volumes_name = fields.Char(string="volumes_name")
    aggregate = fields.Char(string="aggregata")
    ip_addr = fields.Char(string="IP地址")
    config_info = fields.Char(string="配置信息")
    comment = fields.Char(string="备注")


class vlan(models.Model):
    _name = "cinda_cmdb.vlan"
    _description = 'VLAN信息表'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _mail_post_access = 'read'

    vlan_id_id = fields.Char(string="VLAN表ID")
    vlan_id = fields.Char(string="VLAN号")
    vlan_name = fields.Char(string="VLAN名称")
    vlan_segment = fields.Char(string="VLAN网段")
    comment = fields.Char(string="备注") 


class fw_policy1(models.Model):
    _name = "cinda_cmdb.fw_policy1"
    _description = '防火墙策略表1'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _mail_post_access = 'read'

    fw_policy1_id = fields.Char(string="防火墙策略1id")
    fw_name = fields.Char(string="防火墙名称")
    s_addrname = fields.Char(string="源地址命名")
    s_ip = fields.Char(string="源地址")
    d_addrname = fields.Char(string="目的地址命名")
    d_ip = fields.Char(string="目的地址")
    service_name = fields.Char(string="服务命名")
    service_port = fields.Char(string="服务端口")
    policy_date = fields.Date(string="策略时间")


class fw_policy2(models.Model): 
    _name = "cinda_cmdb.fw_policy2"
    _description = '防火墙策略表2'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _mail_post_access = 'read'

    fw_policy2_id = fields.Char(string="防火墙策略2id")
    fw_name = fields.Char(string="防火墙名称")
    switch_mode = fields.Char(string="转换模式")
    s_addrname = fields.Char(string="源地址命名")
    s_ip = fields.Char(string="源地址")
    d_addrname = fields.Char(string="目的地址命名")
    d_ip = fields.Char(string="目的地址")
    switch_addrname = fields.Char(string="转换后地址命名")
    switch_ip = fields.Char(string="转换后地址")
    service_name = fields.Char(string="服务命令")
    service = fields.Char(string="服务")


class spam_policy(models.Model):
    _name = "cinda_cmdb.spam_policy"
    _description = 'spam策略表'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _mail_post_access = 'read'

    spam_policy_id = fields.Char(stirng="SPAM策略id")
    industry = fields.Char(string="行业")
    company_name = fields.Char(string="公司名称")
    domain_name = fields.Char(string="域名")
    mx_name = fields.Char(string="mx名称")
    ip_addr = fields.Char(string="IP")
    desc = fields.Char(string="描述")
    comment = fields.Char(string="备注")


class account(models.Model):
    _name = "cinda_cmdb.account"
    _description = '账户表'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _mail_post_access = 'read'

    account_id = fields.Char(string="账户id")
    dev_id = fields.Integer(string="设备id",  require=True)
    soft_id = fields.Integer(string="软件id")
    acc_nam = fields.Char(string="账户名称",  require=True)
    encr_pasw = fields.Char(string="加密密码",  require=True)
    use_purp = fields.Char(string="使用目的",  require=True)
    use_mode = fields.Char(string="使用类型",  require=True)
    authority = fields.Char(string="账户权限",  require=True)
    owner_id = fields.Integer(string="账户负责人",  require=True)
    auth_owner = fields.Integer(string="授权负责人",  require=True)
    crt_date = fields.Char(string="创建日期")
    crt_pers = fields.Integer(string="创建人")
    crt_appr_pers = fields.Integer(string="创建批准人")
    crt_chg_num = fields.Char(string="创建的变更号")
    curr_user = fields.Integer(string="当前使用人")
    use_appr_pers = fields.Integer(string="当前使用授权人")
    appr_date = fields.Date(string="当前授权日期")
    last_recovery = fields.Date(string="上次回收日期")
    comment1 = fields.Char(string="备注1")
    comment2 = fields.Char(string="备注2")
    last_upd = fields.Datetime(default=fields.datetime.now(), require=True)


class auth_log(models.Model):
    _name = "cinda_cmdb.auth_log"
    _description = '授权记录表'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _mail_post_access = 'read'

    auth_log_id = fields.Char(string="授权记录id")
    exe_date = fields.Char(string="",require=True)
    executor = fields.Integer(string="",require=True)
    chg_num = fields.Char(string="")
    action = fields.Char(string="",require=True)
    per_user = fields.Integer(string="")
    aft_user = fields.Integer(string="")
    per_owner = fields.Integer(string="")
    aft_owner = fields.Integer(string="")
    comment1 = fields.Char(string="")
    comment2 = fields.Char(string="")
    last_upd = fields.Datetime(default=fields.datetime.now(), require=True)


# u位表
class position_u(models.Model):
    _name = "cinda_cmdb.position_u"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'U位表'
    _mail_post_access = 'read'

    name = fields.Char(string="名称")
    status = fields.Boolean(string="状态", default=False)
    cabinet_id = fields.Many2one("cinda_cmdb.cabinet", string="所在机柜", required="True")


class cluster(models.Model):
    _name = "cinda_cmdb.cluster"
    _description = '集群表'
    _rec_name = "name"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _mail_post_access = 'read'

    environment = fields.Many2one("cinda_cmdb.base_type", string="环境", domain=[('class_id', 'ilike', "环境")])
    name = fields.Char(string="集群")
    vm_num = fields.Integer(string="虚机数量")
    action_vm_num = fields.Integer(string="活动虚机数量")
    server_id = fields.One2many("cinda_cmdb.server", "vir_mark")
    vm_id = fields.One2many("cinda_cmdb.vm", "cluster_id")


class vm(models.Model):
    _name = "cinda_cmdb.vm"
    _description = '虚拟机信息表'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _mail_post_access = 'read'
    _rec_name = "cluster_id"

    server_ids = fields.Many2one("cinda_cmdb.server", string="主机")
    host_computer = fields.Char( string="主机")
    cluster_id = fields.Many2one("cinda_cmdb.cluster", string="集群")
    app_user_id = fields.Char(string="应用联系人")
    sequence = fields.Integer(string='序号')
    name = fields.Char(string='虚拟机名称')
    vm_num = fields.Integer(string='虚机数量(台)')
    state = fields.Selection([('start', '开机'),('shutdown', '关机'),], default="", Require="False", string="状况")
    reserve_space = fields.Float(string="置备空间")
    used_space = fields.Float(string="已用空间")
    client_operate_sys = fields.Char(string="客户机操作系统")
    memory_size = fields.Integer(string="内存大小(MB)", track_visibility='onchange')
    cpu = fields.Integer(string="CPU数量")
    vm_ip = fields.Char(string="虚机IP地址")
    vm_run_state = fields.Selection([('running', '正在运行'), ('shutdown', '未运行'),], default="", Require="False", string="VMware Tools 运行状况")
    comment = fields.Char(string="备注")
    sys_module = fields.Char(string="系统模块名称")
    deliver_date = fields.Date(string="交付日期")
    business_type = fields.Char(string="业务类型")
    back_date = fields.Date(string="计划归还日期")


class contract_purchase(models.Model):
    _name = "cinda_cmdb.contract_purchase"
    _description = '采购合同表'
    _rec_name = "number"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _mail_post_access = 'read'


    device_ids = fields.Many2many("cinda_cmdb.device","device_contract_ref", "contract_id","device_id", string="序列号")
    # device_id = fields.Char(string="序列号")
    name = fields.Char(string="合同名称")
    number = fields.Char(string="合同编号")
    vendor = fields.Many2one("cinda_cmdb.vendor_list", stirng="服务商")
    vendor_a = fields.Many2one("cinda_cmdb.vendor_list", stirng="供应商")
    accept_date = fields.Date(string="初验日期")
    reject_date = fields.Date(string="过保日期")
    # reject_device = fields.Char(string="过保设备", compute="reject", store=True)

    # 自动根据合同结束时间提醒邮件--距离合同结束一个月内 频率--每周
    @api.multi
    def email_contract_reject_date(self):
        subject = '您有合同即将过期，请及时处理！'
        date = fields.Date.to_string(fields.date.today()+datetime.timedelta(days=30))
        user_ids=[]
        for contracts in self.env['cinda_cmdb.contract_purchase'].search([('reject_date','<=',date),]):
            if contracts.header_id not in user_ids:
                user_ids.append(contracts.header_id)
        for user_id in user_ids:
            datas=''
            user_contracts = self.env['cinda_cmdb.contract_purchase'].search([('date_end', '<=', date),('header_id','=',user_id.id)])
            for user_contract in user_contracts:
                text=u'合同名:'+user_contract.name+u'-----过期时间 '+user_contract.reject_date
                datas+=u'<p>'+text+u'</p>'
            body= u'<div>'+u'<p>您好:</p>'+u'<p>&nbsp;&nbsp;&nbsp;&nbsp;以下合同即将过期或已经过期，请您及时续签或关闭,您可登录：<a href="http://123.56.147.94:8000">http://123.56.147.94:8000</a>查看详细信息</p>' + datas + u'</div>'
            self.send_email(user_id,body,subject)
    #邮件发送函数
    def send_email(self, cr, uid, users, body='',subject='',context=None):
        to_list = []
        for user in users:
            to_list.append(formataddr((Header(user.name, 'utf-8').encode(), user.email)))
        mail_mail = self.pool.get('mail.mail')
        mail_id = mail_mail.create(cr, uid, {
            'body_html': body,
            'subject': subject,
            'email_to': to_list,
            'auto_delete': True,
        }, context=context)
        mail_mail.browse(cr,uid,[mail_id],context=context).email_from = '<nantian_erp@nantian>'
        mail_mail.send(cr, uid, [mail_id], context=context)


    # @api.one
    # @api.depends('reject_date')
    # def reject(self):
    #     print self
    #     now = int(time.time())
    #     timeArray = time.strptime(self.reject_date, "%Y-%m-%d")
    #     old = int(time.mktime(timeArray))
    #     print self.device_ids.device_id, self.id, type(self.id)
    #     print self.name, type(now), type(old)
    #     print now, old
    #     print now < old
    #     if now < old:
    #         # now.append(self.name)
    #         print "*" * 20

        # print now
            # pool_contract = self.env["cinda_cmdb.contract_purchase"]
            # print self.env.cr
            # now_1 = pool_contract.search(['id', '=', self.id])
            # print now_1
            # record_servers = pool_contract.search(cr, uid, [('dev_id', '=', record.device_id.id)], offset=0)

class parts(models.Model):
    _name = "cinda_cmdb.parts"
    _description = '网络配件表'
    _rec_name = "parts_name"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _mail_post_access = 'read'

    parts_type = fields.Many2one("cinda_cmdb.base_type", string="配件类型", domain=[('class_id', 'ilike', "配件类型")])
    parts_name = fields.Char(string="配件名称")
    sn = fields.Char(string="序列号")
    brand_id = fields.Many2one("cinda_cmdb.base_type", string="品牌", domain=[('class_id', 'ilike', "设备品牌")])
    status_config = fields.Char(string="标准配置")
    parts_source = fields.Char(string="配件来源")
    use_state = fields.Selection([('online', '在用'), ('offline', '下线'),], default="", Require="False", string="使用状态")
    parts_in_device = fields.Many2one("cinda_cmdb.net_dev", string="配件所在设备")
    buy_date = fields.Date(string="购买时间")
    reject_date = fields.Date(string="过保时间")
    vendor = fields.Char(string="供应商")
    location = fields.Char(string="位置")
    number = fields.Integer(string="数量")
    area = fields.Char(string="区域")


class interface(models.Model):
    _name = "cinda_cmdb.interface"
    _description = "接口表"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _mail_post_access = 'read'

    name = fields.Char(sting="接口号")
    type = fields.Selection(
        [
            ('ethernet_electricity', "以太网电口"),
            ('ethernet_fiber', "以太网光口"),
            ('hba', "HBA"),
            ('virtual', "虚拟接口"),
        ],
        string="类型")
    mac = fields.Char(string="MAC地址")
    ip = fields.Char(string="IP地址")
    local_wwn = fields.Char(string="本端wwn")
    peer_wwn = fields.Char(string="对端WWN")
    device_id = fields.Many2one('cinda_cmdb.device', string="所在设备")
    server_id = fields.Many2one('cinda_cmdb.server')
    mini_pc_id = fields.Many2one('cinda_cmdb.mini_pc')
    st_dev_id = fields.Many2one('cinda_cmdb.st_dev')
    fc_switch_id = fields.Many2one('cinda_cmdb.fc_switch')
    tape_station_id = fields.Many2one('cinda_cmdb.tape_station')
    peer_device_id = fields.Many2one('cinda_cmdb.device', string="对端设备")
    peer_interface = fields.Many2one('cinda_cmdb.interface', string="对端接口(导入时勿选)", track_visibility='onchange')
    # 问： 字段中的 track_visibility='onchange' 有什么用   答： 当文档变动的时候，通知关注者。
    status = fields.Boolean(string="是否使用", compute='auto_change_peer', store=True, default=False)
    statuss = fields.Boolean(string="是否使用", store=True, default=False)
    interface_rate = fields.Char(string="本端接口速率")
    peer_rate = fields.Char(string="对端速率")
    purpose = fields.Char(string='用途', domain=[('class_id', 'ilike', "用途")])
    peer_interface_temp = fields.Char(string='对端接口')
    interface_temp = fields.Char(string='计算对端接口(导入时勿选)',compute='auto_compute_peer_interface',store=True )

    # 解决导入时接口名不唯一
    @api.one
    @api.depends('peer_interface_temp','peer_device_id')
    def auto_compute_peer_interface(self):
        self.interface_temp=self.peer_interface_temp
        peer_interface = self.env['cinda_cmdb.interface'].search([('name','=',self.peer_interface_temp),('device_id','=',self.peer_device_id.id)],limit=1)
        value_target = self.id
        col = 'id'
        if peer_interface:
            sql = '''UPDATE cinda_cmdb_interface
                          SET peer_interface = %s
                          WHERE %s = %s''' % \
                (peer_interface.id, col, value_target)
            self.env.cr.execute(sql)

    # 实现在增加、删除对端接口时，自动关联互联设备的对端接口，但修改对端接口时不能取消关联之前的设备
    @api.one
    @api.depends('peer_interface')
    def auto_change_peer(self):
        value_peer_interface = 'null'
        if type(self.id) == int:
            if self.peer_interface.id:
                # 增加
                if not self.statuss:
                    # 修改本条数据的statuss的状态为True
                    col_a = "id"
                    value_target_a = self.id
                    value_status_a = "True"
                    sql_a = '''UPDATE cinda_cmdb_interface
                                      SET statuss = %s
                                      WHERE %s = %s''' % \
                          (value_status_a, col_a, value_target_a)
                    self.env.cr.execute(sql_a)
                    # 然后增加相关联设备的对端接口的信息
                    value_peer_device_id = self.device_id.id
                    value_peer_interface = self.id
                    value_status = "True"
                    value_target = self.peer_interface.id
                    col = 'id'
                    self.statuss = "True"
                    sql = '''UPDATE cinda_cmdb_interface
                                  SET peer_device_id = %s, peer_interface = %s , status = %s
                                  WHERE %s = %s''' % \
                      (value_peer_device_id, value_peer_interface, value_status, col, value_target)
                    self.env.cr.execute(sql)
                # 修改
                else:
                    # 第一步先删除相关联设备的对端接口的值
                    # 修改后，之前关联的设备的对端设备字段peer_device_id是不是也应该改为null???
                    value_peer_device_id = self.device_id.id
                    value_target = self.id
                    value_status = "False"
                    # print "*** 先删除 ***" * 50
                    col = 'peer_interface'
                    self.statuss = "False"
                    sql = '''UPDATE cinda_cmdb_interface
                          SET peer_device_id = %s, peer_interface = %s , status = %s
                          WHERE %s = %s''' % \
                          (value_peer_device_id, value_peer_interface, value_status, col, value_target)
                    self.env.cr.execute(sql)
                    # 第二步 保证本条数据的statuss仍然为True
                    col_a = "id"
                    value_target_a = self.id
                    value_status_a = "True"
                    sql_a = '''UPDATE cinda_cmdb_interface
                                      SET statuss = %s
                                      WHERE %s = %s''' % \
                          (value_status_a, col_a, value_target_a)
                    self.env.cr.execute(sql_a)
                    # 第三步 更新对应的相关联设备的对端接口的数据
                    value_peer_device_id = self.device_id.id
                    value_target = self.peer_interface.id
                    value_status = "False"
                    value_peer_interface = self.id
                    # print "*** 后增加 ***" * 50
                    col = 'id'
                    self.statuss = "True"
                    sql_c = '''UPDATE cinda_cmdb_interface
                          SET peer_device_id = %s, peer_interface = %s , statuss = %s
                          WHERE %s = %s''' % \
                          (value_peer_device_id, value_peer_interface, value_status, col, value_target)
                    self.env.cr.execute(sql_c)
            #删除
            else:
                # 第一步 先删除之前相关联的设备的对端接口数据
                value_peer_device_id = self.device_id.id
                value_target = self.id
                value_status = "False"
                col = 'peer_interface'
                # self.statuss = "False"
                # print '### 删除 ###'* 10
                sql = '''UPDATE cinda_cmdb_interface
                                  SET peer_device_id = %s, peer_interface = %s , status = %s, statuss = %s
                                  WHERE %s = %s''' % \
                      (value_peer_device_id, value_peer_interface, value_status, value_status, col, value_target)
                print sql
                self.env.cr.execute(sql)
                # 第二步 要修改本条数据的statuss为False
                col_a = "id"
                value_target_a = self.id
                value_status_a = "False"
                sql_a = '''UPDATE cinda_cmdb_interface
                                  SET statuss = %s
                                  WHERE %s = %s''' % \
                      (value_status_a, col_a, value_target_a)
                self.env.cr.execute(sql_a)


    # 在接口表里面添加接口信息时，相应的在对应的表里面的一对多接口表的tree视图里面也显示接口信息；反之亦然，在二级表里面添加接口信息时，也要在interface表里面添加信息。
    def create(self, cr, uid, vals, context=None):
        id = super(interface, self).create(cr, uid, vals, context=context)
        record = self.browse(cr, uid, id, context=context)[0]
        if record.device_id:
            record_name = record.device_id.type_id.type_name
            if record_name == "PC服务器":
                pool_server = self.pool.get("cinda_cmdb.server")
                record_servers = pool_server.search(cr, uid, [('dev_id', '=', record.device_id.id)], offset=0)
                record.server_id = record_servers[0]
            elif record_name == "小型计算机":
                pool_mini_pc = self.pool.get("cinda_cmdb.mini_pc")
                record.mini_pc_id = pool_mini_pc.search(cr, uid, [('dev_id', '=', record.device_id.id)], offset=0)[0]
            elif record_name in ["存储",  "磁盘阵列",  "存储扩展柜"]:
                pool_st_dev = self.pool.get("cinda_cmdb.st_dev")
                record.st_dev_id = pool_st_dev.search(cr, uid, [('dev_id', '=', record.device_id.id)], offset=0)[0]
            elif record_name in ["光纤交换机", "光纤连接器"]:
                pool_fc_switch = self.pool.get("cinda_cmdb.fc_switch")
                record.fc_switch_id = pool_fc_switch.search(cr, uid, [('dev_id', '=', record.device_id.id)], offset=0)[0]
            elif record_name in ["磁带机", "磁带库"]:
                pool_tape_station = self.pool.get("cinda_cmdb.tape_station")
                record.tape_station_id = pool_tape_station.search(cr, uid, [('dev_id', '=', record.device_id.id)], offset=0)[0]
        else:
            if record.server_id:
                record.device_id = self.pool.get("cinda_cmdb.server").browse(cr, uid, record.server_id.id).dev_id.id
            elif record.mini_pc_id:
                print '&&&&&&&&&&&&&&&&&&&', record, record.mini_pc_id, record.mini_pc_id.id
                record_mini_pc = self.pool.get("cinda_cmdb.mini_pc").browse(cr, uid, record.mini_pc_id.id)
                record.device_id = record_mini_pc.dev_id.id
            elif record.st_dev_id:
                record.device_id = self.pool.get("cinda_cmdb.st_dev").browse(cr, uid, record.st_dev_id.id).dev_id.id
            elif record.fc_switch_id:
                record.device_id = self.pool.get("cinda_cmdb.fc_switch").browse(cr, uid, record.fc_switch_id.id).dev_id.id
            elif record.tape_station_id:
                record.device_id = self.pool.get("cinda_cmdb.tape_station").browse(cr, uid, record.tape_station_id.id).dev_id
        return id

        # conn = psycopg2.connect(database="rain298",user="root", password="root",host="127.0.0.1",port="5432")
        # cur = conn.cursor()




class st_part(models.Model):
    _name = "cinda_cmdb.st_part"
    _description = "存储组件表"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _mail_post_access = 'read'

    name = fields.Char(string="存储组件名称")
    st_id = fields.Many2one("cinda_cmdb.st_dev", string="存储ID")
    type = fields.Selection([
        ("control", "控制器"),
        ("cage", "机笼")
    ],
            string="类型")
    st_part_id = fields.Integer(string="存储组件ID")
    lab_id = fields.Many2one("cinda_cmdb.base_type", string='机房', domain=[('class_id', 'ilike', "机房")])
    cab = fields.Many2one("cinda_cmdb.cabinet", string="机柜")
    pos_seq = fields.Integer(string="位置序号")
    u_pos = fields.Many2one("cinda_cmdb.base_type", string="位置U", domain=[('class_id', 'ilike', "位置代号")])
    u_space = fields.Integer(string="占位U")
    sn = fields.Char(string="序列号")
    cage_disk_num = fields.Integer(string="笼内已装磁盘数")
    single_disk_size = fields.Float(string="单个磁盘容量")
    disk_spec = fields.Char(string="磁盘规格")
    head_data_disk = fields.Char(string="机头数据盘")
    head_backup_disk = fields.Char(string="机头热备盘")
    enable_size = fields.Float(string="可使用容量(T)")
    allocated_size = fields.Float(string="已分配容量(T)")
    remain_enable_size = fields.Float(string="剩余可用容量(T)")
    admin_ip = fields.Char(string="管理IP")
    t_netcard_num = fields.Integer(string="万兆网口数")
    g_netcard_num = fields.Integer(string="千兆网口数")
    four_g_fc_port = fields.Char(string="4g光纤端口")
    eight_g_fc_port = fields.Char(string="8g光纤端口")
    sixteen_g_fc_port = fields.Char(string="16g光纤端口")
    thirty_two_g_fc_port = fields.Char(string="32g光纤端口")
    cache_config = fields.Float(string="缓存配置(G)")
    nvram = fields.Float(string="NVRAM(G)")
    memory = fields.Float(string="内存(G)")


class fc_switch(models.Model):
    _name = "cinda_cmdb.fc_switch"
    _description = "光纤交换机表"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _mail_post_access = 'read'

    dev_id = fields.Many2one("cinda_cmdb.device", string="设备id",
                             domain=[('type_id.type_name', 'ilike', "光纤交换机")])
    interface_ids = fields.One2many('cinda_cmdb.interface', 'fc_switch_id', string="光口", domain=[('type', 'in', ["ethernet_fiber", "hba"])])
    interface_ids_a = fields.One2many('cinda_cmdb.interface', 'fc_switch_id', string="电口", domain=[('type', '=', "ethernet_electricity")])
    valid_port_number = fields.Integer(string="有效口总数")
    four_g_module_number = fields.Integer(string="4G模块总数")
    eight_g_module_number = fields.Integer(string="8G模块总数")
    sixteen_g_module_number = fields.Integer(string="16G模块总数")
    used_port_number = fields.Integer(string="已使用口数")
    four_g_module_used_number = fields.Integer(string="4G模块已使用的总数")
    eight_g_module_used_number = fields.Integer(string="8G模块已使用的总数")
    sixteen_g_module_used_number = fields.Integer(string="16G模块已使用的总数")
    ip = fields.Char(string="IP")
    #以下是device表中引用过来用来展示的字段
    host_name = fields.Char(related="dev_id.host_name", string="设备命名")
    type_id = fields.Many2one(related="dev_id.type_id", string="设备类型", domain=[('type_name', 'ilike', "光纤交换机")], store="Ture")
    brand_id = fields.Many2one(related="dev_id.brand_id", string="品牌")
    product_name = fields.Char(related="dev_id.product_name", string="产品型号")
    sn = fields.Char(related="dev_id.sn", string="序列号")
    model = fields.Char(related="dev_id.model", string="Model")
    use_mode = fields.Selection(related="dev_id.use_mode", string="使用状态")
    dev_start = fields.Selection(related="dev_id.dev_start", string="设备状态")
    asset_num_old = fields.Char(related="dev_id.asset_num_old", string="旧资产编号")
    asset_num = fields.Char(related="dev_id.asset_num", string="资产编号")
    purpose = fields.Char(related="dev_id.purpose", string="用途")
    owner_id = fields.Many2one(related="dev_id.owner_id", string="资产所有人")
    user = fields.Many2one(related="dev_id.user",  string="使用人")
    admin = fields.Many2one(related="dev_id.admin", string="管理人")
    comment = fields.Char(related="dev_id.comment", string="备注")
    lab_id = fields.Many2one(related="dev_id.lab_id", string="机房")
    cab = fields.Many2one(related="dev_id.cab", string="机柜")
    pos_seq = fields.Integer(related="dev_id.pos_seq", string="位置序号")
    u_pos = fields.Many2one(related="dev_id.u_pos", string="位置U")
    u_space = fields.Integer(related="dev_id.u_space", string="占位U")
    env_id = fields.Many2one(related="dev_id.env_id", string="环境")
    srve_prvd = fields.Many2one(related="dev_id.srve_prvd", string="服务商")
    contract_ids = fields.Many2many(related="dev_id.contract_ids", string="采购合同编号")
    accept_date = fields.Char(related="dev_id.accept_date", string="初验日期")
    reject_date = fields.Char(related="dev_id.reject_date", string="过保日期")
    last_upd = fields.Datetime(related="dev_id.last_upd", string="最后截止日期")



class tape_station(models.Model):
    _name = "cinda_cmdb.tape_station"
    _description = "磁带机磁带库"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _mail_post_access = 'read'

    dev_id = fields.Many2one("cinda_cmdb.device", string="设备资产id",
                             domain=[('type_id.type_name', 'ilike', "磁带机")])
    interface_ids = fields.One2many("cinda_cmdb.interface", "tape_station_id",  string="接口", domain=[('type', 'in', ["ethernet_fiber", "hba", "ethernet_fiber"])])
    driver = fields.Char(string="驱动器")
    tape = fields.Char(string="磁带")
    ip = fields.Char(string="IP")
    cleaning_tape = fields.Char(string="清洗带")
    disk_controller = fields.Char(string="磁盘控制柜")
    extend_cab_num = fields.Integer(string="扩展柜数")
    disk_num = fields.Integer(string="磁盘数")
    da_port_number = fields.Integer(string="DA端口数")
    ha_port_number = fields.Integer(string="HA端口数")
    #以下是device表中引用过来用来展示的字段
    host_name = fields.Char(related="dev_id.host_name", string="设备命名")
    type_id = fields.Many2one(related="dev_id.type_id", string="设备类型", domain=['|',('type_name', 'ilike', "磁带机"),('type_name', 'ilike', "磁带库")], store="Ture")
    brand_id = fields.Many2one(related="dev_id.brand_id", string="品牌")
    product_name = fields.Char(related="dev_id.product_name", string="产品型号")
    sn = fields.Char(related="dev_id.sn", string="序列号")
    model = fields.Char(related="dev_id.model", string="Model")
    use_mode = fields.Selection(related="dev_id.use_mode", string="使用状态")
    dev_start = fields.Selection(related="dev_id.dev_start", string="设备状态")
    asset_num_old = fields.Char(related="dev_id.asset_num_old", string="旧资产编号")
    asset_num = fields.Char(related="dev_id.asset_num", string="资产编号")
    purpose = fields.Char(related="dev_id.purpose", string="用途")
    owner_id = fields.Many2one(related="dev_id.owner_id", string="资产所有人")
    user = fields.Many2one(related="dev_id.user",  string="使用人")
    admin = fields.Many2one(related="dev_id.admin", string="管理人")
    comment = fields.Char(related="dev_id.comment", string="备注")
    lab_id = fields.Many2one(related="dev_id.lab_id", string="机房")
    cab = fields.Many2one(related="dev_id.cab", string="机柜")
    pos_seq = fields.Integer(related="dev_id.pos_seq", string="位置序号")
    u_pos = fields.Many2one(related="dev_id.u_pos", string="位置U")
    u_space = fields.Integer(related="dev_id.u_space", string="占位U")
    env_id = fields.Many2one(related="dev_id.env_id", string="环境")
    srve_prvd = fields.Many2one(related="dev_id.srve_prvd", string="服务商")
    contract_ids = fields.Many2many(related="dev_id.contract_ids", string="采购合同编号")
    accept_date = fields.Char(related="dev_id.accept_date", string="初验日期")
    reject_date = fields.Char(related="dev_id.reject_date", string="过保日期")


class mini_pc(models.Model):
    _name = "cinda_cmdb.mini_pc"
    _description = '小型计算机'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _mail_post_access = 'read'

    dev_id = fields.Many2one("cinda_cmdb.device", string="设备id",
                             domain=[('type_id.type_name', 'ilike', "小型计算机")])
    sn_id = fields.Char(related="dev_id.sn", string="所属设备序列号")
    interface_ids_a = fields.One2many('cinda_cmdb.interface', 'mini_pc_id', string="HBA卡接口", domain=[('type', '=', "hba")])
    interface_ids = fields.One2many('cinda_cmdb.interface', 'mini_pc_id', string="网卡接口",  domain=[('type', 'in', ['ethernet_electricity', 'ethernet_fiber'])])
    dev_name = fields.Char(string="设备名称")
    cpu_num = fields.Integer(string="CPU数量")
    single_cpu_num = fields.Integer(string="单CPU核数")
    cpu_sum = fields.Integer(string="CPU总核数", compute="_cpu_sum", store="True")
    cpu_spec = fields.Char(string="CPU规格")
    mem_num = fields.Integer(string="内存条数")
    single_mem_size = fields.Float(string="单条内存容量")
    mem_sum = fields.Float(string="内存总容量", compute="_mem_sum", store="True")
    mem_spec = fields.Char(string="内存规格")
    disk_spec = fields.Char(string="硬盘规格1")
    disk_num = fields.Integer(string="硬盘数量1")
    single_disk_size = fields.Float(string="单硬盘容量1")
    disk_spec_two = fields.Char(string="硬盘规格2")
    disk_num_two = fields.Integer(string="硬盘数量2")
    single_disk_size_two = fields.Float(string="单硬盘容量2")
    disk_sum = fields.Float(string="硬盘总容量", compute="_disk_sum", store="True")
    four_g_hba_num = fields.Integer(string="4G HBA卡数量")
    four_g_hba_used_num = fields.Integer(string="4G HBA卡已用数量")
    eight_g_hba_num = fields.Integer(string="8G HBA卡数量")
    eight_g_hba_used_num = fields.Integer(string="8G HBA卡已用数量")
    sixteen_g_hba_num = fields.Integer(string="16G HBA卡数量")
    sixteen_g_hba_used_num = fields.Integer(string="16G HBA卡已用数量")
    thirty_two_g_hba_num = fields.Integer(string="32G HBA卡数量")
    thirty_two_g_hba_used_num = fields.Integer(string="32G HBA卡已用数量")
    g_netcard_num = fields.Integer(string="千兆网口数量")
    g_netcard_used_num = fields.Integer(string="千兆网口已用数量")
    t_netcard_num = fields.Integer(string="万兆网口数量")
    t_netcard_used_num = fields.Integer(string="万兆网口已用数量")
    extend_cab_num = fields.Integer(string="扩展柜数量")
    tape_station_num = fields.Integer(string="磁带机数量")
    lpar_num = fields.Integer(string="LPAR数量")
    admin_ip =fields.Char(string="管理网IP")
    admin_info = fields.Char(string="管理口信息点")
    os = fields.Char(string="底层操作系统")
    app_sys = fields.Char(string="所属系统")
    buss_ip_addr = fields.Char(string="业务网IP地址")
    #以下是device表中引用过来用来展示的字段
    host_name = fields.Char(related="dev_id.host_name", string="设备命名")
    type_id = fields.Many2one(related="dev_id.type_id", string="设备类型", domain=[('type_name', 'ilike', "小型计算机")], store="Ture")
    brand_id = fields.Many2one(related="dev_id.brand_id", string="品牌")
    product_name = fields.Char(related="dev_id.product_name", string="产品型号")
    # sn = fields.Char(related="dev_id.sn", string="序列号")
    model = fields.Char(related="dev_id.model", string="Model")
    use_mode = fields.Selection(related="dev_id.use_mode", string="使用状态")
    dev_start = fields.Selection(related="dev_id.dev_start", string="设备状态")
    asset_num_old = fields.Char(related="dev_id.asset_num_old", string="旧资产编号")
    asset_num = fields.Char(related="dev_id.asset_num", string="资产编号")
    purpose = fields.Char(related="dev_id.purpose", string="用途")
    owner_id = fields.Many2one(related="dev_id.owner_id", string="资产所有人")
    user = fields.Many2one(related="dev_id.user",  string="使用人")
    admin = fields.Many2one(related="dev_id.admin", string="管理人")
    comment = fields.Char(related="dev_id.comment", string="备注")
    lab_id = fields.Many2one(related="dev_id.lab_id", string="机房")
    cab = fields.Many2one(related="dev_id.cab", string="机柜")
    pos_seq = fields.Integer(related="dev_id.pos_seq", string="位置序号")
    u_pos = fields.Many2one(related="dev_id.u_pos", string="位置U")
    u_space = fields.Integer(related="dev_id.u_space", string="占位U")
    env_id = fields.Many2one(related="dev_id.env_id", string="环境")
    srve_prvd = fields.Many2one(related="dev_id.srve_prvd", string="服务商")
    contract_ids = fields.Many2many(related="dev_id.contract_ids", string="采购合同编号")
    accept_date = fields.Char(related="dev_id.accept_date", string="初验日期")
    reject_date = fields.Char(related="dev_id.reject_date", string="过保日期")
    last_upd = fields.Datetime(related="dev_id.last_upd", string="最后截止日期")


    #计算CPU核数量
    @api.multi
    @api.depends('cpu_num', 'single_cpu_num')
    def _cpu_sum(self):
        for r in self:
            r.cpu_sum = r.single_cpu_num * r.cpu_num

    # 计算内存总容量
    @api.multi
    @api.depends('mem_num', 'single_mem_size')
    def _mem_sum(self):
        for r in self:
            r.mem_sum = r.mem_num * r.single_mem_size

    #计算硬盘总容量
    @api.multi
    @api.depends('disk_num', 'single_disk_size', 'disk_num_two', 'single_disk_size_two')
    def _disk_sum(self):
        for r in self:
            r.disk_sum = (r.disk_num * r.single_disk_size)+(r.disk_num_two * r.single_disk_size_two)


class fc_interface(models.Model):
    dev_id = fields.Many2one("cinda_cmdb.device", string="设备id",
                             domain=[('type_id.type_name', 'ilike', "PC服务器"),
                                     ('type_id.type_name', 'ilike', "小型计算机"),
                                     ('type_id.type_name', 'ilike', "存储组件"),
                                     ('type_id.type_name', 'ilike', "光纤交换机"),
                                     ('type_id.type_name', 'ilike', "磁带机磁带库")])
    host_sort = fields.Char(string="主机分类")
    host_id = fields.Char(string="主机ID")
    wwn = fields.Char(string="WWN地址")
    type_id = fields.Integer(string="设备类型")
    speed = fields.Char(string="速率")
    fc_card_name = fields.Char(string="光纤卡名")
    slot = fields.Char(string="槽位")
    alias = fields.Char(string="别名")


class sys_relation(models.Model):
    a_config_sort = fields.Char(string="A配置分类")
    a_config_id = fields.Char(string="A配置项ID")
    b_config_sort = fields.Char(sting="B配置分类")
    b_config_id = fields.Char(string="B配置项ID")
    relation_type = fields.Selection([("1", "连接"),
                                      ("2", "依赖于"),
                                      ("3", "运行于"),
                                      ("4", "安装于"),
                                      ("5", "组成"),
                                      ("6", "备份")], string="关系类型")
    relation_state = fields.Char(string="关系说明")
