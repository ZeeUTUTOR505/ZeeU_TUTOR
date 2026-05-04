from utils.common import EmailServicec


class EmailService:

    @staticmethod
    def send_register(name, grade, phone):
        return EmailServicec.send_email(name, grade, phone)

    @staticmethod
    def send_exam(**kwargs):
        return EmailServicec.send_exam_result_email(**kwargs)
