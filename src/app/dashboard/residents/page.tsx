'use client';

import { useState, useEffect } from 'react';
import { supabase } from '@/lib/supabase';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from '@/components/ui/dialog';
import { Plus, User, Phone, MapPin, Languages, Activity, Trash2, Edit2, PhoneCall, CheckCircle, AlertTriangle, Clock } from 'lucide-react';
import { cn } from '@/lib/utils';

// Type definition
type Resident = {
    id: string;
    name: string;
    phone_number: string;
    age?: number;
    address?: string;
    zip_code?: string;
    health_conditions?: string;
    language?: string;
    status: 'safe' | 'distress' | 'unresponsive' | 'pending';
};

export default function ResidentsPage() {
    const [residents, setResidents] = useState<Resident[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [isOpen, setIsOpen] = useState(false);

    // Form State
    const [editingId, setEditingId] = useState<string | null>(null);
    const [formData, setFormData] = useState({
        name: '',
        phone: '',
        age: '',
        address: '',
        zip_code: '',
        health_conditions: '',
        language: 'en'
    });
    const [isSubmitting, setIsSubmitting] = useState(false);

    // Initial Fetch
    useEffect(() => {
        fetchResidents();
    }, []);

    const fetchResidents = async () => {
        setIsLoading(true);
        const { data, error } = await supabase
            .from('residents')
            .select('*')
            .order('created_at', { ascending: false });

        if (data) setResidents(data as Resident[]);
        setIsLoading(false);
    };

    // Open Modal for Editing
    const handleEditClick = (resident: Resident) => {
        setEditingId(resident.id);
        setFormData({
            name: resident.name,
            phone: resident.phone_number,
            age: resident.age ? resident.age.toString() : '',
            address: resident.address || '',
            zip_code: resident.zip_code || '',
            health_conditions: resident.health_conditions || '',
            language: resident.language || 'en'
        });
        setIsOpen(true);
    };

    // Open Modal for Creating
    const handleCreateClick = () => {
        setEditingId(null);
        setFormData({ name: '', phone: '', age: '', address: '', zip_code: '', health_conditions: '', language: 'en' });
        setIsOpen(true);
    };

    const handleSaveResident = async () => {
        if (!formData.name || !formData.phone) return;
        setIsSubmitting(true);

        const { data: { user } } = await supabase.auth.getUser();

        const payload = {
            name: formData.name,
            phone_number: formData.phone,
            age: formData.age ? parseInt(formData.age) : null,
            address: formData.address,
            zip_code: formData.zip_code,
            health_conditions: formData.health_conditions,
            language: formData.language
        };

        let result;
        if (editingId) {
            // Update Existing
            result = await supabase.from('residents').update(payload).eq('id', editingId);
        } else {
            // Create New
            result = await supabase.from('residents').insert({
                ...payload,
                liaison_id: user?.id || '00000000-0000-0000-0000-000000000000',
                status: 'pending'
            });
        }

        if (!result.error) {
            setIsOpen(false);
            fetchResidents(); // Refresh list
        } else {
            alert("Error saving resident: " + result.error.message);
        }
        setIsSubmitting(false);
    };

    const handleDelete = async (id: string, name: string) => {
        if (!confirm(`Are you sure you want to remove ${name}? This cannot be undone.`)) return;

        // 1. Delete associated call logs first (Manual Cascade)
        const { error: logsError } = await supabase.from('call_logs').delete().eq('resident_id', id);

        if (logsError) {
            console.error("Error deleting logs:", logsError);
            // We continue even if logs error, in case there were no logs or constraint handles it, 
            // but usually this clears the way.
        }

        // 2. Delete the resident
        const { error } = await supabase.from('residents').delete().eq('id', id);

        if (!error) {
            fetchResidents();
        } else {
            alert("Error deleting resident: " + error.message);
        }
    };

    const handleSingleCall = async (resident: Resident) => {
        const confirmed = confirm(`Start emergency check-in for ${resident.name}?`);
        if (!confirmed) return;

        try {
            const res = await fetch('/api/vapi/trigger', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ targetResidentId: resident.id })
            });
            const data = await res.json();

            if (res.ok) {
                alert("Call Initiated!");
                fetchResidents();
            } else {
                alert("Call Failed: " + (data.error || "Unknown"));
            }
        } catch (e: any) {
            alert("Network Error: " + e.message);
        }
    };

    const handleUpdateStatus = async (id: string, newStatus: Resident['status']) => {
        const { error } = await supabase.from('residents').update({ status: newStatus }).eq('id', id);
        if (!error) {
            // If manually marking as distress, send Telegram alert
            if (newStatus === 'distress') {
                const resident = residents.find(r => r.id === id);
                if (resident) {
                    try {
                        await fetch('/api/telegram/send-alert', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                residentId: id,
                                residentName: resident.name,
                                source: 'manual'
                            })
                        });
                    } catch (e) {
                        console.error('Failed to send Telegram alert:', e);
                    }
                }
            }
            fetchResidents();
        } else {
            alert("Error updating status: " + error.message);
        }
    };

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-white">Your Pod</h1>
                    <p className="text-slate-400">Manage the vulnerable residents you are responsible for.</p>
                </div>

                <Dialog open={isOpen} onOpenChange={setIsOpen}>
                    <DialogTrigger asChild>
                        <Button className="gap-2 bg-blue-600 hover:bg-blue-700 text-white" onClick={handleCreateClick}>
                            <Plus className="w-4 h-4" /> Add Resident
                        </Button>
                    </DialogTrigger>
                    <DialogContent className="bg-slate-900 border-slate-800 text-slate-100 max-w-lg">
                        <DialogHeader>
                            <DialogTitle>{editingId ? 'Edit Profile' : 'Add New Resident'}</DialogTitle>
                            <DialogDescription className="text-slate-400">
                                {editingId ? 'Update details used for emergency response.' : 'Create a comprehensive profile to help emergency responders.'}
                            </DialogDescription>
                        </DialogHeader>

                        <div className="grid gap-4 py-4">
                            {/* Basic Info */}
                            <div className="grid grid-cols-2 gap-4">
                                <div className="grid gap-2">
                                    <Label htmlFor="name">Full Name *</Label>
                                    <Input id="name" placeholder="Maria Rodriguez" className="bg-slate-950 border-slate-800"
                                        value={formData.name} onChange={(e) => setFormData({ ...formData, name: e.target.value })} />
                                </div>
                                <div className="grid gap-2">
                                    <Label htmlFor="phone">Phone Number *</Label>
                                    <Input id="phone" placeholder="+19175550123" className="bg-slate-950 border-slate-800"
                                        value={formData.phone} onChange={(e) => setFormData({ ...formData, phone: e.target.value })} />
                                </div>
                            </div>

                            {/* Demographics */}
                            <div className="grid grid-cols-2 gap-4">
                                <div className="grid gap-2">
                                    <Label htmlFor="age">Age</Label>
                                    <Input id="age" type="number" placeholder="75" className="bg-slate-950 border-slate-800"
                                        value={formData.age} onChange={(e) => setFormData({ ...formData, age: e.target.value })} />
                                </div>
                                <div className="grid gap-2">
                                    <Label htmlFor="language">Preferred Language</Label>
                                    <select
                                        id="language"
                                        className="flex h-10 w-full items-center justify-between rounded-md border border-slate-800 bg-slate-950 px-3 py-2 text-sm placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-400 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                                        value={formData.language}
                                        onChange={(e) => setFormData({ ...formData, language: e.target.value })}
                                    >
                                        <option value="en">English</option>
                                        <option value="es">Spanish</option>
                                        <option value="zh">Chinese</option>
                                        <option value="ru">Russian</option>
                                        <option value="ht">Haitian Creole</option>
                                    </select>
                                </div>
                            </div>

                            {/* Location */}
                            <div className="grid grid-cols-3 gap-4">
                                <div className="grid gap-2 col-span-2">
                                    <Label htmlFor="address">Street Address</Label>
                                    <Input id="address" placeholder="123 Basement Apt" className="bg-slate-950 border-slate-800"
                                        value={formData.address} onChange={(e) => setFormData({ ...formData, address: e.target.value })} />
                                </div>
                                <div className="grid gap-2">
                                    <Label htmlFor="zip">Zip Code</Label>
                                    <Input id="zip" placeholder="11369" className="bg-slate-950 border-slate-800"
                                        value={formData.zip_code} onChange={(e) => setFormData({ ...formData, zip_code: e.target.value })} />
                                </div>
                            </div>

                            {/* Health */}
                            <div className="grid gap-2">
                                <Label htmlFor="health">Vulnerabilities / Health Conditions</Label>
                                <Textarea
                                    id="health"
                                    placeholder="e.g. Wheelchair user, Insulin dependent, Oxygen tank..."
                                    value={formData.health_conditions}
                                    onChange={(e) => setFormData({ ...formData, health_conditions: e.target.value })}
                                />
                            </div>
                        </div>

                        <DialogFooter>
                            <Button onClick={handleSaveResident} disabled={isSubmitting} className="w-full bg-blue-600 hover:bg-blue-700">
                                {isSubmitting ? 'Saving Profile...' : 'Save Profile'}
                            </Button>
                        </DialogFooter>
                    </DialogContent>
                </Dialog>
            </div>

            {/* Residents Grid */}
            {isLoading ? (
                <div className="text-slate-500">Loading residents...</div>
            ) : residents.length === 0 ? (
                <div className="p-12 border border-dashed border-slate-700 rounded-xl text-center text-slate-500">
                    No residents found. Add someone to get started.
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {residents.map((resident) => (
                        <div key={resident.id} className="glass-panel p-6 rounded-xl flex flex-col justify-between group hover:border-blue-500/30 transition-colors relative overflow-hidden">

                            {/* Top Row: Avatar & Status */}
                            <div className="flex justify-between items-start mb-4">
                                <div className="flex items-center gap-4">
                                    <div className="w-12 h-12 rounded-full bg-slate-800 flex items-center justify-center text-slate-400 group-hover:bg-blue-900/50 group-hover:text-blue-400 transition-colors">
                                        <User className="w-6 h-6" />
                                    </div>
                                    <div>
                                        <h3 className="font-semibold text-white text-lg">{resident.name}</h3>
                                        {resident.age && <span className="text-xs text-slate-500">{resident.age} years old</span>}
                                    </div>
                                </div>
                                <div className={cn(
                                    "px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wide",
                                    resident.status === 'safe' && "bg-green-500/10 text-green-500",
                                    resident.status === 'distress' && "bg-red-500/10 text-red-500",
                                    resident.status === 'pending' && "bg-slate-700 text-slate-300",
                                    resident.status === 'unresponsive' && "bg-yellow-500/10 text-yellow-500",
                                )}>
                                    {resident.status}
                                </div>
                            </div>

                            {/* Details Grid */}
                            <div className="space-y-3 text-sm text-slate-400 mb-6 flex-grow">
                                <div className="flex items-center gap-2">
                                    <Phone className="w-4 h-4 text-slate-600" />
                                    {resident.phone_number}
                                </div>
                                {(resident.address || resident.zip_code) && (
                                    <div className="flex items-center gap-2">
                                        <MapPin className="w-4 h-4 text-slate-600" />
                                        <span className="truncate max-w-[200px]">{resident.address} {resident.zip_code && `(${resident.zip_code})`}</span>
                                    </div>
                                )}
                                {resident.language && resident.language !== 'en' && (
                                    <div className="flex items-center gap-2">
                                        <Languages className="w-4 h-4 text-slate-600" />
                                        <span className="uppercase">{resident.language}</span>
                                    </div>
                                )}
                                {resident.health_conditions && (
                                    <div className="flex items-start gap-2 text-xs text-yellow-500/90 bg-yellow-500/5 p-2 rounded mt-2">
                                        <Activity className="w-4 h-4 mt-0.5 shrink-0" />
                                        <span>{resident.health_conditions}</span>
                                    </div>
                                )}
                            </div>

                            {/* Action Bar */}
                            <div className="flex items-center gap-2 pt-4 border-t border-slate-800">
                                <Button size="sm" variant="outline" className="flex-1 gap-2 border-slate-700 hover:bg-slate-800 hover:text-white"
                                    onClick={() => handleSingleCall(resident)}>
                                    <PhoneCall className="w-3 h-3" /> Call
                                </Button>

                                <div className="w-px h-6 bg-slate-700 mx-1"></div>

                                {/* Status Overrides */}
                                <Button size="icon" variant="ghost" className="h-9 w-9 text-slate-400 hover:text-green-400 hover:bg-green-900/10"
                                    title="Mark as Safe"
                                    onClick={() => handleUpdateStatus(resident.id, 'safe')}>
                                    <CheckCircle className="w-4 h-4" />
                                </Button>
                                <Button size="icon" variant="ghost" className="h-9 w-9 text-slate-400 hover:text-yellow-400 hover:bg-yellow-900/10"
                                    title="Mark as Pending"
                                    onClick={() => handleUpdateStatus(resident.id, 'pending')}>
                                    <Clock className="w-4 h-4" />
                                </Button>
                                <Button size="icon" variant="ghost" className="h-9 w-9 text-slate-400 hover:text-red-400 hover:bg-red-900/10"
                                    title="Mark as Distress"
                                    onClick={() => handleUpdateStatus(resident.id, 'distress')}>
                                    <AlertTriangle className="w-4 h-4" />
                                </Button>

                                <div className="w-px h-6 bg-slate-700 mx-1"></div>

                                <Button size="icon" variant="ghost" className="h-9 w-9 text-slate-400 hover:text-white hover:bg-slate-800"
                                    onClick={() => handleEditClick(resident)}>
                                    <Edit2 className="w-4 h-4" />
                                </Button>
                                <Button size="icon" variant="ghost" className="h-9 w-9 text-slate-400 hover:text-red-400 hover:bg-red-900/10"
                                    onClick={() => handleDelete(resident.id, resident.name)}>
                                    <Trash2 className="w-4 h-4" />
                                </Button>
                            </div>

                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
