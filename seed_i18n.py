"""Seeds the languages table (dropdown options) and translations table (UI
strings). Replaces the old project's two independent hardcoded JS `I18N`
objects (login.html / index.html) and intervention_report.py's `LABELS`
dict with one DB-backed source of truth. Idempotent."""
from app.database import SessionLocal, init_db
from app.models.i18n import Language, Translation

LANGUAGES = [
    {"code": "ms", "name": "Bahasa Malaysia", "native_name": "Bahasa Malaysia", "is_default": True},
    {"code": "en", "name": "English", "native_name": "English", "is_default": False},
    {"code": "zh", "name": "Mandarin", "native_name": "中文", "is_default": False},
    {"code": "ta", "name": "Tamil", "native_name": "தமிழ்", "is_default": False},
]

# key -> {lang_code: translated string}
TRANSLATIONS: dict[str, dict[str, str]] = {
    "app.title": {
        "en": "Student Well-Being Support System",
        "ms": "Sistem Sokongan Kesejahteraan Pelajar",
        "zh": "学生身心福祉智能支援系统",
        "ta": "மாணவர் நல்வாழ்வு ஆதரவு அமைப்பு",
    },
    "hero.title": {
        "en": "Student Well-Being Early Warning, Intervention & Referral Support System",
        "ms": "Sistem Sokongan Amaran Awal, Intervensi & Rujukan Kesejahteraan Pelajar",
        "zh": "学生身心福祉智能预警、干预与转介支援系统",
        "ta": "மாணவர் நல்வாழ்வு முன்னெச்சரிக்கை, தலையீடு மற்றும் பரிந்துரை ஆதரவு அமைப்பு",
    },
    "hero.subtitle": {
        "en": "AI-assisted decision support for Malaysian school counselors",
        "ms": "Sokongan keputusan berbantukan AI untuk kaunselor sekolah Malaysia",
        "zh": "为马来西亚学校辅导老师提供人工智能辅助决策支持",
        "ta": "மலேசிய பள்ளி ஆலோசகர்களுக்கான AI உதவி முடிவெடுக்கும் ஆதரவு",
    },
    "feature.early_detection.title": {
        "en": "Early Detection", "ms": "Pengesanan Awal", "zh": "早期预警", "ta": "ஆரம்ப கண்டறிதல்",
    },
    "feature.early_detection.desc": {
        "en": "Identify well-being risk signals early using attendance, behavior, and assessment data.",
        "ms": "Kenal pasti isyarat risiko kesejahteraan lebih awal menggunakan data kehadiran, tingkah laku dan penilaian.",
        "zh": "利用出勤、行为和评估数据及早识别福祉风险信号。",
        "ta": "வருகை, நடத்தை மற்றும் மதிப்பீட்டு தரவுகளைப் பயன்படுத்தி நல்வாழ்வு அபாய சமிக்ஞைகளை முன்கூட்டியே அடையாளம் காணவும்.",
    },
    "feature.intervention.title": {
        "en": "Intervention", "ms": "Intervensi", "zh": "干预", "ta": "தலையீடு",
    },
    "feature.intervention.desc": {
        "en": "Generate school-based intervention plans tailored to each student's needs.",
        "ms": "Jana pelan intervensi berasaskan sekolah yang disesuaikan dengan keperluan setiap pelajar.",
        "zh": "生成针对每个学生需求量身定制的校本干预计划。",
        "ta": "ஒவ்வொரு மாணவரின் தேவைகளுக்கு ஏற்ப பள்ளி அடிப்படையிலான தலையீட்டுத் திட்டங்களை உருவாக்கவும்.",
    },
    "feature.referral.title": {
        "en": "Referral", "ms": "Rujukan", "zh": "转介", "ta": "பரிந்துரை",
    },
    "feature.referral.desc": {
        "en": "Prepare formal referral documents for external healthcare professionals.",
        "ms": "Sediakan dokumen rujukan formal untuk profesional penjagaan kesihatan luar.",
        "zh": "为外部医疗保健专业人员准备正式转介文件。",
        "ta": "வெளிப்புற சுகாதார நிபுணர்களுக்கான முறையான பரிந்துரை ஆவணங்களைத் தயாரிக்கவும்.",
    },
    "feature.reporting.title": {
        "en": "Reporting", "ms": "Pelaporan", "zh": "报告", "ta": "அறிக்கையிடல்",
    },
    "feature.reporting.desc": {
        "en": "Track school-wide well-being trends with management dashboards.",
        "ms": "Jejaki trend kesejahteraan seluruh sekolah dengan papan pemuka pengurusan.",
        "zh": "通过管理仪表板追踪全校福祉趋势。",
        "ta": "நிர்வாக டாஷ்போர்டுகளுடன் பள்ளி முழுவதும் நல்வாழ்வு போக்குகளைக் கண்காணிக்கவும்.",
    },
    "nav.dashboard": {"en": "Dashboard", "ms": "Papan Pemuka", "zh": "仪表板", "ta": "டாஷ்போர்டு"},
    "nav.students": {"en": "All Students", "ms": "Semua Pelajar", "zh": "所有学生", "ta": "அனைத்து மாணவர்களும்"},
    "nav.early_detection": {"en": "Early Detection", "ms": "Pengesanan Awal", "zh": "早期预警", "ta": "ஆரம்ப கண்டறிதல்"},
    "nav.intervention": {"en": "Intervention", "ms": "Intervensi", "zh": "干预", "ta": "தலையீடு"},
    "nav.referral": {"en": "Referral", "ms": "Rujukan", "zh": "转介", "ta": "பரிந்துரை"},
    "nav.reporting": {"en": "Reporting", "ms": "Pelaporan", "zh": "报告", "ta": "அறிக்கையிடல்"},
    "nav.assessments": {"en": "Assessment Instruments", "ms": "Instrumen Penilaian", "zh": "评估工具", "ta": "மதிப்பீட்டு கருவிகள்"},
    "nav.class_summary": {"en": "Class Summary", "ms": "Ringkasan Kelas", "zh": "班级摘要", "ta": "வகுப்பு சுருக்கம்"},
    "nav.api_docs": {"en": "API Docs", "ms": "Dokumentasi API", "zh": "API 文档", "ta": "API ஆவணங்கள்"},
    "nav.forms_group": {"en": "Forms", "ms": "Borang", "zh": "表单", "ta": "படிவங்கள்"},
    "nav.sms_form": {"en": "SMS Form", "ms": "Borang SMS", "zh": "SMS表单", "ta": "SMS படிவம்"},
    "nav.nichq_form": {"en": "NICHQ Form", "ms": "Borang NICHQ", "zh": "NICHQ表单", "ta": "NICHQ படிவம்"},
    "login.title": {"en": "Login", "ms": "Log Masuk", "zh": "登录", "ta": "உள்நுழைவு"},
    "login.ic_label": {"en": "IC Number", "ms": "Nombor Kad Pengenalan", "zh": "IC号码", "ta": "அடையாள அட்டை எண்"},
    "login.password_label": {"en": "Password", "ms": "Kata Laluan", "zh": "密码", "ta": "கடவுச்சொல்"},
    "login.forgot_password": {"en": "Forgot Password?", "ms": "Lupa Kata Laluan?", "zh": "忘记密码？", "ta": "கடவுச்சொல்லை மறந்துவிட்டீர்களா?"},
    "login.submit": {"en": "Submit", "ms": "Hantar", "zh": "提交", "ta": "சமர்ப்பிக்கவும்"},
    "login.error_invalid": {
        "en": "Invalid IC number or password.",
        "ms": "Nombor kad pengenalan atau kata laluan tidak sah.",
        "zh": "IC号码或密码无效。",
        "ta": "அடையாள அட்டை எண் அல்லது கடவுச்சொல் தவறானது.",
    },
    "common.logout": {"en": "Logout", "ms": "Log Keluar", "zh": "登出", "ta": "வெளியேறு"},
    "common.save": {"en": "Save", "ms": "Simpan", "zh": "保存", "ta": "சேமி"},
    "common.cancel": {"en": "Cancel", "ms": "Batal", "zh": "取消", "ta": "ரத்துசெய்"},
    "common.loading": {"en": "Loading...", "ms": "Memuatkan...", "zh": "加载中...", "ta": "ஏற்றுகிறது..."},
    "common.search": {"en": "Search", "ms": "Cari", "zh": "搜索", "ta": "தேடு"},
    "common.actions": {"en": "Actions", "ms": "Tindakan", "zh": "操作", "ta": "செயல்கள்"},
    "common.status": {"en": "Status", "ms": "Status", "zh": "状态", "ta": "நிலை"},
    "common.close": {"en": "Close", "ms": "Tutup", "zh": "关闭", "ta": "மூடு"},
    "common.view": {"en": "View", "ms": "Lihat", "zh": "查看", "ta": "காண்க"},
    "risk.low": {"en": "Low Risk", "ms": "Risiko Rendah", "zh": "低风险", "ta": "குறைந்த ஆபத்து"},
    "risk.moderate": {"en": "Moderate Risk", "ms": "Risiko Sederhana", "zh": "中等风险", "ta": "மிதமான ஆபத்து"},
    "risk.high": {"en": "High Risk", "ms": "Risiko Tinggi", "zh": "高风险", "ta": "அதிக ஆபத்து"},
    "risk.factors_heading": {"en": "Risk Factors", "ms": "Faktor Risiko", "zh": "风险因素", "ta": "ஆபத்து காரணிகள்"},
    "risk.category": {"en": "Category", "ms": "Kategori", "zh": "类别", "ta": "வகை"},
    "risk.indicator": {"en": "Indicator", "ms": "Petunjuk", "zh": "指标", "ta": "குறிகாட்டி"},
    "risk.severity": {"en": "Severity", "ms": "Keterukan", "zh": "严重程度", "ta": "தீவிரம்"},
    "risk.evidence": {"en": "Evidence", "ms": "Bukti", "zh": "证据", "ta": "சான்று"},
    "risk.score": {"en": "Score", "ms": "Skor", "zh": "分数", "ta": "மதிப்பெண்"},
    "risk.level": {"en": "Risk Level", "ms": "Tahap Risiko", "zh": "风险等级", "ta": "ஆபத்து நிலை"},
    "risk.discard": {"en": "Discard", "ms": "Buang", "zh": "放弃", "ta": "நிராகரி"},
    "risk.print": {"en": "Print", "ms": "Cetak", "zh": "打印", "ta": "அச்சிடு"},
    "risk.report_saved": {"en": "Report saved.", "ms": "Laporan disimpan.", "zh": "报告已保存。", "ta": "அறிக்கை சேமிக்கப்பட்டது."},
    "risk.view_previous_reports": {"en": "View Previous Reports", "ms": "Lihat Laporan Terdahulu", "zh": "查看以往报告", "ta": "முந்தைய அறிக்கைகளைப் பார்க்கவும்"},
    "risk.previous_reports": {"en": "Previous Reports", "ms": "Laporan Terdahulu", "zh": "以往报告", "ta": "முந்தைய அறிக்கைகள்"},
    "risk.timestamp": {"en": "Timestamp", "ms": "Cap Masa", "zh": "时间戳", "ta": "நேர முத்திரை"},
    "risk.no_previous_reports": {"en": "No previous reports found.", "ms": "Tiada laporan terdahulu dijumpai.", "zh": "未找到以往报告。", "ta": "முந்தைய அறிக்கைகள் எதுவும் இல்லை."},
    "risk.already_generated_today": {
        "en": "A report for this student was already generated today — showing the saved report instead of recalculating.",
        "ms": "Laporan untuk pelajar ini telah dijana hari ini — memaparkan laporan yang disimpan tanpa mengira semula.",
        "zh": "该学生今天已生成过报告——显示已保存的报告，不再重新计算。",
        "ta": "இந்த மாணவருக்கான அறிக்கை இன்று ஏற்கனவே உருவாக்கப்பட்டது — மீண்டும் கணக்கிடாமல் சேமிக்கப்பட்ட அறிக்கையைக் காட்டுகிறது.",
    },
    "risk.already_generated_for_referral": {
        "en": "A referral letter for this referral type and recipient was already generated — showing the saved letter instead of recalculating.",
        "ms": "Surat rujukan untuk jenis rujukan dan penerima ini telah dijana — memaparkan surat yang disimpan tanpa mengira semula.",
        "zh": "此转介类型和接收方的转介信已生成过——显示已保存的信件，不再重新计算。",
        "ta": "இந்த பரிந்துரை வகைக்கும் பெறுநருக்கும் ஏற்கனவே பரிந்துரை கடிதம் உருவாக்கப்பட்டது — மீண்டும் கணக்கிடாமல் சேமிக்கப்பட்ட கடிதத்தைக் காட்டுகிறது.",
    },
    "risk.recommended_actions": {"en": "Recommended Actions", "ms": "Tindakan Disyorkan", "zh": "建议行动", "ta": "பரிந்துரைக்கப்பட்ட நடவடிக்கைகள்"},
    "risk.none_flagged": {"en": "None flagged.", "ms": "Tiada yang dikenal pasti.", "zh": "未发现任何问题。", "ta": "எதுவும் குறிக்கப்படவில்லை."},
    "dashboard.title": {"en": "Dashboard Overview", "ms": "Gambaran Papan Pemuka", "zh": "仪表板概览", "ta": "டாஷ்போர்டு மேலோட்டம்"},
    "dashboard.total_students": {"en": "Total Students", "ms": "Jumlah Pelajar", "zh": "学生总数", "ta": "மொத்த மாணவர்கள்"},
    "dashboard.active_interventions": {"en": "Active Interventions", "ms": "Intervensi Aktif", "zh": "进行中的干预", "ta": "செயலில் உள்ள தலையீடுகள்"},
    "dashboard.referrals_made": {"en": "Referrals Made", "ms": "Rujukan Dibuat", "zh": "已作出的转介", "ta": "செய்யப்பட்ட பரிந்துரைகள்"},
    "dashboard.referrals_acknowledged": {"en": "Referrals Acknowledged", "ms": "Rujukan Diakui", "zh": "已确认的转介", "ta": "ஒப்புக்கொள்ளப்பட்ட பரிந்துரைகள்"},
    "students.full_name": {"en": "Full Name", "ms": "Nama Penuh", "zh": "全名", "ta": "முழுப்பெயர்"},
    "students.class_name": {"en": "Class", "ms": "Kelas", "zh": "班级", "ta": "வகுப்பு"},
    "students.school_year": {"en": "School Year", "ms": "Tahun Sekolah", "zh": "学年", "ta": "பள்ளி ஆண்டு"},
    "students.guardian_name": {"en": "Guardian Name", "ms": "Nama Penjaga", "zh": "监护人姓名", "ta": "பாதுகாவலர் பெயர்"},
    "students.guardian_contact": {"en": "Guardian Contact", "ms": "Hubungan Penjaga", "zh": "监护人联系方式", "ta": "பாதுகாவலர் தொடர்பு"},
    "students.add_new": {"en": "Add New Student", "ms": "Tambah Pelajar Baharu", "zh": "添加新学生", "ta": "புதிய மாணவரைச் சேர்"},
    "language.select_label": {"en": "Language", "ms": "Bahasa", "zh": "语言", "ta": "மொழி"},
    "footer.moe_aligned": {
        "en": "MoE 2027 Aligned", "ms": "Selaras dengan KPM 2027", "zh": "符合教育部2027年目标", "ta": "MoE 2027 உடன் இணைந்தது",
    },
    "footer.pdpa_compliant": {
        "en": "PDPA Compliant", "ms": "Mematuhi PDPA", "zh": "符合PDPA（个人资料保护法）", "ta": "PDPA இணக்கம்",
    },
    # Referral/intervention report labels (used by app/services/intervention_report.py)
    "report.school_based_intervention_plan": {
        "en": "School-Based Intervention Plan", "ms": "Pelan Intervensi Berasaskan Sekolah",
        "zh": "校本干预计划", "ta": "பள்ளி அடிப்படையிலான தலையீட்டுத் திட்டம்",
    },
    "prescreen.low_risk_summary": {
        "en": "No significant risk indicators were found in the student's attendance, behavior, or assessment records over the recent monitoring period.",
        "ms": "Tiada penunjuk risiko signifikan dikesan dalam rekod kehadiran, tingkah laku, atau penilaian pelajar bagi tempoh pemantauan terkini.",
        "zh": "在近期监测期内，未在该学生的出勤、行为或评估记录中发现显著的风险指标。",
        "ta": "சமீபத்திய கண்காணிப்பு காலத்தில் மாணவரின் வருகை, நடத்தை அல்லது மதிப்பீட்டு பதிவுகளில் குறிப்பிடத்தக்க ஆபத்து அறிகுறிகள் எதுவும் காணப்படவில்லை.",
    },
    "prescreen.low_risk_action": {
        "en": "Continue routine monitoring. No immediate action required.",
        "ms": "Teruskan pemantauan rutin. Tiada tindakan segera diperlukan.",
        "zh": "继续常规监测。无需立即采取行动。",
        "ta": "வழக்கமான கண்காணிப்பைத் தொடரவும். உடனடி நடவடிக்கை தேவையில்லை.",
    },
    # Behavior incident_type categories (fixed vocabulary, entered in Bahasa Melayu;
    # keys are slugified from the ms value — see slugify() in app/static/index.html)
    "behavior.incident_type.kenakalan": {
        "en": "Misbehavior", "ms": "Kenakalan", "zh": "顽皮行为", "ta": "குறும்பு",
    },
    "behavior.incident_type.tingkah_laku_jenayah": {
        "en": "Criminal Behavior", "ms": "Tingkah laku jenayah", "zh": "犯罪行为", "ta": "குற்றச் செயல்",
    },
    "behavior.incident_type.vandalisme": {
        "en": "Vandalism", "ms": "Vandalisme", "zh": "故意破坏", "ta": "நாசவேலை",
    },
    "behavior.incident_type.ponteng": {
        "en": "Truancy", "ms": "Ponteng", "zh": "逃学", "ta": "பள்ளி புறக்கணிப்பு",
    },
    # Behavior severity categories (fixed vocabulary, same slugify convention)
    "behavior.severity.ringan": {
        "en": "Minor", "ms": "Ringan", "zh": "轻微", "ta": "இலேசான",
    },
    "behavior.severity.sederhana": {
        "en": "Moderate", "ms": "Sederhana", "zh": "中等", "ta": "மிதமான",
    },
    "behavior.severity.berat": {
        "en": "Serious", "ms": "Berat", "zh": "严重", "ta": "கடுமையான",
    },
    "report.disclaimer": {
        "en": "This is an AI-assisted decision-support document. It does NOT constitute a clinical diagnosis and must be reviewed by a qualified school counselor before use.",
        "ms": "Ini adalah dokumen sokongan keputusan berbantukan AI. Ia BUKAN diagnosis klinikal dan mesti disemak oleh kaunselor sekolah yang bertauliah sebelum digunakan.",
        "zh": "本文件为人工智能辅助决策支持文件，并非临床诊断，使用前必须由合格的学校辅导员审核。",
        "ta": "இது AI உதவியுடன் கூடிய முடிவெடுக்கும் ஆவணம். இது மருத்துவ நோய் கண்டறிதல் அல்ல, பயன்படுத்தும் முன் தகுதி வாய்ந்த பள்ளி ஆலோசகரால் மதிப்பாய்வு செய்யப்பட வேண்டும்.",
    },
}


def seed_i18n():
    db = SessionLocal()
    try:
        lang_by_code = {l.code: l for l in db.query(Language).all()}
        for lang_def in LANGUAGES:
            lang = lang_by_code.get(lang_def["code"])
            if lang is None:
                lang = Language(**lang_def)
                db.add(lang)
                db.flush()
                lang_by_code[lang_def["code"]] = lang
            else:
                lang.name = lang_def["name"]
                lang.native_name = lang_def["native_name"]
                lang.is_default = lang_def["is_default"]
        db.commit()

        existing = {(t.language_id, t.key) for t in db.query(Translation).all()}
        added = 0
        for key, by_lang in TRANSLATIONS.items():
            for code, value in by_lang.items():
                lang = lang_by_code[code]
                if (lang.id, key) not in existing:
                    db.add(Translation(language_id=lang.id, key=key, value=value))
                    added += 1
        db.commit()
        print(f"Seeded {len(LANGUAGES)} languages, {added} new translation rows.")
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
    seed_i18n()
