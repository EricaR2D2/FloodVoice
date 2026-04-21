'use client';

import { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { supabase } from '@/lib/supabase';

type Lang = 'en' | 'es' | 'bn' | 'zh';

type Strings = {
    title: string; sub: string; privacy: string; req: string;
    s1: string; s2: string; s3: string; s4: string; s5: string; s6: string;
    name: string; dob: string; phone: string; altPhone: string; email: string;
    address: string; borough: string; floor: string; basement: string; household: string;
    yes: string; no: string;
    kinName: string; kinPhone: string; kinRel: string; kinAddr: string;
    disability: string; disabilityDesc: string; medical: string;
    language: string; langs: string[];
    contactPref: string; call: string; sms: string; both: string;
    bestTime: string; morning: string; afternoon: string; evening: string; anytime: string;
    consent: string; signature: string; date: string;
    forLiaison: string; liaisonName: string; liaisonOrg: string; regDate: string;
    neighborhood: string; formId: string;
    submitBtn: string; successTitle: string; successBody: string;
    validationMsg: string;
};

const T: Record<Lang, Strings> = {
    en: {
        title: 'FloodVoice AI — Resident Registration', sub: 'Flood Emergency Early Warning System',
        privacy: 'PRIVACY NOTICE: Information collected is used solely for flood emergency response. Data is NOT shared with immigration authorities or any government agency. This program serves all residents regardless of immigration status.',
        req: '* Required field',
        s1: 'Section 1 — Personal information', s2: 'Section 2 — Household & housing',
        s3: 'Section 3 — Emergency contact', s4: 'Section 4 — Health & access needs',
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
        successTitle: 'Registration submitted', successBody: 'This resident has been enrolled in FloodVoice AI flood emergency alerts.',
        validationMsg: 'Please complete all required fields (*).',
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
        successTitle: 'Registro enviado', successBody: 'Este residente ha sido inscrito en las alertas de emergencia de FloodVoice AI.',
        validationMsg: 'Por favor complete todos los campos obligatorios (*).',
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
        successTitle: 'নিবন্ধন সম্পন্ন', successBody: 'এই বাসিন্দাকে FloodVoice AI বন্যা জরুরি সতর্কতায় নথিভুক্ত করা হয়েছে।',
        validationMsg: 'অনুগ্রহ করে সমস্ত প্রয়োজনীয় ক্ষেত্র পূরণ করুন।',
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
        successTitle: '登记已提交', successBody: '该居民已成功注册 FloodVoice AI 洪水紧急警报。',
        validationMsg: '请填写所有必填项 (*)。',
    },
};

const TAB_LABEL: Record<Lang, string> = { en: 'English', es: 'Español', bn: 'বাংলা', zh: '中文' };
const LANG_CODES: Lang[] = ['en', 'es', 'bn', 'zh'];

// Internal lang code for the seven preferred-language checkboxes — maps to Supabase `residents.language` column.
const PREF_LANG_CODES = ['en', 'es', 'bn', 'zh', 'ko', 'ht', 'other'] as const;

const emptyForm = () => ({
    name: '', dob: '', phone: '', altPhone: '', email: '',
    address: '', borough: '', floor: '', basement: '', household: '',
    kinName: '', kinPhone: '', kinRel: '', kinAddr: '',
    disability: '', disabilityDesc: '', medical: '',
    prefLangs: [] as number[],
    contactPref: '', bestTime: '',
    signature: '', signDate: '',
    liaisonName: '', liaisonOrg: '', regDate: new Date().toISOString().split('T')[0],
    neighborhood: '', formId: '',
});

type FormState = ReturnType<typeof emptyForm>;

type Props = {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    onSaved?: () => void;
};

export function ResidentIntakeDialog({ open, onOpenChange, onSaved }: Props) {
    const [lang, setLang] = useState<Lang>('en');
    const [form, setForm] = useState<FormState>(emptyForm);
    const [submitting, setSubmitting] = useState(false);
    const [success, setSuccess] = useState(false);
    const t = T[lang];

    useEffect(() => {
        if (open) {
            setForm(emptyForm());
            setSuccess(false);
            setLang('en');
        }
    }, [open]);

    const update = <K extends keyof FormState>(k: K, v: FormState[K]) =>
        setForm(prev => ({ ...prev, [k]: v }));

    const togglePrefLang = (idx: number) => {
        setForm(prev => ({
            ...prev,
            prefLangs: prev.prefLangs.includes(idx)
                ? prev.prefLangs.filter(i => i !== idx)
                : [...prev.prefLangs, idx],
        }));
    };

    const ageFromDob = (dob: string): number | null => {
        if (!dob) return null;
        const d = new Date(dob);
        if (isNaN(d.getTime())) return null;
        const diff = Date.now() - d.getTime();
        const age = Math.floor(diff / (1000 * 60 * 60 * 24 * 365.25));
        return age >= 0 && age < 130 ? age : null;
    };

    const handleSubmit = async () => {
        if (!form.name.trim() || !form.phone.trim() || !form.address.trim() || !form.signature.trim()) {
            alert(t.validationMsg);
            return;
        }
        setSubmitting(true);

        const { data: { user } } = await supabase.auth.getUser();

        // Compose the fields that don't have dedicated columns into health_conditions
        // so nothing is silently dropped.
        const extras: string[] = [];
        if (form.medical.trim()) extras.push(`Medical: ${form.medical.trim()}`);
        if (form.disability === 'yes') {
            extras.push(`Disability affecting evacuation${form.disabilityDesc ? `: ${form.disabilityDesc}` : ''}`);
        }
        if (form.kinName || form.kinPhone) {
            extras.push(`Emergency contact: ${form.kinName}${form.kinPhone ? ` (${form.kinPhone})` : ''}${form.kinRel ? ` — ${form.kinRel}` : ''}`);
        }
        if (form.basement === 'yes') extras.push('Basement apartment');
        if (form.household) extras.push(`Household size: ${form.household}`);
        if (form.contactPref) extras.push(`Contact: ${form.contactPref}`);
        if (form.bestTime) extras.push(`Best time: ${form.bestTime}`);
        if (form.altPhone) extras.push(`Alt phone: ${form.altPhone}`);
        if (form.email) extras.push(`Email: ${form.email}`);
        if (form.floor) extras.push(`Floor/apt: ${form.floor}`);

        const firstPrefLang = form.prefLangs[0] !== undefined ? PREF_LANG_CODES[form.prefLangs[0]] : lang;

        // Pull any 5-digit ZIP out of the borough/zip field for our zip_code column
        const zipMatch = form.borough.match(/\b\d{5}\b/);
        const zip = zipMatch ? zipMatch[0] : form.borough.trim();

        const fullAddress = [form.address, form.floor].filter(Boolean).join(', ');

        const payload = {
            name: form.name.trim(),
            phone_number: form.phone.trim(),
            age: ageFromDob(form.dob),
            address: fullAddress || form.address,
            zip_code: zip,
            health_conditions: extras.join(' | ') || null,
            language: firstPrefLang,
            liaison_id: user?.id || '00000000-0000-0000-0000-000000000000',
            status: 'pending' as const,
        };

        const { error } = await supabase.from('residents').insert(payload);
        setSubmitting(false);

        if (error) {
            alert('Error saving resident: ' + error.message);
            return;
        }

        setSuccess(true);
        onSaved?.();
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent
                className="max-w-xl p-0 overflow-hidden bg-[#f4f6f9] text-[#1a1a1a] border-0 max-h-[92vh]"
            >
                <DialogTitle className="sr-only">{t.title}</DialogTitle>
                <DialogDescription className="sr-only">{t.sub}</DialogDescription>
                <div className="max-h-[92vh] overflow-y-auto">
                    {/* Header */}
                    <div className="bg-[#0C447C] px-4 py-3">
                        <h1 className="text-[#E6F1FB] text-[15px] font-medium leading-tight">{t.title}</h1>
                        <p className="text-[#85B7EB] text-[11px] mt-0.5">{t.sub}</p>
                    </div>
                    <div className="h-1 bg-[#EF9F27]" />

                    {/* Language tabs */}
                    <div className="flex border-b border-[#ccc] bg-[#f4f6f9]">
                        {LANG_CODES.map(code => (
                            <button
                                key={code}
                                type="button"
                                onClick={() => setLang(code)}
                                className={`flex-1 py-2.5 px-1 text-xs text-center transition-all ${
                                    lang === code
                                        ? 'text-[#0C447C] border-b-2 border-[#0C447C] font-medium bg-white'
                                        : 'text-[#666] border-b-2 border-transparent'
                                }`}
                            >
                                {TAB_LABEL[code]}
                            </button>
                        ))}
                    </div>

                    {/* Privacy notice */}
                    <div className="mx-3 mt-3 p-2.5 bg-[#FFF8EC] border-l-[3px] border-[#EF9F27] rounded-r text-[11px] text-[#5C3000] leading-relaxed">
                        {t.privacy}
                    </div>

                    {/* Form body */}
                    {success ? (
                        <div className="px-3 pb-5">
                            <div className="mt-4 p-4 bg-[#E6F1FB] border border-[#378ADD] rounded-xl text-center">
                                <h3 className="text-[#0C447C] text-[15px] font-medium mb-1.5">{t.successTitle}</h3>
                                <p className="text-[13px] text-[#185FA5]">{t.successBody}</p>
                                <button
                                    type="button"
                                    onClick={() => onOpenChange(false)}
                                    className="mt-4 px-4 py-2 bg-[#0C447C] text-[#E6F1FB] text-[13px] rounded-lg"
                                >
                                    ✓
                                </button>
                            </div>
                        </div>
                    ) : (
                        <div className="px-3 pb-3">
                            {/* Section 1 — Personal */}
                            <Section title={t.s1}>
                                <Field label={t.name}>
                                    <input type="text" autoComplete="name" className={fieldInput}
                                        value={form.name} onChange={e => update('name', e.target.value)} />
                                </Field>
                                <Row2>
                                    <Field label={t.dob}>
                                        <input type="date" className={fieldInput}
                                            value={form.dob} onChange={e => update('dob', e.target.value)} />
                                    </Field>
                                    <Field label={t.phone}>
                                        <input type="tel" autoComplete="tel" className={fieldInput}
                                            value={form.phone} onChange={e => update('phone', e.target.value)} />
                                    </Field>
                                </Row2>
                                <Row2>
                                    <Field label={t.altPhone}>
                                        <input type="tel" className={fieldInput}
                                            value={form.altPhone} onChange={e => update('altPhone', e.target.value)} />
                                    </Field>
                                    <Field label={t.email}>
                                        <input type="email" autoComplete="email" className={fieldInput}
                                            value={form.email} onChange={e => update('email', e.target.value)} />
                                    </Field>
                                </Row2>
                            </Section>

                            {/* Section 2 — Household & housing */}
                            <Section title={t.s2}>
                                <Field label={t.address}>
                                    <input type="text" autoComplete="street-address" className={fieldInput}
                                        value={form.address} onChange={e => update('address', e.target.value)} />
                                </Field>
                                <Row2>
                                    <Field label={t.borough}>
                                        <input type="text" className={fieldInput}
                                            value={form.borough} onChange={e => update('borough', e.target.value)} />
                                    </Field>
                                    <Field label={t.floor}>
                                        <input type="text" className={fieldInput}
                                            value={form.floor} onChange={e => update('floor', e.target.value)} />
                                    </Field>
                                </Row2>
                                <YesNoRow
                                    label={t.basement} yesLabel={t.yes} noLabel={t.no}
                                    name="basement" value={form.basement}
                                    onChange={v => update('basement', v)}
                                />
                                <Field label={t.household}>
                                    <input type="number" min={1} max={20} className={`${fieldInput} max-w-[100px]`}
                                        value={form.household} onChange={e => update('household', e.target.value)} />
                                </Field>
                            </Section>

                            {/* Section 3 — Emergency contact */}
                            <Section title={t.s3}>
                                <Row2>
                                    <Field label={t.kinName}>
                                        <input type="text" className={fieldInput}
                                            value={form.kinName} onChange={e => update('kinName', e.target.value)} />
                                    </Field>
                                    <Field label={t.kinPhone}>
                                        <input type="tel" className={fieldInput}
                                            value={form.kinPhone} onChange={e => update('kinPhone', e.target.value)} />
                                    </Field>
                                </Row2>
                                <Row2>
                                    <Field label={t.kinRel}>
                                        <input type="text" className={fieldInput}
                                            value={form.kinRel} onChange={e => update('kinRel', e.target.value)} />
                                    </Field>
                                    <Field label={t.kinAddr}>
                                        <input type="text" className={fieldInput}
                                            value={form.kinAddr} onChange={e => update('kinAddr', e.target.value)} />
                                    </Field>
                                </Row2>
                            </Section>

                            {/* Section 4 — Health & access */}
                            <Section title={t.s4}>
                                <YesNoRow
                                    label={t.disability} yesLabel={t.yes} noLabel={t.no}
                                    name="disability" value={form.disability}
                                    onChange={v => update('disability', v)}
                                />
                                {form.disability === 'yes' && (
                                    <Field label={t.disabilityDesc}>
                                        <input type="text" className={fieldInput}
                                            value={form.disabilityDesc} onChange={e => update('disabilityDesc', e.target.value)} />
                                    </Field>
                                )}
                                <Field label={t.medical}>
                                    <textarea className={`${fieldInput} h-[52px] resize-none`}
                                        value={form.medical} onChange={e => update('medical', e.target.value)} />
                                </Field>
                            </Section>

                            {/* Section 5 — Contact preferences */}
                            <Section title={t.s5}>
                                <Field label={t.language}>
                                    <div className="flex flex-wrap gap-x-4 gap-y-2 mt-1">
                                        {t.langs.map((l, i) => (
                                            <label key={i} className={checkItem}>
                                                <input
                                                    type="checkbox"
                                                    className={checkbox}
                                                    checked={form.prefLangs.includes(i)}
                                                    onChange={() => togglePrefLang(i)}
                                                />
                                                <span>{l}</span>
                                            </label>
                                        ))}
                                    </div>
                                </Field>
                                <Field label={t.contactPref}>
                                    <div className="flex flex-wrap gap-x-4 gap-y-2 mt-1">
                                        {[['call', t.call], ['sms', t.sms], ['both', t.both]].map(([v, label]) => (
                                            <label key={v} className={checkItem}>
                                                <input
                                                    type="radio" name="contact_pref" value={v}
                                                    className={checkbox}
                                                    checked={form.contactPref === v}
                                                    onChange={e => update('contactPref', e.target.value)}
                                                />
                                                <span>{label}</span>
                                            </label>
                                        ))}
                                    </div>
                                </Field>
                                <Field label={t.bestTime}>
                                    <div className="flex flex-wrap gap-x-4 gap-y-2 mt-1">
                                        {[['morning', t.morning], ['afternoon', t.afternoon], ['evening', t.evening], ['anytime', t.anytime]].map(([v, label]) => (
                                            <label key={v} className={checkItem}>
                                                <input
                                                    type="radio" name="best_time" value={v}
                                                    className={checkbox}
                                                    checked={form.bestTime === v}
                                                    onChange={e => update('bestTime', e.target.value)}
                                                />
                                                <span>{label}</span>
                                            </label>
                                        ))}
                                    </div>
                                </Field>
                            </Section>

                            {/* Section 6 — Consent */}
                            <Section title={t.s6}>
                                <p className="text-[12px] text-[#555] leading-relaxed mb-3">{t.consent}</p>
                                <Row2>
                                    <Field label={t.signature}>
                                        <input type="text" className={fieldInput} placeholder="Type full name"
                                            value={form.signature} onChange={e => update('signature', e.target.value)} />
                                    </Field>
                                    <Field label={t.date}>
                                        <input type="date" className={fieldInput}
                                            value={form.signDate} onChange={e => update('signDate', e.target.value)} />
                                    </Field>
                                </Row2>
                            </Section>

                            {/* Liaison section */}
                            <div className="mt-3.5 bg-[#F4F6F9] rounded-xl border border-[#ccc] overflow-hidden">
                                <div className="bg-[#185FA5] text-[#E6F1FB] text-[11px] font-medium px-2.5 py-1.5">
                                    {t.forLiaison}
                                </div>
                                <div className="p-3 space-y-2.5">
                                    <div className="grid grid-cols-3 gap-2.5">
                                        <Field label={t.liaisonName}>
                                            <input type="text" className={fieldInput}
                                                value={form.liaisonName} onChange={e => update('liaisonName', e.target.value)} />
                                        </Field>
                                        <Field label={t.liaisonOrg}>
                                            <input type="text" className={fieldInput}
                                                value={form.liaisonOrg} onChange={e => update('liaisonOrg', e.target.value)} />
                                        </Field>
                                        <Field label={t.regDate}>
                                            <input type="date" className={fieldInput}
                                                value={form.regDate} onChange={e => update('regDate', e.target.value)} />
                                        </Field>
                                    </div>
                                    <Row2>
                                        <Field label={t.neighborhood}>
                                            <input type="text" className={fieldInput}
                                                value={form.neighborhood} onChange={e => update('neighborhood', e.target.value)} />
                                        </Field>
                                        <Field label={t.formId}>
                                            <input type="text" className={fieldInput} placeholder="FV-"
                                                value={form.formId} onChange={e => update('formId', e.target.value)} />
                                        </Field>
                                    </Row2>
                                </div>
                            </div>

                            <p className="text-[11px] text-[#CC0000] mt-2">{t.req}</p>
                            <button
                                type="button"
                                onClick={handleSubmit}
                                disabled={submitting}
                                className="block w-full mt-4 py-3 bg-[#0C447C] hover:bg-[#185FA5] text-[#E6F1FB] text-[14px] font-medium rounded-xl disabled:opacity-60"
                            >
                                {submitting ? '...' : t.submitBtn}
                            </button>
                        </div>
                    )}
                </div>
            </DialogContent>
        </Dialog>
    );
}

// ─── Small subcomponents ───

const fieldInput = 'w-full text-[13px] px-2 py-1.5 border border-[#ccc] rounded-md bg-white text-[#1a1a1a] outline-none focus:border-[#378ADD] focus:ring-2 focus:ring-[#E6F1FB]';
const checkItem = 'flex items-center gap-1.5 text-[12px] text-[#1a1a1a] cursor-pointer';
const checkbox = 'w-[14px] h-[14px] cursor-pointer accent-[#0C447C]';

function Section({ title, children }: { title: string; children: React.ReactNode }) {
    return (
        <div className="mt-3.5">
            <div className="bg-[#0C447C] text-[#E6F1FB] text-[11px] font-medium px-2.5 py-1.5 rounded-t-lg tracking-[0.02em]">
                {title}
            </div>
            <div className="border border-t-0 border-[#ccc] rounded-b-lg p-3 bg-white space-y-2.5">
                {children}
            </div>
        </div>
    );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
    return (
        <div>
            <label className="block text-[11px] text-[#0C447C] font-medium mb-1">{label}</label>
            {children}
        </div>
    );
}

function Row2({ children }: { children: React.ReactNode }) {
    return <div className="grid grid-cols-2 gap-2.5">{children}</div>;
}

function YesNoRow({
    label, yesLabel, noLabel, name, value, onChange,
}: {
    label: string; yesLabel: string; noLabel: string; name: string;
    value: string; onChange: (v: string) => void;
}) {
    return (
        <div className="flex items-center justify-between py-1.5 border-b border-[#eee]">
            <label className="text-[12px] text-[#0C447C] font-medium">{label}</label>
            <div className="flex gap-4">
                <label className={checkItem}>
                    <input type="radio" name={name} value="yes" className={checkbox}
                        checked={value === 'yes'} onChange={() => onChange('yes')} />
                    <span>{yesLabel}</span>
                </label>
                <label className={checkItem}>
                    <input type="radio" name={name} value="no" className={checkbox}
                        checked={value === 'no'} onChange={() => onChange('no')} />
                    <span>{noLabel}</span>
                </label>
            </div>
        </div>
    );
}
