from django.shortcuts import render, redirect
from django.views import View
from goods.models import GoodsChannel
from contents.models import ContentCategory
from meiduo.utils import my_category


class IndexView(View):
    def get(self, request):
        # 1. 定义字典categories
        categories = {}

        # 2. 获取频道（一级分类）
        channels = GoodsChannel.objects.order_by("group_id", "sequence")

        # 3. 遍历频道
        for channel in channels:
            # 3.1 获取频道中的组号
            group_id = channel.group_id
            # 3.2 判断组号是否在categories中
            if group_id not in categories:
                categories[group_id] = {"channels": [], "sub_cats": []}

            # 3.3 获取一级分类
            category1 = channel.category
            category1_dict = {
                "id": channel.id,
                "name": category1.name,
                "url": channel.url
            }
            # 3.4 添加一级分类到categories中
            categories[group_id]["channels"].append(category1_dict)
            # 3.5 获取二级分类
            cats2 = category1.subs.all()
            for cat2 in cats2:
                categories[group_id]["sub_cats"].append(cat2)

        # 4 查询分类广告数据
        contents = {}
        content_category = ContentCategory.objects.order_by("id")
        for category in content_category:
            contents[category.key] = category.content_set.all()

        # 5 组装返回数据
        # categories = my_category.get_categories()
        context = {
            "categories": categories,
            "contents": contents,
        }

        return render(request, "index.html", context=context)

