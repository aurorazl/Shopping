from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.db.models import Q
from django.utils.safestring import mark_safe
from django.db import models
import hashlib
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    mobile = models.CharField(verbose_name="手机号码", max_length=15, unique=True)
    avatar = models.ImageField(upload_to='avatar', verbose_name='用户头像', null=True, blank=True,
                               help_text="头像图片的大小规格：256x256，或者对应的比例的图片")
    class Meta:
        db_table = 'luffy_user'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username

class BaseModel(models.Model):
    """公共模型"""
    orders = models.IntegerField(verbose_name='显示顺序')
    is_show = models.BooleanField(verbose_name="是否上架", default=False)
    is_delete = models.BooleanField(verbose_name="逻辑删除", default=False)
    created_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True, null=True, blank=True)
    updated_time = models.DateTimeField(verbose_name="更新时间", auto_now=True, null=True, blank=True)
    class Meta:
        # 抽象模型，一般用于设置公共模型字段的，一旦设置这个相关以后，那么dajngo在数据迁移的时候就不会为这个模型单独创建一个数据表了
        abstract=True

class Banner(BaseModel):
    """轮播图"""
    # upload_to 存储子目录，真实存放地址会使用配置中的MADIE_ROOT+upload_to
    image = models.ImageField(upload_to='banner', verbose_name='轮播图', null=True, blank=True)
    name = models.CharField(max_length=150, verbose_name='轮播图名称')
    note = models.CharField(max_length=150, verbose_name='备注信息')
    link = models.CharField(max_length=150, verbose_name='轮播图广告地址')
    # orders = models.IntegerField(verbose_name='显示顺序')
    # is_show=models.BooleanField(verbose_name="是否上架", default=False)
    # is_delete=models.BooleanField(verbose_name="逻辑删除", default=False)

    class Meta:
        db_table = 'luffy_banner'
        verbose_name = '轮播图'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

class Nav(BaseModel):
    """导航"""
    NAV_POSITION = (
        (0, '顶部导航'),
        (1, '底部导航')
    )
    name = models.CharField(max_length=50, verbose_name='导航名称')
    link = models.CharField(max_length=250, verbose_name='导航地址')
    opt = models.SmallIntegerField(choices=NAV_POSITION, default=0, verbose_name='位置')

    class Meta:
        db_table = 'luffy_nav'
        verbose_name = '导航'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

# ########################### 1.课程相关 ################################
class TCourse(models.Model):
    """
    课程表
    """
    title = models.CharField(verbose_name='课程名称',max_length=32)
    course_img = models.CharField(verbose_name='课程图片',max_length=64)
    level_choices = (
        (1,'初级'),
        (2,'中级'),
        (3,'高级'),
    )
    level = models.IntegerField(verbose_name='课程难易程度',choices=level_choices,default=1)

    def __str__(self):
        return self.title

class CourseDetail(models.Model):
    """
    课程详细
    """
    course = models.OneToOneField(to='TCourse',on_delete=models.CASCADE)
    slogon = models.CharField(verbose_name='口号',max_length=255)
    why = models.CharField(verbose_name='为什么要学？',max_length=255)
    recommend_courses = models.ManyToManyField(verbose_name='推荐课程',to='TCourse',related_name='rc')

    def __str__(self):
        return "课程详细："+self.course.title

