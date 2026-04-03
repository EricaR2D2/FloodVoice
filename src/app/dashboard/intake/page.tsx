'use client';

import { useState, useEffect } from 'react';
import { supabase } from '@/lib/supabase';
import { CheckCircle } from 'lucide-react';

// ─── Translation Dictionary (ported from FloodVoice Intake Code.txt) ──────────
const T = {
  en: {
    title: 'FloodVoice AI — Resident Registration', sub: 'Flood Emergency Early Warning System',
    privacy: 'PRIVACY NOTICE: Information collected is used solely for flood emergency response. Data is NOT shared with immigration authorities or any government agency. This program serves all residents regardless of immigration status.',
    req: '* Required field',
    s1: 'Section 1 — Personal information', s2: 'Section 2 — Household & housing',
    s3: 'Section 3 — Emergency contact',   s4: 'Section 4 — Health & access needs',
    s5: 'Section 5 — Contact preferences', s6: 'Section 6 — Consent',
    name: 'Full name *', dob: 'Date of birth *', phone: 'Phone number *',
    altPhone: 'Alternate phone', email: 'Email (optional)',
    address: 'Home address *', borough: 'Borough / ZIP code *', floor: 'Floor / apt #',
    basement: 'Basement apartment?', household: '# people in household *',
    yes: 'Yes', no: 'No',
    kinName: 'Next of kin — full name *', kinPhone: 'Next of kin — phone *',
    kinRel: 'Relationship', kinAddr: 'Next of kin address (if different)',
    disability: 'Disability affecting evacuation?', disabilityDesc: 'Please describe',
    medical: 'Medical conditions relevant to emergency response (optional)',
    language: 'Preferred language *',
    langs: ['English', 'Español', 'Bengali', 'Mandarin', 'Korean', 'Haitian Creole', 'Other'],
    contactPref: 'Preferred contact method *',
    call: 'Voice call', sms: 'SMS / text', both: 'Both',
    bestTime: 'Best time to reach you',
    morning: 'Morning (8am–12pm)', afternoon: 'Afternoon (12–5pm)', evening: 'Evening (5–8pm)', anytime: 'Anytime',
    consent: 'I consent to be contacted by FloodVoice AI during flood warnings for welfare checks. I understand that pressing 2 during a call will alert emergency responders to my location. Data is used only for flood emergency response.',
    signature: 'Signature (type full name) *', date: 'Date *',
    forLiaison: 'For liaison use only',
    liaisonName: 'Liaison name', liaisonOrg: 'Organization', regDate: 'Registration date',
    neighborhood: 'Neighborhood / pilot site', formId: 'Form ID',
    submitBtn: 'Submit registration',
    successTitle: 'Registration submitted',
    successBody: 'This resident has been enrolled in FloodVoice AI flood emergency alerts.',
  },
  es: {
    title: 'FloodVoice AI — Registro de Residente', sub: 'Sistema de Alerta Temprana de Emergencias por Inundaciones',
    privacy: 'AVISO DE PRIVACIDAD: La información recopilada se utiliza únicamente para la respuesta a emergencias por inundaciones. Los datos NO se comparten con autoridades de inmigración. Este programa sirve a todos los residentes independientemente de su estatus migratorio.',
    req: '* Campo obligatorio',
    s1: 'Sección 1 — Información personal', s2: 'Sección 2 — Hogar y vivienda',
    s3: 'Sección 3 — Contacto de emergencia', s4: 'Sección 4 — Salud y necesidades de acceso',
    s5: 'Sección 5 — Preferencias de contacto', s6: 'Sección 6 — Consentimiento',
    name: 'Nombre completo *', dob: 'Fecha de nacimiento *', phone: 'Teléfono *',
    altPhone: 'Teléfono alternativo', email: 'Correo electrónico (opcional)',
    address: 'Dirección *', borough: 'Borough / código postal *', floor: 'Piso / apto',
    basement: '¿Apartamento en sótano?', household: '# de personas en el hogar *',
    yes: 'Sí', no: 'No',
    kinName: 'Familiar de emergencia — nombre *', kinPhone: 'Familiar — teléfono *',
    kinRel: 'Parentesco', kinAddr: 'Dirección del familiar (si es diferente)',
    disability: '¿Discapacidad que afecte la evacuación?', disabilityDesc: 'Por favor describa',
    medical: 'Condiciones médicas relevantes (opcional)',
    language: 'Idioma preferido *',
    langs: ['Inglés', 'Español', 'Bengalí', 'Mandarín', 'Coreano', 'Criollo haitiano', 'Otro'],
    contactPref: 'Método de contacto preferido *',
    call: 'Llamada de voz', sms: 'SMS / texto', both: 'Ambos',
    bestTime: 'Mejor hora para comunicarse',
    morning: 'Mañana (8–12)', afternoon: 'Tarde (12–17)', evening: 'Noche (17–20)', anytime: 'Cualquier hora',
    consent: 'Doy mi consentimiento para ser contactado/a por FloodVoice AI durante alertas de inundación. Entiendo que al presionar 2 durante una llamada alertará a los servicios de emergencia sobre mi ubicación.',
    signature: 'Firma (escriba nombre completo) *', date: 'Fecha *',
    forLiaison: 'Solo para uso del enlace comunitario',
    liaisonName: 'Nombre del enlace', liaisonOrg: 'Organización', regDate: 'Fecha de registro',
    neighborhood: 'Vecindario / sitio piloto', formId: 'ID del formulario',
    submitBtn: 'Enviar registro',
    successTitle: 'Registro enviado',
    successBody: 'Este residente ha sido inscrito en las alertas de emergencia de FloodVoice AI.',
  },
  bn: {
    title: 'FloodVoice AI — বাসিন্দা নিবন্ধন', sub: 'বন্যা জরুরি প্রাথমিক সতর্কতা ব্যবস্থা',
    privacy: 'গোপনীয়তার নোটিশ: তথ্য শুধুমাত্র বন্যা জরুরি সাড়ার জন্য ব্যবহার করা হয়। অভিবাসন কর্তৃপক্ষের সাথে শেয়ার করা হয় না। অভিবাসন মর্যাদা নির্বিশেষে সকলকে সেবা দেওয়া হয়।',
    req: '* প্রয়োজনীয় তথ্য',
    s1: 'বিভাগ ১ — ব্যক্তিগত তথ্য', s2: 'বিভাগ ২ — পরিবার ও আবাসন',
    s3: 'বিভাগ ৩ — জরুরি যোগাযোগ', s4: 'বিভাগ ৪ — স্বাস্থ্য ও প্রবেশাধিকার',
    s5: 'বিভাগ ৫ — যোগাযোগের পছন্দ', s6: 'বিভাগ ৬ — সম্মতি',
    name: 'পুরো নাম *', dob: 'জন্ম তারিখ *', phone: 'ফোন নম্বর *',
    altPhone: 'বিকল্প ফোন', email: 'ইমেইল (ঐচ্ছিক)',
    address: 'বাড়ির ঠিকানা *', borough: 'বরো / জিপ কোড *', floor: 'তলা / অ্যাপার্টমেন্ট',
    basement: 'বেসমেন্ট অ্যাপার্টমেন্ট?', household: 'পরিবারের সদস্য সংখ্যা *',
    yes: 'হ্যাঁ', no: 'না',
    kinName: 'নিকটতম স্বজন — নাম *', kinPhone: 'নিকটতম স্বজন — ফোন *',
    kinRel: 'সম্পর্ক', kinAddr: 'স্বজনের ঠিকানা (যদি আলাদা হয়)',
    disability: 'সরিয়ে নেওয়াকে প্রভাবিত করে এমন প্রতিবন্ধিতা?', disabilityDesc: 'বর্ণনা করুন',
    medical: 'জরুরি সাড়ার জন্য চিকিৎসা অবস্থা (ঐচ্ছিক)',
    language: 'পছন্দের ভাষা *',
    langs: ['ইংরেজি', 'স্প্যানিশ', 'বাংলা', 'ম্যান্ডারিন', 'কোরিয়ান', 'হাইতিয়ান ক্রেওল', 'অন্যান্য'],
    contactPref: 'পছন্দের যোগাযোগ পদ্ধতি *',
    call: 'ভয়েস কল', sms: 'এসএমএস', both: 'উভয়',
    bestTime: 'যোগাযোগের সেরা সময়',
    morning: 'সকাল (৮–১২)', afternoon: 'বিকেল (১২–৫)', evening: 'সন্ধ্যা (৫–৮)', anytime: 'যেকোনো সময়',
    consent: 'আমি বন্যার সতর্কতার সময় FloodVoice AI দ্বারা যোগাযোগের অনুমতি দিচ্ছি। কলের সময় ২ চাপলে জরুরি সেবাকারীদের কাছে আমার অবস্থান জানানো হবে।',
    signature: 'স্বাক্ষর (পুরো নাম লিখুন) *', date: 'তারিখ *',
    forLiaison: 'শুধুমাত্র কমিউনিটি লিয়াজোঁর ব্যবহারের জন্য',
    liaisonName: 'লিয়াজোঁর নাম', liaisonOrg: 'সংস্থা', regDate: 'নিবন্ধনের তারিখ',
    neighborhood: 'এলাকা / পাইলট সাইট', formId: 'ফর্ম আইডি',
    submitBtn: 'নিবন্ধন জমা দিন',
    successTitle: 'নিবন্ধন সম্পন্ন',
    successBody: 'এই বাসিন্দাকে FloodVoice AI বন্যা জরুরি সতর্কতায় নথিভুক্ত করা হয়েছে।',
  },
  zh: {
    title: 'FloodVoice AI — 居民登记', sub: '洪水紧急预警系统',
    privacy: '隐私声明：收集的信息仅用于洪水紧急响应，不与移民局共享。本项目为所有居民服务，无论移民身份如何。',
    req: '* 必填项',
    s1: '第一部分 — 个人信息', s2: '第二部分 — 家庭与住房',
    s3: '第三部分 — 紧急联系人', s4: '第四部分 — 健康与无障碍需求',
    s5: '第五部分 — 联系偏好', s6: '第六部分 — 同意书',
    name: '姓名 *', dob: '出生日期 *', phone: '电话号码 *',
    altPhone: '备用电话', email: '电子邮件（可选）',
    address: '家庭地址 *', borough: '行政区 / 邮编 *', floor: '楼层 / 公寓号',
    basement: '地下室公寓？', household: '家庭成员人数 *',
    yes: '是', no: '否',
    kinName: '紧急联系人 — 姓名 *', kinPhone: '紧急联系人 — 电话 *',
    kinRel: '关系', kinAddr: '紧急联系人地址（如不同）',
    disability: '是否有影响疏散的残疾？', disabilityDesc: '请描述',
    medical: '与紧急响应相关的病情（可选）',
    language: '首选语言 *',
    langs: ['英语', '西班牙语', '孟加拉语', '普通话', '韩语', '海地克里奥尔语', '其他'],
    contactPref: '首选联系方式 *',
    call: '语音电话', sms: '短信', both: '两者均可',
    bestTime: '最佳联系时间',
    morning: '上午（8–12时）', afternoon: '下午（12–17时）', evening: '傍晚（17–20时）', anytime: '任何时间',
    consent: '本人同意在洪水预警期间接受 FloodVoice AI 的联系进行安全确认。通话中按 2 将向急救人员发送位置信息。数据仅用于洪水紧急响应。',
    signature: '签名（请输入全名）*', date: '日期 *',
    forLiaison: '仅供社区联络员使用',
    liaisonName: '联络员姓名', liaisonOrg: '所属机构', regDate: '注册日期',
    neighborhood: '社区 / 试点地点', formId: '表格编号',
    submitBtn: '提交登记',
    successTitle: '登记已提交',
    successBody: '该居民已成功注册 FloodVoice AI 洪水紧急警报。',
  },
} as const;

