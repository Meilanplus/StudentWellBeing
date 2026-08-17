# Role codes used across registration, login, and the role-assignment page.
# Mirrors the 6-role structure from the source Roles-and-Tasks matrix.
# "guru_kelas" from the old project (a non-registerable specialization of
# guru with an identical task set) is intentionally not carried forward —
# it added no distinct permissions and cannot be granted via any task in the
# matrix, so it's dropped here to keep the seeded role table an exact 1:1
# match with the image.
ROLE_GURU = "guru"
ROLE_COUNSELOR = "counselor"
ROLE_PK_HEM = "pk_hem"
ROLE_GURU_BESAR = "guru_besar"
ROLE_ADMIN_SEKOLAH = "admin_sekolah"
ROLE_SUPER_ADMIN = "super_admin"

ALL_ROLES = [
    ROLE_GURU,
    ROLE_COUNSELOR,
    ROLE_PK_HEM,
    ROLE_GURU_BESAR,
    ROLE_ADMIN_SEKOLAH,
    ROLE_SUPER_ADMIN,
]

ROLE_NAMES = {
    ROLE_GURU: "Teacher",
    ROLE_COUNSELOR: "Counselor",
    ROLE_PK_HEM: "Assistant Headmaster",
    ROLE_GURU_BESAR: "Headmaster",
    ROLE_ADMIN_SEKOLAH: "School Admin",
    ROLE_SUPER_ADMIN: "Super Admin",
}

# ── Task definitions (S.No 1-16 from the source Roles-and-Tasks matrix) ────
TASK_FILL_STUDENT_DETAIL = 1
TASK_FILL_STUDENT_RELATED_INFO = 2
TASK_INVOKE_AGENT1_RISK = 3
TASK_INVOKE_AGENT2_INTERVENTION = 4
TASK_REGISTER_TEACHER_OWN_SCHOOL = 5
TASK_REGISTER_TEACHER_ANY_SCHOOL = 6
TASK_REGISTER_COUNSELOR_OWN_SCHOOL = 7
TASK_REGISTER_COUNSELOR_ANY_SCHOOL = 8
TASK_INVOKE_AGENT3_REFERRAL = 9
TASK_REGISTER_ASST_HEADMASTER_OWN_SCHOOL = 10
TASK_REGISTER_ASST_HEADMASTER_ANY_SCHOOL = 11
TASK_REGISTER_HEADMASTER_OWN_SCHOOL = 12
TASK_REGISTER_HEADMASTER_ANY_SCHOOL = 13
TASK_VIEW_EDIT_ALL_DATA_OWN_SCHOOL = 14
TASK_VIEW_EDIT_ALL_DATA_ANY_SCHOOL = 15
TASK_INVOKE_AGENT4_REPORTING = 16

TASK_CODES = {
    TASK_FILL_STUDENT_DETAIL: "fill_student_detail",
    TASK_FILL_STUDENT_RELATED_INFO: "fill_student_related_info",
    TASK_INVOKE_AGENT1_RISK: "invoke_agent1_risk",
    TASK_INVOKE_AGENT2_INTERVENTION: "invoke_agent2_intervention",
    TASK_REGISTER_TEACHER_OWN_SCHOOL: "register_teacher_own_school",
    TASK_REGISTER_TEACHER_ANY_SCHOOL: "register_teacher_any_school",
    TASK_REGISTER_COUNSELOR_OWN_SCHOOL: "register_counselor_own_school",
    TASK_REGISTER_COUNSELOR_ANY_SCHOOL: "register_counselor_any_school",
    TASK_INVOKE_AGENT3_REFERRAL: "invoke_agent3_referral",
    TASK_REGISTER_ASST_HEADMASTER_OWN_SCHOOL: "register_asst_headmaster_own_school",
    TASK_REGISTER_ASST_HEADMASTER_ANY_SCHOOL: "register_asst_headmaster_any_school",
    TASK_REGISTER_HEADMASTER_OWN_SCHOOL: "register_headmaster_own_school",
    TASK_REGISTER_HEADMASTER_ANY_SCHOOL: "register_headmaster_any_school",
    TASK_VIEW_EDIT_ALL_DATA_OWN_SCHOOL: "view_edit_all_data_own_school",
    TASK_VIEW_EDIT_ALL_DATA_ANY_SCHOOL: "view_edit_all_data_any_school",
    TASK_INVOKE_AGENT4_REPORTING: "invoke_agent4_reporting",
}

