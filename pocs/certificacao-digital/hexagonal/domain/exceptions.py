class DomainException(Exception):
    pass


class CertificateNotFoundError(DomainException):
    def __init__(self, certificate_id: str):
        super().__init__(f"Certificate not found: {certificate_id}")
        self.certificate_id = certificate_id


class CertificateAlreadyRevokedError(DomainException):
    def __init__(self, certificate_id: str):
        super().__init__(f"Certificate already revoked: {certificate_id}")
        self.certificate_id = certificate_id


class DuplicateCertificateError(DomainException):
    def __init__(self, student_id: str, course_id: str):
        super().__init__(
            f"Active certificate already issued for student '{student_id}' on course '{course_id}'"
        )
        self.student_id = student_id
        self.course_id = course_id