type Lang = keyof typeof T;

interface IntakeFormData {
  name: string; dob: string; phone: string; altPhone: string; email: string;
  address: string; borough: string; floor: string; basement: string; household: string;
  kinName: string; kinPhone: string; kinRel: string; kinAddr: string;
  disability: string; disabilityDesc: string; medical: string;
  preferredLangs: string[]; contactMethod: string; bestTime: string;
  signature: string; consentDate: string;
  liaisonName: string; liaisonOrg: string; regDate: string; neighborhood: string; formId: string;
}

function generateFormId(): string {
  const d = new Date().toISOString().slice(0, 10).replace(/-/g, '');
  const r = Math.floor(1000 + Math.random() * 9000);
  return `FV-${d}-${r}`;
}

// ─── Reusable styled sub-components ───────────────────────────────────────────
const inputCls = 'w-full text-sm px-2 py-1.5 border border-gray-300 rounded-md bg-white text-gray-900 outline-none focus:border-[#378ADD] focus:ring-2 focus:ring-[#E6F1FB]';
const labelCls = 'block text-[11px] font-medium text-[#0C447C] mb-1';

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <label className={labelCls}>{label}</label>
      {children}
    </div>
  );
}

function SectionHeader({ text }: { text: string }) {
  return <div className="bg-[#0C447C] text-[#E6F1FB] text-[11px] font-medium px-3 py-1.5 rounded-t-lg tracking-wide">{text}</div>;
}

