/**
 * Created by Administrator on 2019/7/16.
 */
$(function () {
    $('#save-banner-btn').click(function (event) {
        event.preventDefault();
        var self = $(this);
        var dialog = $('#banner-dialog');
        var nameinput = $("input[name='name']");
        var imageinput = $("input[name='image_url']");
        var linkinput = $("input[name='link_url']");
        var priorityinput = $("input[name='priority']");

        var name = nameinput.val();
        var image_url = imageinput.val();
        var link_url = linkinput.val();
        var priority = priorityinput.val();
        var submitType = self.attr('data-type');  // 获取修改标签
        var bannerid = self.attr('data-id');  // 获取id

        if (!name || !image_url || !link_url || !priority) {
            zlalert.alertInfoToast('请输入完整的轮播图数据');
            return;
        }
        var url = '';
        if (submitType == 'update') {
            url = '/cms/ubanner/';
        } else {
            url = '/cms/abanner/'
        }
        zlajax.post({
            'url': url,
            'data': {
                'name': name,
                'image_url': image_url,
                'link_url': link_url,
                'priority': priority,
                'banner_id': bannerid
            },
            'success': function (data) {
                dialog.modal('hide');
                if (data['code'] == 200) {
                    // 重新加载当前页面
                    window.location.reload()
                } else {
                    zlalert.alertInfo(data['message']);
                }
            },
            'fail': function (error) {
                zlalert.alertNetworkError()
            }
        });
    });
});

$(function () {
    $('.edit-banner-btn').click(function (event) {
        // 获取当前点击对象
        var self = $(this);
        var dialog = $('#banner-dialog');
        // 显示弹框
        dialog.modal('show');
        // 获取绑定在首级标签上的值，便于回填到输入框中
        var tr = self.parent().parent();
        var name = tr.attr('data-name');
        var image_url = tr.attr('data-image');
        var link_url = tr.attr('data-link');
        var priority = tr.attr('data-priority');
        // 获取输入框
        var nameinput = dialog.find("input[name='name']");
        var imageinput = dialog.find("input[name='image_url']");
        var linkinput = dialog.find("input[name='link_url']");
        var priorityinput = dialog.find("input[name='priority']");
        var saveBtn = dialog.find('#save-banner-btn');  // 获取点击标签传递修改事件
        // 将值填入框中
        nameinput.val(name);
        imageinput.val(image_url);
        linkinput.val(link_url);
        priorityinput.val(priority);
        saveBtn.attr('data-type', 'update');  //绑定标签属性
        saveBtn.attr('data-id', tr.attr('data-id'));  // 绑定id
    });
});

$(function () {
    $(".delete-banner-btn").click(function (event) {
        var self = $(this);
        var tr = self.parent().parent();
        var banner_id = tr.attr('data-id');
        zlalert.alertConfirm({
            "msg": "您确定要删除这个轮播图吗？",
            'confirmCallback': function () {
                zlajax.post({
                    'url': '/cms/dbanner/',
                    'data': {
                        'banner_id': banner_id
                    },
                    'success': function (data) {
                        if (data['code'] == 200) {
                            window.location.reload();
                        } else {
                            zlalert.alertInfo(data['message']);
                        }
                    }
                })
            }
        });
    });
});