'use client';

import { useState, ChangeEvent } from 'react';

import { API_URL } from '../utils/config';

export default function ComparisonView() {
  const [beforeImage, setBeforeImage] = useState<File | null>(null);
  const [afterImage, setAfterImage] = useState<File | null>(null);
  const [beforePreview, setBeforePreview] = useState<string | null>(null);
  const [afterPreview, setAfterPreview] = useState<string | null>(null);
  const [alignedImage, setAlignedImage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [opacity, setOpacity] = useState(50);

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>, type: 'before' | 'after') => {
    const file = e.target.files?.[0];
    if (file) {
      if (type === 'before') {
        setBeforeImage(file);
        setBeforePreview(URL.createObjectURL(file));
      } else {
        setAfterImage(file);
        setAfterPreview(URL.createObjectURL(file));
      }
    }
  };

  const handleAlign = async () => {
    if (!beforeImage || !afterImage) return;

    setLoading(true);
    const formData = new FormData();
    formData.append('before_image', beforeImage);
    formData.append('after_image', afterImage);

    try {
      const response = await fetch(`${API_URL}/align`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        alert('Fotoğraflar işlenirken bir hata oluştu');
        throw new Error('Alignment failed');
      }

      const blob = await response.blob();
      setAlignedImage(URL.createObjectURL(blob));
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center gap-8 w-full max-w-4xl mx-auto p-4">
      <div className="grid grid-cols-2 gap-8 w-full">
        {/* Before Upload */}
        <div className="flex flex-col gap-2">
          <label className="font-bold text-lg text-gray-700">Before (Önce)</label>
          <input
            type="file"
            accept="image/*"
            onChange={(e) => handleFileChange(e, 'before')}
            className="block w-full text-sm text-gray-500
              file:mr-4 file:py-2 file:px-4
              file:rounded-full file:border-0
              file:text-sm file:font-semibold
              file:bg-violet-50 file:text-violet-700
              hover:file:bg-violet-100"
          />
          {beforePreview && (
            <img src={beforePreview} alt="Before" className="w-full h-64 object-contain bg-gray-100 rounded-lg" />
          )}
        </div>

        {/* After Upload */}
        <div className="flex flex-col gap-2">
          <label className="font-bold text-lg text-gray-700">After (Sonra)</label>
          <input
            type="file"
            accept="image/*"
            onChange={(e) => handleFileChange(e, 'after')}
            className="block w-full text-sm text-gray-500
              file:mr-4 file:py-2 file:px-4
              file:rounded-full file:border-0
              file:text-sm file:font-semibold
              file:bg-violet-50 file:text-violet-700
              hover:file:bg-violet-100"
          />
          {afterPreview && (
            <img src={afterPreview} alt="After" className="w-full h-64 object-contain bg-gray-100 rounded-lg" />
          )}
        </div>
      </div>

      <button
        onClick={handleAlign}
        disabled={!beforeImage || !afterImage || loading}
        className="px-8 py-3 bg-blue-600 text-white font-bold rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {loading ? 'İşleniyor...' : 'Fotoğrafları Hizala ve Karşılaştır'}
      </button>

      {/* Comparison Area */}
      {alignedImage && beforePreview && (
        <div className="w-full flex flex-col items-center gap-4 mt-8 border-t pt-8">
          <h2 className="text-2xl font-bold">Karşılaştırma</h2>

          <div className="relative w-full max-w-[500px] aspect-[3/4] border border-gray-300 rounded-lg overflow-hidden bg-gray-100">
            {/* Base Image (Before) */}
            <img
              src={beforePreview}
              alt="Base"
              className="absolute top-0 left-0 w-full h-full object-contain"
            />

            {/* Overlay Image (Aligned After) */}
            <img
              src={alignedImage}
              alt="Overlay"
              className="absolute top-0 left-0 w-full h-full object-contain"
              style={{ opacity: opacity / 100 }}
            />
          </div>

          <div className="w-full max-w-[500px] flex flex-col gap-2">
            <label className="flex justify-between font-semibold text-gray-700">
              <span>Before (0%)</span>
              <span>After (100%)</span>
            </label>
            <input
              type="range"
              min="0"
              max="100"
              value={opacity}
              onChange={(e) => setOpacity(Number(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
          </div>
        </div>
      )}
    </div>
  );
}