function SectionBody({ children }: { children: React.ReactNode }) {
  return <div className="border border-t-0 border-gray-300 rounded-b-lg p-3 bg-white space-y-3">{children}</div>;
}

function YesNo({ name, value, onChange, yesLabel, noLabel }: { name: string; value: string; onChange: (v: string) => void; yesLabel: string; noLabel: string }) {
  return (
    <div className="flex gap-4">
      {[['yes', yesLabel], ['no', noLabel]].map(([v, lbl]) => (
        <label key={v} className="flex items-center gap-1.5 text-xs text-gray-800 cursor-pointer">
          <input type="radio" name={name} value={v} checked={value === v} onChange={() => onChange(v)}
            className="w-3.5 h-3.5 accent-[#0C447C]" />
          {lbl}
        </label>
      ))}
    </div>
  );
}

// ─── Main Page Component ──────────────────────────────────────────────────────
export default function IntakePage() {
  const [lang, setLang] = useState<Lang>('en');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [form, setForm] = useState<IntakeFormData>({
    name: '', dob: '', phone: '', altPhone: '', email: '',
    address: '', borough: '', floor: '', basement: '', household: '',
    kinName: '', kinPhone: '', kinRel: '', kinAddr: '',
    disability: '', disabilityDesc: '', medical: '',
    preferredLangs: [], contactMethod: '', bestTime: '',
    signature: '', consentDate: '',
    liaisonName: '', liaisonOrg: '',
    regDate: new Date().toISOString().split('T')[0],
    neighborhood: '', formId: generateFormId(),
  });

  const t = T[lang];
  const upd = (field: keyof IntakeFormData, val: string) => setForm(p => ({ ...p, [field]: val }));

  const toggleLang = (langLabel: string) => {
    setForm(p => ({
      ...p,
      preferredLangs: p.preferredLangs.includes(langLabel)
        ? p.preferredLangs.filter(l => l !== langLabel)
        : [...p.preferredLangs, langLabel],
    }));
  };

  const handleSubmit = async () => {
    const missing = !form.name || !form.phone || !form.address || !form.signature;
    if (missing) {
      const msg: Record<Lang, string> = {
        en: 'Please complete all required fields (*).',
        es: 'Por favor complete todos los campos obligatorios (*).',
        bn: 'অনুগ্রহ করে সমস্ত প্রয়োজনীয় ক্ষেত্র পূরণ করুন।',
        zh: '请填写所有必填项 (*)。',
      };
      alert(msg[lang]);
      return;
    }
    setIsSubmitting(true);
    const { data: { user } } = await supabase.auth.getUser();
    const { error } = await supabase.from('residents').insert({
      name: form.name,
      phone_number: form.phone,
      address: form.address,
      zip_code: form.borough,
      health_conditions: form.medical || null,
      language: form.preferredLangs[0]?.toLowerCase().slice(0, 2) || 'en',
      status: 'pending',
      liaison_id: user?.id || '00000000-0000-0000-0000-000000000000',
      // New intake columns (require migration_intake_form.sql to be run first)
      date_of_birth: form.dob || null,
      alternate_phone: form.altPhone || null,
      email: form.email || null,
      floor_apt: form.floor || null,
      basement_apartment: form.basement === 'yes' ? true : form.basement === 'no' ? false : null,
      household_size: form.household ? parseInt(form.household) : null,
      next_of_kin_name: form.kinName || null,
      next_of_kin_phone: form.kinPhone || null,
      next_of_kin_relationship: form.kinRel || null,
      next_of_kin_address: form.kinAddr || null,
      has_disability: form.disability === 'yes' ? true : form.disability === 'no' ? false : null,
      disability_description: form.disabilityDesc || null,
      preferred_languages: form.preferredLangs.join(', ') || null,
      contact_method: form.contactMethod || null,
      best_time_to_reach: form.bestTime || null,
      consent_signature: form.signature,
      consent_date: form.consentDate || null,
      liaison_name: form.liaisonName || null,
      liaison_org: form.liaisonOrg || null,
      registration_date: form.regDate || null,
      neighborhood: form.neighborhood || null,
      form_id: form.formId,
    });
    setIsSubmitting(false);
    if (!error) { setIsSuccess(true); }
    else { alert('Error saving registration: ' + error.message); }
  };

  return (
    <div className="max-w-xl mx-auto pb-10" style={{ fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" }}>

      {/* ── Header ── */}
      <div className="bg-[#0C447C] px-4 py-3 rounded-t-xl">
        <h1 className="text-[#E6F1FB] text-[15px] font-medium">{t.title}</h1>
        <p className="text-[#85B7EB] text-[11px]">{t.sub}</p>
      </div>
      <div className="h-1 bg-[#EF9F27]" />

      {/* ── Language Tabs ── */}
      <div className="flex border-b border-gray-300 bg-gray-100">
        {(['en', 'es', 'bn', 'zh'] as Lang[]).map((l, i) => (
          <button key={l} onClick={() => setLang(l)}
            className={`flex-1 py-2.5 text-xs text-center border-b-2 transition-all ${lang === l ? 'border-[#0C447C] text-[#0C447C] font-medium bg-white' : 'border-transparent text-gray-500'}`}>
            {['English', 'Español', 'বাংলা', '中文'][i]}
          </button>
        ))}
      </div>

      {/* ── Privacy Notice ── */}
      <div className="mx-0 mt-3 px-3 py-2.5 bg-[#FFF8EC] border-l-4 border-[#EF9F27] rounded-r-md text-[11px] text-[#5C3000] leading-relaxed">
        {t.privacy}
      </div>

      <div className="space-y-3.5 mt-3.5">

        {/* ── Section 1: Personal Information ── */}
        <div>
          <SectionHeader text={t.s1} />
          <SectionBody>
            <Field label={t.name}><input className={inputCls} type="text" autoComplete="name" value={form.name} onChange={e => upd('name', e.target.value)} /></Field>
            <div className="grid grid-cols-2 gap-2.5">
              <Field label={t.dob}><input className={inputCls} type="date" value={form.dob} onChange={e => upd('dob', e.target.value)} /></Field>
              <Field label={t.phone}><input className={inputCls} type="tel" autoComplete="tel" value={form.phone} onChange={e => upd('phone', e.target.value)} /></Field>
            </div>
            <div className="grid grid-cols-2 gap-2.5">
              <Field label={t.altPhone}><input className={inputCls} type="tel" value={form.altPhone} onChange={e => upd('altPhone', e.target.value)} /></Field>
              <Field label={t.email}><input className={inputCls} type="email" autoComplete="email" value={form.email} onChange={e => upd('email', e.target.value)} /></Field>
            </div>
          </SectionBody>
        </div>

        {/* ── Section 2: Household & Housing ── */}
        <div>
          <SectionHeader text={t.s2} />
          <SectionBody>
            <Field label={t.address}><input className={inputCls} type="text" autoComplete="street-address" value={form.address} onChange={e => upd('address', e.target.value)} /></Field>
            <div className="grid grid-cols-2 gap-2.5">
              <Field label={t.borough}><input className={inputCls} type="text" value={form.borough} onChange={e => upd('borough', e.target.value)} /></Field>
              <Field label={t.floor}><input className={inputCls} type="text" value={form.floor} onChange={e => upd('floor', e.target.value)} /></Field>
            </div>
            <div className="flex items-center justify-between py-1.5 border-b border-gray-100">
              <span className={labelCls + ' mb-0'}>{t.basement}</span>
              <YesNo name="basement" value={form.basement} onChange={v => upd('basement', v)} yesLabel={t.yes} noLabel={t.no} />
            </div>
            <Field label={t.household}><input className={inputCls} type="number" min="1" max="20" style={{ width: 80 }} value={form.household} onChange={e => upd('household', e.target.value)} /></Field>
          </SectionBody>
        </div>

        {/* ── Section 3: Emergency Contact ── */}
        <div>
          <SectionHeader text={t.s3} />
          <SectionBody>
            <div className="grid grid-cols-2 gap-2.5">
              <Field label={t.kinName}><input className={inputCls} type="text" value={form.kinName} onChange={e => upd('kinName', e.target.value)} /></Field>
              <Field label={t.kinPhone}><input className={inputCls} type="tel" value={form.kinPhone} onChange={e => upd('kinPhone', e.target.value)} /></Field>
            </div>
            <div className="grid grid-cols-2 gap-2.5">
              <Field label={t.kinRel}><input className={inputCls} type="text" value={form.kinRel} onChange={e => upd('kinRel', e.target.value)} /></Field>
              <Field label={t.kinAddr}><input className={inputCls} type="text" value={form.kinAddr} onChange={e => upd('kinAddr', e.target.value)} /></Field>
            </div>
          </SectionBody>
        </div>

        {/* ── Section 4: Health & Access Needs ── */}
        <div>
          <SectionHeader text={t.s4} />
          <SectionBody>
            <div className="flex items-center justify-between py-1.5 border-b border-gray-100">
              <span className={labelCls + ' mb-0'}>{t.disability}</span>
              <YesNo name="disability" value={form.disability} onChange={v => upd('disability', v)} yesLabel={t.yes} noLabel={t.no} />
            </div>
            {form.disability === 'yes' && (
              <Field label={t.disabilityDesc}><input className={inputCls} type="text" value={form.disabilityDesc} onChange={e => upd('disabilityDesc', e.target.value)} /></Field>
            )}
            <Field label={t.medical}>
              <textarea className={inputCls + ' resize-none h-14'} value={form.medical} onChange={e => upd('medical', e.target.value)} />
            </Field>
          </SectionBody>
        </div>

        {/* ── Section 5: Contact Preferences ── */}
        <div>
          <SectionHeader text={t.s5} />
          <SectionBody>
            <div>
              <label className={labelCls}>{t.language}</label>
              <div className="flex flex-wrap gap-x-4 gap-y-2 mt-1">
                {t.langs.map((lbl) => (
                  <label key={lbl} className="flex items-center gap-1.5 text-xs text-gray-800 cursor-pointer">
                    <input type="checkbox" checked={form.preferredLangs.includes(lbl)} onChange={() => toggleLang(lbl)} className="w-3.5 h-3.5 accent-[#0C447C]" />
                    {lbl}
                  </label>
                ))}
              </div>
            </div>
            <div>
              <label className={labelCls}>{t.contactPref}</label>
              <div className="flex gap-4 mt-1">
                {[['call', t.call], ['sms', t.sms], ['both', t.both]].map(([v, lbl]) => (
                  <label key={v} className="flex items-center gap-1.5 text-xs text-gray-800 cursor-pointer">
                    <input type="radio" name="contact_method" value={v} checked={form.contactMethod === v} onChange={() => upd('contactMethod', v)} className="w-3.5 h-3.5 accent-[#0C447C]" />
                    {lbl}
                  </label>
                ))}
              </div>
            </div>
            <div>
              <label className={labelCls}>{t.bestTime}</label>
              <div className="flex flex-wrap gap-x-4 gap-y-2 mt-1">
                {[['morning', t.morning], ['afternoon', t.afternoon], ['evening', t.evening], ['anytime', t.anytime]].map(([v, lbl]) => (
                  <label key={v} className="flex items-center gap-1.5 text-xs text-gray-800 cursor-pointer">
                    <input type="radio" name="best_time" value={v} checked={form.bestTime === v} onChange={() => upd('bestTime', v)} className="w-3.5 h-3.5 accent-[#0C447C]" />
                    {lbl}
                  </label>
                ))}
              </div>
            </div>
          </SectionBody>
        </div>

        {/* ── Section 6: Consent ── */}
        <div>
          <SectionHeader text={t.s6} />
          <SectionBody>
            <p className="text-[12px] text-gray-600 leading-relaxed">{t.consent}</p>
            <div className="grid grid-cols-2 gap-2.5">
              <Field label={t.signature}><input className={inputCls} type="text" placeholder="Type full name" value={form.signature} onChange={e => upd('signature', e.target.value)} /></Field>
              <Field label={t.date}><input className={inputCls} type="date" value={form.consentDate} onChange={e => upd('consentDate', e.target.value)} /></Field>
            </div>
          </SectionBody>
        </div>

        {/* ── Liaison Section ── */}
        <div className="bg-gray-50 rounded-xl border border-gray-300 overflow-hidden">
          <div className="bg-[#185FA5] text-[#E6F1FB] text-[11px] font-medium px-3 py-1.5">{t.forLiaison}</div>
          <div className="p-3 space-y-3">
            <div className="grid grid-cols-3 gap-2.5">
              <Field label={t.liaisonName}><input className={inputCls} type="text" value={form.liaisonName} onChange={e => upd('liaisonName', e.target.value)} /></Field>
              <Field label={t.liaisonOrg}><input className={inputCls} type="text" value={form.liaisonOrg} onChange={e => upd('liaisonOrg', e.target.value)} /></Field>
              <Field label={t.regDate}><input className={inputCls} type="date" value={form.regDate} onChange={e => upd('regDate', e.target.value)} /></Field>
            </div>
            <div className="grid grid-cols-2 gap-2.5">
              <Field label={t.neighborhood}><input className={inputCls} type="text" value={form.neighborhood} onChange={e => upd('neighborhood', e.target.value)} /></Field>
              <Field label={t.formId}><input className={inputCls} type="text" value={form.formId} onChange={e => upd('formId', e.target.value)} /></Field>
            </div>
          </div>
        </div>

        {/* ── Required Note + Submit ── */}
        <p className="text-[11px] text-red-600">{t.req}</p>

        {!isSuccess ? (
          <button onClick={handleSubmit} disabled={isSubmitting}
            className="w-full py-3 bg-[#0C447C] hover:bg-[#185FA5] text-[#E6F1FB] text-sm font-medium rounded-xl transition-colors disabled:opacity-60">
            {isSubmitting ? '...' : t.submitBtn}
          </button>
        ) : (
          <div className="p-5 bg-[#E6F1FB] border border-[#378ADD] rounded-xl text-center">
            <CheckCircle className="w-8 h-8 text-[#0C447C] mx-auto mb-2" />
            <h3 className="text-[#0C447C] text-[15px] font-medium mb-1">{t.successTitle}</h3>
            <p className="text-[13px] text-[#185FA5]">{t.successBody}</p>
          </div>
        )}

      </div>
    </div>
  );
}
