from django.core.mail.backends.smtp import EmailBackend
import smtplib

class CustomEmailBackend(EmailBackend):
    def open(self):
        """Fix Python 3.12 'keyfile' issue with SMTP.starttls()."""
        if self.connection:
            return False
        try:
            self.connection = smtplib.SMTP(self.host, self.port, timeout=self.timeout)
            self.connection.ehlo()
            if self.use_tls:
                self.connection.starttls()  # Removed unexpected arguments
                self.connection.ehlo()
            if self.username and self.password:
                self.connection.login(self.username, self.password)
            return True
        except:
            if self.fail_silently:
                return False
            raise