TASK_LABELS = {
    TASK_FILL_STUDENT_DETAIL: "Fill in the student's detail",
    TASK_FILL_STUDENT_RELATED_INFO: "Fill in student's related information",
    TASK_INVOKE_AGENT1_RISK: "Invoke Agent 1 (Risk Detection)",
    TASK_INVOKE_AGENT2_INTERVENTION: "Invoke Agent 2 (Intervention)",
    TASK_REGISTER_TEACHER_OWN_SCHOOL: "Register and give role to teacher of one school",
    TASK_REGISTER_TEACHER_ANY_SCHOOL: "Register and give role to teacher of any school",
    TASK_REGISTER_COUNSELOR_OWN_SCHOOL: "Register and give role to counselor of one school",
    TASK_REGISTER_COUNSELOR_ANY_SCHOOL: "Register and give role to counselor of any school",
    TASK_INVOKE_AGENT3_REFERRAL: "Invoke Agent 3 (Referral)",
    TASK_REGISTER_ASST_HEADMASTER_OWN_SCHOOL: "Register and give role to assistant headmaster of one school",
    TASK_REGISTER_ASST_HEADMASTER_ANY_SCHOOL: "Register and give role to assistant headmaster of any school",
    TASK_REGISTER_HEADMASTER_OWN_SCHOOL: "Register and give role to headmaster of one school",
    TASK_REGISTER_HEADMASTER_ANY_SCHOOL: "Register and give role to headmaster of any school",
    TASK_VIEW_EDIT_ALL_DATA_OWN_SCHOOL: "View and edit all data of one school",
    TASK_VIEW_EDIT_ALL_DATA_ANY_SCHOOL: "View and edit all data of any school",
    TASK_INVOKE_AGENT4_REPORTING: "Invoke Agent 4 (Reporting)",
}

# Role -> task set, exactly per the source matrix's Task_def column.
ROLE_TASKS: dict[str, set[int]] = {
    ROLE_GURU: {1, 2, 3, 4},
    ROLE_COUNSELOR: {2, 3, 4},
    ROLE_PK_HEM: {1, 2, 3, 4, 5, 7, 9, 16},
    ROLE_GURU_BESAR: {1, 2, 3, 4, 5, 7, 9, 10, 16},
    ROLE_ADMIN_SEKOLAH: {1, 2, 3, 4, 5, 7, 9, 10, 12, 14, 16},
    ROLE_SUPER_ADMIN: {1, 2, 3, 4, 6, 8, 9, 11, 13, 15, 16},
}

ANY_SCHOOL_TASKS = {
    TASK_REGISTER_TEACHER_ANY_SCHOOL,
    TASK_REGISTER_COUNSELOR_ANY_SCHOOL,
    TASK_REGISTER_ASST_HEADMASTER_ANY_SCHOOL,
    TASK_REGISTER_HEADMASTER_ANY_SCHOOL,
    TASK_VIEW_EDIT_ALL_DATA_ANY_SCHOOL,
}
ONE_SCHOOL_TASKS = {
    TASK_REGISTER_TEACHER_OWN_SCHOOL,
    TASK_REGISTER_COUNSELOR_OWN_SCHOOL,
    TASK_REGISTER_ASST_HEADMASTER_OWN_SCHOOL,
    TASK_REGISTER_HEADMASTER_OWN_SCHOOL,
    TASK_VIEW_EDIT_ALL_DATA_OWN_SCHOOL,
}

# Target role being registered/assigned -> (one-school task, any-school task).
# admin_sekolah and super_admin have no registration task in the matrix, so
# nobody can be granted those roles through the API (seeded directly instead).
REGISTRATION_TASK_BY_ROLE: dict[str, tuple[int, int]] = {
    ROLE_GURU: (TASK_REGISTER_TEACHER_OWN_SCHOOL, TASK_REGISTER_TEACHER_ANY_SCHOOL),
    ROLE_COUNSELOR: (TASK_REGISTER_COUNSELOR_OWN_SCHOOL, TASK_REGISTER_COUNSELOR_ANY_SCHOOL),
    ROLE_PK_HEM: (TASK_REGISTER_ASST_HEADMASTER_OWN_SCHOOL, TASK_REGISTER_ASST_HEADMASTER_ANY_SCHOOL),
    ROLE_GURU_BESAR: (TASK_REGISTER_HEADMASTER_OWN_SCHOOL, TASK_REGISTER_HEADMASTER_ANY_SCHOOL),
}

REGISTRATION_TASKS = {
    TASK_REGISTER_TEACHER_OWN_SCHOOL,
    TASK_REGISTER_TEACHER_ANY_SCHOOL,
    TASK_REGISTER_COUNSELOR_OWN_SCHOOL,
    TASK_REGISTER_COUNSELOR_ANY_SCHOOL,
    TASK_REGISTER_ASST_HEADMASTER_OWN_SCHOOL,
    TASK_REGISTER_ASST_HEADMASTER_ANY_SCHOOL,
    TASK_REGISTER_HEADMASTER_OWN_SCHOOL,
    TASK_REGISTER_HEADMASTER_ANY_SCHOOL,
}
