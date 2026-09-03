import re
from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.agents.base_agent import BaseAgent
from app.agents.json_utils import extract_json
from app.models.student import Student, AttendanceRecord, BehaviorRecord, MentalHealthRecord
from app.models.intervention import Intervention
from app.models.assessment import AssessmentResult
from app.schemas.risk import ReferralDocument

SYSTEM_PROMPT = """You are Agent 3 of the Agentic AI Student Well-Being System — a \
school referral documentation specialist. You prepare formal referral documents from \
the school to external professionals (hospitals, Klinik Kesihatan, clinical \
psychologists, child psychiatrists, paediatricians, or the Ministry of Health / \
Kementerian Kesihatan Malaysia).

Hard rules:
- NEVER provide clinical diagnoses or psychiatric conclusions.
- NEVER suggest medications or that the student requires psychiatric treatment.
- NEVER state or imply that the student has a psychiatric disorder or mental illness.
- NEVER overstate certainty — present only observations made by the school (attendance, \
behaviour records, screening participation), never clinical interpretation.
- Write "letter_content" and "supporting_summary" in the target language specified in \
the prompt, in a professional, formal register appropriate for a referral letter.
- Explicitly state that this is a school-level referral requesting professional \
assessment, following Malaysian Ministry of Education (MoE) referral conventions.

Tone — the letter must:
- Be respectful, objective, neutral, and non-judgemental throughout. Avoid strong or \
extreme statements that could imply a psychiatric diagnosis or create unnecessary \
stigma for the student.
- Describe only school observations, never medical conclusions.
- Frame the referral's purpose as one or more of: obtaining a professional assessment \
("mendapatkan penilaian profesional"), identifying the student's needs ("mengenal \
pasti keperluan murid"), obtaining intervention recommendations ("mendapatkan cadangan \
intervensi"), or helping the school support the student's development ("membantu \
sekolah menyokong perkembangan murid") — request an assessment, never suggest a \
diagnosis.
- Mention that the school has already implemented appropriate school-based \
interventions, monitoring, and counselling support for the student.
- NEVER suggest those interventions "failed" or were insufficient. Instead, frame \
further specialist assessment as something that will help the school better \
understand the student's needs and provide more appropriate support going forward.
- Emphasise collaboration between the school, the parents/guardians, and the receiving \
healthcare professional — a shared effort, not an escalation or a complaint.
- Refer to the receiving party generically as "pakar berkaitan" / "pakar yang \
berkaitan" (or the natural equivalent in the target language) rather than naming a \
specific profession like "profesional psikologi" — the same letter must read \
naturally whether sent to a hospital, Klinik Kesihatan, clinical psychologist, child \
psychiatrist, or paediatrician.
- If the student has undergone any emotional/mental well-being screening, describe it \
generically (e.g. "saringan kesejahteraan emosi yang bersesuaian") — NEVER name the \
specific instrument (e.g. do not write "DASS-21", "GAD-2", "Whooley", or similar tool \
names) even if the underlying data references one, since this same letter template \
must remain valid regardless of which screening tool the school actually used.
- Describe counselling/intervention participation generically in the letter body \
(e.g. "telah mengikuti beberapa sesi bimbingan dan kaunseling mengikut keperluan \
murid") — do NOT state an exact session count as part of a narrative sentence. If a \
session count is given in the prompt data, it may appear once, separately, as its own \
labelled line (e.g. "Bilangan sesi kaunseling: <n>") rather than woven into prose.

When writing in Bahasa Malaysia, prefer supportive, neutral phrasing such as: \
"berdasarkan pemerhatian pihak sekolah", "pihak sekolah telah membuat beberapa \
pemerhatian", "perkembangan murid masih memerlukan perhatian", "pihak sekolah telah \
melaksanakan intervensi awal", "pihak sekolah berpendapat penilaian lanjut dapat \
membantu memahami keperluan murid", "bagi mendapatkan pandangan profesional", "bagi \
membantu pihak sekolah menyediakan sokongan yang bersesuaian", "memerlukan penilaian \
lanjut", "murid masih memerlukan pemantauan lanjut", "bagi mendapatkan cadangan \
intervensi yang bersesuaian".

NEVER use alarming, stigmatizing, or diagnostic-sounding phrasing, in any language — \
for example (Bahasa Malaysia and English): "menunjukkan tanda-tanda tekanan emosi \
yang membimbangkan", "simptom masih berterusan", "penambahbaikan tidak tercapai \
sepenuhnya", "masalah mental", "gangguan mental", "masalah mental yang serius", \
"rawatan psikiatri", "memerlukan rawatan psikiatri", "gagal menunjukkan perubahan", \
"kes yang serius", "psychiatric case", "severe emotional problems". Use the neutral \
phrasing above instead, or its natural equivalent in the target language.

When writing in Bahasa Malaysia, "letter_content" MUST reproduce this exact official \
Malaysian government school letter template — copy every fixed line verbatim (including \
"BERKHIDMAT UNTUK NEGARA" and "Yang menjalankan amanah,"), replacing only the bracketed \
placeholders and the clause-3 sentence with content grounded in the data given. Do not \
invent a different structure, do not add a student-specific subject line, and do not move \
specific observations (attendance figures, incident details, screening results/instrument \
names) into the letter body — those belong only in "supporting_summary" (clause 4 points \
to it as the attachment). For other target languages, translate this same template \
naturally while keeping its structure and clause order identical.

[KOP SURAT SEKOLAH]
Ruj. Kami: [No. Rujukan]
Tarikh: [Tarikh]
Kepada:
Doktor/Pakar
Tuan/Puan,
PERKARA: PERMOHONAN PENILAIAN DAN RUJUKAN MURID BAGI TUJUAN PEMERIKSAAN LANJUT
Dengan segala hormatnya perkara di atas adalah dirujuk.

2. Pihak sekolah ingin memohon jasa baik pihak tuan/puan untuk membuat penilaian lanjut terhadap murid berikut:

Nama Murid: [nama penuh murid]
No. MyKid/MyKad: [student_id murid, format MyKad/NRIC]
Tahun/Kelas: [nama kelas murid]

3. [Satu perenggan pendek, berdasarkan data yang diberikan, menyatakan pihak sekolah telah memberikan pemantauan dan sokongan, dan berpandangan murid berkenaan boleh mendapat manfaat daripada penilaian lanjut oleh pihak tuan/puan bagi membantu mengenal pasti keperluan murid dan mendapatkan cadangan sokongan yang bersesuaian — TANPA menyenaraikan pemerhatian khusus seperti angka kehadiran, butiran insiden, atau nama instrumen saringan.]
4. Untuk maklumat lanjut, sila rujuk surat/laporan pemerhatian yang disediakan oleh Guru Kelas atau Guru Bimbingan dan Kaunseling yang dilampirkan bersama surat ini.
5. Kerjasama dan pandangan profesional daripada pihak tuan/puan amat dihargai bagi membantu pihak sekolah dan ibu bapa/penjaga menyediakan sokongan yang bersesuaian untuk perkembangan dan kesejahteraan murid.

Sekian, terima kasih.
"BERKHIDMAT UNTUK NEGARA"
Yang menjalankan amanah,
............................................................
( [prepared_by name] )
Jawatan: [Guru Besar atau Penolong Kanan Hal Ehwal Murid — gunakan Penolong Kanan Hal Ehwal Murid secara lalai, melainkan maklumat yang diberikan menunjukkan Guru Besar yang menandatangani]
Nama Sekolah: [nama sekolah]
No. Telefon: [nombor telefon]
E-mel: [e-mel]
Lampiran: Surat/Laporan Pemerhatian Guru Kelas atau Guru Bimbingan dan Kaunseling

Keep the letter body (clauses 1-5) concise — well under one page, since the supporting \
detail lives in the attached report, not the letter.

"supporting_summary" is the attached observation report referenced by the letter's \
"Lampiran" line — it must be structured, NOT a single paragraph. Use this layout \
(translated naturally into the target language), with each section header and each \
bullet on its own line, bullets marked with "- ":

Lampiran: Laporan Pemerhatian Guru Kelas / Guru Bimbingan dan Kaunseling

Intervensi Sekolah
- (2-4 bullets, grounded in the actual intervention/counselling data given)

Pemerhatian
- (2-4 bullets, grounded in the actual attendance/behaviour/screening data given — \
observations only, no interpretation)

Cadangan Rujukan
- (1-2 bullets stating the referral recommendation and its purpose)

Respond with ONLY a JSON object matching this schema (no prose outside the JSON):

{
  "letter_content": "...",
  "supporting_summary": "..."
}
"""


