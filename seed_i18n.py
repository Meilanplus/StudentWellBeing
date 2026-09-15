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
    "risk.saving_and_translating": {
        "en": "Saving & translating", "ms": "Menyimpan & menterjemah", "zh": "正在保存并翻译", "ta": "சேமித்து மொழிபெயர்க்கிறது",
    },
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
    "dashboard.trend_analysis": {"en": "Trend Analysis", "ms": "Analisis Trend", "zh": "趋势分析", "ta": "போக்கு பகுப்பாய்வு"},
    "dashboard.management_summary": {"en": "Management Summary", "ms": "Ringkasan Pengurusan", "zh": "管理摘要", "ta": "மேலாண்மைச் சுருக்கம்"},
    "dashboard.recommendations": {"en": "Recommendations", "ms": "Cadangan", "zh": "建议", "ta": "பரிந்துரைகள்"},
    "dashboard.narrative_not_generated": {
        "en": "AI insights have not been generated yet for this period/language.",
        "ms": "Wawasan AI belum dijana lagi untuk tempoh/bahasa ini.",
        "zh": "此期间/语言尚未生成AI洞察。",
        "ta": "இந்த காலகட்டம்/மொழிக்கு AI நுண்ணறிவுகள் இன்னும் உருவாக்கப்படவில்லை.",
    },
    "dashboard.generate_insights": {"en": "Generate AI Insights", "ms": "Jana Wawasan AI", "zh": "生成AI洞察", "ta": "AI நுண்ணறிவுகளை உருவாக்கு"},
    "risk.generating_dashboard": {
        "en": "Agent 4 is generating the dashboard summary — this can take a few minutes.",
        "ms": "Agent 4 sedang menjana ringkasan papan pemuka — ini boleh mengambil masa beberapa minit.",
        "zh": "Agent 4 正在生成仪表板摘要——这可能需要几分钟。",
        "ta": "Agent 4 டாஷ்போர்டு சுருக்கத்தை உருவாக்குகிறது — இதற்கு சில நிமிடங்கள் ஆகலாம்.",
    },
    "reporting.student_cases": {"en": "Student Cases", "ms": "Kes Pelajar", "zh": "学生个案", "ta": "மாணவர் வழக்குகள்"},
    "reporting.no_cases": {
        "en": "No active cases this period.", "ms": "Tiada kes aktif bagi tempoh ini.",
        "zh": "本期无活跃个案。", "ta": "இந்த காலகட்டத்தில் செயலில் உள்ள வழக்குகள் இல்லை.",
    },
    "reporting.intervention_status": {"en": "Intervention", "ms": "Intervensi", "zh": "干预", "ta": "தலையீடு"},
    "reporting.referral_status": {"en": "Referral", "ms": "Rujukan", "zh": "转介", "ta": "பரிந்துரை"},
    # Student Cases table values (Intervention.status / Referral.status fixed
    # enums) — same untranslated-fixed-value gap as behavior.severity/
    # risk.category, found while checking the Reporting page.
    "reporting.intervention_status.active": {"en": "Active", "ms": "Aktif", "zh": "进行中", "ta": "செயலில்"},
    "reporting.intervention_status.completed": {"en": "Completed", "ms": "Selesai", "zh": "已完成", "ta": "முடிந்தது"},
    "reporting.intervention_status.escalated": {
        "en": "Escalated", "ms": "Dinaikkan Taraf", "zh": "已升级", "ta": "தீவிரப்படுத்தப்பட்டது",
    },
    "reporting.referral_status.pending": {"en": "Pending", "ms": "Menunggu", "zh": "待处理", "ta": "நிலுவையில்"},
    "reporting.referral_status.sent": {"en": "Sent", "ms": "Telah Dihantar", "zh": "已发送", "ta": "அனுப்பப்பட்டது"},
    "reporting.back_to_current": {
        "en": "Back to Current Period", "ms": "Kembali ke Tempoh Semasa",
        "zh": "返回当前期间", "ta": "தற்போதைய காலகட்டத்திற்குத் திரும்பு",
    },
    "common.total": {"en": "Total", "ms": "Jumlah", "zh": "总计", "ta": "மொத்தம்"},
    "common.student": {"en": "Student", "ms": "Pelajar", "zh": "学生", "ta": "மாணவர்"},
    "common.prepared_by": {"en": "Prepared by", "ms": "Disediakan oleh", "zh": "编制人", "ta": "தயாரித்தவர்"},

    "referral.type": {"en": "Referral Type", "ms": "Jenis Rujukan", "zh": "转介类型", "ta": "பரிந்துரை வகை"},
    "referral.to": {"en": "Referral To", "ms": "Dirujuk Kepada", "zh": "转介对象", "ta": "பரிந்துரைக்கப்பட்டவர்"},
    "referral.to_placeholder": {
        "en": "e.g. Klinik Kesihatan Sentul", "ms": "cth. Klinik Kesihatan Sentul",
        "zh": "例如：Klinik Kesihatan Sentul", "ta": "எ.கா. Klinik Kesihatan Sentul",
    },
    "referral.additional_notes": {"en": "Additional Notes", "ms": "Nota Tambahan", "zh": "附加说明", "ta": "கூடுதல் குறிப்புகள்"},
    "referral.run_agent3": {"en": "Run Agent 3: Generate Referral", "ms": "Jalankan Agent 3: Jana Rujukan", "zh": "运行代理3：生成转介", "ta": "Agent 3-ஐ இயக்கு: பரிந்துரையை உருவாக்கு"},
    "referral.type.psychologist": {"en": "Psychologist", "ms": "Ahli Psikologi", "zh": "心理学家", "ta": "உளவியலாளர்"},
    "referral.type.psychiatrist": {"en": "Psychiatrist", "ms": "Pakar Psikiatri", "zh": "精神科医生", "ta": "மனநல மருத்துவர்"},
    "referral.type.klinik_kesihatan": {"en": "Health Clinic", "ms": "Klinik Kesihatan", "zh": "健康诊所", "ta": "சுகாதார கிளினிக்"},
    "referral.type.hospital": {"en": "Hospital", "ms": "Hospital", "zh": "医院", "ta": "மருத்துவமனை"},
    "referral.letter_title": {"en": "Referral Letter", "ms": "Surat Rujukan", "zh": "转介信", "ta": "பரிந்துரைக் கடிதம்"},
    "referral.supporting_summary": {"en": "Supporting Summary", "ms": "Ringkasan Sokongan", "zh": "支持摘要", "ta": "ஆதரவுச் சுருக்கம்"},
    "referral.information_heading": {"en": "Referral Information", "ms": "Maklumat Rujukan", "zh": "转介信息", "ta": "பரிந்துரைத் தகவல்"},
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
    # Intervention report section headings — used by both the frontend
    # screen/print view (interventionReportHtml in index.html) and the
    # downloadable .docx (app/services/intervention_report.py), which were
    # previously hardcoded in English in both places.
    "intervention.student_information": {
        "en": "Student Information", "ms": "Maklumat Pelajar", "zh": "学生信息", "ta": "மாணவர் தகவல்",
    },
    "intervention.rationale": {"en": "Rationale", "ms": "Rasional", "zh": "理由", "ta": "காரணம்"},
    "intervention.reason_for_intervention": {
        "en": "Reason for Intervention", "ms": "Sebab Intervensi", "zh": "干预原因", "ta": "தலையீட்டிற்கான காரணம்",
    },
    "intervention.objectives": {
        "en": "Intervention Objectives", "ms": "Objektif Intervensi", "zh": "干预目标", "ta": "தலையீட்டு நோக்கங்கள்",
    },
    "intervention.strategies": {"en": "Strategies", "ms": "Strategi", "zh": "策略", "ta": "உத்திகள்"},
    "intervention.ai_recommended_plan": {
        "en": "AI Recommended Intervention Plan", "ms": "Pelan Intervensi Disyorkan AI",
        "zh": "AI推荐的干预计划", "ta": "AI பரிந்துரைக்கும் தலையீட்டுத் திட்டம்",
    },
    "intervention.area": {"en": "Area", "ms": "Bidang", "zh": "领域", "ta": "பகுதி"},
    "intervention.strategy_col": {"en": "Strategy", "ms": "Strategi", "zh": "策略", "ta": "உத்தி"},
    "intervention.responsible": {
        "en": "Responsible", "ms": "Bertanggungjawab", "zh": "负责人", "ta": "பொறுப்பானவர்",
    },
    "intervention.responsible_person": {
        "en": "Responsible Person", "ms": "Orang Bertanggungjawab", "zh": "负责人", "ta": "பொறுப்பான நபர்",
    },
    "intervention.frequency": {"en": "Frequency", "ms": "Kekerapan", "zh": "频率", "ta": "அதிர்வெண்"},
    "intervention.success_indicator": {
        "en": "Success Indicator", "ms": "Penunjuk Kejayaan", "zh": "成功指标", "ta": "வெற்றிக் குறிகாட்டி",
    },
    "intervention.recommended_tools": {
        "en": "Recommended Tools", "ms": "Alat Disyorkan", "zh": "推荐工具", "ta": "பரிந்துரைக்கப்பட்ட கருவிகள்",
    },
    "intervention.home_strategies": {
        "en": "Home Strategies", "ms": "Strategi di Rumah", "zh": "家庭策略", "ta": "வீட்டு உத்திகள்",
    },
    "intervention.parent_support_guide": {
        "en": "Parent Support Guide", "ms": "Panduan Sokongan Ibu Bapa", "zh": "家长支持指南", "ta": "பெற்றோர் ஆதரவு வழிகாட்டி",
    },
    "intervention.expected_outcomes": {
        "en": "Expected Outcomes", "ms": "Hasil Dijangka", "zh": "预期成果", "ta": "எதிர்பார்க்கப்படும் முடிவுகள்",
    },
    "intervention.monitoring_checklist": {
        "en": "Monitoring Checklist", "ms": "Senarai Semak Pemantauan", "zh": "监测清单", "ta": "கண்காணிப்புப் பட்டியல்",
    },
    "intervention.action_items": {"en": "Action Items", "ms": "Item Tindakan", "zh": "行动项目", "ta": "செயல் பணிகள்"},
    "intervention.counselor_recommendation": {
        "en": "Counselor Recommendation", "ms": "Cadangan Kaunselor", "zh": "辅导员建议", "ta": "ஆலோசகர் பரிந்துரை",
    },
    "intervention.referral_recommended_label": {
        "en": "Referral recommended:", "ms": "Rujukan disyorkan:", "zh": "建议转介：", "ta": "பரிந்துரை செய்யப்படுகிறது:",
    },
    "intervention.referral_recommendation_heading": {
        "en": "Referral Recommendation", "ms": "Cadangan Rujukan", "zh": "转介建议", "ta": "பரிந்துரை சிபாரிசு",
    },
    "intervention.referral_to_agent3_default": {
        "en": "Referral to Agent 3 recommended.", "ms": "Rujukan kepada Agent 3 disyorkan.",
        "zh": "建议转介至代理3。", "ta": "Agent 3-க்கு பரிந்துரை செய்யப்படுகிறது.",
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
    "behavior.incident_type.buli": {
        "en": "Bullying", "ms": "Buli", "zh": "欺凌", "ta": "கொடுமைப்படுத்துதல்",
    },
    "behavior.incident_type.pergaduhan": {
        "en": "Fighting", "ms": "Pergaduhan", "zh": "打架", "ta": "சண்டை",
    },
    "behavior.incident_type.isu_emosi": {
        "en": "Emotional Issue", "ms": "Isu Emosi", "zh": "情绪问题", "ta": "உணர்ச்சிச் சிக்கல்",
    },
    "behavior.incident_type.isu_sosial": {
        "en": "Social/Peer Issue", "ms": "Isu Sosial", "zh": "社交问题", "ta": "சமூகச் சிக்கல்",
    },
    "behavior.incident_type.isu_akademik": {
        "en": "Academic Issue", "ms": "Isu Akademik", "zh": "学业问题", "ta": "கல்விச் சிக்கல்",
    },
    # Behavior/risk-factor severity categories (fixed vocabulary, same
    # slugify convention). Keyed by every spelling Agent 1 has actually been
    # observed to emit — it's told to use a fixed English enum but doesn't
    # always comply, and even when it does it sometimes reaches for
    # High/Moderate/Low (echoing risk_level's wording) instead of
    # Minor/Moderate/Serious. Covering all variants means the display still
    # resolves to the currently-selected language regardless of which the
    # model picked.
    "behavior.severity.ringan": {
        "en": "Minor", "ms": "Ringan", "zh": "轻微", "ta": "இலேசான",
    },
    "behavior.severity.minor": {
        "en": "Minor", "ms": "Ringan", "zh": "轻微", "ta": "இலேசான",
    },
    "behavior.severity.low": {
        "en": "Minor", "ms": "Ringan", "zh": "轻微", "ta": "இலேசான",
    },
    "behavior.severity.sederhana": {
        "en": "Moderate", "ms": "Sederhana", "zh": "中等", "ta": "மிதமான",
    },
    "behavior.severity.moderate": {
        "en": "Moderate", "ms": "Sederhana", "zh": "中等", "ta": "மிதமான",
    },
    "behavior.severity.berat": {
        "en": "Serious", "ms": "Berat", "zh": "严重", "ta": "கடுமையான",
    },
    "behavior.severity.serious": {
        "en": "Serious", "ms": "Berat", "zh": "严重", "ta": "கடுமையான",
    },
    "behavior.severity.high": {
        "en": "Serious", "ms": "Berat", "zh": "严重", "ta": "கடுமையான",
    },
    # Risk factor category (risk_factors[].category from Agent 1) — same
    # rationale as behavior.severity.*: the prompt asks for a fixed English
    # enum (Attendance/Behavior/Mental Health) but Agent 1 doesn't always
    # comply and sometimes emits the Malay term instead, so every observed
    # spelling (from actual saved reports) is covered here.
    "risk.category.attendance": {
        "en": "Attendance", "ms": "Kehadiran", "zh": "出勤", "ta": "வருகை",
    },
    "risk.category.kehadiran": {
        "en": "Attendance", "ms": "Kehadiran", "zh": "出勤", "ta": "வருகை",
    },
    "risk.category.behavior": {
        "en": "Behavior", "ms": "Tingkah Laku", "zh": "行为", "ta": "நடத்தை",
    },
    "risk.category.behavioral": {
        "en": "Behavior", "ms": "Tingkah Laku", "zh": "行为", "ta": "நடத்தை",
    },
    "risk.category.tingkah_laku": {
        "en": "Behavior", "ms": "Tingkah Laku", "zh": "行为", "ta": "நடத்தை",
    },
    "risk.category.mental_health": {
        "en": "Mental Health", "ms": "Kesihatan Mental", "zh": "心理健康", "ta": "மனநலம்",
    },
    "risk.category.kesihatan_mental": {
        "en": "Mental Health", "ms": "Kesihatan Mental", "zh": "心理健康", "ta": "மனநலம்",
    },
    "risk.category.kesihatan_mental_emosi": {
        "en": "Mental Health / Emotional", "ms": "Kesihatan Mental / Emosi", "zh": "心理健康/情绪", "ta": "மனநலம்/உணர்ச்சி",
    },
    "common.edit": {"en": "Edit", "ms": "Sunting", "zh": "编辑", "ta": "திருத்து"},
    "common.delete": {"en": "Delete", "ms": "Padam", "zh": "删除", "ta": "நீக்கு"},
    "common.add": {"en": "Add", "ms": "Tambah", "zh": "添加", "ta": "சேர்"},
    "common.date": {"en": "Date", "ms": "Tarikh", "zh": "日期", "ta": "தேதி"},
    "common.type": {"en": "Type", "ms": "Jenis", "zh": "类型", "ta": "வகை"},
    "common.description": {"en": "Description", "ms": "Penerangan", "zh": "描述", "ta": "விளக்கம்"},
    "common.reason": {"en": "Reason", "ms": "Sebab", "zh": "原因", "ta": "காரணம்"},
    "common.year": {"en": "Year", "ms": "Tahun", "zh": "年份", "ta": "ஆண்டு"},
    # Shared report field labels — used across the Intervention and Referral
    # docx generators and screen/print views, so any new report type can
    # reuse them instead of duplicating per-report label keys.
    "common.case_reference": {"en": "Case Reference", "ms": "Rujukan Kes", "zh": "案例编号", "ta": "வழக்கு எண்"},
    "common.student_name": {"en": "Student Name", "ms": "Nama Pelajar", "zh": "学生姓名", "ta": "மாணவர் பெயர்"},
    "common.class": {"en": "Class", "ms": "Kelas", "zh": "班级", "ta": "வகுப்பு"},
    "common.age": {"en": "Age", "ms": "Umur", "zh": "年龄", "ta": "வயது"},
    "common.risk_level": {"en": "Risk Level", "ms": "Tahap Risiko", "zh": "风险等级", "ta": "ஆபத்து நிலை"},
    "common.school": {"en": "School", "ms": "Sekolah", "zh": "学校", "ta": "பள்ளி"},
    "common.teacher": {"en": "Teacher", "ms": "Guru", "zh": "教师", "ta": "ஆசிரியர்"},
    "common.counselor": {"en": "Counselor", "ms": "Kaunselor", "zh": "辅导员", "ta": "ஆலோசகர்"},
    "common.parent": {"en": "Parent", "ms": "Ibu Bapa", "zh": "家长", "ta": "பெற்றோர்"},
    "common.download_docx_report": {
        "en": "Download .docx Report", "ms": "Muat Turun Laporan .docx", "zh": "下载 .docx 报告", "ta": "டாக்ஸ் அறிக்கையைப் பதிவிறக்கவும்",
    },
    "common.semester": {"en": "Semester", "ms": "Semester", "zh": "学期", "ta": "செமஸ்டர்"},
    "common.back_to_students": {"en": "Back to Students", "ms": "Kembali ke Pelajar", "zh": "返回学生列表", "ta": "மாணவர்களுக்குத் திரும்பு"},
    "students.gender": {"en": "Gender", "ms": "Jantina", "zh": "性别", "ta": "பாலினம்"},

    "attendance.section_title": {"en": "Attendance", "ms": "Kehadiran", "zh": "出勤", "ta": "வருகை"},
    "attendance.record_title": {"en": "Attendance Record", "ms": "Rekod Kehadiran", "zh": "出勤记录", "ta": "வருகைப் பதிவு"},
    "attendance.percentage": {"en": "Attendance %", "ms": "Peratus Kehadiran", "zh": "出勤率", "ta": "வருகை %"},
    "attendance.recorded_by": {"en": "Recorded By", "ms": "Direkodkan Oleh", "zh": "记录人", "ta": "பதிவு செய்தவர்"},
    "students.confirm_delete_attendance": {
        "en": "Delete this attendance record? This cannot be undone.",
        "ms": "Padam rekod kehadiran ini? Tindakan ini tidak boleh dibuat asal.",
        "zh": "确定要删除此出勤记录吗？此操作无法撤销。",
        "ta": "இந்த வருகைப் பதிவை நீக்கவா? இதை மீட்டெடுக்க முடியாது.",
    },
    # Attendance reason taxonomy — mirrors the MOE's official "Senarai
    # Kategori & Sebab Ketidakhadiran Murid (IDME Terkini)" reference list.
    # Categories (attendance.reason_category.*) group the cascading dropdown;
    # sub-reasons (attendance.reason.*) are the actual stored/selected values,
    # same slugify convention as behavior.incident_type.*.
    "attendance.reason_category.aktiviti_luar_sekolah": {
        "en": "Outside School Activity", "ms": "Aktiviti Luar Sekolah", "zh": "校外活动", "ta": "பள்ளிக்கு வெளியே செயல்பாடு",
    },
    "attendance.reason_category.ancaman_keselamatan": {
        "en": "Safety Threat", "ms": "Ancaman Keselamatan", "zh": "安全威胁", "ta": "பாதுகாப்பு அச்சுறுத்தல்",
    },
    "attendance.reason_category.bencana_alam": {
        "en": "Natural Disaster", "ms": "Bencana Alam", "zh": "自然灾害", "ta": "இயற்கை பேரிடர்",
    },
    "attendance.reason_category.digantung_sekolah": {
        "en": "Suspended from School", "ms": "Digantung Sekolah", "zh": "被学校停学", "ta": "பள்ளியிலிருந்து இடைநிறுத்தம்",
    },
    "attendance.reason_category.masalah_keluarga": {
        "en": "Family Problem", "ms": "Masalah Keluarga", "zh": "家庭问题", "ta": "குடும்பப் பிரச்சினை",
    },
    "attendance.reason_category.masalah_peribadi": {
        "en": "Personal Problem", "ms": "Masalah Peribadi", "zh": "个人问题", "ta": "தனிப்பட்ட பிரச்சினை",
    },
    "attendance.reason_category.pdpr": {
        "en": "Home-Based Learning (PDPR)", "ms": "PDPR", "zh": "居家学习（PDPR）", "ta": "வீட்டில் கற்றல் (PDPR)",
    },
    "attendance.reason_category.penggiliran_peperiksaan": {
        "en": "Examination Rotation", "ms": "Penggiliran Peperiksaan", "zh": "考试轮值安排", "ta": "தேர்வு சுழற்சி",
    },
    "attendance.reason_category.kebenaran_pengetua_guru_besar": {
        "en": "Principal/Headmaster's Permission", "ms": "Kebenaran Pengetua / Guru Besar", "zh": "校长准假", "ta": "அதிபர்/தலைமை ஆசிரியர் அனுமதி",
    },
    "attendance.reason.wakil_sekolah": {
        "en": "School Representative", "ms": "Wakil sekolah", "zh": "学校代表", "ta": "பள்ளி பிரதிநிதி",
    },
    "attendance.reason.binatang_liar_buas_berbisa": {
        "en": "Wild/Venomous Animal", "ms": "Binatang liar / buas / berbisa", "zh": "野生/毒性动物", "ta": "காட்டு/விஷ விலங்கு",
    },
    "attendance.reason.diculik": {
        "en": "Kidnapped", "ms": "Diculik", "zh": "被绑架", "ta": "கடத்தப்பட்டது",
    },
    "attendance.reason.gangguan_mistik_makhluk_halus": {
        "en": "Mystical/Supernatural Disturbance", "ms": "Gangguan mistik / makhluk halus", "zh": "灵异干扰", "ta": "மாய/ஆவி தொல்லை",
    },
    "attendance.reason.gangguan_kongsi_gelap": {
        "en": "Secret Society Disturbance", "ms": "Gangguan kongsi gelap", "zh": "黑社会骚扰", "ta": "இரகசிய சங்கத் தொல்லை",
    },
    "attendance.reason.kebakaran": {
        "en": "Fire", "ms": "Kebakaran", "zh": "火灾", "ta": "தீ விபத்து",
    },
    "attendance.reason.penganas": {
        "en": "Terrorist", "ms": "Penganas", "zh": "恐怖分子", "ta": "பயங்கரவாதி",
    },
    "attendance.reason.lanun": {
        "en": "Pirate/Kidnapper (Lanun)", "ms": "Lanun", "zh": "海盗", "ta": "கடல் கொள்ளையர்",
    },
    "attendance.reason.ugutan_daripada_pihak_luar": {
        "en": "Threat from Outside Party", "ms": "Ugutan daripada pihak luar", "zh": "外部威胁", "ta": "வெளிக் கட்சியிடமிருந்து மிரட்டல்",
    },
    "attendance.reason.rusuhan_di_luar_kawasan_sekolah": {
        "en": "Riot Outside School Area", "ms": "Rusuhan di luar kawasan sekolah", "zh": "校外骚乱", "ta": "பள்ளிக்கு வெளியே கலவரம்",
    },
    "attendance.reason.mangsa_buli": {
        "en": "Bullying Victim", "ms": "Mangsa buli", "zh": "欺凌受害者", "ta": "கொடுமைப்படுத்தலுக்கு ஆளானவர்",
    },
    "attendance.reason.mangsa_seksual": {
        "en": "Sexual Abuse Victim", "ms": "Mangsa seksual", "zh": "性侵受害者", "ta": "பாலியல் துன்புறுத்தலுக்கு ஆளானவர்",
    },
    "attendance.reason.tidak_dapat_dikesan_hilang": {
        "en": "Untraceable/Missing", "ms": "Tidak dapat dikesan / hilang", "zh": "失踪/无法追踪", "ta": "காணவில்லை/கண்டறிய முடியவில்லை",
    },
    "attendance.reason.jerebu": {
        "en": "Haze", "ms": "Jerebu", "zh": "烟霾", "ta": "புகைமூட்டம்",
    },
    "attendance.reason.kemalangan": {
        "en": "Accident", "ms": "Kemalangan", "zh": "意外事故", "ta": "விபத்து",
    },
    "attendance.reason.banjir": {
        "en": "Flood", "ms": "Banjir", "zh": "水灾", "ta": "வெள்ளம்",
    },
    "attendance.reason.gempa_bumi": {
        "en": "Earthquake", "ms": "Gempa bumi", "zh": "地震", "ta": "நிலநடுக்கம்",
    },
    "attendance.reason.hujan_lebat_ribut_taufan": {
        "en": "Heavy Rain/Storm", "ms": "Hujan lebat / ribut taufan", "zh": "暴雨/风暴", "ta": "கனமழை/புயல்",
    },
    "attendance.reason.pencemaran_udara": {
        "en": "Air Pollution", "ms": "Pencemaran udara", "zh": "空气污染", "ta": "காற்று மாசுபாடு",
    },
    "attendance.reason.kemarau": {
        "en": "Drought", "ms": "Kemarau", "zh": "干旱", "ta": "வறட்சி",
    },
    "attendance.reason.cuaca_panas_el_nino": {
        "en": "Hot Weather (El Nino)", "ms": "Cuaca panas (El Nino)", "zh": "高温天气（厄尔尼诺）", "ta": "வெப்பமான வானிலை (எல் நினோ)",
    },
    "attendance.reason.pencemaran_sisa_kimia": {
        "en": "Chemical Waste Pollution", "ms": "Pencemaran sisa kimia", "zh": "化学废料污染", "ta": "இரசாயன கழிவு மாசுபாடு",
    },
    "attendance.reason.pencemaran_alam": {
        "en": "Environmental Pollution", "ms": "Pencemaran alam", "zh": "环境污染", "ta": "சுற்றுச்சூழல் மாசுபாடு",
    },
    "attendance.reason.tanah_runtuh": {
        "en": "Landslide", "ms": "Tanah runtuh", "zh": "山体滑坡", "ta": "நிலச்சரிவு",
    },
    "attendance.reason.digantung_sekolah": {
        "en": "Suspended from School", "ms": "Digantung sekolah", "zh": "被学校停学", "ta": "பள்ளியிலிருந்து இடைநிறுத்தப்பட்டது",
    },
    "attendance.reason.bekerja": {
        "en": "Work", "ms": "Bekerja", "zh": "工作", "ta": "வேலை",
    },
    "attendance.reason.berpindah_randah": {
        "en": "Frequent Relocation", "ms": "Berpindah-randah", "zh": "经常搬迁", "ta": "அடிக்கடி இடம்பெயர்வு",
    },
    "attendance.reason.perebutan_hak_penjagaan_anak": {
        "en": "Child Custody Dispute", "ms": "Perebutan hak penjagaan anak", "zh": "子女监护权争夺", "ta": "குழந்தை பாதுகாப்பு உரிமைத் தகராறு",
    },
    "attendance.reason.mengikut_keluarga_bercuti_berkursus": {
        "en": "Accompanying Family on Vacation/Course", "ms": "Mengikut keluarga bercuti / berkursus", "zh": "陪同家人度假/上课", "ta": "குடும்பத்துடன் விடுமுறை/பயிற்சிக்குச் செல்லுதல்",
    },
    "attendance.reason.menjaga_menguruskan_ahli_keluarga": {
        "en": "Caring for/Managing Family Member", "ms": "Menjaga / menguruskan ahli keluarga", "zh": "照顾/处理家庭成员事务", "ta": "குடும்ப உறுப்பினரை கவனித்தல்/நிர்வகித்தல்",
    },
    "attendance.reason.menjaga_ahli_keluarga_sakit": {
        "en": "Caring for Sick Family Member", "ms": "Menjaga ahli keluarga sakit", "zh": "照顾生病的家庭成员", "ta": "நோய்வாய்ப்பட்ட குடும்ப உறுப்பினரைப் பராமரித்தல்",
    },
    "attendance.reason.kematian_keluarga_terdekat": {
        "en": "Death of Immediate Family Member", "ms": "Kematian keluarga terdekat", "zh": "近亲去世", "ta": "நெருங்கிய குடும்ப உறுப்பினரின் மரணம்",
    },
    "attendance.reason.kemiskinan_kesempitan_hidup": {
        "en": "Poverty/Financial Hardship", "ms": "Kemiskinan / kesempitan hidup", "zh": "贫困/生活拮据", "ta": "வறுமை/பொருளாதார சிரமம்",
    },
    "attendance.reason.masalah_pengangkutan": {
        "en": "Transport Problem", "ms": "Masalah pengangkutan", "zh": "交通问题", "ta": "போக்குவரத்துப் பிரச்சினை",
    },
    "attendance.reason.menziarahi_keluarga_sakit": {
        "en": "Visiting Sick Family Member", "ms": "Menziarahi keluarga sakit", "zh": "探望生病的家人", "ta": "நோய்வாய்ப்பட்ட குடும்ப உறுப்பினரை சந்திக்கச் செல்லுதல்",
    },
    "attendance.reason.balik_kampung": {
        "en": "Returning to Hometown", "ms": "Balik kampung", "zh": "回乡", "ta": "சொந்த ஊருக்குச் செல்லுதல்",
    },
    "attendance.reason.berpindah_ke_luar_negara": {
        "en": "Moving Abroad", "ms": "Berpindah ke luar negara", "zh": "移居国外", "ta": "வெளிநாட்டிற்கு இடம்பெயர்தல்",
    },
    "attendance.reason.krisis_keluarga": {
        "en": "Family Crisis", "ms": "Krisis keluarga", "zh": "家庭危机", "ta": "குடும்ப நெருக்கடி",
    },
    "attendance.reason.lari_dari_rumah": {
        "en": "Ran Away from Home", "ms": "Lari dari rumah", "zh": "离家出走", "ta": "வீட்டை விட்டு ஓடிவிட்டது",
    },
    "attendance.reason.tekanan_perasaan_trauma": {
        "en": "Emotional Stress/Trauma", "ms": "Tekanan perasaan / trauma", "zh": "情绪压力/创伤", "ta": "உணர்ச்சி அழுத்தம்/அதிர்ச்சி",
    },
    "attendance.reason.kesakitan_akibat_haid_permulaan_haid": {
        "en": "Menstrual Pain/Onset of Menstruation", "ms": "Kesakitan akibat haid / permulaan haid", "zh": "经痛/月经初潮", "ta": "மாதவிடாய் வலி/முதல் மாதவிடாய்",
    },
    "attendance.reason.pembelajaran_di_rumah": {
        "en": "Home-Based Learning", "ms": "Pembelajaran di rumah", "zh": "居家学习", "ta": "வீட்டில் கற்றல்",
    },
    "attendance.reason.urusan_peperiksaan": {
        "en": "Examination Matters", "ms": "Urusan peperiksaan", "zh": "考试事务", "ta": "தேர்வு விவகாரங்கள்",
    },
    "attendance.reason.haji_umrah_kegiatan_agama": {
        "en": "Hajj/Umrah/Religious Activity", "ms": "Haji / Umrah / kegiatan agama", "zh": "朝觐/副朝/宗教活动", "ta": "ஹஜ்/உம்ரா/மத நடவடிக்கை",
    },

    "behavior.section_title": {"en": "Behavior", "ms": "Tingkah Laku", "zh": "行为", "ta": "நடத்தை"},
    "behavior.record_title": {"en": "Behavior Record", "ms": "Rekod Tingkah Laku", "zh": "行为记录", "ta": "நடத்தைப் பதிவு"},
    "behavior.incident_type_label": {"en": "Incident Type", "ms": "Jenis Insiden", "zh": "事件类型", "ta": "சம்பவ வகை"},
    "behavior.severity_hint": {
        "en": "<b>Ringan</b>/Minor — one-off, no harm, easily corrected in the moment.<br><b>Sederhana</b>/Moderate — disrupts others or breaches a rule, no safety risk.<br><b>Berat</b>/Serious — actual or credible risk to safety (weapon, injury, violence).",
        "ms": "<b>Ringan</b> — insiden sekali sahaja, tiada kemudaratan, mudah dibetulkan pada masa itu.<br><b>Sederhana</b> — mengganggu orang lain atau melanggar peraturan, tiada risiko keselamatan.<br><b>Berat</b> — risiko sebenar atau munasabah terhadap keselamatan (senjata, kecederaan, keganasan).",
        "zh": "<b>轻微</b>——一次性事件，无伤害，当场可轻易纠正。<br><b>中等</b>——干扰他人或违反规则，无安全风险。<br><b>严重</b>——对安全构成实际或可信的风险（武器、伤害、暴力）。",
        "ta": "<b>ஒல்லியான</b> — ஒரே முறை, தீங்கு இல்லை, உடனடியாக சரிசெய்யக்கூடியது.<br><b>மிதமான</b> — மற்றவர்களைத் தொந்தரவு செய்கிறது அல்லது விதியை மீறுகிறது, பாதுகாப்பு அபாயம் இல்லை.<br><b>கடுமையான</b> — பாதுகாப்புக்கு உண்மையான அல்லது நம்பகமான அபாயம் (ஆயுதம், காயம், வன்முறை).",
    },
    "behavior.action_taken": {"en": "Action Taken", "ms": "Tindakan Diambil", "zh": "已采取的行动", "ta": "எடுக்கப்பட்ட நடவடிக்கை"},
    "behavior.reported_by": {"en": "Reported By", "ms": "Dilaporkan Oleh", "zh": "报告人", "ta": "புகாரளித்தவர்"},
    # Action-taken categories (fixed vocabulary, same convention as
    # incident_type: value entered/stored as the Malay term, keys slugified
    # from it). "Other" is handled separately in the UI (reveals a free-text
    # box) rather than being a translated category itself.
    "behavior.action.amaran_lisan_diberikan": {
        "en": "Verbal Warning Given", "ms": "Amaran Lisan Diberikan", "zh": "已给予口头警告", "ta": "வாய்மொழி எச்சரிக்கை வழங்கப்பட்டது",
    },
    "behavior.action.ibu_bapa_penjaga_dimaklumkan": {
        "en": "Parent/Guardian Notified", "ms": "Ibu Bapa/Penjaga Dimaklumkan", "zh": "已通知家长/监护人", "ta": "பெற்றோர்/பாதுகாவலருக்குத் தெரிவிக்கப்பட்டது",
    },
    "behavior.action.sesi_kaunseling_dijadualkan": {
        "en": "Counseling Session Scheduled", "ms": "Sesi Kaunseling Dijadualkan", "zh": "已安排辅导会谈", "ta": "ஆலோசனை அமர்வு திட்டமிடப்பட்டது",
    },
    "behavior.action.dirujuk_kepada_guru_kelas": {
        "en": "Referred to Class Teacher", "ms": "Dirujuk kepada Guru Kelas", "zh": "已转介给班主任", "ta": "வகுப்பு ஆசிரியரிடம் பரிந்துரைக்கப்பட்டது",
    },
    "behavior.action.dirujuk_kepada_kaunselor_sekolah": {
        "en": "Referred to School Counselor", "ms": "Dirujuk kepada Kaunselor Sekolah", "zh": "已转介给学校辅导员", "ta": "பள்ளி ஆலோசகரிடம் பரிந்துரைக்கப்பட்டது",
    },
    "behavior.action.detensi_dikenakan": {
        "en": "Detention Assigned", "ms": "Detensi Dikenakan", "zh": "已安排留堂", "ta": "தடுப்புக் காவல் வழங்கப்பட்டது",
    },
    "behavior.action.kes_dinaikkan_kepada_pentadbiran": {
        "en": "Case Escalated to Administration", "ms": "Kes Dinaikkan kepada Pentadbiran", "zh": "个案已上报行政部门", "ta": "வழக்கு நிர்வாகத்திற்கு உயர்த்தப்பட்டது",
    },
    "common.other_specify": {"en": "Other (specify)", "ms": "Lain-lain (nyatakan)", "zh": "其他（请注明）", "ta": "மற்றவை (குறிப்பிடவும்)"},
    "common.none": {"en": "None", "ms": "Tiada", "zh": "无", "ta": "எதுவுமில்லை"},

    "mental_health.section_title": {"en": "Mental Health", "ms": "Kesihatan Mental", "zh": "心理健康", "ta": "மனநலம்"},
    "mental_health.record_title": {"en": "Mental Health Record", "ms": "Rekod Kesihatan Mental", "zh": "心理健康记录", "ta": "மனநலப் பதிவு"},
    "mental_health.whooley": {"en": "WHOOLEY", "ms": "WHOOLEY", "zh": "WHOOLEY", "ta": "WHOOLEY"},
    "mental_health.gad2_score": {"en": "GAD-2 Score", "ms": "Skor GAD-2", "zh": "GAD-2 评分", "ta": "GAD-2 மதிப்பெண்"},
    "mental_health.gad2_status": {"en": "GAD-2 Status", "ms": "Status GAD-2", "zh": "GAD-2 状态", "ta": "GAD-2 நிலை"},

    "report.disclaimer": {
        "en": "This is an AI-assisted decision-support document. It does NOT constitute a clinical diagnosis and must be reviewed by a qualified school counselor before use.",
        "ms": "Ini adalah dokumen sokongan keputusan berbantukan AI. Ia BUKAN diagnosis klinikal dan mesti disemak oleh kaunselor sekolah yang bertauliah sebelum digunakan.",
        "zh": "本文件为人工智能辅助决策支持文件，并非临床诊断，使用前必须由合格的学校辅导员审核。",
        "ta": "இது AI உதவியுடன் கூடிய முடிவெடுக்கும் ஆவணம். இது மருத்துவ நோய் கண்டறிதல் அல்ல, பயன்படுத்தும் முன் தகுதி வாய்ந்த பள்ளி ஆலோசகரால் மதிப்பாய்வு செய்யப்பட வேண்டும்.",
    },
    # Dashboard/Reporting disclaimer (report.py's REPORT_DISCLAIMER) — unlike
    # the AI-generated narrative, this is a fixed Python string constant that
    # was never translated at all (always English regardless of `language`).
    # Found while checking the Reporting page after generating a fresh
    # Chinese narrative and seeing everything else translate except this.
    "report.dashboard_disclaimer": {
        "en": (
            "This report is restricted to school leadership and contains identifiable "
            "student information (the Student Cases section). The trend/management "
            "narrative is AI-assisted and aggregate; the case list is not. Handle, "
            "store, and share this document in compliance with the Personal Data "
            "Protection Act 2010 (PDPA). Individual student matters must still follow "
            "established counseling protocols."
        ),
        "ms": (
            "Laporan ini terhad kepada pihak kepimpinan sekolah dan mengandungi maklumat "
            "pelajar yang boleh dikenal pasti (bahagian Kes Pelajar). Naratif trend/"
            "pengurusan adalah berbantukan AI dan bersifat agregat; senarai kes tidak. "
            "Kendalikan, simpan, dan kongsi dokumen ini mengikut Akta Perlindungan Data "
            "Peribadi 2010 (PDPA). Hal ehwal pelajar secara individu masih perlu mengikut "
            "protokol kaunseling yang ditetapkan."
        ),
        "zh": (
            "本报告仅限学校领导层查阅，并包含可识别身份的学生信息（学生个案部分）。"
            "趋势/管理叙述由人工智能辅助生成，属于汇总性质；个案列表则不属于人工智能生成内容。"
            "处理、存储和分享本文件时，须遵守《2010年个人资料保护法》（PDPA）。"
            "个别学生事务仍须遵循既定的辅导程序。"
        ),
        "ta": (
            "இந்த அறிக்கை பள்ளி தலைமைப் பொறுப்பாளர்களுக்கு மட்டுமே வரையறுக்கப்பட்டுள்ளது "
            "மற்றும் அடையாளம் காணக்கூடிய மாணவர் தகவல்களை (மாணவர் வழக்குகள் பிரிவு) "
            "கொண்டுள்ளது. போக்கு/மேலாண்மை விவரிப்பு AI உதவியுடன் உருவாக்கப்பட்டது மற்றும் "
            "திரட்டப்பட்டது; வழக்குப் பட்டியல் அவ்வாறு அல்ல. இந்த ஆவணத்தை 2010 தனிநபர் "
            "தரவு பாதுகாப்புச் சட்டத்திற்கு (PDPA) இணங்க கையாளவும், சேமிக்கவும், பகிரவும். "
            "தனிப்பட்ட மாணவர் விவகாரங்கள் நிறுவப்பட்ட ஆலோசனை நெறிமுறைகளைத் தொடர வேண்டும்."
        ),
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
