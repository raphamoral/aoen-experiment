from enum import Enum


class ComplianceArea(str, Enum):
    LGPD = "LGPD"
    GDPR = "GDPR"
    SOX = "SOX"
    BASEL_III = "BASEL_III"
    AML_KYC = "AML_KYC"
    ISO_27001 = "ISO_27001"
    PCI_DSS = "PCI_DSS"
    HIPAA = "HIPAA"
    COBIT = "COBIT"
    COSO = "COSO"
    IFRS = "IFRS"
    CVM = "CVM"