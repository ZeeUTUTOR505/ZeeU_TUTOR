from utils.common import PasswordGenerator


class AuthService:

    @staticmethod
    def validate(input_password, password_type):
        if password_type == "prelearn":
            expected = PasswordGenerator.generate_pretest_password()
        else:
            expected = PasswordGenerator.generate_exam_password()

        return input_password == expected
