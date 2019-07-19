from flask_wtf import Form


class BaseForm(Form):
    # 抽象父类方法，定义错误信息
    def get_error(self):
        message = self.errors.popitem()[1][0]
        return message