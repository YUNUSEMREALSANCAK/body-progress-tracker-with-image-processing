'use client';

import { useState, ChangeEvent } from 'react';
import { API_URL } from '../utils/config';

export default function AnalysisView() {
    const [image, setImage] = useState<File | null>(null);
    const [preview, setPreview] = useState<string | null>(null);
    const [analyzedImage, setAnalyzedImage] = useState<string | null>(null);
    const [data, setData] = useState<{ ipd: string } | null>(null);
    const [loading, setLoading] = useState(false);

    const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            setImage(file);
            setPreview(URL.createObjectURL(file));
            setAnalyzedImage(null);
            setData(null);
        }
    };

    const handleAnalyze = async () => {
        if (!image) return;

        setLoading(true);
        const formData = new FormData();
        formData.append('image', image);

        try {
            const response = await fetch(`${API_URL}/analyze`, {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                alert('Resim analiz edilirken bir hata oluştu');
                throw new Error('Analysis failed');
            }

            // Get headers
            const ipd = response.headers.get('X-Pupil-Distance-Px');
            if (ipd) {
                setData({ ipd });
            }

            const blob = await response.blob();
            setAnalyzedImage(URL.createObjectURL(blob));
        } catch (error) {
            console.error("Analysis Error:", error);
            alert(`Error: ${error instanceof Error ? error.message : String(error)}`);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex flex-col items-center gap-8 w-full max-w-4xl mx-auto p-4 border rounded-xl bg-gray-50 mt-12 shadow-sm">
            <h2 className="text-2xl font-bold text-gray-800">Veri Analizi ve İşaretleme</h2>
            <p className="text-sm text-gray-600 text-center -mt-4">
                Tek bir fotoğraf yükleyerek göz bebekleri arasındaki mesafeyi ve vücut hatlarını analiz edin.
            </p>

            <div className="w-full max-w-md flex flex-col gap-4">
                <label className="font-bold text-lg text-gray-700">Analiz Edilecek Fotoğraf</label>
                <input
                    type="file"
                    accept="image/*"
                    onChange={handleFileChange}
                    className="block w-full text-sm text-gray-500
            file:mr-4 file:py-2 file:px-4
            file:rounded-full file:border-0
            file:text-sm file:font-semibold
            file:bg-violet-50 file:text-violet-700
            hover:file:bg-violet-100"
                />
                {preview && !analyzedImage && (
                    <img src={preview} alt="Preview" className="w-full h-auto max-h-[400px] object-contain bg-white rounded-lg border" />
                )}
            </div>

            <button
                onClick={handleAnalyze}
                disabled={!image || loading}
                className="px-8 py-3 bg-indigo-600 text-white font-bold rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
                {loading ? 'Analiz Ediliyor...' : 'Analiz Et ve İşaretle'}
            </button>

            {analyzedImage && (
                <div className="w-full flex flex-col items-center gap-4 mt-8 border-t pt-8">
                    <h3 className="text-xl font-bold text-gray-800">Analiz Sonucu</h3>

                    <img
                        src={analyzedImage}
                        alt="Analyzed"
                        className="w-full max-w-[600px] h-auto object-contain rounded-lg border-2 border-indigo-200"
                    />

                    {data && (
                        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200 w-full max-w-[600px]">
                            <h4 className="font-bold text-gray-700 mb-2">Tespit Edilen Veriler:</h4>
                            <ul className="list-disc list-inside text-gray-600">
                                <li>Göz Bebekleri Arası Mesafe (Piksel): <span className="font-mono font-bold text-indigo-600">{data.ipd} px</span></li>
                                <li>Vücut Dış Hattı: <span className="text-green-600 font-semibold">Çizildi</span></li>
                            </ul>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
