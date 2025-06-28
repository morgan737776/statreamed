from hl7apy.core import Message

def export_patient_to_hl7(patient):
    msg = Message("ADT_A01")
    msg.msh.msh_3 = "MIS"
    msg.msh.msh_4 = "RehabCenter"
    msg.msh.msh_9 = "ADT^A01"
    msg.msh.msh_10 = "123456"
    msg.msh.msh_11 = "P"
    msg.msh.msh_12 = "2.5"
    msg.pid.pid_3 = getattr(patient, 'snils', '')
    msg.pid.pid_5 = f"{patient.last_name}^{patient.first_name}"
    msg.pid.pid_7 = patient.birth_date.strftime("%Y%m%d")
    return msg.to_er7()