class Chapter(models.Model):
    """
    章节
    """
    num =  models.IntegerField(verbose_name='章节')
    name = models.CharField(verbose_name='章节名称',max_length=32)
    course = models.ForeignKey(verbose_name='所属课程',to='TCourse',on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class UserInfo(models.Model):
    user = models.CharField(max_length=32)
    pwd = models.CharField(max_length=32)
    balance = models.PositiveIntegerField(default=0, verbose_name="可提现和使用余额")

class Token(models.Model):
    user = models.OneToOneField(UserInfo,on_delete=models.CASCADE)
    token = models.CharField(max_length=32)


#=================================================================
class CourseCategory(models.Model):
    """课程大类, e.g 前端  后端..."""
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return "%s" % self.name

    class Meta:
        verbose_name_plural = "01.课程大类"


class CourseSubCategory(models.Model):
    """课程子类, e.g python linux """
    category = models.ForeignKey("CourseCategory",on_delete=models.CASCADE)
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return "%s" % self.name

    class Meta:
        verbose_name_plural = "02.课程子类"

class DegreeCourse(models.Model):
    """学位课程"""
    name = models.CharField(max_length=128, unique=True)
    course_img = models.CharField(max_length=255, verbose_name="缩略图")
    brief = models.TextField(verbose_name="学位课程简介", )
    total_scholarship = models.PositiveIntegerField(verbose_name="总奖学金(贝里)", default=40000)
    mentor_compensation_bonus = models.PositiveIntegerField(verbose_name="本课程的导师辅导费用(贝里)", default=15000)
    # 用于GenericForeignKey反向查询， 不会生成表字段，切勿删除
    coupon = GenericRelation("Coupon")
    # 为了计算学位奖学金
    period = models.PositiveIntegerField(verbose_name="建议学习周期(days)", default=150)
    prerequisite = models.TextField(verbose_name="课程先修要求", max_length=1024)
    teachers = models.ManyToManyField("Teacher", verbose_name="课程讲师")
    # 用于GenericForeignKey反向查询，不会生成表字段，切勿删除
    degreecourse_price_policy = GenericRelation("PricePolicy")

    def __str__(self):
        return self.name

class Scholarship(models.Model):
    """学位课程奖学金"""
    degree_course = models.ForeignKey("DegreeCourse",on_delete=models.CASCADE)
    time_percent = models.PositiveSmallIntegerField(verbose_name="奖励档位(时间百分比)", help_text="只填百分值，如80,代表80%")
    value = models.PositiveIntegerField(verbose_name="奖学金数额")

    def __str__(self):
        return "%s:%s" % (self.degree_course, self.value)

    class Meta:
        verbose_name_plural = "05.学位课奖学金"

class Course(models.Model):
    """课程"""
    name = models.CharField(max_length=128, unique=True)
    course_img = models.CharField(max_length=255)
    sub_category = models.ForeignKey("CourseSubCategory",on_delete=models.CASCADE)
    course_type_choices = ((0, '付费'), (1, 'VIP专享'), (2, '学位课程'))
    course_type = models.SmallIntegerField(choices=course_type_choices)
    degree_course = models.ForeignKey("DegreeCourse", blank=True, null=True, help_text="若是学位课程，此处关联学位表",on_delete=models.CASCADE)
    brief = models.TextField(verbose_name="课程概述", max_length=2048)
    level_choices = ((0, '初级'), (1, '中级'), (2, '高级'))
    level = models.SmallIntegerField(choices=level_choices, default=1)
    pub_date = models.DateField(verbose_name="发布日期", blank=True, null=True)
    period = models.PositiveIntegerField(verbose_name="建议学习周期(days)", default=7)
    order = models.IntegerField("课程顺序", help_text="从上一个课程数字往后排")
    attachment_path = models.CharField(max_length=128, verbose_name="课件路径", blank=True, null=True)
    status_choices = ((0, '上线'), (1, '下线'), (2, '预上线'))
    status = models.SmallIntegerField(choices=status_choices, default=0)
    template_id = models.SmallIntegerField("前端模板id", default=1)
    coupon = GenericRelation("Coupon")
    # 用于GenericForeignKey反向查询，不会生成表字段，切勿删除
    price_policy = GenericRelation("PricePolicy")

    def __str__(self):
        return "%s(%s)" % (self.name, self.get_course_type_display())

    def save(self, *args, **kwargs):
        if self.course_type == 2:
            if not self.degree_course:
                raise ValueError("学位课程必须关联对应的学位表")
        super(Course, self).save(*args, **kwargs)

class CourseDetail_new(models.Model):
    """课程详情页内容"""
    course = models.OneToOneField("Course",on_delete=models.CASCADE)
    hours = models.IntegerField("课时")
    course_slogan = models.CharField(max_length=125, blank=True, null=True)
    video_brief_link = models.CharField(verbose_name='课程介绍', max_length=255, blank=True, null=True)
    why_study = models.TextField(verbose_name="为什么学习这门课程")
    what_to_study_brief = models.TextField(verbose_name="我将学到哪些内容")
    career_improvement = models.TextField(verbose_name="此项目如何有助于我的职业生涯")
    prerequisite = models.TextField(verbose_name="课程先修要求", max_length=1024)
    recommend_courses = models.ManyToManyField("Course", related_name="recommend_by", blank=True)
    teachers = models.ManyToManyField("Teacher", verbose_name="课程讲师")

    def __str__(self):
        return "%s" % self.course

    class Meta:
        verbose_name_plural = "07.课程或学位模块详细"

class OftenAskedQuestion(models.Model):
    """常见问题"""
    content_type = models.ForeignKey(ContentType,on_delete=models.CASCADE)  # 关联course or degree_course
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    question = models.CharField(max_length=255)
    answer = models.TextField(max_length=1024)

    def __str__(self):
        return "%s-%s" % (self.content_object, self.question)

    class Meta:
        unique_together = ('content_type', 'object_id', 'question')
        verbose_name_plural = "08. 常见问题"


class CourseOutline(models.Model):
    """课程大纲"""
    course_detail = models.ForeignKey("CourseDetail_new",on_delete=models.CASCADE)

    # 前端显示顺序
    order = models.PositiveSmallIntegerField(default=1)

    title = models.CharField(max_length=128)
    content = models.TextField("内容", max_length=2048)

    def __str__(self):
        return "%s" % self.title

    class Meta:
        unique_together = ('course_detail', 'title')
        verbose_name_plural = "09. 课程大纲"

class CourseChapter(models.Model):
    """课程章节"""
    course = models.ForeignKey("Course", related_name='coursechapters',on_delete=models.CASCADE)
    chapter = models.SmallIntegerField(verbose_name="第几章", default=1)
    name = models.CharField(max_length=128)
    summary = models.TextField(verbose_name="章节介绍", blank=True, null=True)
    pub_date = models.DateField(verbose_name="发布日期", auto_now_add=True)

    class Meta:
        unique_together = ("course", 'chapter')
        verbose_name_plural = "10. 课程章节"

    def __str__(self):
        return "%s:(第%s章)%s" % (self.course, self.chapter, self.name)

class Teacher(models.Model):
    """讲师、导师表"""
    name = models.CharField(max_length=32)
    role_choices = ((0, '讲师'), (1, '导师'))
    role = models.SmallIntegerField(choices=role_choices, default=0)
    title = models.CharField(max_length=64, verbose_name="职位、职称")
    signature = models.CharField(max_length=255, help_text="导师签名", blank=True, null=True)
    image = models.CharField(max_length=128)
    brief = models.TextField(max_length=1024)

    def __str__(self):
        return self.name

class CourseSection(models.Model):
    """课时目录"""
    chapter = models.ForeignKey("CourseChapter", related_name='coursesections',on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    order = models.PositiveSmallIntegerField(verbose_name="课时排序", help_text="建议每个课时之间空1至2个值，以备后续插入课时")
    section_type_choices = ((0, '文档'), (1, '练习'), (2, '视频'))
    section_type = models.SmallIntegerField(default=2, choices=section_type_choices)
    # 59EE3275E977AADB9C33DC5901307461
    section_link = models.CharField(max_length=255, blank=True, null=True, help_text="若是video，填vid,若是文档，填link")

    video_time = models.CharField(verbose_name="视频时长", blank=True, null=True, max_length=32)  # 仅在前端展示使用
    pub_date = models.DateTimeField(verbose_name="发布时间", auto_now_add=True)
    free_trail = models.BooleanField("是否可试看", default=False)

    class Meta:
        unique_together = ('chapter', 'section_link')
        verbose_name_plural = "11. 课时"

    def __str__(self):
        return "%s-%s" % (self.chapter, self.name)


class PricePolicy(models.Model):
    """价格与有课程效期表"""
    content_type = models.ForeignKey(ContentType,on_delete=models.CASCADE)  # 关联course or degree_course
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    # course = models.ForeignKey("Course")
    valid_period_choices = ((1, '1天'), (3, '3天'),
                            (7, '1周'), (14, '2周'),
                            (30, '1个月'),
                            (60, '2个月'),
                            (90, '3个月'),
                            (180, '6个月'), (210, '12个月'),
                            (540, '18个月'), (720, '24个月'),
                            )
    valid_period = models.SmallIntegerField(choices=valid_period_choices)
    price = models.FloatField()

    class Meta:
        unique_together = ("content_type", 'object_id', "valid_period")

    def __str__(self):
        return "%s(%s)%s" % (self.content_object, self.get_valid_period_display(), self.price)


class Homework(models.Model):
    """章节作业"""
    chapter = models.ForeignKey("CourseChapter",on_delete=models.CASCADE)
    title = models.CharField(max_length=128, verbose_name="作业题目")
    order = models.PositiveSmallIntegerField("作业顺序", help_text="同一课程的每个作业之前的order值间隔1-2个数")
    homework_type_choices = ((0, '作业'), (1, '模块通关考核'))
    homework_type = models.SmallIntegerField(choices=homework_type_choices, default=0)
    requirement = models.TextField(max_length=1024, verbose_name="作业需求")
    threshold = models.TextField(max_length=1024, verbose_name="踩分点")
    recommend_period = models.PositiveSmallIntegerField("推荐完成周期(天)", default=7)
    scholarship_value = models.PositiveSmallIntegerField("为该作业分配的奖学金(贝里)")
    note = models.TextField(blank=True, null=True)
    enabled = models.BooleanField(default=True, help_text="本作业如果后期不需要了，不想让学员看到，可以设置为False")

    class Meta:
        unique_together = ("chapter", "title")
        verbose_name_plural = "12. 章节作业"

    def __str__(self):
        return "%s - %s" % (self.chapter, self.title)

#
class CourseReview(models.Model):
    """课程评价"""
    enrolled_course = models.OneToOneField("EnrolledCourse",on_delete=models.CASCADE)
    about_teacher = models.FloatField(default=0, verbose_name="讲师讲解是否清晰")
    about_video = models.FloatField(default=0, verbose_name="内容实用")
    about_course = models.FloatField(default=0, verbose_name="课程内容通俗易懂")
    review = models.TextField(max_length=1024, verbose_name="评价")
    disagree_number = models.IntegerField(default=0, verbose_name="踩")
    agree_number = models.IntegerField(default=0, verbose_name="赞同数")
    tags = models.ManyToManyField("Tags", blank=True, verbose_name="标签")
    date = models.DateTimeField(auto_now_add=True, verbose_name="评价日期")
    is_recommend = models.BooleanField("热评推荐", default=False)
    hide = models.BooleanField("不在前端页面显示此条评价", default=False)

    def __str__(self):
        return "%s-%s" % (self.enrolled_course.course, self.review)

    class Meta:
        verbose_name_plural = "13. 课程评价（购买课程后才能评价）"
#
#
class DegreeCourseReview(models.Model):
    """学位课程评价
    为了以后可以定制单独的评价内容，所以不与普通课程的评价混在一起，单独建表
    """
    enrolled_course = models.ForeignKey("EnrolledDegreeCourse",on_delete=models.CASCADE)
    course = models.ForeignKey("Course", verbose_name="评价学位模块", blank=True, null=True,
                               help_text="不填写即代表评价整个学位课程", limit_choices_to={'course_type': 2},on_delete=models.CASCADE)
    about_teacher = models.FloatField(default=0, verbose_name="讲师讲解是否清晰")
    about_video = models.FloatField(default=0, verbose_name="视频质量")
    about_course = models.FloatField(default=0, verbose_name="课程")
    review = models.TextField(max_length=1024, verbose_name="评价")
    disagree_number = models.IntegerField(default=0, verbose_name="踩")
    agree_number = models.IntegerField(default=0, verbose_name="赞同数")
    tags = models.ManyToManyField("Tags", blank=True, verbose_name="标签")
    date = models.DateTimeField(auto_now_add=True, verbose_name="评价日期")
    is_recommend = models.BooleanField("热评推荐", default=False)
    hide = models.BooleanField("不在前端页面显示此条评价", default=False)

    def __str__(self):
        return "%s-%s" % (self.enrolled_course, self.review)

    class Meta:
        verbose_name_plural = "14. 学位课评价（购买课程后才能评价）"
#

# ######################## 深科技相关 ########################
class ArticleSource(models.Model):
    """文章来源"""
    name = models.CharField(max_length=64, unique=True)

    class Meta:
        verbose_name_plural = "16. 文章来源"

    def __str__(self):
        return self.name


class Article(models.Model):
    """文章资讯"""
    title = models.CharField(max_length=255, unique=True, db_index=True, verbose_name="标题")
    source = models.ForeignKey("ArticleSource", verbose_name="来源",on_delete=models.CASCADE)
    article_type_choices = ((0, '资讯'), (1, '视频'))
    article_type = models.SmallIntegerField(choices=article_type_choices, default=0)
    brief = models.TextField(max_length=512, verbose_name="摘要")
    head_img = models.CharField(max_length=255)
    content = models.TextField(verbose_name="文章正文")
    pub_date = models.DateTimeField(verbose_name="上架日期")
    offline_date = models.DateTimeField(verbose_name="下架日期")
    status_choices = ((0, '在线'), (1, '下线'))
    status = models.SmallIntegerField(choices=status_choices, default=0, verbose_name="状态")
    order = models.SmallIntegerField(default=0, verbose_name="权重", help_text="文章想置顶，可以把数字调大，不要超过1000")
    vid = models.CharField(max_length=128, verbose_name="视频VID", help_text="文章类型是视频, 则需要添加视频VID", blank=True, null=True)
    comment_num = models.SmallIntegerField(default=0, verbose_name="评论数")
    agree_num = models.SmallIntegerField(default=0, verbose_name="点赞数")
    view_num = models.SmallIntegerField(default=0, verbose_name="观看数")
    collect_num = models.SmallIntegerField(default=0, verbose_name="收藏数")

    # tags = models.ManyToManyField("Tags", blank=True, verbose_name="标签")
    date = models.DateTimeField(auto_now_add=True, verbose_name="创建日期")

    position_choices = ((0, '信息流'), (1, 'banner大图'), (2, 'banner小图'))
    position = models.SmallIntegerField(choices=position_choices, default=0, verbose_name="位置")

    # comment = GenericRelation("Comment")

    class Meta:
        verbose_name_plural = "17. 文章"

    def __str__(self):
        return "%s-%s" % (self.source, self.title)


class Collection(models.Model):
    """收藏"""
    content_type = models.ForeignKey(ContentType,on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    account = models.ForeignKey("Account",on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('content_type', 'object_id', 'account')
        verbose_name_plural = "18. 通用收藏表"


class Comment(models.Model):
    """通用的评论表"""
    content_type = models.ForeignKey(ContentType, blank=True, null=True, verbose_name="类型",on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    p_node = models.ForeignKey("self", blank=True, null=True, verbose_name="父级评论",on_delete=models.CASCADE)
    content = models.TextField(max_length=1024)
    account = models.ForeignKey("Account", verbose_name="会员名",on_delete=models.CASCADE)
    disagree_number = models.IntegerField(default=0, verbose_name="踩")
    agree_number = models.IntegerField(default=0, verbose_name="赞同数")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content

    class Meta:
        verbose_name_plural = "19. 通用评论表"
# ########################### 3. 用户相关 ################################
class Account(models.Model):
    """用户表"""
    username = models.CharField("用户名", max_length=64, unique=True)
    password = models.CharField("密码", max_length=64)

    uid = models.CharField(max_length=64, unique=True, help_text='微信用户绑定和CC视频统计',blank=True, null=True)  # 与第3方交互用户信息时，用这个uid,以避免泄露敏感用户信息
    openid = models.CharField(max_length=128, blank=True, null=True)
    # 贝里余额
    balance = models.PositiveIntegerField(default=0, verbose_name="可提现和使用余额")
    def __str__(self):
        return self.username

    class Meta:
        verbose_name_plural = "20. 用户表"


class UserAuthToken(models.Model):
    """
    用户Token表
    """
    user = models.OneToOneField(to="Account",on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return '用户{}Token'.format(self.user)

    class Meta:
        verbose_name_plural = "21. 用户Token表"

#===================================================
import hashlib
class UserInfo2(models.Model):
    username = models.CharField("用户名", max_length=64, unique=True)
    password = models.CharField("密码", max_length=64)
    uid = models.CharField(verbose_name='个人唯一ID',max_length=64, unique=True)
    wx_id = models.CharField(verbose_name="微信ID", max_length=128, blank=True, null=True, db_index=True)

    def save(self, *args, **kwargs):
        # 创建用户时，为用户自动生成个人唯一ID
        if not self.pk:
            m = hashlib.md5()
            m.update(self.username.encode(encoding="utf-8"))
            self.uid = m.hexdigest()
        super(UserInfo2, self).save(*args, **kwargs)

# ########################### 优惠券 ################################
class Coupon(models.Model):
    """优惠券生成规则"""
    name = models.CharField(max_length=64, verbose_name="活动名称")
    brief = models.TextField(blank=True, null=True, verbose_name="优惠券介绍")
    coupon_type_choices = ((0, '通用券'), (1, '满减券'), (2, '折扣券'))
    coupon_type = models.SmallIntegerField(choices=coupon_type_choices, default=0, verbose_name="券类型")

    """
    通用：
        money_equivalent_value=100
        off_percent=null
        minimum_consume=0
    满减：
        money_equivalent_value=100
        off_percent=null
        minimum_consume=1000
    折扣：
        money_equivalent_value=0        # 0表示零门槛
        off_percent=79
        minimum_consume=0
    """
    money_equivalent_value = models.IntegerField(verbose_name="等值货币")
    off_percent = models.PositiveSmallIntegerField("折扣百分比", help_text="只针对折扣券，例7.9折，写79", blank=True, null=True)
    minimum_consume = models.PositiveIntegerField("最低消费", default=0, help_text="仅在满减券时填写此字段")

    content_type = models.ForeignKey(ContentType, blank=True, null=True,on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField("绑定课程", blank=True, null=True, help_text="可以把优惠券跟课程绑定")
    content_object = GenericForeignKey('content_type', 'object_id')

    quantity = models.PositiveIntegerField("数量(张)", default=1)
    open_date = models.DateField("优惠券领取开始时间")
    close_date = models.DateField("优惠券领取结束时间")
    valid_begin_date = models.DateField(verbose_name="有效期开始时间", blank=True, null=True)
    valid_end_date = models.DateField(verbose_name="有效结束时间", blank=True, null=True)
    coupon_valid_days = models.PositiveIntegerField(verbose_name="优惠券有效期（天）", blank=True, null=True,
                                                    help_text="自券被领时开始算起")
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "31. 优惠券生成记录"

    def __str__(self):
        return "%s(%s)" % (self.get_coupon_type_display(), self.name)

    def save(self, *args, **kwargs):
        if not self.coupon_valid_days or (self.valid_begin_date and self.valid_end_date):
            if self.valid_begin_date and self.valid_end_date:
                if self.valid_end_date <= self.valid_begin_date:
                    raise ValueError("valid_end_date 有效期结束日期必须晚于 valid_begin_date ")
            if self.coupon_valid_days == 0:
                raise ValueError("coupon_valid_days 有效期不能为0")
        if self.close_date < self.open_date:
            raise ValueError("close_date 优惠券领取结束时间必须晚于 open_date优惠券领取开始时间 ")

        super(Coupon, self).save(*args, **kwargs)


class CouponRecord(models.Model):
    """优惠券发放、消费纪录"""
    coupon = models.ForeignKey("Coupon",on_delete=models.CASCADE)
    number = models.CharField(max_length=64, unique=True)   # 优惠券的唯一id
    account = models.ForeignKey("UserInfo", verbose_name="拥有者",on_delete=models.CASCADE)
    status_choices = ((0, '未使用'), (1, '已使用'), (2, '已过期'))
    status = models.SmallIntegerField(choices=status_choices, default=0)
    get_time = models.DateTimeField(verbose_name="领取时间", help_text="用户领取时间")
    used_time = models.DateTimeField(blank=True, null=True, verbose_name="使用时间")
    order = models.ForeignKey("Order", blank=True, null=True, verbose_name="关联订单",on_delete=models.CASCADE)  # 一个订单可以有多个优惠券

    class Meta:
        verbose_name_plural = "32. 用户优惠券"

    def __str__(self):
        return '%s-%s-%s' % (self.account, self.number, self.status)

# ########################### 4. 奖惩相关 ################################

class ScoreRule(models.Model):
    """积分规则"""
    score_rule_choices = (
        (0, '未按时交作业'),
        (1, '未及时批改作业'),
        (2, '作业成绩'),
        (3, '未在规定时间内对学员进行跟进'),
        (4, '未在规定时间内回复学员问题'),
        (5, '收到学员投诉'),
        (6, '导师相关'),
        (7, '学位奖学金'),
    )
    rule = models.SmallIntegerField(choices=score_rule_choices, verbose_name="积分规则")
    score_type_choices = ((0, '奖励'), (1, '惩罚'), (2, '初始分配'))
    score_type = models.SmallIntegerField(choices=score_type_choices, verbose_name="奖惩", default=0)
    score = models.IntegerField(help_text="扣分数与贝里相等,若为0则代表规则的值可以从别处取得")
    # maturity_days = models.IntegerField("成熟周期", help_text="自纪录创建时开始计算")
    memo = models.TextField(blank=True, null=True)

    def __str__(self):
        return "%s-%s:%s" % (self.get_rule_display(), self.get_score_type_display(), self.score)

    class Meta:
        unique_together = ('rule', 'score_type')
        verbose_name_plural = "29. 奖惩规则"


class ScoreRecord(models.Model):
    """积分奖惩记录"""
    content_type = models.ForeignKey(ContentType, blank=True, null=True,on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    degree_course = models.ForeignKey("DegreeCourse", blank=True, null=True, verbose_name="关联学位课程",on_delete=models.CASCADE)
    score_rule = models.ForeignKey("ScoreRule", verbose_name="关联规则",on_delete=models.CASCADE)
    account = models.ForeignKey("Account", verbose_name="被执行人",on_delete=models.CASCADE)
    score = models.IntegerField(verbose_name="金额(贝里)")  # 这里单独有一个字段存积分而不是从score_rule里引用的原因是考虑到如果引用的话， # 一旦score_rule里的积分有变更，那么所有用户的历史积分也会被影响
    received_score = models.IntegerField("实际到账金额贝里)", help_text="仅奖励用", default=0)
    balance = models.PositiveIntegerField(verbose_name="奖金余额(贝里)")

    maturity_date = models.DateField("成熟日期(可提现日期)")
    applied = models.BooleanField(default=False, help_text="奖赏纪录是否已被执行", verbose_name="是否已被执行")
    applied_date = models.DateTimeField(blank=True, null=True, verbose_name="事件生效日期")
    date = models.DateTimeField(auto_now_add=True, verbose_name="事件触发日期")
    memo = models.TextField(blank=True, null=True)

    def __str__(self):
        return "%s-%s - %s - %s 奖金余额:%s" % (self.id, self.score_rule, self.account, self.score, self.balance)

    class Meta:
        verbose_name_plural = "30. 奖惩记录"

class CourseSchedule(models.Model):
    """课程进度计划表,针对学位课程，每开通一个模块，就为这个学员生成这个模块的推荐学习计划表，后面的奖惩均按此表进行"""
    study_record = models.ForeignKey("StudyRecord",on_delete=models.CASCADE)
    homework = models.ForeignKey("Homework",on_delete=models.CASCADE)
    recommend_date = models.DateField("推荐交作业日期")

    def __str__(self):
        return "%s - %s - %s " % (self.study_record, self.homework, self.recommend_date)

    class Meta:
        unique_together = ('study_record', 'homework')
        verbose_name_plural = "33. 课程模块计划表（学位课）"


class EnrolledCourse(models.Model):
    """已报名课程,不包括学位课程"""
    account = models.ForeignKey("Account",on_delete=models.CASCADE)
    course = models.ForeignKey("Course", limit_choices_to=~Q(course_type=2),on_delete=models.CASCADE)
    enrolled_date = models.DateTimeField(auto_now_add=True)
    valid_begin_date = models.DateField(verbose_name="有效期开始自")
    valid_end_date = models.DateField(verbose_name="有效期结束至")
    status_choices = ((0, '已开通'), (1, '已过期'))
    status = models.SmallIntegerField(choices=status_choices, default=0)
    order_detail = models.OneToOneField("OrderDetail",on_delete=models.CASCADE)  # 使订单购买后支持 课程评价

    # order = models.ForeignKey("Order",blank=True,null=True)

    def __str__(self):
        return "%s:%s" % (self.account, self.course)

    class Meta:
        verbose_name_plural = "34. 报名专题课"


class DegreeRegistrationForm(models.Model):
    """学位课程报名表"""
    enrolled_degree = models.OneToOneField("EnrolledDegreeCourse",on_delete=models.CASCADE)
    current_company = models.CharField(max_length=64, )
    current_position = models.CharField(max_length=64, )
    current_salary = models.IntegerField()
    work_experience_choices = ((0, "应届生"),
                               (1, "1年"),
                               (2, "2年"),
                               (3, "3年"),
                               (4, "4年"),
                               (5, "5年"),
                               (6, "6年"),
                               (7, "7年"),
                               (8, "8年"),
                               (9, "9年"),
                               (10, "10年"),
                               (11, "超过10年"),
                               )
    work_experience = models.IntegerField()
    open_module = models.BooleanField("是否开通第1模块", default=True)
    stu_specified_mentor = models.CharField("学员自行指定的导师名", max_length=32, blank=True, null=True)
    study_plan_choices = ((0, "1-2小时/天"),
                          (1, "2-3小时/天"),
                          (2, "3-5小时/天"),
                          (3, "5小时+/天"),
                          )
    study_plan = models.SmallIntegerField(choices=study_plan_choices, default=1)
    why_take_this_course = models.TextField("报此课程原因", max_length=1024)
    why_choose_us = models.TextField("为何选路飞", max_length=1024)
    your_expectation = models.TextField("你的期待", max_length=1024)
    memo = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name_plural = "35. 报名表（学位课）"

    def __str__(self):
        return "%s" % self.enrolled_degree


class EnrolledDegreeCourse(models.Model):
    """已报名的学位课程"""
    account = models.ForeignKey("Account",on_delete=models.CASCADE)
    degree_course = models.ForeignKey("DegreeCourse",on_delete=models.CASCADE)
    enrolled_date = models.DateTimeField(auto_now_add=True)
    valid_begin_date = models.DateField(verbose_name="有效期开始自", blank=True, null=True)  # 开通第一个模块时，再添加课程有效期，2年
    valid_end_date = models.DateField(verbose_name="有效期结束至", blank=True, null=True)
    status_choices = (
        (0, '在学中'),
        (1, '休学中'),
        (2, '已毕业'),
        (3, '超时结业'),
        (4, '未开始'),
        # (3, '其它'),
    )
    study_status = models.SmallIntegerField(choices=status_choices, default=0)
    mentor = models.ForeignKey("Account", verbose_name="导师", related_name='my_students',
                               blank=True, null=True, limit_choices_to={'role': 1},on_delete=models.CASCADE)
    mentor_fee_balance = models.PositiveIntegerField("导师费用余额", help_text="这个学员的导师费用，每有惩罚，需在此字段同时扣除")
    order_detail = models.OneToOneField("OrderDetail",on_delete=models.CASCADE)  # 使订单购买后支持填写报名表

    def __str__(self):
        return "%s:%s" % (self.account, self.degree_course)

    class Meta:
        unique_together = ('account', 'degree_course')
        verbose_name_plural = "36. 报名学位课"


class Order(models.Model):
    """订单"""
    payment_type_choices = ((0, '微信'), (1, '支付宝'), (2, '优惠码'), (3, '贝里'))
    payment_type = models.SmallIntegerField(choices=payment_type_choices)

    payment_number = models.CharField(max_length=128, verbose_name="支付第3方订单号", null=True, blank=True)
    order_number = models.CharField(max_length=128, verbose_name="订单号", unique=True)  # 考虑到订单合并支付的问题
    account = models.ForeignKey("Account",on_delete=models.CASCADE)
    actual_amount = models.FloatField(verbose_name="实付金额")

    status_choices = ((0, '交易成功'), (1, '待支付'), (2, '退费申请中'), (3, '已退费'), (4, '主动取消'), (5, '超时取消'))
    status = models.SmallIntegerField(choices=status_choices, verbose_name="状态")
    date = models.DateTimeField(auto_now_add=True, verbose_name="订单生成时间")
    pay_time = models.DateTimeField(blank=True, null=True, verbose_name="付款时间")
    cancel_time = models.DateTimeField(blank=True, null=True, verbose_name="订单取消时间")

    class Meta:
        verbose_name_plural = "37. 订单表"

    def __str__(self):
        return "%s" % self.order_number


class OrderDetail(models.Model):
    """订单详情"""
    order = models.ForeignKey("Order",on_delete=models.CASCADE)

    content_type = models.ForeignKey(ContentType,on_delete=models.CASCADE)  # 可关联普通课程或学位
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    original_price = models.FloatField("课程原价")
    price = models.FloatField("折后价格")
    content = models.CharField(max_length=255, blank=True, null=True)  # ？
    valid_period_display = models.CharField("有效期显示", max_length=32)  # 在订单页显示
    valid_period = models.PositiveIntegerField("有效期(days)")  # 课程有效期
    memo = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return "%s - %s - %s" % (self.order, self.content_type, self.price)

    class Meta:
        verbose_name_plural = "38. 订单详细"
        unique_together = ("order", 'content_type', 'object_id')


class StudyRecord(models.Model):
    """学位课程的模块学习进度，报名学位课程后，每个模块会立刻生成一条学习纪录"""
    enrolled_degree_course = models.ForeignKey("EnrolledDegreeCourse",on_delete=models.CASCADE)
    course_module = models.ForeignKey("Course", verbose_name="学位模块", limit_choices_to={'course_type': 2},on_delete=models.CASCADE)
    open_date = models.DateField(blank=True, null=True, verbose_name="开通日期")
    end_date = models.DateField(blank=True, null=True, verbose_name="完成日期")
    status_choices = ((2, '在学'), (1, '未开通'), (0, '已完成'))
    status = models.SmallIntegerField(choices=status_choices, default=1)

    class Meta:
        verbose_name_plural = "39. 学习记录表（报名学位课程后，每个模块会立刻生成一条学习纪录）"
        unique_together = ('enrolled_degree_course', 'course_module')

    def __str__(self):
        return '%s-%s' % (self.enrolled_degree_course, self.course_module)

    def save(self, *args, **kwargs):
        if self.course_module.degree_course_id != self.enrolled_degree_course.degree_course_id:
            raise ValueError("学员要开通的模块必须与其报名的学位课程一致！")

        super(StudyRecord, self).save(*args, **kwargs)


class TransactionRecord(models.Model):
    """贝里交易纪录"""
    account = models.ForeignKey("Account",on_delete=models.CASCADE)
    amount = models.IntegerField("金额")
    balance = models.IntegerField("账户余额",blank=True, null=True)
    transaction_type_choices = ((0, '收入'), (1, '支出'), (2, '退款'), (3, "提现"))  # 2 为了处理 订单过期未支付时，锁定期贝里的回退
    transaction_type = models.SmallIntegerField(choices=transaction_type_choices)

    content_type = models.ForeignKey(ContentType, blank=True, null=True,on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(blank=True, null=True, verbose_name="关联对象")
    content_object = GenericForeignKey('content_type', 'object_id')

    transaction_number = models.CharField(unique=True, verbose_name="流水号", max_length=128)
    date = models.DateTimeField(auto_now_add=True)
    memo = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        verbose_name_plural = "40. 贝里交易记录"

    def __str__(self):
        return "%s" % self.transaction_number


class HomeworkRecord(models.Model):
    """学员作业记录及成绩"""
    homework = models.ForeignKey("Homework",on_delete=models.CASCADE)
    student = models.ForeignKey("EnrolledDegreeCourse", verbose_name="学生",on_delete=models.CASCADE)
    score_choices = ((100, 'A+'),
                     (90, 'A'),
                     (85, 'B+'),
                     (80, 'B'),
                     (70, 'B-'),
                     (60, 'C+'),
                     (50, 'C'),
                     (40, 'C-'),
                     (-1, 'D'),
                     (0, 'N/A'),
                     (-100, 'COPY'),
                     )
    score = models.SmallIntegerField(verbose_name="分数", choices=score_choices, null=True, blank=True)
    mentor = models.ForeignKey("Account", related_name="my_stu_homework_record", limit_choices_to={'role': 1},
                               verbose_name="导师",on_delete=models.CASCADE)
    mentor_comment = models.TextField(verbose_name="导师批注", blank=True, null=True)  # 导师
    status_choice = (
        (0, '待批改'),
        (1, '已通过'),
        (2, '不合格'),
    )
    status = models.SmallIntegerField(verbose_name='作业状态', choices=status_choice, default=0)

    submit_num = models.SmallIntegerField(verbose_name='提交次数', default=0)
    correct_date = models.DateTimeField('备注日期', blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    date = models.DateTimeField("作业提交日期", auto_now_add=True)

    check_date = models.DateTimeField("批改日期", null=True, blank=True)

    update_time = models.DateTimeField(auto_now=True, verbose_name="提交日期")

    # homework_path = models.CharField(verbose_name='作业路径', max_length=256,blank=True,null=True) 作业路径可以动态拿到，没必要存

    reward_choice = ((0, '新提交'),
                     (1, '按时提交'),
                     (2, '未按时提交'),
                     (3, '成绩已奖励'),
                     (4, '成绩已处罚'),
                     (5, '未作按时检测'),
                     )
    reward_status = models.SmallIntegerField(verbose_name='作业记录奖惩状态', default=0)

    def __str__(self):
        return "%s %s" % (self.homework, self.student)

    class Meta:
        verbose_name_plural = "41. 作业"
        unique_together = ("homework", "student")


class StuFollowUpRecord(models.Model):
    """学员跟进记录"""
    enrolled_degree_course = models.ForeignKey("EnrolledDegreeCourse", verbose_name="学生",on_delete=models.CASCADE)
    mentor = models.ForeignKey("Account", related_name='mentor', limit_choices_to={'role': 1}, verbose_name="导师",on_delete=models.CASCADE)
    followup_tool_choices = ((0, 'QQ'), (1, '微信'), (2, '电话'), (3, '系统通知'))
    followup_tool = models.SmallIntegerField(choices=followup_tool_choices, default=1)
    record = models.TextField(verbose_name="跟进记录")
    attachment_path = models.CharField(max_length=128, blank=True, null=True, verbose_name="附件路径", help_text="跟进记录的截图等")
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "42. 学员跟进记录"

    def __str__(self):
        return "%s --%s --%s" % (self.enrolled_degree_course, self.record, self.date)

class Question(models.Model):
    """课程提问"""
    name = models.CharField(max_length=128, blank=True, null=True, verbose_name="问题概要", db_index=True)
    question_type_choices = ((0, '专题课程问题'), (1, '学位课程问题'))
    question_type = models.SmallIntegerField(choices=question_type_choices, default=0, verbose_name="来源")
    account = models.ForeignKey("Account", verbose_name="提问者",on_delete=models.CASCADE)
    degree_course = models.ForeignKey("DegreeCourse", blank=True, null=True,on_delete=models.CASCADE)  # 若是针对整个学位课程的提问，关联这个
    course_section = models.ForeignKey("CourseSection", blank=True, null=True,on_delete=models.CASCADE)  # 针对整个学位课程的提问不需关联特定课时
    content = models.TextField(max_length=1024, verbose_name="问题内容")
    enquiries_count = models.IntegerField(default=0, verbose_name="同问者计数")
    attachment_path = models.CharField(max_length=128, blank=True, null=True, verbose_name="附件路径", help_text="问题记录的截图等")
    date = models.DateTimeField(auto_now_add=True)
    status_choices = ((0, '待解答'), (1, '已解答'), (2, '已关闭'))
    status = models.SmallIntegerField(choices=status_choices, default=0)

    def __str__(self):
        return "%s" % self.name

    def save(self, *args, **kwargs):
        if self.degree_course is None and self.course_section is None:
            raise ValueError("提的问题必须关联学位课程或具体课时！")

        super(Question, self).save(*args, **kwargs)

class Answer(models.Model):
    """问题解答"""
    question = models.ForeignKey("Question", verbose_name="问题",on_delete=models.CASCADE)
    content = models.TextField(verbose_name="回答")
    account = models.ForeignKey("Account", verbose_name="回答者",on_delete=models.CASCADE)
    agree_number = models.IntegerField(default=0, verbose_name="点赞数")
    disagree_number = models.IntegerField(default=0, verbose_name="点踩数")
    answer_date = models.DateTimeField(auto_now=True, verbose_name="日期")

    def __str__(self):
        return "%s" % self.question


class AnswerComment(models.Model):
    """答案回复评论"""
    answer = models.ForeignKey("Answer",on_delete=models.CASCADE)
    reply_to = models.ForeignKey("self", blank=True, null=True, verbose_name="基于评论的评论",on_delete=models.CASCADE)
    comment = models.TextField(max_length=512, verbose_name="评论内容")
    attachment_path = models.CharField(max_length=128, blank=True, null=True, verbose_name="附件路径", help_text="跟进记录的截图等")
    account = models.ForeignKey("Account", verbose_name="评论者",on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s - %s" % (self.account, self.comment)


class QACounter(models.Model):
    """ 问题和回答的赞同数量统计 """
    content_type = models.ForeignKey(ContentType,on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    data_type_choices = ((0, '点赞'), (1, '踩'), (2, '同问'))
    data_type = models.SmallIntegerField(choices=data_type_choices)
    account = models.ForeignKey("Account",on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("content_type", 'object_id', "account")

class Tags(models.Model):
    tag_type_choices = ((0, '文章标签'), (1, '课程评价标签'), (2, '用户感兴趣技术标签'))
    tag_type = models.SmallIntegerField(choices=tag_type_choices)
    name = models.CharField(max_length=64, unique=True, db_index=True)

    def __str__(self):
        return self.name


class Notification(models.Model):
    """消息通知纪录"""
    account = models.ForeignKey("Account", blank=True, null=True, help_text="不填用户的话代表给未注册用户发通知",on_delete=models.CASCADE)
    notify_obj = models.CharField(max_length=64, verbose_name='通知对象', help_text='account_id,email、mobile、open_id')
    content = models.TextField(max_length=1024)
    date = models.DateTimeField(auto_now_add=True, verbose_name='消息添加时间')
    msg_type_choices = (
        (0, "奖惩通知"),
        (1, "订单通知"),
        (2, "专题课程报名"),
        (3, "课程过期"),
        (4, "课程评论"),
        (5, "优惠券通知"),
        (6, "课程开课通知"),
        (7, "学位课程作业"),
        (8, "学位课程问答"),
        (9, "资讯阅读通知"),
        (11, "课程问答"),
        (12, "学位课程报名"),
        (13, "导师分配通知"),
        (15, "学位学习事务通知"),
        (16, "其他"),
    )

    msg_type = models.SmallIntegerField(choices=msg_type_choices)
    notify_type_choices = ((0, '站内信'), (1, '短信'), (2, '邮件'), (3, '微信'), (4, '其它'))
    notify_type = models.SmallIntegerField(choices=notify_type_choices)

    # notify_belong_choices = ((0, '站内事务通知'), (4, '课程相关通知'), (2, '资讯相关通知'))
    # notify_belong = models.SmallIntegerField(choices=notify_belong_choices)

    content_type = models.ForeignKey(ContentType, blank=True, null=True,on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(blank=True, null=True, verbose_name="关联对象")
    content_object = GenericForeignKey('content_type', 'object_id')

    apply_now = models.BooleanField(default=False, help_text="如果需要立刻通知用户，请勾选", verbose_name="是否立即执行")
    applied_status = models.BooleanField(default=False, help_text="消息通知是否已被执行", verbose_name="是否已被执行")
    excution_status = models.BooleanField("执行是否成功", default=False)
    excution_result = models.TextField("执行返回结果", blank=True, null=True)
    applied_date = models.DateTimeField(blank=True, null=True, verbose_name="通知日期时间", help_text="若不是立刻执行，需设置执行时间")

    def __str__(self):
        return '%s-%s-%s' % (self.notify_obj, self.msg_type, self.notify_type)


class MentorGroup(models.Model):
    """导师组"""

    name = models.CharField(max_length=64, unique=True)
    brief = models.TextField(blank=True, null=True)
    mentors = models.ManyToManyField("Account", limit_choices_to={'role': 1})

    def __str__(self):
        return self.name


class Feedback(models.Model):
    """用户反馈表"""
    name = models.CharField(max_length=32, blank=True, null=True)
    contact = models.CharField(max_length=64, blank=True, null=True)
    feedback_type_choices = ((0, '网站优化建议'), (1, '烂!我想吐槽'), (2, '网站bug反馈'))
    feedback_type = models.SmallIntegerField(choices=feedback_type_choices)
    content = models.TextField(max_length=1024)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class BulletScreen(models.Model):
    account = models.ForeignKey("Account",on_delete=models.CASCADE)  # 发弹幕的人
    content = models.CharField(max_length=255)  # 弹幕详情
    course_section = models.ForeignKey("CourseSection",on_delete=models.CASCADE)  # 具体发送到哪个课时(视频 )
    play_point = models.IntegerField()  # 发送弹幕的时间处于该课时视频的具体秒数
    date = models.DateTimeField(auto_now_add=True)  # 弹幕存储时间




