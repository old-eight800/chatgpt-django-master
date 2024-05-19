from django.db import models
import os
import hashlib

# Create your models here.


class ImageMessage(models.Model):
    id = models.AutoField(primary_key=True)
    baseUserId = models.IntegerField(verbose_name="用户ID", null=True, blank=True, help_text="用户ID")
    uuid = models.CharField(max_length=255, verbose_name="唯一编码", null=True, blank=True, help_text="唯一编码")
    prompt = models.TextField(verbose_name="提示语", null=True, blank=True, help_text="提示语")
    draw_model = models.CharField(max_length=32, verbose_name="绘画模型", null=True, blank=True, help_text="绘画模型")
    imageQuality = models.CharField(max_length=16, verbose_name="图像质量", null=True, blank=True, help_text="图像质量")
    size = models.CharField(max_length=255, verbose_name="生成分辨率", null=True, blank=True, help_text="生成分辨率")
    number = models.IntegerField(verbose_name="生成数量", null=True, blank=True, help_text="生成数量", default=1)
    res_data = models.JSONField(verbose_name="返回的图片数据", null=True)
    update_datetime = models.DateTimeField(auto_now=True, null=True, blank=True, help_text="修改时间", verbose_name="修改时间")
    create_datetime = models.DateTimeField(auto_now_add=True, null=True, blank=True, help_text="创建时间", verbose_name="创建时间")

    
    class Meta:
        db_table = "Image_message"
        verbose_name = "图片消息表"
        verbose_name_plural = verbose_name
        ordering = ("-create_datetime",)

def media_file_name(instance, filename):
    h = instance.md5sum
    basename, ext = os.path.splitext(filename)
    # 创建文件保存
    return os.path.join("static", "template", "files", h[0:1], h[1:2], h + ext.lower())


class FileList(models.Model):

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, null=True, blank=True, verbose_name="名称", help_text="名称")
    url = models.FileField(upload_to=media_file_name)
    md5sum = models.CharField(max_length=36, blank=True, verbose_name="文件md5", help_text="文件md5")
    update_datetime = models.DateTimeField(auto_now=True, null=True, blank=True, help_text="修改时间", verbose_name="修改时间")
    create_datetime = models.DateTimeField(auto_now_add=True, null=True, blank=True, help_text="创建时间", verbose_name="创建时间")

    def save(self, *args, **kwargs):
        if not self.md5sum:  # file is new
            md5 = hashlib.md5()
            for chunk in self.url.chunks():
                md5.update(chunk)
            self.md5sum = md5.hexdigest()
        super(FileList, self).save(*args, **kwargs)

    class Meta:
        db_table = "Image_file"
        verbose_name = "文件管理"
        verbose_name_plural = verbose_name
        ordering = ("-create_datetime",)