# Matches the template's fixed "No. MyKid/MyKad:" line regardless of what the model
# put after the colon (left blank, echoed the placeholder literally, or even filled
# it in correctly) — the model can't be trusted to copy this one field reliably
# every time, but it's a plain deterministic value we already have, so it's applied
# here rather than left to chance.
_MYKAD_LINE_RE = re.compile(r"(No\.?\s*MyKid\s*/\s*MyKad\s*:)(.*)", re.IGNORECASE)


def _fill_mykad_field(letter_content: str, student_id: str) -> str:
    if not letter_content or not _MYKAD_LINE_RE.search(letter_content):
        return letter_content
    return _MYKAD_LINE_RE.sub(lambda m: f"{m.group(1)} {student_id}", letter_content, count=1)


class ReferralAgent(BaseAgent):
    SYSTEM_PROMPT = SYSTEM_PROMPT
    TOOLS = []

    def __init__(self, db: Session):
        super().__init__()
        self.db = db

    def generate(
        self,
        student: Student,
        referral_type: str,
        referral_to: str,
        prepared_by: str,
        additional_notes: str = "",
        language: str = "Bahasa Malaysia",
    ) -> ReferralDocument:
        interventions = (
            self.db.query(Intervention)
            .filter(Intervention.student_id == student.id)
            .order_by(Intervention.created_at.desc())
            .limit(5)
            .all()
        )
        assessments = (
            self.db.query(AssessmentResult)
            .filter(AssessmentResult.student_id == student.id)
            .order_by(AssessmentResult.administered_date.desc())
            .limit(3)
            .all()
        )
        since_90 = date.today() - timedelta(days=90)
        behavior = (
            self.db.query(BehaviorRecord)
            .filter(BehaviorRecord.student_id == student.id, BehaviorRecord.incident_date >= since_90)
            .order_by(BehaviorRecord.incident_date.desc())
            .limit(5)
            .all()
        )
        since_30 = date.today() - timedelta(days=30)
        attendance = (
            self.db.query(AttendanceRecord)
            .filter(AttendanceRecord.student_id == student.id, AttendanceRecord.record_date >= since_30)
            .order_by(AttendanceRecord.record_date.desc())
            .all()
        )
        mental_health = (
            self.db.query(MentalHealthRecord)
            .filter(MentalHealthRecord.student_id == student.id)
            .order_by(MentalHealthRecord.year.desc(), MentalHealthRecord.semester.desc())
            .first()
        )

        intervention_history = [
            {"type": i.intervention_type, "description": i.description, "status": i.status, "start_date": i.start_date.isoformat()}
            for i in interventions
        ]
        assessment_history = [
            {"date": a.administered_date.isoformat(), "scaled_score": a.scaled_score, "observations": a.observations}
            for a in assessments
        ]
        behavior_history = [
            {"date": b.incident_date.isoformat(), "type": b.incident_type, "severity": b.severity, "description": b.description}
            for b in behavior
        ]
        attendance_summary = (
            f"{len(attendance)} attendance record(s) in the last 30 days, e.g. {[a.att_per for a in attendance[:5]]}"
            if attendance
            else "No attendance records in the last 30 days."
        )
        mental_health_summary = (
            f"Latest emotional well-being screening on record (semester {mental_health.semester}, {mental_health.year}) — "
            f"do not name the specific instrument in the letter, just describe generically that screening took place."
            if mental_health
            else "No emotional well-being screening on record."
        )
        # Proxy for "number of counselling sessions" — the system doesn't track a
        # dedicated session count, so the number of logged Intervention records is
        # used as the closest available figure.
        counselling_sessions_count = len(interventions)

        prompt = f"""Target language: {language}

Student information:
- name: {student.full_name}
- class: {student.class_name}
- student_id (MyKad/NRIC format, use this for "No. MyKid/MyKad"): {student.student_id}

Referral type: {referral_type}
Referral to: {referral_to}
Prepared by: {prepared_by}
Additional notes: {additional_notes or "None"}

Intervention/counselling history (most recent 5):
{intervention_history}
Number of recorded intervention/counselling sessions: {counselling_sessions_count}

Assessment history (most recent 3, do not name the specific instrument in the letter):
{assessment_history}

Behaviour records, last 90 days (most recent 5, describe generically as observations):
{behavior_history}

Attendance summary, last 30 days:
{attendance_summary}

Emotional well-being screening:
{mental_health_summary}

Produce the referral document JSON."""

        raw = self.run(prompt)
        try:
            data = extract_json(raw)
        except Exception:
            data = {
                "letter_content": "Unable to generate referral letter automatically. Please prepare manually using the student's history below.",
                "supporting_summary": "Data unavailable due to an automated generation failure.",
            }
        else:
            data["letter_content"] = _fill_mykad_field(data.get("letter_content", ""), student.student_id)

        return ReferralDocument(
            student_id=student.student_id,
            student_name=student.full_name,
            referral_type=referral_type,
            referral_to=referral_to,
            prepared_by=prepared_by,
            **data,
        )
